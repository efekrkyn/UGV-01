#ifndef UGV_HMAC_SHA256_H
#define UGV_HMAC_SHA256_H

#include <stddef.h>
#include <stdint.h>

/* Portable SHA-256 (FIPS 180-4) and HMAC-SHA256 (RFC 2104); host-testable, used by the Lite link. */
void ugv_sha256(const uint8_t *data, size_t len, uint8_t out[32]);
void ugv_hmac_sha256(const uint8_t *key, size_t key_len, const uint8_t *data, size_t len, uint8_t out[32]);

#endif
