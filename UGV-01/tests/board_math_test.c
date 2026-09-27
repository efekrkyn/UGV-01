#include <assert.h>
#include <stdio.h>
#include "../firmware/lite/board_math.h"

/* L4a (DD86): the ESP32 board layer's arithmetic, host-tested before any hardware or ESP-IDF toolchain. */
static double pulse_us(uint16_t counts, uint8_t prescale, double osc_hz) {  /* what the chip really puts out */
    return counts * (prescale + 1) / osc_hz * 1e6;
}

/* Fake ACT_EN / servo /OE / E-stop pins. isr_after_check fires the E-stop ISR (drops ACT_EN, raises /OE, latches the
   edge) right after the release check, i.e. between the check and the enable writes. */
typedef struct { int pressed, act_en, oe, isr_after_check; } Io;
static int io_estop(void *c) {
    Io *io = c;
    const int was = io->pressed;
    if (io->isr_after_check) io->isr_after_check = 0, io->pressed = 1, io->act_en = 0, io->oe = 1;
    return was;
}
static void io_act(void *c, int level) { ((Io *)c)->act_en = level; }
static void io_oe(void *c, int level) {
    Io *io = c;
    assert(level || io->act_en);  /* pin map: /OE Low only while ACT_EN is High */
    io->oe = level;
}

int main(void) {
    /* PCA9685 at 50 Hz: prescale 121 on the nominal 25 MHz oscillator; 1500 us -> OFF count 307. */
    const uint8_t pre = ugv_pca9685_prescale(25000000u, 50);
    assert(pre == 121 && ugv_pca9685_counts(1500, 25000000u, pre) == 307);
    assert(ugv_pca9685_counts(500, 25000000u, pre) == 102 && ugv_pca9685_counts(2500, 25000000u, pre) == 512);
    /* The internal oscillator is often a few percent fast. Uncalibrated, a 4 % fast chip shortens every pulse by
       4 % (60 us at centre: ~5 deg on a servo); with the measured frequency in NVS the pulse is right again. */
    const double real = 26000000.0;
    assert(pulse_us(ugv_pca9685_counts(1500, 25000000u, pre), pre, real) < 1445.0);
    const uint8_t pre_cal = ugv_pca9685_prescale(26000000u, 50);
    const double cal = pulse_us(ugv_pca9685_counts(1500, 26000000u, pre_cal), pre_cal, real);
    assert(cal > 1497.0 && cal < 1503.0);
    assert(ugv_pca9685_prescale(1000u, 50) == 3 && ugv_pca9685_counts(30000, 25000000u, pre) == 4095);  /* clamps */
    /* LEDn registers: ON at 0, OFF at the count; 0 us means no pulse at all (full-off bit), not a 0-width one. */
    uint8_t regs[4];
    ugv_pca9685_led_regs(307, regs);
    assert(regs[0] == 0 && regs[1] == 0 && regs[2] == 0x33 && regs[3] == 0x01);
    ugv_pca9685_led_regs(0, regs);
    assert(regs[0] == 0 && regs[1] == 0 && regs[2] == 0 && regs[3] == 0x10);

    /* TB6612 per motor: forward = PWM on IN1 (drive/coast), reverse = PWM on IN2, 0 = coast; polarity -1 swaps a
       motor wired the other way round in software (calibrated per motor at bring-up). */
    uint16_t in1, in2;
    ugv_motor_inputs(600, 1, &in1, &in2);
    assert(in1 == 600 && in2 == 0);
    ugv_motor_inputs(-600, 1, &in1, &in2);
    assert(in1 == 0 && in2 == 600);
    ugv_motor_inputs(600, -1, &in1, &in2);
    assert(in1 == 0 && in2 == 600);
    ugv_motor_inputs(0, 1, &in1, &in2);
    assert(in1 == 0 && in2 == 0);
    ugv_motor_inputs(-1500, -1, &in1, &in2);
    assert(in1 == 1000 && in2 == 0);  /* clamped */

    /* Pack voltage through the 100k/22k divider (lite_electronics_A3.md): 2270 mV at the pin = 12.59 V. */
    assert(ugv_vbat_mv(2270, 1000) == 12588 && ugv_vbat_mv(2270, 1010) == 12714 && ugv_vbat_mv(0, 1000) == 0);

    /* Enable sequence (self-review of DD86): released -> ACT_EN High, then /OE Low; pressed -> nothing enabled. An
       E-stop edge between the release check and the writes wins at once, not at the next 20 ms tick. */
    Io io = {0, 0, 1, 0};
    const UgvEnableIo pins = {io_estop, io_act, io_oe, &io};
    ugv_enable_actuators(&pins);
    assert(io.act_en == 1 && io.oe == 0);
    io = (Io){1, 0, 1, 0};
    ugv_enable_actuators(&pins);
    assert(io.act_en == 0 && io.oe == 1);
    io = (Io){0, 0, 1, 1};
    ugv_enable_actuators(&pins);
    assert(io.act_en == 0 && io.oe == 1 && io.pressed);
    puts("PASS: PCA9685 prescale/counts with oscillator calibration and full-off, TB6612 IN1/IN2 with polarity, "
         "battery divider (L4a); ACT_EN/OE enable order with an E-stop edge between check and write");
    return 0;
}
