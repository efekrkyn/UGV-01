#ifndef UGV_LITE_LINK_H
#define UGV_LITE_LINK_H

#include <stddef.h>
#include <stdint.h>

/* A3 Lite Wi-Fi UDP datagram: 'U', direction ('C' command / 'T' telemetry), version 1, id16 (LE),
   8-byte payload (A2 CAN frame layouts), first 8 bytes of HMAC-SHA256 over bytes 0..12.
   The direction byte is authenticated, so telemetry cannot be reflected back as a command.
   Commands: replay protection comes from the session/sequence fields inside the payloads.
   Telemetry (M3 review): the tag also covers a binding = the lease session (LE32) and the extended lease sequence
   (LE32) the core last accepted, both 0 before the first lease. The MacBook verifies it only against leases it
   sent within its staleness window, so recorded, delayed or other-session telemetry is dropped. */
#define UGV_LITE_DGRAM_LEN 21
#define UGV_LITE_TAG_LEN 8
enum { UGV_LITE_CMD = 'C', UGV_LITE_TLM = 'T' };

void ugv_lite_pack(uint8_t out[UGV_LITE_DGRAM_LEN], uint8_t direction, uint16_t id, const uint8_t payload[8],
                   const uint8_t *key, size_t key_len);
/* 1 = authentic datagram of the expected direction; 0 = drop it. */
int ugv_lite_unpack(const uint8_t *in, size_t len, uint8_t direction, uint16_t *id, uint8_t payload[8],
                    const uint8_t *key, size_t key_len);
void ugv_lite_pack_bound(uint8_t out[UGV_LITE_DGRAM_LEN], uint8_t direction, uint16_t id, const uint8_t payload[8],
                         const uint8_t *key, size_t key_len, uint32_t session, uint32_t lease_ext);
int ugv_lite_unpack_bound(const uint8_t *in, size_t len, uint8_t direction, uint16_t *id, uint8_t payload[8],
                          const uint8_t *key, size_t key_len, uint32_t session, uint32_t lease_ext);

#endif
