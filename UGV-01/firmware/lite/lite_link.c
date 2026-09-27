#include "lite_link.h"

#include <string.h>

#include "hmac_sha256.h"

/* HMAC over the 13 datagram bytes, followed by the 8-byte binding when there is one. */
static void tag(const uint8_t *body, const uint8_t *bind, const uint8_t *key, size_t key_len,
                uint8_t out[UGV_LITE_TAG_LEN]) {
    enum { BODY = UGV_LITE_DGRAM_LEN - UGV_LITE_TAG_LEN };
    uint8_t msg[BODY + 8], mac[32];
    memcpy(msg, body, BODY);
    if (bind) memcpy(msg + BODY, bind, 8);
    ugv_hmac_sha256(key, key_len, msg, bind ? sizeof msg : BODY, mac);
    memcpy(out, mac, UGV_LITE_TAG_LEN);
}

static void binding(uint8_t out[8], uint32_t session, uint32_t lease_ext) {
    for (int i = 0; i < 4; ++i) out[i] = (uint8_t)(session >> 8 * i), out[4 + i] = (uint8_t)(lease_ext >> 8 * i);
}

static void pack(uint8_t out[UGV_LITE_DGRAM_LEN], uint8_t direction, uint16_t id, const uint8_t payload[8],
                 const uint8_t *bind, const uint8_t *key, size_t key_len) {
    out[0] = 'U';
    out[1] = direction;
    out[2] = 1;
    out[3] = (uint8_t)id;
    out[4] = (uint8_t)(id >> 8);
    memcpy(out + 5, payload, 8);
    tag(out, bind, key, key_len, out + 13);
}

static int unpack(const uint8_t *in, size_t len, uint8_t direction, uint16_t *id, uint8_t payload[8],
                  const uint8_t *bind, const uint8_t *key, size_t key_len) {
    if (!in || len != UGV_LITE_DGRAM_LEN || in[0] != 'U' || in[1] != direction || in[2] != 1) return 0;
    uint8_t expect[UGV_LITE_TAG_LEN], diff = 0;
    tag(in, bind, key, key_len, expect);
    for (int i = 0; i < UGV_LITE_TAG_LEN; ++i) diff |= expect[i] ^ in[13 + i];  /* constant time */
    if (diff) return 0;
    *id = (uint16_t)(in[3] | in[4] << 8);
    memcpy(payload, in + 5, 8);
    return 1;
}

void ugv_lite_pack(uint8_t out[UGV_LITE_DGRAM_LEN], uint8_t direction, uint16_t id, const uint8_t payload[8],
                   const uint8_t *key, size_t key_len) {
    pack(out, direction, id, payload, 0, key, key_len);
}

int ugv_lite_unpack(const uint8_t *in, size_t len, uint8_t direction, uint16_t *id, uint8_t payload[8],
                    const uint8_t *key, size_t key_len) {
    return unpack(in, len, direction, id, payload, 0, key, key_len);
}

void ugv_lite_pack_bound(uint8_t out[UGV_LITE_DGRAM_LEN], uint8_t direction, uint16_t id, const uint8_t payload[8],
                         const uint8_t *key, size_t key_len, uint32_t session, uint32_t lease_ext) {
    uint8_t bind[8];
    binding(bind, session, lease_ext);
    pack(out, direction, id, payload, bind, key, key_len);
}

int ugv_lite_unpack_bound(const uint8_t *in, size_t len, uint8_t direction, uint16_t *id, uint8_t payload[8],
                          const uint8_t *key, size_t key_len, uint32_t session, uint32_t lease_ext) {
    uint8_t bind[8];
    binding(bind, session, lease_ext);
    return unpack(in, len, direction, id, payload, bind, key, key_len);
}
