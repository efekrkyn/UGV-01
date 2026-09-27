#include <assert.h>
#include <stdio.h>
#include "../firmware/stm32/light_bar.h"
#include "../firmware/stm32/servo_control.h"

static void rail_on(UgvServo *s, uint32_t t) {
    ugv_servo_enable(s, 1, t);
    ugv_servo_tick(s, t + 100, 0, 1);
    assert(s->pwm_on);
}

int main(void) {
    UgvServo s;
    ugv_servo_init(&s);

    /* Joint limits (centi-degrees) and park start. */
    assert(!ugv_servo_set_target(&s, UGV_SERVO_PAN, 9001) && !ugv_servo_set_target(&s, UGV_SERVO_PAN, -9001));
    assert(!ugv_servo_set_target(&s, UGV_SERVO_TILT, -6001) && !ugv_servo_set_target(&s, UGV_SERVO_TILT, 3001));
    assert(!ugv_servo_set_target(&s, UGV_SERVO_SHOULDER, -4501) && !ugv_servo_set_target(&s, UGV_SERVO_SHOULDER, 18001));
    /* M3 arm joints (config geometry.arm.limits_deg): twist -80..90, elbow -30..135, wrist -70..100, roll -85..85. */
    assert(!ugv_servo_set_target(&s, UGV_SERVO_TWIST, -8001) && !ugv_servo_set_target(&s, UGV_SERVO_TWIST, 9001));
    assert(!ugv_servo_set_target(&s, UGV_SERVO_ELBOW, -3001) && !ugv_servo_set_target(&s, UGV_SERVO_ELBOW, 13501));
    assert(!ugv_servo_set_target(&s, UGV_SERVO_WRIST, -7001) && !ugv_servo_set_target(&s, UGV_SERVO_WRIST, 10001));
    assert(!ugv_servo_set_target(&s, UGV_SERVO_ROLL, -8501) && !ugv_servo_set_target(&s, UGV_SERVO_ROLL, 8501));
    assert(!ugv_servo_set_target(&s, UGV_SERVO_COUNT, 0) && !ugv_servo_set_target(&s, -1, 0) && UGV_SERVO_COUNT == 8);
    /* Park = the CAD stow pose: shoulder 180, twist 90, elbow/wrist/roll 0. */
    assert(s.pos_cdeg[UGV_SERVO_SHOULDER] == 18000 && s.target_cdeg[UGV_SERVO_SHOULDER] == 18000);
    assert(s.pos_cdeg[UGV_SERVO_TWIST] == 9000 && s.pos_cdeg[UGV_SERVO_ELBOW] == 0 && s.pos_cdeg[UGV_SERVO_WRIST] == 0);

    /* Rail on: PWM only 100 ms after the rail request. */
    ugv_servo_tick(&s, 0, 0, 1);
    ugv_servo_enable(&s, 1, 0);
    assert(s.rail_req && !s.pwm_on && ugv_servo_pulse_us(&s, UGV_SERVO_PAN) == 0);
    ugv_servo_tick(&s, 99, 0, 1);
    assert(ugv_servo_pulse_us(&s, UGV_SERVO_PAN) == 0);
    ugv_servo_tick(&s, 100, 0, 1);
    assert(ugv_servo_pulse_us(&s, UGV_SERVO_PAN) == 1500);
    /* M3: the DS3218MG 270 deg drives the shoulder directly; 225 deg of arm travel centred on its 270 deg. */
    assert(ugv_servo_pulse_us(&s, UGV_SERVO_SHOULDER) == 2333 && ugv_servo_pulse_us(&s, UGV_SERVO_TWIST) == 2444);

    /* Ramp: shoulder 180 -> -45 deg at 60 deg/s goes over the top, monotonically. */
    assert(ugv_servo_set_target(&s, UGV_SERVO_SHOULDER, -4500));
    ugv_servo_tick(&s, 1100, 0, 1);
    assert(s.pos_cdeg[UGV_SERVO_SHOULDER] == 12000);
    ugv_servo_tick(&s, 2600, 0, 1);
    assert(s.pos_cdeg[UGV_SERVO_SHOULDER] == 3000);
    ugv_servo_tick(&s, 9000, 0, 1);
    assert(s.pos_cdeg[UGV_SERVO_SHOULDER] == -4500 && ugv_servo_pulse_us(&s, UGV_SERVO_SHOULDER) == 667);
    /* Every MG996R/MG90S arm joint maps its limits onto <= 170 deg of servo travel (11.1 us/deg). */
    for (int j = UGV_SERVO_TWIST; j <= UGV_SERVO_ROLL; ++j) {
        const UgvServoJoint *k = &s.joint[j];
        assert(k->max_cdeg - k->min_cdeg <= 17000 && k->us_at_max - k->us_at_min <= 1890);
    }

    /* Pulse map covers 500..2500 us at the pan limits. */
    assert(ugv_servo_set_target(&s, UGV_SERVO_PAN, 9000));
    ugv_servo_tick(&s, 11000, 0, 1);
    assert(ugv_servo_pulse_us(&s, UGV_SERVO_PAN) == 2500);
    assert(ugv_servo_set_target(&s, UGV_SERVO_PAN, -9000));
    ugv_servo_tick(&s, 13000, 0, 1);
    assert(ugv_servo_pulse_us(&s, UGV_SERVO_PAN) == 500);

    /* Off: PWM stops first, the rail request drops on the next tick. */
    ugv_servo_enable(&s, 0, 13001);
    assert(ugv_servo_pulse_us(&s, UGV_SERVO_PAN) == 0 && s.rail_req);
    ugv_servo_tick(&s, 13002, 0, 1);
    assert(!s.rail_req);

    /* Instant overcurrent > 5.5 A latches a fault; no re-enable until cleared with the rail off. */
    rail_on(&s, 14000);
    ugv_servo_tick(&s, 14200, 5600, 1);
    assert(s.fault && !s.pwm_on && s.rail_req);
    ugv_servo_tick(&s, 14201, 0, 1);
    assert(!s.rail_req);
    ugv_servo_enable(&s, 1, 14202);
    assert(!s.rail_req && !ugv_servo_set_target(&s, UGV_SERVO_PAN, 0));
    assert(ugv_servo_clear_fault(&s) && !s.fault);

    /* Sustained > 3.5 A for 200 ms latches; a dip below restarts the timer. */
    rail_on(&s, 15000);
    ugv_servo_tick(&s, 15100, 3600, 1);
    ugv_servo_tick(&s, 15200, 3000, 1);
    ugv_servo_tick(&s, 15250, 3600, 1);
    ugv_servo_tick(&s, 15449, 3600, 1);
    assert(!s.fault);
    ugv_servo_tick(&s, 15450, 3600, 1);
    assert(s.fault && !s.pwm_on);
    ugv_servo_tick(&s, 15451, 0, 1);
    assert(ugv_servo_clear_fault(&s));

    /* Hardware permit loss (E-stop, PWR permit) drops PWM and rail request at once. */
    rail_on(&s, 16000);
    ugv_servo_tick(&s, 16200, 0, 0);
    assert(!s.pwm_on && !s.rail_req && ugv_servo_pulse_us(&s, UGV_SERVO_TILT) == 0);

    /* Light bar: mode colours, battery bar, <= 0.5 W for every mode and charge. */
    UgvRgb px[UGV_LIGHT_LEDS];
    ugv_light_frame(px, UGV_LIGHT_FAULT, 10, 0);
    for (int i = 0; i < UGV_LIGHT_LEDS; ++i) assert(px[i].r > 0 && px[i].g == 0 && px[i].b == 0);
    ugv_light_frame(px, UGV_LIGHT_AI, 50, 0);
    for (int i = 0; i < UGV_LIGHT_LEDS; ++i)
        assert(i < 4 ? (px[i].b > 0 && px[i].r == 0) : (px[i].r == 0 && px[i].g == 0 && px[i].b == 0));
    ugv_light_frame(px, UGV_LIGHT_ARMED, 100, 0);
    assert(px[7].r > 0 && px[7].g > 0 && px[7].b == 0);
    ugv_light_frame(px, UGV_LIGHT_ESTOP, 100, 300);
    for (int i = 0; i < UGV_LIGHT_LEDS; ++i) assert(px[i].r == 0); /* blink off-phase */
    for (int mode = 0; mode < UGV_LIGHT_MODES; ++mode)
        for (int pct = 0; pct <= 100; pct += 5)
            for (uint32_t t = 0; t < 1000; t += 125) {
                ugv_light_frame(px, (uint8_t)mode, (uint8_t)pct, t);
                assert(ugv_light_power_mw(px) <= 500);
            }
    puts("PASS: 8 servo limits and stow park, 100 ms rail delay, ramp over the top, 500-2500 us, PWM-before-rail off, "
         "overcurrent latch, permit cut; light colours and 0.5 W cap");
    return 0;
}
