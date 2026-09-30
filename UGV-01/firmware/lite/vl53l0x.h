#ifndef UGV_VL53L0X_H
#define UGV_VL53L0X_H

#include <stddef.h>
#include <stdint.h>

/* L4b (DD87): the front VL53L0X pair on I2C0 with one XSHUT line, on the left sensor only (lite_electronics_A3.md).
   Plain C over injected bus callbacks, so the host test runs it against a register model; the ESP-IDF glue is in
   esp32/main/app_main.c. */
enum { UGV_TOF_BOOT_ADDR = 0x29, UGV_TOF_STALE_MS = 100,
       UGV_TOF_NO_TARGET = 0xFFFF };  /* DD94: "nothing seen in range" - not a distance and not a clear road */

typedef struct {
    int (*write)(void *ctx, uint8_t addr, const uint8_t *buf, size_t n);        /* buf[0] = register; 0 = ACK */
    int (*read)(void *ctx, uint8_t addr, uint8_t reg, uint8_t *buf, size_t n);  /* 0 = ok */
    void (*xshut)(void *ctx, int level);                                        /* the left sensor's XSHUT */
    void (*delay_ms)(void *ctx, uint32_t ms);
    void *ctx;
} UgvI2cBus;

/* tof[0] = left, tof[1] = right. The caller sets addr (pins.h TOF_ADDR); the rest belongs to the driver. */
typedef struct {
    uint8_t addr, ok;
    uint16_t mm;
    uint32_t at_ms;
} UgvTof;

/* Hold the left sensor in reset, move the right one off the boot address, release the left, then initialise both
   and start back-to-back ranging. Returns how many sensors are ranging (0..2). */
int ugv_tof_pair_start(const UgvI2cBus *bus, UgvTof tof[2]);

/* Once per control tick, never blocks: out_mm = the latest valid distance (range status 11), UGV_TOF_NO_TARGET when the
   sensor saw nothing in range (signal/phase fail carrying the out-of-range code), or 0 when a sensor is down, its latest
   sample is invalid (A02) or it has not produced a sample for UGV_TOF_STALE_MS. The core treats 0 as "forward blocked"
   and NO_TARGET as "blind": forward only at a creep (DD94), never as a clear road. */
void ugv_tof_pair_poll(const UgvI2cBus *bus, UgvTof tof[2], uint32_t now_ms, uint16_t out_mm[2]);

#endif
