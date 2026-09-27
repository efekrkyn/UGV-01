#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../firmware/lite/hmac_sha256.h"
#include "../firmware/lite/lite_link.h"
#include "../firmware/stm32/can_protocol.h"

static int hex_eq(const uint8_t *bytes, size_t n, const char *hex) {
    char buf[129];
    for (size_t i = 0; i < n; ++i) snprintf(buf + 2 * i, 3, "%02x", bytes[i]);
    return strcmp(buf, hex) == 0;
}

/* Sign a command payload, verify it like the ESP32 does, then hand it to the A2 session decoder. */
static int deliver(UgvCanCommand *c, const uint8_t *key, const uint8_t d[UGV_LITE_DGRAM_LEN], uint32_t now,
                   uint8_t may_start) {
    uint16_t id;
    uint8_t payload[8];
    return ugv_lite_unpack(d, UGV_LITE_DGRAM_LEN, UGV_LITE_CMD, &id, payload, key, 32) &&
           ugv_can_command_receive(c, id, payload, 8, now, may_start);
}

static int send(UgvCanCommand *c, const uint8_t *key, uint16_t id, const uint8_t p[8], uint32_t now,
                uint8_t may_start, uint8_t out[UGV_LITE_DGRAM_LEN]) {
    ugv_lite_pack(out, UGV_LITE_CMD, id, p, key, 32);
    return deliver(c, key, out, now, may_start);
}

/* R3 over the Lite link: a correctly signed drive datagram replayed after DRIVE -> ARM -> DRIVE is dropped. */
static void signed_replay(const uint8_t key[32]) {
    UgvCanCommand c;
    uint8_t d[UGV_LITE_DGRAM_LEN], old_go[UGV_LITE_DGRAM_LEN];
    const uint8_t idle0[8] = {0x78,0x56,0x34,0x12, 0,0, 0x10,0}, drive1[8] = {0x78,0x56,0x34,0x12, 1,0, 0x12,1};
    const uint8_t arm2[8] = {0x78,0x56,0x34,0x12, 2,0, 0x11,1}, drive3[8] = {0x78,0x56,0x34,0x12, 3,0, 0x12,1};
    const uint8_t go100[8] = {0xC8,0, 0xC8,0, 100,0, 0x78,0x56}, neutral101[8] = {0,0, 0,0, 101,0, 0x78,0x56};
    ugv_can_command_init(&c, 800);
    assert(send(&c, key, 0x110, idle0, 0, 1, d) && send(&c, key, 0x110, drive1, 10, 0, d));
    assert(send(&c, key, 0x100, go100, 11, 0, old_go) && c.left_mm_s == 200);  /* captured by an attacker */
    assert(send(&c, key, 0x110, arm2, 20, 0, d) && send(&c, key, 0x100, neutral101, 21, 0, d));
    assert(send(&c, key, 0x110, drive3, 30, 0, d));
    assert(!deliver(&c, key, old_go, 31, 0) && !ugv_can_command_fresh(&c, 31) && c.left_mm_s == 0);
}

int main(void) {
    uint8_t digest[32];
    ugv_sha256((const uint8_t *)"abc", 3, digest);
    assert(hex_eq(digest, 32, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"));
    uint8_t key1[20];
    memset(key1, 0x0b, sizeof key1);
    ugv_hmac_sha256(key1, sizeof key1, (const uint8_t *)"Hi There", 8, digest); /* RFC 4231 case 1 */
    assert(hex_eq(digest, 32, "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"));
    ugv_hmac_sha256((const uint8_t *)"Jefe", 4, (const uint8_t *)"what do ya want for nothing?", 28, digest);
    assert(hex_eq(digest, 32, "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"));

    /* Datagram: 'U' + direction + version + id16 + 8-byte payload + 8-byte HMAC tag. */
    uint8_t key[32];
    for (int i = 0; i < 32; ++i) key[i] = (uint8_t)i;
    const uint8_t lease[8] = {0x78, 0x56, 0x34, 0x12, 0, 0, 0x11, 1};
    uint8_t d[UGV_LITE_DGRAM_LEN];
    ugv_lite_pack(d, UGV_LITE_CMD, 0x110, lease, key, sizeof key);
    assert(hex_eq(d, UGV_LITE_DGRAM_LEN, "554301100178563412000011014fd3dde0206c7b81"));  /* same vector as Python */
    uint16_t id = 0;
    uint8_t payload[8];
    assert(ugv_lite_unpack(d, sizeof d, UGV_LITE_CMD, &id, payload, key, sizeof key));
    assert(id == 0x110 && memcmp(payload, lease, 8) == 0);

    uint8_t bad[UGV_LITE_DGRAM_LEN];
    for (int i = 0; i < UGV_LITE_DGRAM_LEN; ++i) {  /* any flipped bit is rejected */
        memcpy(bad, d, sizeof d);
        bad[i] ^= 0x01;
        assert(!ugv_lite_unpack(bad, sizeof bad, UGV_LITE_CMD, &id, payload, key, sizeof key));
    }
    uint8_t other[32];
    memcpy(other, key, sizeof key);
    other[0] ^= 1;
    assert(!ugv_lite_unpack(d, sizeof d, UGV_LITE_CMD, &id, payload, other, sizeof other));  /* wrong key */
    assert(!ugv_lite_unpack(d, sizeof d, UGV_LITE_TLM, &id, payload, key, sizeof key));      /* reflected */
    assert(!ugv_lite_unpack(d, sizeof d - 1, UGV_LITE_CMD, &id, payload, key, sizeof key));  /* short */
    ugv_lite_pack(d, UGV_LITE_TLM, 0x190, lease, key, sizeof key);
    assert(d[1] == 'T' && ugv_lite_unpack(d, sizeof d, UGV_LITE_TLM, &id, payload, key, sizeof key) && id == 0x190);
    /* M3 review: telemetry is bound to the lease it answers (session + extended lease sequence). The tag differs
       from the unbound one, so recorded telemetry verifies only against that one lease. */
    const uint8_t arm_tlm[8] = {3, 4, 0xFF, 0xFF, 0xFF, 0xFF, 1, 0};
    ugv_lite_pack_bound(d, UGV_LITE_TLM, 0x1A2, arm_tlm, key, sizeof key, 0x12345678u, 0x00010002u);
    assert(hex_eq(d, UGV_LITE_DGRAM_LEN, "555401a2010304ffffffff01002e94ae8f88cbcbdd"));  /* Python hmac, same bytes */
    assert(ugv_lite_unpack_bound(d, sizeof d, UGV_LITE_TLM, &id, payload, key, sizeof key, 0x12345678u, 0x00010002u));
    assert(id == 0x1A2 && !memcmp(payload, arm_tlm, 8));
    assert(!ugv_lite_unpack_bound(d, sizeof d, UGV_LITE_TLM, &id, payload, key, sizeof key, 0x12345678u, 0x00010003u));
    assert(!ugv_lite_unpack_bound(d, sizeof d, UGV_LITE_TLM, &id, payload, key, sizeof key, 0x12345679u, 0x00010002u));
    assert(!ugv_lite_unpack(d, sizeof d, UGV_LITE_TLM, &id, payload, key, sizeof key));
    signed_replay(key);
    puts("PASS: SHA-256 and HMAC RFC 4231 vectors; Lite datagram pack/verify, bit flips, wrong key, reflection, length; "
         "signed replay after a mode switch dropped (R3); telemetry bound to its lease (session + sequence)");
    return 0;
}
