#ifndef UGV_SAFETY_CORE_H
#define UGV_SAFETY_CORE_H

#include <stdint.h>

typedef enum {
    UGV_BOOT, UGV_SELF_TEST, UGV_IDLE, UGV_ARMING,
    UGV_ARMED, UGV_DRIVING, UGV_FAULT, UGV_EMERGENCY_STOP
} UgvSafetyState;

typedef struct {
    uint8_t power_ok, estop_ok, watchdog_ok, hard_fault;
    uint8_t command_fresh, neutral, deadman, stationary;
    uint8_t arm_request, drive_request, stop_request, local_reset;
    uint8_t baseline_ok, separator_test_ok, separator_test_failed;
    uint8_t k1_feedback, precharge_complete, k2_feedback;
} UgvSafetyInputs;

typedef struct {
    UgvSafetyState state;
    uint8_t run_request, k1, k2, bleed, test_injection, precharge, actuator_request;
} UgvSafetyOutputs;

typedef struct {
    UgvSafetyState state;
    uint8_t phase, arm_prev, reset_prev, estop_release_seen, neutral_seen;
    uint32_t state_since_ms, estop_released_ms, neutral_since_ms;
} UgvSafety;

void ugv_safety_init(UgvSafety *s);
UgvSafetyOutputs ugv_safety_step(UgvSafety *s, const UgvSafetyInputs *in, uint32_t now_ms);

#endif
