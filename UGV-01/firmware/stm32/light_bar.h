#ifndef UGV_LIGHT_BAR_H
#define UGV_LIGHT_BAR_H

#include <stdint.h>

/* A2 front status bar: 8 addressable LEDs, mode colour + battery bar, <= 0.5 W. */
#define UGV_LIGHT_LEDS 8
#define UGV_LIGHT_CAP_MW 500u

enum { UGV_LIGHT_IDLE, UGV_LIGHT_ARMED, UGV_LIGHT_DRIVING, UGV_LIGHT_AI, UGV_LIGHT_FAULT,
       UGV_LIGHT_ESTOP, UGV_LIGHT_MODES };

typedef struct { uint8_t r, g, b; } UgvRgb;

void ugv_light_frame(UgvRgb out[UGV_LIGHT_LEDS], uint8_t mode, uint8_t battery_pct, uint32_t now_ms);
uint32_t ugv_light_power_mw(const UgvRgb px[UGV_LIGHT_LEDS]);

#endif
