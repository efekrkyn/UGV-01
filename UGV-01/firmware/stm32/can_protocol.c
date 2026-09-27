#include "can_protocol.h"

static uint16_t u16(const uint8_t *p) { return (uint16_t)p[0] | (uint16_t)p[1] << 8; }
static uint32_t u32(const uint8_t *p) { return (uint32_t)u16(p) | (uint32_t)u16(p+2) << 16; }
static uint8_t forward(uint16_t next, uint16_t previous) {
    uint16_t d = (uint16_t)(next - previous);
    return d != 0 && d < 0x8000;
}

void ugv_can_command_init(UgvCanCommand *c, uint16_t max_speed_mm_s) {
    *c = (UgvCanCommand){.max_speed_mm_s = max_speed_mm_s};
}

uint8_t ugv_can_command_fresh(const UgvCanCommand *c, uint32_t now_ms) {
    return c->have_lease && c->have_command && c->deadman &&
           (c->mode == UGV_CAN_MODE_ARM || c->mode == UGV_CAN_MODE_DRIVE) &&
           now_ms - c->lease_at_ms <= 100 && now_ms - c->command_at_ms <= 100;
}

uint8_t ugv_can_take_stop(UgvCanCommand *c) {
    uint8_t pending = c->stop_pending;
    c->stop_pending = 0;
    return pending;
}

int ugv_can_command_receive(UgvCanCommand *c, uint16_t id, const uint8_t data[8],
                            uint8_t dlc, uint32_t now_ms, uint8_t may_start_session) {
    if (!c || !data || dlc != 8) return 0;
    if (id == 0x080) {
        if (data[0] != 1) return 0;
        c->stop_pending = 1;
        return 1;
    }
    if (id == 0x110) {
        const uint32_t session = u32(data);
        const uint16_t seq = u16(data+4);
        const uint8_t mode = data[6] & 0x0F;
        const uint8_t version = data[6] >> 4;
        const uint8_t deadman = data[7];
        if (version != 1 || mode > UGV_CAN_MODE_DRIVE || deadman > 1) return 0;
        if (!c->have_session || session != c->session) {
            if (!may_start_session || mode != UGV_CAN_MODE_IDLE || deadman) return 0;
            c->session = session;
            c->have_session = 1;
            c->have_command = c->have_command_seq = 0;
        } else if (!forward(seq, c->lease_seq)) return 0;
        if (mode != c->mode) c->have_command = 0;
        c->lease_seq = seq;
        c->lease_at_ms = now_ms;
        c->have_lease = 1;
        c->mode = mode;
        c->deadman = deadman;
        return 1;
    }
    if (id == 0x100) {
        if (!c->have_lease || now_ms - c->lease_at_ms > 100 ||
            !c->deadman || c->mode == UGV_CAN_MODE_IDLE ||
            u16(data+6) != (uint16_t)c->session) return 0;
        const int16_t left = (int16_t)u16(data);
        const int16_t right = (int16_t)u16(data+2);
        const uint16_t seq = u16(data+4);
        if ((int32_t)left > c->max_speed_mm_s || (int32_t)left < -(int32_t)c->max_speed_mm_s ||
            (int32_t)right > c->max_speed_mm_s || (int32_t)right < -(int32_t)c->max_speed_mm_s ||
            (c->mode == UGV_CAN_MODE_ARM && (left || right)) ||
            (c->have_command_seq && !forward(seq, c->command_seq))) return 0;
        c->left_mm_s = left;
        c->right_mm_s = right;
        c->command_seq = seq;
        c->command_at_ms = now_ms;
        c->have_command = c->have_command_seq = 1;
        return 1;
    }
    return 0;
}

void ugv_can_servo_init(UgvCanServo *s) {
    *s = (UgvCanServo){0};
}

int ugv_can_servo_receive(UgvCanServo *s, const UgvCanCommand *c, uint16_t id,
                          const uint8_t data[8], uint8_t dlc, uint32_t now_ms) {
    if (!s || !c || !data || dlc != 8 || id < 0x120 || id > 0x122) return 0;
    const uint16_t seq = u16(data+4);
    const uint16_t tag = u16(data+6);
    if (!c->have_lease || now_ms - c->lease_at_ms > 100 || !c->deadman ||
        c->mode == UGV_CAN_MODE_IDLE || tag != (uint16_t)c->session) return 0;
    if (tag != s->tag) {  /* new session: sequence history starts over */
        s->have_head = s->have_arm = s->have_path = 0;
        s->tag = tag;
    }
    if (id == 0x120) {
        if (s->have_head && !forward(seq, s->head_seq)) return 0;
        s->pan_cdeg = (int16_t)u16(data);
        s->tilt_cdeg = (int16_t)u16(data+2);
        s->head_seq = seq;
        s->head_at_ms = now_ms;
        s->have_head = 1;
        return 1;
    }
    if (id == 0x122) {
        if (s->have_path && !forward(seq, s->path_seq)) return 0;
        s->path_from = data[0];
        s->path_to = data[1];
        s->path_target = u16(data+2);
        s->path_seq = seq;
        s->have_path = 1;
        return 1;
    }
    if (data[2] > 1 || (data[3] & 0xFE) || (s->have_arm && !forward(seq, s->arm_seq))) return 0;
    s->shoulder_cdeg = (int16_t)u16(data);
    s->gripper = data[2];
    s->ai_mode = data[3] & 1;
    s->arm_seq = seq;
    s->arm_at_ms = now_ms;
    s->have_arm = 1;
    return 1;
}

uint16_t ugv_can_speed_cap_mm_s(const UgvCanServo *s, uint16_t base_mm_s, uint32_t now_ms) {
    const uint8_t manual = s->have_arm && !s->ai_mode &&
                           now_ms - s->arm_at_ms <= UGV_CAN_ARM_FRAME_TIMEOUT_MS;
    return manual || base_mm_s < UGV_CAN_AI_SPEED_MM_S ? base_mm_s : UGV_CAN_AI_SPEED_MM_S;
}
