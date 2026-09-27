#ifndef UGV_SERVO_CONTROL_H
#define UGV_SERVO_CONTROL_H

#include <stdint.h>

/* Head and M3 arm servos, in PCA9685 channel order (config/esp32_pinmap.json). Angles in centi-degrees, arm
   joints as in config geometry.arm: shoulder 0 = level forward, +up; twist + bends the elbow toward the body;
   elbow and wrist + down; park = the CAD stow pose (shoulder 180, twist 90). */
enum { UGV_SERVO_PAN, UGV_SERVO_TILT, UGV_SERVO_SHOULDER, UGV_SERVO_TWIST, UGV_SERVO_ELBOW, UGV_SERVO_WRIST,
       UGV_SERVO_ROLL, UGV_SERVO_GRIPPER, UGV_SERVO_COUNT };

typedef struct {
    int32_t min_cdeg, max_cdeg, park_cdeg, rate_cdeg_s;
    uint16_t us_at_min, us_at_max; /* calibration: pulse at each end of travel */
} UgvServoJoint;

typedef struct {
    UgvServoJoint joint[UGV_SERVO_COUNT];
    int32_t pos_cdeg[UGV_SERVO_COUNT], target_cdeg[UGV_SERVO_COUNT];
    uint32_t last_ms, rail_on_ms, over_since_ms;
    uint8_t rail_req, pwm_on, off_pending, fault, over_active;
} UgvServo;

void ugv_servo_init(UgvServo *s);
int ugv_servo_set_target(UgvServo *s, int joint, int32_t cdeg);        /* 1 accepted, 0 rejected */
void ugv_servo_enable(UgvServo *s, uint8_t want, uint32_t now_ms);      /* rail request; off = PWM first */
void ugv_servo_tick(UgvServo *s, uint32_t now_ms, uint16_t rail_ma, uint8_t permit);
uint16_t ugv_servo_pulse_us(const UgvServo *s, int joint);              /* 0 = no pulse */
int ugv_servo_clear_fault(UgvServo *s);                                 /* only with the rail off */

#endif
