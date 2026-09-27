#include <assert.h>
#include <stdio.h>
#include "../firmware/stm32/safety_core.h"

static UgvSafetyInputs healthy(void) {
    return (UgvSafetyInputs){.power_ok=1, .estop_ok=1, .watchdog_ok=1,
        .command_fresh=1, .neutral=1, .deadman=1, .stationary=1,
        .baseline_ok=1};
}

static UgvSafetyOutputs tick(UgvSafety *s, UgvSafetyInputs *in, unsigned ms) {
    return ugv_safety_step(s, in, ms);
}

/* Fresh core in IDLE with neutral held; returns the first time an ARM edge is accepted. */
static unsigned ready(UgvSafety *s, UgvSafetyInputs *in) {
    ugv_safety_init(s);
    *in = healthy();
    tick(s, in, 0); tick(s, in, 1); tick(s, in, 2);
    return 502;
}

int main(void) {
    UgvSafety s;
    UgvSafetyInputs in = healthy();
    UgvSafetyOutputs out;
    unsigned t;
    ugv_safety_init(&s);
    in.watchdog_ok = 0;
    assert(tick(&s, &in, 0).state == UGV_BOOT); /* TPS3431 startup is not a latched fault */
    in.watchdog_ok = 1;
    assert(tick(&s, &in, 230).state == UGV_SELF_TEST);

    /* IDLE -> ARMING needs 500 ms continuous neutral (safety_architecture.md). */
    ugv_safety_init(&s);
    in = healthy();
    tick(&s, &in, 0); tick(&s, &in, 1);
    in.arm_request = 1;
    assert(tick(&s, &in, 300).state == UGV_IDLE);
    in.arm_request = 0;
    tick(&s, &in, 301);
    in.neutral = 0;
    tick(&s, &in, 350);
    in.neutral = 1;
    tick(&s, &in, 400);
    in.arm_request = 1;
    assert(tick(&s, &in, 850).state == UGV_IDLE); /* neutral break restarted the timer */
    in.arm_request = 0;
    tick(&s, &in, 851);
    in.arm_request = 1;
    assert(tick(&s, &in, 900).state == UGV_ARMING);

    t = ready(&s, &in);
    assert(s.state == UGV_IDLE);
    in.arm_request = 1;
    out = tick(&s, &in, t);
    assert(out.state == UGV_ARMING && out.bleed && !out.actuator_request);
    out = tick(&s, &in, t + 1);
    assert(out.test_injection && !out.k1 && !out.actuator_request);
    in.separator_test_ok = 1;
    out = tick(&s, &in, t + 2);
    assert(out.k1 && !out.k2 && !out.precharge && !out.actuator_request);
    in.k1_feedback = 1;
    out = tick(&s, &in, t + 3);
    assert(out.k1 && out.precharge && !out.k2 && !out.actuator_request);
    in.precharge_complete = 1;
    out = tick(&s, &in, t + 4);
    assert(out.k1 && out.k2 && !out.precharge && !out.actuator_request);
    in.k2_feedback = 1;
    out = tick(&s, &in, t + 5);
    assert(out.state == UGV_ARMED && out.actuator_request && out.run_request);
    in.drive_request = 1;
    in.neutral = 0;
    assert(tick(&s, &in, t + 6).state == UGV_DRIVING);
    in.drive_request = 0;
    in.neutral = 1;
    assert(tick(&s, &in, t + 7).state == UGV_DRIVING);
    assert(tick(&s, &in, t + 206).state == UGV_DRIVING);
    assert(tick(&s, &in, t + 207).state == UGV_ARMED);
    in.estop_ok = 0;
    out = tick(&s, &in, t + 208);
    assert(out.state == UGV_EMERGENCY_STOP && !out.k1 && !out.k2 && !out.actuator_request && !out.test_injection);
    in.estop_ok = 1;
    in.neutral = 1;
    in.drive_request = 0;
    in.local_reset = 0;
    assert(tick(&s, &in, t + 209).state == UGV_EMERGENCY_STOP);
    assert(tick(&s, &in, t + 708).state == UGV_EMERGENCY_STOP);
    in.local_reset = 1;
    assert(tick(&s, &in, t + 709).state == UGV_SELF_TEST);
    assert(tick(&s, &in, t + 710).state == UGV_IDLE);
    assert(tick(&s, &in, t + 1300).state == UGV_IDLE); /* held arm is not a new request */

    t = ready(&s, &in);
    in.arm_request = 1;
    tick(&s, &in, t); tick(&s, &in, t + 1);
    in.separator_test_failed = 1;
    out = tick(&s, &in, t + 2);
    assert(out.state == UGV_FAULT && !out.k1 && !out.actuator_request);

    t = ready(&s, &in);
    in.arm_request = 1;
    tick(&s, &in, t); tick(&s, &in, t + 1);
    in.separator_test_ok = 1;
    tick(&s, &in, t + 2);
    in.k1_feedback = 1;
    assert(tick(&s, &in, t + 3).precharge);
    out = tick(&s, &in, t + 15001);
    assert(out.state == UGV_FAULT && !out.k1 && !out.precharge);

    t = ready(&s, &in);
    in.arm_request = 1;
    tick(&s, &in, t);
    in.command_fresh = 0;
    out = tick(&s, &in, t + 1);
    assert(out.state == UGV_FAULT && !out.actuator_request);

    t = ready(&s, &in);
    in.arm_request = 1;
    tick(&s, &in, t);
    in.hard_fault = 1;
    in.local_reset = 1;
    assert(tick(&s, &in, t + 1).state == UGV_FAULT);
    in.hard_fault = 0;
    assert(tick(&s, &in, t + 2).state == UGV_FAULT); /* held reset cannot clear a new fault */
    in.local_reset = 0;
    tick(&s, &in, t + 3);
    in.local_reset = 1;
    assert(tick(&s, &in, t + 4).state == UGV_SELF_TEST);

    t = ready(&s, &in);
    in.arm_request = 1;
    tick(&s, &in, t); tick(&s, &in, t + 1);
    in.separator_test_ok = 1;
    tick(&s, &in, t + 2);
    in.k1_feedback = 1;
    in.precharge_complete = 1; /* stale-high sensor must not skip charging */
    out = tick(&s, &in, t + 3);
    assert(out.state == UGV_FAULT && !out.k2 && !out.actuator_request);

    for (unsigned welded = 0; welded < 2; ++welded) {
        t = ready(&s, &in);
        in.arm_request = 1;
        tick(&s, &in, t); tick(&s, &in, t + 1);
        in.separator_test_ok = 1;
        in.k1_feedback = welded == 0;
        in.k2_feedback = welded == 1;
        out = tick(&s, &in, t + 2);
        assert(out.state == UGV_FAULT && !out.k1 && !out.actuator_request);
    }

    t = ready(&s, &in);
    in.arm_request = 1;
    in.separator_test_ok = 1; /* a result before test power is stale */
    out = tick(&s, &in, t);
    assert(out.state == UGV_FAULT && !out.test_injection && !out.k1);

    t = ready(&s, &in);
    in.arm_request = 1;
    tick(&s, &in, t); tick(&s, &in, t + 1);
    in.separator_test_ok = 1;
    tick(&s, &in, t + 2);
    in.k2_feedback = 1; /* K2 conducts before K2 command */
    out = tick(&s, &in, t + 3);
    assert(out.state == UGV_FAULT && !out.k1 && !out.k2);

    puts("PASS: ARMING order, 500 ms neutral before ARM, no early motion, faults/timeouts, reset edge and E-stop holdoff");
    return 0;
}
