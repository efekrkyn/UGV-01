#include "servo_control.h"

#define RAIL_SETTLE_MS 100u
#define OVER_INSTANT_MA 5500u
#define OVER_SUSTAINED_MA 3500u
#define OVER_SUSTAINED_MS 200u

/* Pulse ends are calibration values (MG90S/MG996R ~11.1 us/deg, DS3218MG 270 deg ~7.41 us/deg), trimmed per unit
   at bring-up. M3 (DD73): each arm joint's range is centred on its servo's travel; the DS3218MG drives the
   shoulder directly (225 of 270 deg). Limits = config geometry.arm.limits_deg (tests/check_lite_gateway.py). */
static const UgvServoJoint JOINTS[UGV_SERVO_COUNT] = {
    [UGV_SERVO_PAN] = {-9000, 9000, 0, 12000, 500, 2500},
    [UGV_SERVO_TILT] = {-6000, 3000, 0, 9000, 833, 1833},
    [UGV_SERVO_SHOULDER] = {-4500, 18000, 18000, 6000, 667, 2333},
    [UGV_SERVO_TWIST] = {-8000, 9000, 9000, 9000, 556, 2444},
    [UGV_SERVO_ELBOW] = {-3000, 13500, 0, 9000, 583, 2417},
    [UGV_SERVO_WRIST] = {-7000, 10000, 0, 9000, 556, 2444},
    [UGV_SERVO_ROLL] = {-8500, 8500, 0, 18000, 556, 2444},
    [UGV_SERVO_GRIPPER] = {0, 9000, 0, 18000, 1500, 2500},
};

void ugv_servo_init(UgvServo *s) {
    *s = (UgvServo){0};
    for (int j = 0; j < UGV_SERVO_COUNT; ++j) {
        s->joint[j] = JOINTS[j];
        s->pos_cdeg[j] = s->target_cdeg[j] = JOINTS[j].park_cdeg;
    }
}

int ugv_servo_set_target(UgvServo *s, int joint, int32_t cdeg) {
    if (joint < 0 || joint >= UGV_SERVO_COUNT || s->fault ||
        cdeg < s->joint[joint].min_cdeg || cdeg > s->joint[joint].max_cdeg) return 0;
    s->target_cdeg[joint] = cdeg;
    return 1;
}

static void pwm_off_then_rail(UgvServo *s) {
    s->pwm_on = 0;
    s->off_pending = s->rail_req; /* rail request drops on the next tick, after the PWM is Low */
}

void ugv_servo_enable(UgvServo *s, uint8_t want, uint32_t now_ms) {
    if (want && !s->fault && !s->rail_req) {
        s->rail_req = 1;
        s->off_pending = 0;
        s->rail_on_ms = now_ms;
    } else if (!want) {
        pwm_off_then_rail(s);
    }
}

void ugv_servo_tick(UgvServo *s, uint32_t now_ms, uint16_t rail_ma, uint8_t permit) {
    const uint32_t dt = now_ms - s->last_ms;
    const uint8_t was_on = s->pwm_on;
    s->last_ms = now_ms;
    if (!permit) { /* hardware already cut the rail: follow it at once */
        s->pwm_on = s->rail_req = s->off_pending = s->over_active = 0;
        return;
    }
    if (s->off_pending) {
        s->rail_req = s->off_pending = 0;
        return;
    }
    /* ponytail: continuous-threshold timer, not a window mean; move to a 200 ms mean if PWM ripple trips it */
    if (s->pwm_on && rail_ma > OVER_SUSTAINED_MA) {
        if (!s->over_active) {
            s->over_active = 1;
            s->over_since_ms = now_ms;
        }
    } else {
        s->over_active = 0;
    }
    if (s->pwm_on && (rail_ma > OVER_INSTANT_MA ||
                      (s->over_active && now_ms - s->over_since_ms >= OVER_SUSTAINED_MS))) {
        s->fault = 1;
        pwm_off_then_rail(s);
        return;
    }
    if (s->rail_req && !s->pwm_on && now_ms - s->rail_on_ms >= RAIL_SETTLE_MS) s->pwm_on = 1;
    if (!was_on) return;
    for (int j = 0; j < UGV_SERVO_COUNT; ++j) {
        const int32_t step = (int32_t)((int64_t)s->joint[j].rate_cdeg_s * dt / 1000);
        const int32_t error = s->target_cdeg[j] - s->pos_cdeg[j];
        s->pos_cdeg[j] += error > step ? step : error < -step ? -step : error;
    }
}

uint16_t ugv_servo_pulse_us(const UgvServo *s, int joint) {
    if (!s->pwm_on || joint < 0 || joint >= UGV_SERVO_COUNT) return 0;
    const UgvServoJoint *j = &s->joint[joint];
    return (uint16_t)(j->us_at_min + (int64_t)(s->pos_cdeg[joint] - j->min_cdeg) *
                      (j->us_at_max - j->us_at_min) / (j->max_cdeg - j->min_cdeg));
}

int ugv_servo_clear_fault(UgvServo *s) {
    if (s->rail_req) return 0;
    s->fault = s->over_active = 0;
    return 1;
}
