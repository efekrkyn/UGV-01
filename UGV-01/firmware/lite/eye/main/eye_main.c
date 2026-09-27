/* A3 Lite eye (L4b, DD88): ESP32-CAM (AI-Thinker, OV2640) serving the latest JPEG at GET /capture, port 80.
   The MacBook gateway fetches it (UGV_EYE_URLS). Builds with ESP-IDF 5.3.2 + espressif/esp32-camera
   (tests/README.md); not yet run on hardware. The endpoint has no authentication: keep the eyes on the robot's own
   SSID (lite_software_A3.md). */
#include <string.h>

#include "driver/gpio.h"
#include "esp_camera.h"
#include "esp_event.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "nvs.h"
#include "nvs_flash.h"

static const char *TAG = "eye";

/* AI-Thinker ESP32-CAM camera wiring (module schematic). VGA JPEG, quality 12 (lite_software_A3.md); two
   buffers in PSRAM and "latest" grab mode, so /capture returns the newest frame rather than a queued old one. */
static const camera_config_t CAMERA = {
    .pin_pwdn = 32, .pin_reset = -1, .pin_xclk = 0, .pin_sccb_sda = 26, .pin_sccb_scl = 27,
    .pin_d7 = 35, .pin_d6 = 34, .pin_d5 = 39, .pin_d4 = 36, .pin_d3 = 21, .pin_d2 = 19, .pin_d1 = 18, .pin_d0 = 5,
    .pin_vsync = 25, .pin_href = 23, .pin_pclk = 22,
    .xclk_freq_hz = 20000000, .ledc_timer = LEDC_TIMER_0, .ledc_channel = LEDC_CHANNEL_0,
    .pixel_format = PIXFORMAT_JPEG, .frame_size = FRAMESIZE_VGA, .jpeg_quality = 12,
    .fb_count = 2, .fb_location = CAMERA_FB_IN_PSRAM, .grab_mode = CAMERA_GRAB_LATEST,
};
enum { FLASH_LED = 4 };

/* NVS namespace "ugv", written at bring-up. Exposure, gain and white balance stay automatic until the stereo
   calibration writes the same fixed values into both eyes, so the pair sees the same brightness and colour. */
static struct {
    char ssid[33], pass[65];
    int32_t aec, agc, wb_mode;  /* aec 0..1200 and agc 0..30 (-1 = auto); wb_mode 1..4 preset (0 = auto) */
} cfg = {.aec = -1, .agc = -1};

static void settings_load(void) {
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);
    nvs_handle_t h;
    if (nvs_open("ugv", NVS_READONLY, &h) != ESP_OK) {
        ESP_LOGE(TAG, "no 'ugv' NVS namespace: Wi-Fi missing");
        return;
    }
    size_t n = sizeof cfg.ssid;
    nvs_get_str(h, "ssid", cfg.ssid, &n);
    n = sizeof cfg.pass;
    nvs_get_str(h, "pass", cfg.pass, &n);
    nvs_get_i32(h, "aec", &cfg.aec);
    nvs_get_i32(h, "agc", &cfg.agc);
    nvs_get_i32(h, "wb_mode", &cfg.wb_mode);
    nvs_close(h);
}

static void camera_start(void) {
    ESP_ERROR_CHECK(esp_camera_init(&CAMERA));  /* a failed init aborts and reboots: usually a supply dip */
    sensor_t *s = esp_camera_sensor_get();
    if (cfg.aec >= 0) s->set_exposure_ctrl(s, 0), s->set_aec_value(s, cfg.aec);
    if (cfg.agc >= 0) s->set_gain_ctrl(s, 0), s->set_agc_gain(s, cfg.agc);
    if (cfg.wb_mode > 0) s->set_wb_mode(s, cfg.wb_mode);  /* 1 sunny, 2 cloudy, 3 office, 4 home */
}

static void wifi_event(void *arg, esp_event_base_t base, int32_t id, void *data) {
    (void)arg, (void)data;
    if (base == WIFI_EVENT && (id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED)) esp_wifi_connect();
}

static void wifi_start(void) {  /* fixed address from a DHCP lease reservation on the router */
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
    esp_wifi_set_ps(WIFI_PS_NONE);  /* no modem-sleep delay on a capture request */
}

static esp_err_t capture(httpd_req_t *req) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGW(TAG, "no frame");
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }
    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    const esp_err_t err = httpd_resp_send(req, (const char *)fb->buf, (ssize_t)fb->len);
    esp_camera_fb_return(fb);
    return err;
}

void app_main(void) {
    gpio_reset_pin(FLASH_LED);  /* the module's white LED: kept off, it would dazzle whoever the eyes look at */
    gpio_set_direction(FLASH_LED, GPIO_MODE_OUTPUT);
    gpio_set_level(FLASH_LED, 0);
    settings_load();
    camera_start();
    wifi_start();
    httpd_handle_t server = NULL;
    const httpd_config_t hc = HTTPD_DEFAULT_CONFIG();
    ESP_ERROR_CHECK(httpd_start(&server, &hc));
    const httpd_uri_t uri = {.uri = "/capture", .method = HTTP_GET, .handler = capture};
    ESP_ERROR_CHECK(httpd_register_uri_handler(server, &uri));
}
