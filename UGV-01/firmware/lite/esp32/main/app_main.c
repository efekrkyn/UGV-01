/* A3 Lite ESP32-S3 firmware (L4a DD86, ToF L4b DD87): the host-tested core (lite_core.c) on the real peripherals.
   Builds with ESP-IDF 5.3.2 (command in tests/README.md); not yet run on hardware, bring-up and TL1-TL5 remain.
   Every safety decision stays in lite_core.c; this file only moves bits. */
#include <fcntl.h>
#include <string.h>

#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "driver/mcpwm_prelude.h"
#include "driver/pulse_cnt.h"
#include "driver/rmt_tx.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_task_wdt.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lwip/sockets.h"
#include "nvs.h"
#include "nvs_flash.h"

#include "board_math.h"
#include "lite_core.h"
#include "pins.h"
#include "vl53l0x.h"

static const char *TAG = "ugv";

/* ---- settings (NVS namespace "ugv"; written at bring-up, never in the repo) */
typedef struct {
    uint8_t key[32];
    size_t key_len;
    char ssid[33], pass[65];
    uint16_t port, vbat_cal;
    uint32_t pca_osc_hz;
    int8_t motor_pol[LITE_MOTORS];
} Settings;
static Settings cfg = {.port = 4210, .vbat_cal = 1000, .pca_osc_hz = 25000000u, .motor_pol = {1, 1, 1, 1}};

static void settings_load(void) {
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);
    nvs_handle_t h;
    if (nvs_open("ugv", NVS_READONLY, &h) != ESP_OK) {
        ESP_LOGE(TAG, "no 'ugv' NVS namespace: link key and Wi-Fi missing, the core stays IDLE");
        return;
    }
    size_t n = sizeof cfg.key;
    if (nvs_get_blob(h, "link_key", cfg.key, &n) == ESP_OK) cfg.key_len = n;
    n = sizeof cfg.ssid;
    nvs_get_str(h, "ssid", cfg.ssid, &n);
    n = sizeof cfg.pass;
    nvs_get_str(h, "pass", cfg.pass, &n);
    nvs_get_u16(h, "port", &cfg.port);
    nvs_get_u16(h, "vbat_cal", &cfg.vbat_cal);      /* per mille, from a multimeter reading (TL1) */
    nvs_get_u32(h, "pca_osc_hz", &cfg.pca_osc_hz);  /* measured PCA9685 oscillator (TL4 pulse check) */
    n = sizeof cfg.motor_pol;
    nvs_get_blob(h, "motor_pol", cfg.motor_pol, &n);  /* +1 / -1 per motor FL, FR, RL, RR */
    nvs_close(h);
    if (cfg.key_len != 32) ESP_LOGE(TAG, "link key missing or not 32 bytes: every datagram will be refused");
}

/* ---- ACT_EN, servo /OE and the E-stop interrupt */
static volatile uint32_t estop_edge;

static void IRAM_ATTR estop_isr(void *arg) {
    (void)arg;
    gpio_set_level(PIN_ACT_EN, 0);  /* drivers and servo rails off at once, before the core's next tick */
    gpio_set_level(PIN_SERVO_OE, 1);
    estop_edge = 1;
}

static void safety_io_init(void) {
    const gpio_config_t out = {.pin_bit_mask = 1ull << PIN_ACT_EN | 1ull << PIN_SERVO_OE, .mode = GPIO_MODE_OUTPUT};
    gpio_set_level(PIN_ACT_EN, 0);
    gpio_set_level(PIN_SERVO_OE, 1);
    ESP_ERROR_CHECK(gpio_config(&out));
    /* 10k pull-up + 1k/100n on the board: closed NC contact = Low (released), open or broken wire = High. */
    const gpio_config_t in = {.pin_bit_mask = 1ull << PIN_ESTOP_SENSE, .mode = GPIO_MODE_INPUT,
                              .intr_type = GPIO_INTR_POSEDGE};
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(PIN_ESTOP_SENSE, estop_isr, NULL));
}

/* ---- motors: TB6612 IN1/IN2 on MCPWM, 20 kHz */
enum { MOTOR_RES_HZ = 10000000, MOTOR_TICKS = MOTOR_RES_HZ / 20000 };
static mcpwm_cmpr_handle_t cmpr[LITE_MOTORS][2];
static mcpwm_gen_handle_t gen[LITE_MOTORS][2];

static void motors_init(void) {
    static const int pins[LITE_MOTORS][2] = {{PIN_M_FL_IN1, PIN_M_FL_IN2}, {PIN_M_FR_IN1, PIN_M_FR_IN2},
                                             {PIN_M_RL_IN1, PIN_M_RL_IN2}, {PIN_M_RR_IN1, PIN_M_RR_IN2}};
    mcpwm_timer_handle_t timer[2];
    for (int g = 0; g < 2; ++g) {
        const mcpwm_timer_config_t tc = {.group_id = g, .clk_src = MCPWM_TIMER_CLK_SRC_DEFAULT,
                                         .resolution_hz = MOTOR_RES_HZ, .period_ticks = MOTOR_TICKS,
                                         .count_mode = MCPWM_TIMER_COUNT_MODE_UP};
        ESP_ERROR_CHECK(mcpwm_new_timer(&tc, &timer[g]));
    }
    for (int m = 0; m < LITE_MOTORS; ++m) {
        const int g = m < 3 ? 0 : 1;  /* three operators per group */
        mcpwm_oper_handle_t op;
        const mcpwm_operator_config_t oc = {.group_id = g};
        ESP_ERROR_CHECK(mcpwm_new_operator(&oc, &op));
        ESP_ERROR_CHECK(mcpwm_operator_connect_timer(op, timer[g]));
        for (int k = 0; k < 2; ++k) {
            const mcpwm_comparator_config_t cc = {.flags.update_cmp_on_tez = true};
            ESP_ERROR_CHECK(mcpwm_new_comparator(op, &cc, &cmpr[m][k]));
            ESP_ERROR_CHECK(mcpwm_comparator_set_compare_value(cmpr[m][k], 0));
            const mcpwm_generator_config_t gc = {.gen_gpio_num = pins[m][k]};
            ESP_ERROR_CHECK(mcpwm_new_generator(op, &gc, &gen[m][k]));
            ESP_ERROR_CHECK(mcpwm_generator_set_action_on_timer_event(gen[m][k],
                MCPWM_GEN_TIMER_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, MCPWM_TIMER_EVENT_EMPTY, MCPWM_GEN_ACTION_HIGH)));
            ESP_ERROR_CHECK(mcpwm_generator_set_action_on_compare_event(gen[m][k],
                MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, cmpr[m][k], MCPWM_GEN_ACTION_LOW)));
            ESP_ERROR_CHECK(mcpwm_generator_set_force_level(gen[m][k], 0, true));  /* coast until the core drives */
        }
    }
    for (int g = 0; g < 2; ++g) {
        ESP_ERROR_CHECK(mcpwm_timer_enable(timer[g]));
        ESP_ERROR_CHECK(mcpwm_timer_start_stop(timer[g], MCPWM_TIMER_START_NO_STOP));
    }
}

static void motor_pin(int m, int k, uint16_t permil) {
    if (!permil) {  /* 0 %: hold Low (a compare of 0 would race the period start) */
        mcpwm_generator_set_force_level(gen[m][k], 0, true);
        return;
    }
    mcpwm_comparator_set_compare_value(cmpr[m][k], (uint32_t)permil * MOTOR_TICKS / 1000);
    mcpwm_generator_set_force_level(gen[m][k], -1, true);
}

/* ---- encoders: channel A, both edges, one PCNT unit each, accumulated past the 16-bit counter */
enum { PCNT_LIMIT = 30000 };
static pcnt_unit_handle_t pcnt[LITE_MOTORS];

static void encoders_init(void) {
    static const int pins[LITE_MOTORS] = {PIN_ENC_FL_A, PIN_ENC_FR_A, PIN_ENC_RL_A, PIN_ENC_RR_A};
    for (int m = 0; m < LITE_MOTORS; ++m) {
        const pcnt_unit_config_t uc = {.low_limit = -PCNT_LIMIT, .high_limit = PCNT_LIMIT, .flags.accum_count = true};
        ESP_ERROR_CHECK(pcnt_new_unit(&uc, &pcnt[m]));
        const pcnt_glitch_filter_config_t fc = {.max_glitch_ns = 1000};
        ESP_ERROR_CHECK(pcnt_unit_set_glitch_filter(pcnt[m], &fc));
        const pcnt_chan_config_t ch = {.edge_gpio_num = pins[m], .level_gpio_num = -1};
        pcnt_channel_handle_t c;
        ESP_ERROR_CHECK(pcnt_new_channel(pcnt[m], &ch, &c));
        ESP_ERROR_CHECK(pcnt_channel_set_edge_action(c, PCNT_CHANNEL_EDGE_ACTION_INCREASE, PCNT_CHANNEL_EDGE_ACTION_INCREASE));
        ESP_ERROR_CHECK(pcnt_unit_add_watch_point(pcnt[m], PCNT_LIMIT));  /* needed for accumulation */
        ESP_ERROR_CHECK(pcnt_unit_enable(pcnt[m]));
        ESP_ERROR_CHECK(pcnt_unit_clear_count(pcnt[m]));
        ESP_ERROR_CHECK(pcnt_unit_start(pcnt[m]));
    }
}

static void encoders_read(uint32_t enc[LITE_MOTORS]) {
    for (int m = 0; m < LITE_MOTORS; ++m) {
        int count = 0;
        pcnt_unit_get_count(pcnt[m], &count);
        enc[m] = (uint32_t)count;  /* cumulative edges; the core signs them by the commanded direction */
    }
}

/* ---- PCA9685 servo driver on I2C0 (shared with the VL53L0X pair) */
static i2c_master_bus_handle_t i2c_bus;
static i2c_master_dev_handle_t pca;
static uint8_t pca_pre;
static uint16_t pca_last[UGV_SERVO_COUNT];

static int pca_write(uint8_t reg, const uint8_t *data, size_t n) {
    uint8_t buf[5];
    buf[0] = reg;
    memcpy(buf + 1, data, n);
    if (i2c_master_transmit(pca, buf, n + 1, 5) == ESP_OK) return 1;
    ESP_LOGW(TAG, "PCA9685 write 0x%02x failed", reg);
    return 0;
}

static void pca_init(void) {
    const i2c_master_bus_config_t bc = {.i2c_port = I2C_NUM_0, .sda_io_num = PIN_I2C_SDA, .scl_io_num = PIN_I2C_SCL,
                                        .clk_source = I2C_CLK_SRC_DEFAULT, .glitch_ignore_cnt = 7,
                                        .flags.enable_internal_pullup = true};
    ESP_ERROR_CHECK(i2c_new_master_bus(&bc, &i2c_bus));
    const i2c_device_config_t dc = {.dev_addr_length = I2C_ADDR_BIT_LEN_7, .device_address = PCA9685_ADDR,
                                    .scl_speed_hz = 400000};
    ESP_ERROR_CHECK(i2c_master_bus_add_device(i2c_bus, &dc, &pca));
    pca_pre = ugv_pca9685_prescale(cfg.pca_osc_hz, PCA9685_PWM_HZ);
    const uint8_t sleep_ai = 0x30, wake_ai = 0x20, totem = 0x04, all_off[4] = {0, 0, 0, 0x10};
    pca_write(0x00, &sleep_ai, 1);  /* MODE1: SLEEP + auto-increment; the prescale is writable only asleep */
    pca_write(0xFE, &pca_pre, 1);
    pca_write(0x00, &wake_ai, 1);
    vTaskDelay(pdMS_TO_TICKS(2));   /* oscillator start-up (500 us) */
    pca_write(0x01, &totem, 1);     /* MODE2: totem-pole outputs */
    pca_write(0xFA, all_off, 4);    /* ALL_LED: full off until the core asks for pulses */
}

static void pca_apply(const uint16_t us[UGV_SERVO_COUNT]) {
    for (int k = 0; k < UGV_SERVO_COUNT; ++k) {
        if (us[k] == pca_last[k]) continue;
        uint8_t regs[4];
        ugv_pca9685_led_regs(us[k] ? ugv_pca9685_counts(us[k], cfg.pca_osc_hz, pca_pre) : 0, regs);
        if (pca_write((uint8_t)(0x06 + 4 * k), regs, 4)) pca_last[k] = us[k];  /* a failed write retries next tick */
    }
}

/* ---- front VL53L0X pair on the same bus (vl53l0x.c): one device handle per address it can answer on */
static i2c_master_dev_handle_t tof_h[2];  /* [0] boot address 0x29, [1] TOF_ADDR[1] */
static UgvTof tof[2];

static int tof_write(void *ctx, uint8_t addr, const uint8_t *buf, size_t n) {
    (void)ctx;
    return i2c_master_transmit(tof_h[addr == TOF_ADDR[1]], buf, n, 5) == ESP_OK ? 0 : -1;
}

static int tof_read(void *ctx, uint8_t addr, uint8_t reg, uint8_t *buf, size_t n) {
    (void)ctx;
    return i2c_master_transmit_receive(tof_h[addr == TOF_ADDR[1]], &reg, 1, buf, n, 5) == ESP_OK ? 0 : -1;
}

static void tof_xshut(void *ctx, int level) { (void)ctx, gpio_set_level(PIN_TOF_XSHUT, level); }
static void tof_delay(void *ctx, uint32_t ms) { (void)ctx, vTaskDelay(pdMS_TO_TICKS(ms)); }
static const UgvI2cBus tof_bus = {tof_write, tof_read, tof_xshut, tof_delay, NULL};

static void tof_init(void) {  /* after pca_init (the bus) and before the control task (blocks ~0.1 s) */
    const gpio_config_t x = {.pin_bit_mask = 1ull << PIN_TOF_XSHUT, .mode = GPIO_MODE_OUTPUT};
    gpio_set_level(PIN_TOF_XSHUT, 0);
    ESP_ERROR_CHECK(gpio_config(&x));
    for (int i = 0; i < 2; ++i) {
        const i2c_device_config_t dc = {.dev_addr_length = I2C_ADDR_BIT_LEN_7, .scl_speed_hz = 400000,
                                        .device_address = i ? TOF_ADDR[1] : UGV_TOF_BOOT_ADDR};
        ESP_ERROR_CHECK(i2c_master_bus_add_device(i2c_bus, &dc, &tof_h[i]));
    }
    tof[0].addr = TOF_ADDR[0], tof[1].addr = TOF_ADDR[1];
    const int n = ugv_tof_pair_start(&tof_bus, tof);
    if (n < 2) ESP_LOGE(TAG, "%d of 2 VL53L0X ranging: forward motion stays blocked", n);
}

/* ---- battery on ADC1 channel 0 (GPIO1), 12 dB, curve-fitting calibration */
static adc_oneshot_unit_handle_t adc;
static adc_cali_handle_t adc_cal;

static void battery_init(void) {
    const adc_oneshot_unit_init_cfg_t uc = {.unit_id = ADC_UNIT_1};
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&uc, &adc));
    const adc_oneshot_chan_cfg_t cc = {.atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT};
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc, ADC_CHANNEL_0, &cc));  /* GPIO1 = ADC1_CH0 on the S3 */
    const adc_cali_curve_fitting_config_t cf = {.unit_id = ADC_UNIT_1, .chan = ADC_CHANNEL_0,
                                                .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT};
    ESP_ERROR_CHECK(adc_cali_create_scheme_curve_fitting(&cf, &adc_cal));
}

static uint16_t battery_read(void) {
    int sum = 0;
    for (int i = 0; i < 4; ++i) {
        int raw = 0, mv = 0;
        adc_oneshot_read(adc, ADC_CHANNEL_0, &raw);
        adc_cali_raw_to_voltage(adc_cal, raw, &mv);
        sum += mv;
    }
    return ugv_vbat_mv((uint32_t)(sum / 4), cfg.vbat_cal);
}

/* ---- status light: 8 x WS2812 (GRB) on RMT, 10 MHz */
static rmt_channel_handle_t rmt;
static rmt_encoder_handle_t rmt_enc;

static void light_init(void) {
    const rmt_tx_channel_config_t tc = {.gpio_num = PIN_LIGHT_DATA, .clk_src = RMT_CLK_SRC_DEFAULT,
                                        .resolution_hz = 10000000, .mem_block_symbols = 64, .trans_queue_depth = 2};
    ESP_ERROR_CHECK(rmt_new_tx_channel(&tc, &rmt));
    const rmt_bytes_encoder_config_t bc = {.bit0 = {.level0 = 1, .duration0 = 3, .level1 = 0, .duration1 = 9},
                                           .bit1 = {.level0 = 1, .duration0 = 9, .level1 = 0, .duration1 = 3},
                                           .flags.msb_first = 1};
    ESP_ERROR_CHECK(rmt_new_bytes_encoder(&bc, &rmt_enc));
    ESP_ERROR_CHECK(rmt_enable(rmt));
}

static void light_send(const UgvRgb px[UGV_LIGHT_LEDS]) {
    static uint8_t grb[3 * UGV_LIGHT_LEDS];  /* static: the transfer outlives this call; the 20 ms gap is the reset */
    for (int i = 0; i < UGV_LIGHT_LEDS; ++i) grb[3 * i] = px[i].g, grb[3 * i + 1] = px[i].r, grb[3 * i + 2] = px[i].b;
    const rmt_transmit_config_t t = {.loop_count = 0};
    rmt_transmit(rmt, rmt_enc, grb, sizeof grb, &t);
}

/* ---- Wi-Fi station + UDP */
static void wifi_event(void *arg, esp_event_base_t base, int32_t id, void *data) {
    (void)arg, (void)data;
    if (base == WIFI_EVENT && (id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED)) esp_wifi_connect();
}

static void wifi_start(void) {
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();
    const wifi_init_config_t ic = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&ic));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event, NULL));
    wifi_config_t wc = {0};
    strncpy((char *)wc.sta.ssid, cfg.ssid, sizeof wc.sta.ssid);
    strncpy((char *)wc.sta.password, cfg.pass, sizeof wc.sta.password);
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wc));
    ESP_ERROR_CHECK(esp_wifi_start());
    esp_wifi_set_ps(WIFI_PS_NONE);  /* 20 ms lease cadence: no modem sleep latency */
}

static int udp_open(uint16_t port) {
    const int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    const struct sockaddr_in a = {.sin_family = AF_INET, .sin_port = htons(port), .sin_addr.s_addr = htonl(INADDR_ANY)};
    if (s < 0 || bind(s, (const struct sockaddr *)&a, sizeof a) < 0) return -1;
    fcntl(s, F_SETFL, O_NONBLOCK);
    return s;
}

/* ---- the 20 ms control loop */
static LiteCore core;

static int io_estop(void *ctx) { (void)ctx; return estop_edge || gpio_get_level(PIN_ESTOP_SENSE); }
static void io_act_en(void *ctx, int level) { (void)ctx, gpio_set_level(PIN_ACT_EN, level); }
static void io_servo_oe(void *ctx, int level) { (void)ctx, gpio_set_level(PIN_SERVO_OE, level); }
static const UgvEnableIo enable_io = {io_estop, io_act_en, io_servo_oe, NULL};

static void apply(const LiteOutputs *out) {
    if (!out->act_en) {  /* off: enables first, then the outputs the core already zeroed */
        gpio_set_level(PIN_SERVO_OE, 1);
        gpio_set_level(PIN_ACT_EN, 0);
    }
    for (int m = 0; m < LITE_MOTORS; ++m) {
        uint16_t in1, in2;
        ugv_motor_inputs(out->duty_permil[m], cfg.motor_pol[m], &in1, &in2);
        motor_pin(m, 0, in1);
        motor_pin(m, 1, in2);
    }
    pca_apply(out->servo_us);
    if (out->act_en) ugv_enable_actuators(&enable_io);  /* E-stop checked before and after the writes (board_math.c) */
    light_send(out->light);
}

static void control_task(void *arg) {
    const int sock = (int)(intptr_t)arg;
    struct sockaddr_in peer = {0};
    int have_peer = 0;
    ESP_ERROR_CHECK(esp_task_wdt_add(NULL));
    TickType_t wake = xTaskGetTickCount();
    for (;;) {
        vTaskDelayUntil(&wake, pdMS_TO_TICKS(LITE_TICK_MS));
        const uint32_t now = (uint32_t)(esp_timer_get_time() / 1000);
        uint8_t buf[64];
        struct sockaddr_in from;
        socklen_t len = sizeof from;
        int n;
        while (sock >= 0 && (n = recvfrom(sock, buf, sizeof buf, 0, (struct sockaddr *)&from, &len)) > 0) {
            if (lite_core_receive(&core, buf, (size_t)n, now)) peer = from, have_peer = 1;  /* only an authentic sender */
            len = sizeof from;
        }
        LiteInputs in = {0};
        in.vbat_mv = battery_read();
        in.estop_edge = (uint8_t)__atomic_exchange_n(&estop_edge, 0, __ATOMIC_SEQ_CST);
        in.estop_level = (uint8_t)gpio_get_level(PIN_ESTOP_SENSE);
        ugv_tof_pair_poll(&tof_bus, tof, now, in.tof_mm);  /* 0 = no fresh reading: the core blocks forward motion */
        encoders_read(in.enc);
        const LiteOutputs out = lite_core_tick(&core, &in, now);
        apply(&out);
        uint8_t tlm[4][UGV_LITE_DGRAM_LEN];
        const int k = lite_core_telemetry(&core, now, tlm);
        for (int i = 0; have_peer && i < k; ++i)
            sendto(sock, tlm[i], UGV_LITE_DGRAM_LEN, 0, (const struct sockaddr *)&peer, sizeof peer);
        esp_task_wdt_reset();
    }
}

void app_main(void) {
    safety_io_init();  /* ACT_EN Low and /OE High before anything else */
    settings_load();
    motors_init();
    encoders_init();
    pca_init();
    tof_init();
    battery_init();
    light_init();
    lite_core_init(&core, cfg.key, cfg.key_len, (uint32_t)(esp_timer_get_time() / 1000));
    wifi_start();
    const int sock = udp_open(cfg.port);
    if (sock < 0) ESP_LOGE(TAG, "UDP port %u not open: no link, the core stays IDLE", cfg.port);
    xTaskCreatePinnedToCore(control_task, "control", 6144, (void *)(intptr_t)sock, configMAX_PRIORITIES - 2, NULL, 1);
}
