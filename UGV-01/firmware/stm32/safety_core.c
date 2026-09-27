#include "safety_core.h"

enum { BLEED, TEST, K1, PRECHARGE, K2 };

static void enter(UgvSafety *s, UgvSafetyState state, uint32_t now_ms) {
    s->state = state;
    s->state_since_ms = now_ms;
    s->neutral_seen = 0; /* neutral hold timers restart in every state */
}

void ugv_safety_init(UgvSafety *s) {
    *s = (UgvSafety){.state = UGV_BOOT};
}

UgvSafetyOutputs ugv_safety_step(UgvSafety *s, const UgvSafetyInputs *in, uint32_t now_ms) {
    const uint8_t new_arm = in->arm_request && !s->arm_prev;
    const uint8_t new_reset = in->local_reset && !s->reset_prev;
    s->arm_prev = in->arm_request;
    s->reset_prev = in->local_reset;

    if (!in->estop_ok) {
        enter(s, UGV_EMERGENCY_STOP, now_ms);
        s->estop_release_seen = 0;
    } else if (s->state == UGV_EMERGENCY_STOP) {
        if (!s->estop_release_seen) {
            s->estop_released_ms = now_ms;
            s->estop_release_seen = 1;
        }
        if (new_reset && now_ms - s->estop_released_ms >= 500 &&
            in->power_ok && in->watchdog_ok && !in->hard_fault)
            enter(s, UGV_SELF_TEST, now_ms);
    } else if (s->state == UGV_BOOT && !in->hard_fault &&
               (!in->power_ok || !in->watchdog_ok)) {
        /* TPS3431 and rails may be starting; outputs stay de-energized. */
    } else if (!in->power_ok || !in->watchdog_ok || in->hard_fault ||
               ((s->state == UGV_ARMING || s->state == UGV_ARMED || s->state == UGV_DRIVING) &&
                (!in->command_fresh || !in->deadman)) ||
               ((s->state == UGV_ARMED || s->state == UGV_DRIVING) &&
                (!in->k1_feedback || !in->k2_feedback))) {
        enter(s, UGV_FAULT, now_ms);
    } else switch (s->state) {
    case UGV_BOOT:
        enter(s, UGV_SELF_TEST, now_ms);
        break;
    case UGV_SELF_TEST:
        if (now_ms - s->state_since_ms > 5000)
            enter(s, UGV_FAULT, now_ms);
        else if (in->baseline_ok)
            enter(s, UGV_IDLE, now_ms);
        break;
    case UGV_IDLE:
        if (!in->neutral) {
            s->neutral_seen = 0;
        } else if (!s->neutral_seen) {
            s->neutral_since_ms = now_ms;
            s->neutral_seen = 1;
        }
        /* safety_architecture.md: IDLE -> ARMING needs 500 ms continuous neutral. */
        if (new_arm && s->neutral_seen && now_ms - s->neutral_since_ms >= 500 &&
            in->command_fresh && in->deadman && in->stationary) {
            if (in->separator_test_ok || in->separator_test_failed ||
                in->precharge_complete || in->k1_feedback || in->k2_feedback)
                enter(s, UGV_FAULT, now_ms);
            else {
                enter(s, UGV_ARMING, now_ms);
                s->phase = BLEED;
            }
        }
        break;
    case UGV_ARMING:
        if (in->stop_request) {
            enter(s, UGV_IDLE, now_ms);
        } else if (now_ms - s->state_since_ms > 15000 || !in->stationary || !in->neutral ||
                   (s->phase < K1 && in->k1_feedback) ||
                   (s->phase < K2 && in->k2_feedback)) {
            enter(s, UGV_FAULT, now_ms);
        } else switch (s->phase) {
        case BLEED:
            if (in->baseline_ok) s->phase = TEST;
            break;
        case TEST:
            if (in->separator_test_failed)
                enter(s, UGV_FAULT, now_ms);
            else if (in->separator_test_ok) {
                if (in->k1_feedback || in->k2_feedback)
                    enter(s, UGV_FAULT, now_ms);
                else
                    s->phase = K1;
            }
            break;
        case K1:
            if (in->k1_feedback) {
                if (in->precharge_complete)
                    enter(s, UGV_FAULT, now_ms);
                else
                    s->phase = PRECHARGE;
            }
            break;
        case PRECHARGE:
            if (!in->k1_feedback)
                enter(s, UGV_FAULT, now_ms);
            else if (in->precharge_complete)
                s->phase = K2;
            break;
        case K2:
            if (!in->k1_feedback)
                enter(s, UGV_FAULT, now_ms);
            else if (in->k2_feedback)
                enter(s, UGV_ARMED, now_ms);
            break;
        default:
            enter(s, UGV_FAULT, now_ms);
        }
        break;
    case UGV_ARMED:
        if (in->stop_request)
            enter(s, UGV_IDLE, now_ms);
        else if (in->drive_request && !in->neutral) {
            enter(s, UGV_DRIVING, now_ms);
            s->neutral_seen = 0;
        }
        break;
    case UGV_DRIVING:
        if (in->stop_request)
            enter(s, UGV_IDLE, now_ms);
        else if (in->neutral && !in->drive_request && in->stationary) {
            if (!s->neutral_seen) {
                s->neutral_since_ms = now_ms;
                s->neutral_seen = 1;
            }
            if (now_ms - s->neutral_since_ms >= 200)
                enter(s, UGV_ARMED, now_ms);
        } else s->neutral_seen = 0;
        break;
    case UGV_FAULT:
        if (new_reset && in->baseline_ok && !in->separator_test_failed)
            enter(s, UGV_SELF_TEST, now_ms);
        break;
    case UGV_EMERGENCY_STOP:
        break;
    default:
        enter(s, UGV_FAULT, now_ms);
    }

    UgvSafetyOutputs out = {.state = s->state};
    if (s->state == UGV_ARMING) {
        out.run_request = 1;
        out.bleed = s->phase == BLEED;
        out.test_injection = s->phase == TEST;
        out.k1 = s->phase >= K1;
        out.precharge = s->phase == PRECHARGE;
        out.k2 = s->phase == K2;
    } else if (s->state == UGV_ARMED || s->state == UGV_DRIVING) {
        out.run_request = out.k1 = out.k2 = out.actuator_request = 1;
    }
    return out;
}
