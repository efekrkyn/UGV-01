#ifndef UGV_BOARD_MATH_H
#define UGV_BOARD_MATH_H

#include <stdint.h>

/* L4a (DD86): arithmetic of the ESP32-S3 board layer, kept free of ESP-IDF so the host tests cover it. */

/* PCA9685 (NXP datasheet rev. 4, 7.3.5): prescale = round(osc / (4096 * pwm_hz)) - 1, limited to 3..255. The
   internal oscillator is nominally 25 MHz but often runs a few percent fast: osc_hz is the measured value (NVS). */
uint8_t ugv_pca9685_prescale(uint32_t osc_hz, uint16_t pwm_hz);
/* OFF count (ON at 0) for a pulse of `us`, for the period this prescale really gives; clamped to 4095. */
uint16_t ugv_pca9685_counts(uint16_t us, uint32_t osc_hz, uint8_t prescale);
/* LEDn_ON_L, LEDn_ON_H, LEDn_OFF_L, LEDn_OFF_H. counts 0 = full off (OFF_H bit 4): no pulse, the servo goes limp. */
void ugv_pca9685_led_regs(uint16_t counts, uint8_t regs[4]);

/* TB6612FNG, one motor on IN1/IN2 (PWMx tied high): forward = PWM on IN1 (drive/coast), reverse = PWM on IN2,
   0 = both low (coast). polarity -1 swaps a motor wired the other way round (per-motor calibration in NVS). */
void ugv_motor_inputs(int16_t duty_permil, int8_t polarity, uint16_t *in1_permil, uint16_t *in2_permil);

/* Pack voltage (mV) from the ADC1 pin voltage through the 100k/22k divider, trimmed by cal_permille (1000 = none). */
uint16_t ugv_vbat_mv(uint32_t pin_mv, uint16_t cal_permille);

/* Enable order for ACT_EN and the PCA9685 /OE (pin map: /OE Low only while ACT_EN is High). Nothing is enabled while
   the E-stop reads pressed or has an edge pending, and it is read again after the writes: an edge that lands in
   between (its ISR already dropped ACT_EN) wins at once instead of at the next 20 ms tick. */
typedef struct {
    int (*estop)(void *ctx);                 /* 1 = pressed, open wire, or an edge since the core last looked */
    void (*act_en)(void *ctx, int level);
    void (*servo_oe)(void *ctx, int level);  /* active low */
    void *ctx;
} UgvEnableIo;
void ugv_enable_actuators(const UgvEnableIo *io);

#endif
