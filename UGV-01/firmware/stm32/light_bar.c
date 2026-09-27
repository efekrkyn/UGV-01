#include "light_bar.h"

/* Power model (verify on the chosen strip): 20 mA per channel at 255 and 5 mW idle per LED, 5 V. */
#define IDLE_MW (UGV_LIGHT_LEDS * 5u)
#define CHANNEL_SUM_MAX ((UGV_LIGHT_CAP_MW - IDLE_MW) * 255u / 100u)

static const UgvRgb COLOUR[UGV_LIGHT_MODES] = {
    [UGV_LIGHT_IDLE] = {255, 255, 255}, [UGV_LIGHT_ARMED] = {255, 255, 0},
    [UGV_LIGHT_DRIVING] = {0, 255, 0},  [UGV_LIGHT_AI] = {0, 0, 255},
    [UGV_LIGHT_FAULT] = {255, 0, 0},    [UGV_LIGHT_ESTOP] = {255, 0, 0},
};

uint32_t ugv_light_power_mw(const UgvRgb px[UGV_LIGHT_LEDS]) {
    uint32_t sum = 0;
    for (int i = 0; i < UGV_LIGHT_LEDS; ++i) sum += px[i].r + px[i].g + px[i].b;
    return IDLE_MW + sum * 100u / 255u;
}

void ugv_light_frame(UgvRgb out[UGV_LIGHT_LEDS], uint8_t mode, uint8_t battery_pct, uint32_t now_ms) {
    const UgvRgb c = COLOUR[mode < UGV_LIGHT_MODES ? mode : UGV_LIGHT_FAULT];
    const uint8_t pct = battery_pct > 100 ? 100 : battery_pct;
    uint32_t lit = (pct * UGV_LIGHT_LEDS + 99u) / 100u;       /* battery bar */
    if (mode == UGV_LIGHT_FAULT || mode >= UGV_LIGHT_MODES) lit = UGV_LIGHT_LEDS;
    if (mode == UGV_LIGHT_ESTOP) lit = now_ms % 500u < 250u ? UGV_LIGHT_LEDS : 0; /* 2 Hz blink */
    uint32_t sum = 0;
    for (uint32_t i = 0; i < UGV_LIGHT_LEDS; ++i) {
        out[i] = i < lit ? c : (UgvRgb){0, 0, 0};
        sum += out[i].r + out[i].g + out[i].b;
    }
    if (sum <= CHANNEL_SUM_MAX) return;
    for (int i = 0; i < UGV_LIGHT_LEDS; ++i) { /* brightness cap: scale all channels together */
        out[i].r = (uint8_t)(out[i].r * CHANNEL_SUM_MAX / sum);
        out[i].g = (uint8_t)(out[i].g * CHANNEL_SUM_MAX / sum);
        out[i].b = (uint8_t)(out[i].b * CHANNEL_SUM_MAX / sum);
    }
}
