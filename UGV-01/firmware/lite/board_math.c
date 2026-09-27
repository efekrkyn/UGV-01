#include "board_math.h"

static uint32_t div_round(uint64_t num, uint64_t den) { return (uint32_t)((num + den / 2) / den); }

uint8_t ugv_pca9685_prescale(uint32_t osc_hz, uint16_t pwm_hz) {
    const int32_t p = (int32_t)div_round(osc_hz, 4096ull * pwm_hz) - 1;
    return (uint8_t)(p < 3 ? 3 : p > 255 ? 255 : p);
}

uint16_t ugv_pca9685_counts(uint16_t us, uint32_t osc_hz, uint8_t prescale) {
    const uint32_t c = div_round((uint64_t)us * osc_hz, (uint64_t)(prescale + 1) * 1000000u);
    return (uint16_t)(c > 4095 ? 4095 : c);
}

void ugv_pca9685_led_regs(uint16_t counts, uint8_t regs[4]) {
    regs[0] = regs[1] = 0;
    regs[2] = (uint8_t)counts;
    regs[3] = counts ? (uint8_t)(counts >> 8 & 0x0F) : 0x10;
}

void ugv_motor_inputs(int16_t duty_permil, int8_t polarity, uint16_t *in1_permil, uint16_t *in2_permil) {
    int32_t d = (int32_t)duty_permil * (polarity < 0 ? -1 : 1);
    if (d > 1000) d = 1000;
    if (d < -1000) d = -1000;
    *in1_permil = (uint16_t)(d > 0 ? d : 0);
    *in2_permil = (uint16_t)(d < 0 ? -d : 0);
}

uint16_t ugv_vbat_mv(uint32_t pin_mv, uint16_t cal_permille) {
    const uint64_t mv = (uint64_t)pin_mv * (100 + 22) * cal_permille / (22u * 1000u);
    return (uint16_t)(mv > 65535 ? 65535 : mv);
}

void ugv_enable_actuators(const UgvEnableIo *io) {
    if (io->estop(io->ctx)) return;
    io->act_en(io->ctx, 1);
    io->servo_oe(io->ctx, 0);
    if (io->estop(io->ctx)) {  /* an edge landed after the check: undo in reverse order */
        io->servo_oe(io->ctx, 1);
        io->act_en(io->ctx, 0);
    }
}
