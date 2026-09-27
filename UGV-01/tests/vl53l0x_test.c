#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../firmware/lite/vl53l0x.h"

/* L4b (DD87): the front VL53L0X pair against a register model of two sensors on one bus: 0xFF register pages,
   the address change, XSHUT reset and bus collisions (two sensors answering one address aborts the test). */
typedef struct {
    uint8_t addr, present, in_reset, page, spad_stuck, ranging, reg[8][256];
} Fake;
static Fake dev[2]; /* [0] left (on XSHUT), [1] right (always powered) */
static int delays;

static void boot(Fake *f) { /* power-on state: boot address, page 0, NVM values */
    const uint8_t present = f->present, stuck = f->spad_stuck;
    memset(f, 0, sizeof *f);
    f->present = present, f->spad_stuck = stuck, f->addr = 0x29;
    f->reg[0][0xC0] = 0xEE;                /* model ID */
    f->reg[1][0x91] = 0x3C;                /* stop variable */
    f->reg[7][0x92] = 0x85;                /* reference SPADs: aperture type, 5 of them */
    memset(&f->reg[0][0xB0], 0xFF, 6);     /* NVM reference SPAD map */
    f->reg[0][0x84] = 0x11;
}

static Fake *at(uint8_t addr) {
    Fake *hit = NULL;
    for (int i = 0; i < 2; ++i)
        if (dev[i].present && !dev[i].in_reset && dev[i].addr == addr) {
            assert(!hit); /* bus collision */
            hit = &dev[i];
        }
    return hit;
}

static int fw(void *ctx, uint8_t addr, const uint8_t *buf, size_t n) {
    (void)ctx;
    Fake *f = at(addr);
    if (!f) return -1; /* NACK */
    for (size_t k = 1; k < n; ++k) {
        const uint8_t reg = (uint8_t)(buf[0] + k - 1), v = buf[k];
        if (reg == 0xFF) {
            assert(v < 8);
            f->page = v;
            continue;
        }
        f->reg[f->page][reg] = v;
        if (f->page == 0 && reg == 0x8A) f->addr = v;
        if (f->page == 0 && reg == 0x00) {           /* SYSRANGE_START */
            if (v & 0x01) f->reg[0][0x13] = 0x03;     /* calibration done at once */
            f->ranging = v == 0x02;
        }
        if (f->page == 0 && reg == 0x0B && v) f->reg[0][0x13] = 0;
        if (f->page == 7 && reg == 0x83 && v == 0 && !f->spad_stuck) f->reg[7][0x83] = 0x10;
    }
    return 0;
}

static int fr(void *ctx, uint8_t addr, uint8_t reg, uint8_t *buf, size_t n) {
    (void)ctx;
    Fake *f = at(addr);
    if (!f) return -1;
    for (size_t k = 0; k < n; ++k) buf[k] = f->reg[f->page][(uint8_t)(reg + k)];
    return 0;
}

static void fx(void *ctx, int level) {
    (void)ctx;
    if (level && dev[0].in_reset) boot(&dev[0]); /* released: wakes at the boot address */
    dev[0].in_reset = !level;
}

static void fd(void *ctx, uint32_t ms) { (void)ctx, (void)ms, ++delays; }

static void sample(Fake *f, uint16_t mm) {
    assert(f->ranging);
    f->reg[0][0x1E] = (uint8_t)(mm >> 8), f->reg[0][0x1F] = (uint8_t)mm, f->reg[0][0x13] = 0x04;
}

static const UgvI2cBus bus = {fw, fr, fx, fd, NULL};

static int start(UgvTof tof[2]) {
    tof[0] = (UgvTof){.addr = 0x29}, tof[1] = (UgvTof){.addr = 0x30};
    return ugv_tof_pair_start(&bus, tof);
}

int main(void) {
    /* Cold boot: both powered at 0x29 (the module's pull-up holds XSHUT High until the GPIO drives it). Holding the
       left one in reset first is what keeps the address change off the left sensor; the model aborts otherwise. */
    dev[0].present = dev[1].present = 1;
    boot(&dev[0]), boot(&dev[1]);
    UgvTof tof[2];
    assert(start(tof) == 2 && tof[0].ok && tof[1].ok);
    assert(dev[0].addr == 0x29 && dev[1].addr == 0x30 && dev[0].ranging && dev[1].ranging);
    const Fake *r = &dev[1];
    assert(r->reg[0][0x89] & 0x01);                                   /* 2V8 I/O pads */
    static const uint8_t spads[6] = {0x00, 0xF0, 0x01, 0x00, 0x00, 0x00}; /* 5 aperture SPADs from bit 12 */
    assert(memcmp(&r->reg[0][0xB0], spads, 6) == 0);
    assert(r->reg[0][0x52] == 0x96 && r->reg[1][0x22] == 0x32 && r->reg[0][0x72] == 0xFE); /* tuning, both pages */
    assert(r->reg[0][0x44] == 0x00 && r->reg[0][0x45] == 0x20);       /* 0.25 MCPS final range limit */
    assert(r->reg[0][0x0A] == 0x04 && !(r->reg[0][0x84] & 0x10));      /* new-sample interrupt, active low */
    assert(r->reg[0][0x01] == 0xE8 && r->reg[1][0x91] == 0x3C);        /* MSRC/TCC off; stop variable restored */
    assert(r->page == 0 && dev[0].page == 0);                         /* every page switch undone */

    /* Polling: nothing yet -> 0; a sample is read once and its interrupt cleared; 8190 = nothing in range. */
    uint16_t mm[2];
    ugv_tof_pair_poll(&bus, tof, 1000, mm);
    assert(mm[0] == 0 && mm[1] == 0);
    sample(&dev[0], 612), sample(&dev[1], 8190);
    ugv_tof_pair_poll(&bus, tof, 1020, mm);
    assert(mm[0] == 612 && mm[1] == 8190 && !dev[0].reg[0][0x13] && !dev[1].reg[0][0x13]);
    ugv_tof_pair_poll(&bus, tof, 1020 + UGV_TOF_STALE_MS, mm); /* still fresh */
    assert(mm[0] == 612 && mm[1] == 8190);
    ugv_tof_pair_poll(&bus, tof, 1021 + UGV_TOF_STALE_MS, mm); /* no new sample for too long */
    assert(mm[0] == 0 && mm[1] == 0);
    /* A sensor that stops answering goes stale; it never reads as an empty road. */
    sample(&dev[0], 700), sample(&dev[1], 700);
    dev[1].present = 0;
    ugv_tof_pair_poll(&bus, tof, 2000, mm);
    ugv_tof_pair_poll(&bus, tof, 2200, mm);
    assert(mm[0] == 0 && mm[1] == 0);
    dev[1].present = 1;

    /* Warm restart of the ESP32 (watchdog): the right sensor kept 0x30, so the move NACKs; both still come up. */
    assert(start(tof) == 2 && dev[1].addr == 0x30);

    /* A missing or foreign right sensor is reported; its side stays 0, so the core blocks forward motion. */
    boot(&dev[0]), boot(&dev[1]);
    dev[1].present = 0;
    assert(start(tof) == 1 && tof[0].ok && !tof[1].ok);
    dev[1].present = 1;
    boot(&dev[0]), boot(&dev[1]);
    dev[1].reg[0][0xC0] = 0x00;
    assert(start(tof) == 1 && !tof[1].ok);
    sample(&dev[0], 400);
    ugv_tof_pair_poll(&bus, tof, 3000, mm);
    assert(mm[0] == 400 && mm[1] == 0);

    /* SPAD info that never becomes ready fails the init after a bounded wait instead of hanging the boot. */
    boot(&dev[0]), boot(&dev[1]);
    dev[1].spad_stuck = 1;
    delays = 0;
    assert(start(tof) == 1 && !tof[1].ok && delays < 1000);

    puts("PASS: VL53L0X pair: left held in reset while the right moves to 0x30 (no collision), init/tuning/SPAD "
         "map, ranging, stale -> 0, lost/missing/foreign sensor, warm restart, bounded waits (L4b)");
    return 0;
}
