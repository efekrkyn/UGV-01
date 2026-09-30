#include "vl53l0x.h"

#include <string.h>

/* Bring-up in the order of ST's VL53L0X API (DataInit, StaticInit with DefaultTuningSettings from
   vl53l0x_tuning.h, PerformRefCalibration), at register level as in Pololu's vl53l0x-arduino (MIT). */
enum {
    SYSRANGE_START = 0x00, SYSTEM_SEQUENCE_CONFIG = 0x01, SYSTEM_INTERRUPT_CONFIG_GPIO = 0x0A,
    SYSTEM_INTERRUPT_CLEAR = 0x0B, RESULT_INTERRUPT_STATUS = 0x13, RESULT_RANGE_STATUS = 0x14,
    FINAL_RANGE_MIN_COUNT_RATE = 0x44, SPAD_NUM_REQUESTED_REF = 0x4E, SPAD_REF_EN_START_OFFSET = 0x4F,
    MSRC_CONFIG_CONTROL = 0x60, GPIO_HV_MUX_ACTIVE_HIGH = 0x84, PAD_EXTSUP_HV = 0x89, SLAVE_DEVICE_ADDRESS = 0x8A,
    SPAD_ENABLES_REF_0 = 0xB0, REF_EN_START_SELECT = 0xB6, MODEL_ID = 0xC0, PAGE = 0xFF,
    POLL_LIMIT = 500, /* x 1 ms; SPAD info and each calibration take a few tens of ms */
};

static const uint8_t TUNING[][2] = {
    {0xFF, 0x01}, {0x00, 0x00}, {0xFF, 0x00}, {0x09, 0x00}, {0x10, 0x00}, {0x11, 0x00}, {0x24, 0x01}, {0x25, 0xFF},
    {0x75, 0x00}, {0xFF, 0x01}, {0x4E, 0x2C}, {0x48, 0x00}, {0x30, 0x20}, {0xFF, 0x00}, {0x30, 0x09}, {0x54, 0x00},
    {0x31, 0x04}, {0x32, 0x03}, {0x40, 0x83}, {0x46, 0x25}, {0x60, 0x00}, {0x27, 0x00}, {0x50, 0x06}, {0x51, 0x00},
    {0x52, 0x96}, {0x56, 0x08}, {0x57, 0x30}, {0x61, 0x00}, {0x62, 0x00}, {0x64, 0x00}, {0x65, 0x00}, {0x66, 0xA0},
    {0xFF, 0x01}, {0x22, 0x32}, {0x47, 0x14}, {0x49, 0xFF}, {0x4A, 0x00}, {0xFF, 0x00}, {0x7A, 0x0A}, {0x7B, 0x00},
    {0x78, 0x21}, {0xFF, 0x01}, {0x23, 0x34}, {0x42, 0x00}, {0x44, 0xFF}, {0x45, 0x26}, {0x46, 0x05}, {0x40, 0x40},
    {0x0E, 0x06}, {0x20, 0x1A}, {0x43, 0x40}, {0xFF, 0x00}, {0x34, 0x03}, {0x35, 0x44}, {0xFF, 0x01}, {0x31, 0x04},
    {0x4B, 0x09}, {0x4C, 0x05}, {0x4D, 0x04}, {0xFF, 0x00}, {0x44, 0x00}, {0x45, 0x20}, {0x47, 0x08}, {0x48, 0x28},
    {0x67, 0x00}, {0x70, 0x04}, {0x71, 0x01}, {0x72, 0xFE}, {0x76, 0x00}, {0x77, 0x00}, {0xFF, 0x01}, {0x0D, 0x01},
    {0xFF, 0x00}, {0x80, 0x01}, {0x01, 0xF8}, {0xFF, 0x01}, {0x8E, 0x01}, {0x00, 0x01}, {0xFF, 0x00}, {0x80, 0x00},
};

/* One sensor; the first failed transfer sticks in err and turns the rest into no-ops that read 0. */
typedef struct {
    const UgvI2cBus *b;
    uint8_t a;
    int err;
} Dev;

static void wr(Dev *d, uint8_t reg, const uint8_t *v, size_t n) {
    uint8_t buf[8];
    if (d->err) return;
    buf[0] = reg;
    memcpy(buf + 1, v, n);
    d->err = d->b->write(d->b->ctx, d->a, buf, n + 1);
}

static void w8(Dev *d, uint8_t reg, uint8_t v) { wr(d, reg, &v, 1); }

static void rd(Dev *d, uint8_t reg, uint8_t *v, size_t n) {
    if (!d->err) d->err = d->b->read(d->b->ctx, d->a, reg, v, n);
    if (d->err) memset(v, 0, n);
}

static uint8_t r8(Dev *d, uint8_t reg) {
    uint8_t v;
    rd(d, reg, &v, 1);
    return v;
}

static int wait(Dev *d, uint8_t reg, uint8_t mask) { /* 1 once (reg & mask) != 0 */
    for (int i = 0; i < POLL_LIMIT && !d->err; ++i) {
        if (r8(d, reg) & mask) return 1;
        d->b->delay_ms(d->b->ctx, 1);
    }
    return 0;
}

static void stop_variable_page(Dev *d, int enter) { /* the 0x80/0xFF/0x00 dance around page-1 register 0x91 */
    if (enter) w8(d, 0x80, 0x01), w8(d, PAGE, 0x01), w8(d, 0x00, 0x00);
    else w8(d, 0x00, 0x01), w8(d, PAGE, 0x00), w8(d, 0x80, 0x00);
}

static int init(Dev *d) {
    if (r8(d, MODEL_ID) != 0xEE) return -1;
    w8(d, PAD_EXTSUP_HV, r8(d, PAD_EXTSUP_HV) | 0x01); /* 2V8 I/O pads */
    w8(d, 0x88, 0x00);                                  /* I2C standard mode */
    stop_variable_page(d, 1);
    const uint8_t stop = r8(d, 0x91);
    stop_variable_page(d, 0);
    w8(d, MSRC_CONFIG_CONTROL, r8(d, MSRC_CONFIG_CONTROL) | 0x12);
    static const uint8_t rate[2] = {0x00, 0x20}; /* 0.25 MCPS, 9.7 fixed point */
    wr(d, FINAL_RANGE_MIN_COUNT_RATE, rate, 2);
    w8(d, SYSTEM_SEQUENCE_CONFIG, 0xFF);

    /* Reference SPADs: count and type from NVM, then keep only that many enabled bits of the stored map. */
    w8(d, 0x80, 0x01), w8(d, PAGE, 0x01), w8(d, 0x00, 0x00);
    w8(d, PAGE, 0x06), w8(d, 0x83, r8(d, 0x83) | 0x04), w8(d, PAGE, 0x07), w8(d, 0x81, 0x01);
    w8(d, 0x80, 0x01), w8(d, 0x94, 0x6B), w8(d, 0x83, 0x00);
    if (!wait(d, 0x83, 0xFF)) return -1;
    w8(d, 0x83, 0x01);
    const uint8_t info = r8(d, 0x92);
    w8(d, 0x81, 0x00), w8(d, PAGE, 0x06), w8(d, 0x83, r8(d, 0x83) & (uint8_t)~0x04), w8(d, PAGE, 0x01);
    w8(d, 0x00, 0x01), w8(d, PAGE, 0x00), w8(d, 0x80, 0x00);
    uint8_t map[6];
    rd(d, SPAD_ENABLES_REF_0, map, sizeof map);
    w8(d, PAGE, 0x01), w8(d, SPAD_REF_EN_START_OFFSET, 0x00), w8(d, SPAD_NUM_REQUESTED_REF, 0x2C), w8(d, PAGE, 0x00);
    w8(d, REF_EN_START_SELECT, 0xB4);
    const unsigned count = info & 0x7Fu, first = (info & 0x80u) ? 12u : 0u; /* aperture SPADs start at 12 */
    unsigned on = 0;
    for (unsigned i = 0; i < 48; ++i) {
        const uint8_t bit = (uint8_t)(1u << (i % 8));
        if (i < first || on == count) map[i / 8] &= (uint8_t)~bit;
        else if (map[i / 8] & bit) ++on;
    }
    wr(d, SPAD_ENABLES_REF_0, map, sizeof map);

    for (size_t i = 0; i < sizeof TUNING / sizeof TUNING[0]; ++i) w8(d, TUNING[i][0], TUNING[i][1]);
    w8(d, SYSTEM_INTERRUPT_CONFIG_GPIO, 0x04); /* interrupt on a new sample */
    w8(d, GPIO_HV_MUX_ACTIVE_HIGH, r8(d, GPIO_HV_MUX_ACTIVE_HIGH) & (uint8_t)~0x10);
    w8(d, SYSTEM_INTERRUPT_CLEAR, 0x01);
    /* MSRC and TCC off. ponytail: ST then stretches the final-range timeout back to the 33 ms budget; skipped, so a
       sample is a little quicker and a little less precise. Add the budget maths if TL5 shows range jitter. */
    w8(d, SYSTEM_SEQUENCE_CONFIG, 0xE8);

    static const uint8_t cal[2][2] = {{0x01, 0x40}, {0x02, 0x00}}; /* VHV, then phase calibration */
    for (int k = 0; k < 2; ++k) {
        w8(d, SYSTEM_SEQUENCE_CONFIG, cal[k][0]);
        w8(d, SYSRANGE_START, 0x01 | cal[k][1]);
        if (!wait(d, RESULT_INTERRUPT_STATUS, 0x07)) return -1;
        w8(d, SYSTEM_INTERRUPT_CLEAR, 0x01);
        w8(d, SYSRANGE_START, 0x00);
    }
    w8(d, SYSTEM_SEQUENCE_CONFIG, 0xE8);

    stop_variable_page(d, 1); /* back-to-back continuous ranging */
    w8(d, 0x91, stop);
    stop_variable_page(d, 0);
    w8(d, SYSRANGE_START, 0x02);
    return d->err ? -1 : 0;
}

int ugv_tof_pair_start(const UgvI2cBus *bus, UgvTof tof[2]) {
    bus->xshut(bus->ctx, 0); /* left in reset: the right one is alone at the boot address */
    bus->delay_ms(bus->ctx, 2);
    Dev right = {bus, UGV_TOF_BOOT_ADDR, 0};
    w8(&right, SLAVE_DEVICE_ADDRESS, tof[1].addr & 0x7F); /* NACKs after a warm restart: it already moved */
    bus->xshut(bus->ctx, 1);
    bus->delay_ms(bus->ctx, 2); /* tBOOT 1.2 ms */
    if (tof[0].addr != UGV_TOF_BOOT_ADDR) {
        Dev left = {bus, UGV_TOF_BOOT_ADDR, 0};
        w8(&left, SLAVE_DEVICE_ADDRESS, tof[0].addr & 0x7F);
    }
    int n = 0;
    for (int i = 0; i < 2; ++i) {
        Dev d = {bus, tof[i].addr, 0};
        tof[i].mm = 0, tof[i].at_ms = 0;
        tof[i].ok = init(&d) == 0;
        n += tof[i].ok;
    }
    return n;
}

/* A02/DD94: the device range status (0x14 bits 6:3, the raw DeviceRangeStatus, not the API's RangeStatus) decides what
   the distance means. 11 = range valid (a distance, capped below the out-of-range code). A signal fail (4) or phase
   fail (6, 9) carrying the out-of-range code (>= 8190) means the sensor saw nothing it trusts in range: that proves no
   empty road (a dark or glassy target can read so), so it is UGV_TOF_NO_TARGET, which the core drives into only at a
   creep. Everything else is invalid: 0 = forward blocked at once, and the older valid sample is dropped.
   ponytail: which status the real sensor gives for open space is checked at bring-up (TL5); any other only blocks. */
static uint16_t reading(uint8_t status_reg, uint16_t mm) {
    const uint8_t s = (uint8_t)(status_reg >> 3 & 0x0F);
    if (s == 11) return mm < 1 ? 1 : mm > 8189 ? 8189 : mm;
    return (s == 4 || s == 6 || s == 9) && mm >= 8190 ? UGV_TOF_NO_TARGET : 0;
}

void ugv_tof_pair_poll(const UgvI2cBus *bus, UgvTof tof[2], uint32_t now_ms, uint16_t out_mm[2]) {
    for (int i = 0; i < 2; ++i) {
        UgvTof *t = &tof[i];
        Dev d = {bus, t->addr, 0};
        if (t->ok && (r8(&d, RESULT_INTERRUPT_STATUS) & 0x07)) {
            uint8_t res[12]; /* range status .. distance in one burst, as ST's API reads them */
            rd(&d, RESULT_RANGE_STATUS, res, sizeof res);
            w8(&d, SYSTEM_INTERRUPT_CLEAR, 0x01);
            if (!d.err) t->mm = reading(res[0], (uint16_t)(res[10] << 8 | res[11])), t->at_ms = now_ms;
        }
        /* ponytail: a sensor that browns out stays stale (forward blocked) until the next boot; re-init if TL5 needs it */
        out_mm[i] = t->ok && t->mm && now_ms - t->at_ms <= UGV_TOF_STALE_MS ? t->mm : 0;
    }
}
