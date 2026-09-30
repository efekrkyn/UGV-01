#include "lite_core.h"

#include <math.h>
#include <string.h>

static float clampf(float v, float lo, float hi) { return v < lo ? lo : v > hi ? hi : v; }
static int sgn(float v) { return (v > 0.0f) - (v < 0.0f); }
static void put16(uint8_t *p, uint16_t v) { p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8); }
static void put32(uint8_t *p, uint32_t v) { put16(p, (uint16_t)v); put16(p + 2, (uint16_t)(v >> 16)); }

float lite_core_limit_mv(float want_mv, float emf_mv) {
    const float span = LITE_I_LIMIT_A * LITE_PATH_OHM_MIN * 1000.0f;
    return clampf(want_mv, emf_mv - span, emf_mv + span);
}

size_t lite_core_sizeof(int which) {
    return which == 0 ? sizeof(LiteCore) : which == 1 ? sizeof(LiteInputs) : sizeof(LiteOutputs);
}

void lite_core_init(LiteCore *c, const uint8_t *key, size_t key_len, uint32_t now_ms) {
    memset(c, 0, sizeof *c);
    ugv_can_command_init(&c->cmd, LITE_MAX_SPEED_MM_S);
    ugv_can_servo_init(&c->servo_cmd);
    ugv_servo_init(&c->servo);
    ugv_arm_path_init(&c->arm);
    c->state = LITE_IDLE;
    c->need_idle = 1;  /* the first session starts with an IDLE handshake */
    c->arm_limp = 1;   /* power-on: where the arm is, only the operator knows (0x123) */
    c->grip_empty = 0; /* DD94: power-on (or a watchdog reset): whether the claw holds something is unknown (0x123) */
    c->key_len = key && key_len == LITE_KEY_LEN ? LITE_KEY_LEN : 0;  /* A01: no usable key = no link at all */
    if (c->key_len) memcpy(c->key, key, LITE_KEY_LEN);
    c->last_ms = c->tlm_at = now_ms;
    for (int m = 0; m < LITE_MOTORS; ++m) c->moving_at[m] = now_ms;
}

/* 0x123 (M3 review, DD94): the operator parked the arm at stow by hand AND closed the claw and emptied it (payload
   1, 1, 0, 0: both statements are required). Accepted only with the actuators off, the session tag and a forward
   sequence (per session); the core then trusts the stow pose and a closed, empty claw again - and nothing older. */
static int park_confirm(LiteCore *c, const uint8_t p[8]) {
    const uint16_t seq = (uint16_t)(p[4] | p[5] << 8), tag = (uint16_t)(p[6] | p[7] << 8);
    if (p[0] != 1 || p[1] != 1 || p[2] || p[3] || !c->cmd.have_session || tag != (uint16_t)c->cmd.session ||
        c->state == LITE_ARMED || c->state == LITE_DRIVING) return 0;
    if (c->park_session != c->cmd.session) c->have_park_seq = 0, c->park_session = c->cmd.session;
    if (c->have_park_seq && (int16_t)(seq - c->park_seq) <= 0) return 0;
    c->park_seq = seq;
    c->have_park_seq = 1;
    c->arm_limp = 0;
    ugv_arm_path_init(&c->arm);
    int32_t stow[UGV_ARM_JOINTS];
    ugv_arm_path_cdeg(&c->arm, stow);
    for (int j = 0; j < UGV_ARM_JOINTS; ++j)
        c->servo.pos_cdeg[UGV_SERVO_SHOULDER + j] = c->servo.target_cdeg[UGV_SERVO_SHOULDER + j] = stow[j];
    c->servo.pos_cdeg[UGV_SERVO_GRIPPER] = c->servo.target_cdeg[UGV_SERVO_GRIPPER] = 0;  /* closed, as confirmed */
    c->grip_empty = 1;
    return 1;
}

static int settled_node(const LiteCore *c) {  /* the pose the arm is known to be settled at, or -1 */
    const uint8_t node = c->arm.frac == 65535 ? c->arm.to : c->arm.frac == 0 ? c->arm.from : 0xFF;
    return !c->arm_limp && node < UGV_ARM_POSES && lite_core_arm_settled(c) ? node : -1;
}

static int claw_closed(const LiteCore *c) {  /* commanded closed and there */
    return !c->servo.target_cdeg[UGV_SERVO_GRIPPER] && !c->servo.pos_cdeg[UGV_SERVO_GRIPPER];
}

/* DD93 (M01): an "open" counts only with the arm settled at an OPEN pose (else the jaws stay put; the frame's AI flag
   still counts). DD94: a close keeps "empty" only settled at a RELEASE pose (over the cargo bin); anywhere else it may
   hold an object, so "empty" clears until the claw has been fully open again (lite_core_tick). */
static void claw_command(LiteCore *c, uint8_t close) {
    const int g = UGV_SERVO_GRIPPER, node = settled_node(c);
    if (c->arm_limp) return;  /* DD94 recheck: no pulse while limp, so no target either - the claw stays unknown */
    if (close) {
        if (c->servo.target_cdeg[g] && (node < 0 || !((UGV_ARM_RELEASE_MASK >> node) & 1))) c->grip_empty = 0;
        ugv_servo_set_target(&c->servo, g, 0);
    } else if (node >= 0 && ((UGV_ARM_OPEN_MASK >> node) & 1)) {
        ugv_servo_set_target(&c->servo, g, UGV_GRIP_OPEN_CDEG);
    }
}

static int open_edge(uint8_t from, uint8_t to) {  /* both ends swept with the jaws open */
    return from < UGV_ARM_POSES && to < UGV_ARM_POSES && ((UGV_ARM_OPEN_MASK >> from) & 1) && ((UGV_ARM_OPEN_MASK >> to) & 1);
}

int lite_core_receive(LiteCore *c, const uint8_t *dgram, size_t len, uint32_t now_ms) {
    uint16_t id;
    uint8_t p[8];
    if (c->key_len != LITE_KEY_LEN || !ugv_lite_unpack(dgram, len, UGV_LITE_CMD, &id, p, c->key, c->key_len)) return 0;
    if (id == 0x123) return park_confirm(c, p);
    if (id >= 0x120 && id <= 0x122) {
        if (!ugv_can_servo_receive(&c->servo_cmd, &c->cmd, id, p, 8, now_ms)) return 0;
        const UgvCanServo *v = &c->servo_cmd;
        if (id == 0x120) {
            ugv_servo_set_target(&c->servo, UGV_SERVO_PAN, v->pan_cdeg);
            ugv_servo_set_target(&c->servo, UGV_SERVO_TILT, v->tilt_cdeg);
        } else if (id == 0x121) {  /* M3: gripper + AI flag only; the arm joints follow the path */
            claw_command(c, v->gripper);
        } else {
            if (c->arm_limp || (!claw_closed(c) && !open_edge(v->path_from, v->path_to)) ||
                !ugv_arm_path_command(&c->arm, v->path_from, v->path_to, v->path_target)) return 0;
            c->path_ack = v->path_seq;  /* A06: the echo moves only with a command the arm took (a refused one, new
                                           sequence or not, still burns its sequence against replay) */
        }
        return 1;
    }
    const uint8_t may_start = c->state != LITE_ARMED && c->state != LITE_DRIVING;
    if (!ugv_can_command_receive(&c->cmd, id, p, 8, now_ms, may_start)) return 0;
    if (id == 0x110) {  /* telemetry binding follows the accepted lease stream (sequence extended to 32 bits) */
        if (!c->bound || c->cmd.session != c->tlm_session)  /* new session: no arm command taken in it yet */
            c->bound = 1, c->tlm_session = c->cmd.session, c->lease_ext = c->cmd.lease_seq, c->path_ack = 0;
        else
            c->lease_ext += (uint16_t)(c->cmd.lease_seq - (uint16_t)c->lease_ext);
    }
    return 1;
}

static void trip(LiteCore *c, uint8_t bits, uint32_t now_ms) {
    c->faults |= bits;
    c->fault_at = now_ms;
    c->state = LITE_FAULT;
}

static uint8_t idle_handshake(const UgvCanCommand *m, uint32_t now_ms) {
    return m->have_lease && now_ms - m->lease_at_ms <= 100 && m->mode == UGV_CAN_MODE_IDLE && !m->deadman;
}

LiteOutputs lite_core_tick(LiteCore *c, const LiteInputs *in, uint32_t now_ms) {
    LiteOutputs out;
    memset(&out, 0, sizeof out);
    const uint32_t dt = now_ms - c->last_ms ? now_ms - c->last_ms : 1;
    c->last_ms = now_ms;

    /* E-stop: an edge or the level latches; release leaves IDLE (or FAULT) and needs a new handshake. */
    if (in->estop_edge || in->estop_level) {
        c->state = LITE_ESTOP;
        c->need_idle = 1;
    } else if (c->state == LITE_ESTOP) {
        c->state = c->faults ? LITE_FAULT : LITE_IDLE;
    }
    if (ugv_can_take_stop(&c->cmd)) {
        c->need_idle = 1;
        if (c->state == LITE_ARMED || c->state == LITE_DRIVING) c->state = LITE_IDLE;
    }
    if (in->vbat_mv < LITE_VBAT_LOW_MV) {
        if (!c->low_timing) c->low_timing = 1, c->low_since = now_ms;
        if (now_ms - c->low_since >= LITE_VBAT_LOW_MS && !(c->faults & LITE_FAULT_LOW_BATTERY))
            trip(c, LITE_FAULT_LOW_BATTERY, now_ms);
    } else if (in->vbat_mv >= LITE_VBAT_OK_MV) {
        c->low_timing = 0;
    }
    /* IDLE handshake (fresh lease, mode IDLE, deadman released) re-enables arming and clears faults
       whose cause is gone: battery back above 9.9 V; stall/thermal after the cooldown with no stored heat. */
    if (idle_handshake(&c->cmd, now_ms) && !in->estop_level) {
        c->need_idle = 0;
        if (in->vbat_mv >= LITE_VBAT_OK_MV) c->faults &= (uint8_t)~LITE_FAULT_LOW_BATTERY;
        if (now_ms - c->fault_at >= LITE_FAULT_COOLDOWN_MS && c->heat_j[0] <= 0.0f && c->heat_j[1] <= 0.0f)
            c->faults &= LITE_FAULT_LOW_BATTERY;
        if (!c->faults && c->state == LITE_FAULT) c->state = LITE_IDLE;
    }

    const uint8_t fresh = ugv_can_command_fresh(&c->cmd, now_ms);
    switch (c->state) {
    case LITE_IDLE:
        if (!c->need_idle && !c->faults && fresh && c->cmd.mode == UGV_CAN_MODE_ARM &&
            !c->cmd.left_mm_s && !c->cmd.right_mm_s) {
            if (!c->arming) c->arming = 1, c->arm_since = now_ms;
            if (now_ms - c->arm_since >= LITE_ARM_NEUTRAL_MS) c->state = LITE_ARMED, c->arming = 0;
        } else {
            c->arming = 0;
        }
        break;
    case LITE_ARMED:
    case LITE_DRIVING:
        if (!fresh) {
            c->state = LITE_IDLE;
            c->need_idle = 1;
        } else {
            c->state = c->cmd.mode == UGV_CAN_MODE_DRIVE ? LITE_DRIVING : LITE_ARMED;
        }
        break;
    default:
        break;
    }

    /* Side targets: speed ceiling (200 mm/s in AI mode), ToF forward block at once, 0.5 m/s2 ramp. */
    const uint8_t driving = c->state == LITE_DRIVING;
    const uint8_t blocked = !in->tof_mm[0] || !in->tof_mm[1] || in->tof_mm[0] < LITE_TOF_STOP_MM ||
                            in->tof_mm[1] < LITE_TOF_STOP_MM;
    /* DD94: a sensor that saw nothing in range is no clear road: forward at a creep only (0xFFFF, vl53l0x.h) */
    const uint8_t blind = !blocked && (in->tof_mm[0] == 0xFFFF || in->tof_mm[1] == 0xFFFF);
    const int32_t cap = driving ? ugv_can_speed_cap_mm_s(&c->servo_cmd, LITE_MAX_SPEED_MM_S, now_ms) : 0;
    const uint8_t arm_ok = (uint8_t)lite_core_arm_allows_drive(c);
    const int32_t want[2] = {c->cmd.left_mm_s, c->cmd.right_mm_s};
    const int32_t step = (int32_t)(LITE_ACCEL_MM_S2 * dt / 1000);
    for (int s = 0; s < 2; ++s) {
        int32_t w = driving ? (want[s] > cap ? cap : want[s] < -cap ? -cap : want[s]) : 0;
        if (blocked && w > 0) w = 0;
        if (blind && w > LITE_TOF_BLIND_MM_S) w = LITE_TOF_BLIND_MM_S;
        if (!arm_ok) w = 0;  /* DD84: ramped stop while the arm is out of a drive pose */
        if ((blocked && c->target_mm_s[s] > 0) || !driving) c->target_mm_s[s] = 0;
        const int32_t d = w - c->target_mm_s[s];
        c->target_mm_s[s] += d > step ? step : d < -step ? -step : d;
    }

    /* Per motor: feed-forward voltage + PI speed loop, back-EMF limit, zero crossing through a coast tick,
       stall and the conservative current estimate for the TB6612 thermal budget. */
    const float vbat = in->vbat_mv;
    float chip_w[2] = {0.0f, 0.0f};
    for (int m = 0; m < LITE_MOTORS; ++m) {
        const int side = m == LITE_FR || m == LITE_RR;
        const uint32_t edges = in->enc[m] - c->last.enc[m];
        const float rpm = edges * 60000.0f / LITE_COUNTS_PER_REV / (float)dt;
        const float emf = LITE_KE_MV_PER_RPM * rpm * c->dir[m];
        float v = 0.0f;
        if (driving && vbat > 1000.0f && c->target_mm_s[side]) {
            const float wheel_rpm = c->target_mm_s[side] * 60.0f / LITE_WHEEL_MM;
            const float err = wheel_rpm - rpm * (float)(c->dir[m] ? c->dir[m] : sgn(wheel_rpm));
            const float want = LITE_KE_MV_PER_RPM * wheel_rpm + sgn(wheel_rpm) * LITE_RUN_A * LITE_PATH_OHM * 1000.0f
                               + LITE_KP_MV_PER_RPM * err + c->integ_mv[m];
            v = clampf(lite_core_limit_mv(want, emf), -vbat, vbat);
            /* anti-windup: no integration further into a limit that already clips the output */
            const int pinned = (v < want - 0.5f && err > 0.0f) || (v > want + 0.5f && err < 0.0f);
            if (!pinned)
                c->integ_mv[m] = clampf(c->integ_mv[m] + LITE_KI_MV_PER_RPM_S * err * (float)dt / 1000.0f, -vbat, vbat);
        } else {
            c->integ_mv[m] = 0.0f;
        }
        if (c->dir[m] && sgn(v) && sgn(v) != c->dir[m]) {
            c->integ_mv[m] = 0.0f;  /* the old direction's integral must not push the new one */
            if (!c->coasted[m]) {
                v = 0.0f;  /* reversal: one tick of coast before any opposite drive */
                c->coasted[m] = 1;
            } else if (rpm <= LITE_REVERSE_RPM) {
                c->dir[m] = (int8_t)sgn(v);
            }
        } else if (sgn(v)) {
            c->coasted[m] = 0;
            if (!c->dir[m]) c->dir[m] = (int8_t)sgn(v);
        }
        c->odo[m] += (int32_t)edges * (c->dir[m] ? c->dir[m] : 1);
        if (driving && fabsf(v) >= LITE_STALL_MIN_MV && !edges) {
            if (now_ms - c->moving_at[m] >= LITE_STALL_MS) trip(c, (uint8_t)(LITE_FAULT_STALL_FL << m), now_ms);
        } else {
            c->moving_at[m] = now_ms;
        }
        const float amps = v != 0.0f ? fabsf(v - emf) / 1000.0f / LITE_PATH_OHM_MIN : 0.0f;
        chip_w[side] += amps * amps * LITE_BRIDGE_OHM;
        out.duty_permil[m] = (int16_t)(vbat > 1000.0f ? v / vbat * 1000.0f : 0.0f);
    }
    for (int k = 0; k < 2; ++k) {
        c->heat_j[k] += (chip_w[k] - LITE_CHIP_CONT_W) * (float)dt / 1000.0f;
        if (c->heat_j[k] < 0.0f) c->heat_j[k] = 0.0f;
        if (c->heat_j[k] > LITE_CHIP_HEAT_J && !(c->faults & LITE_FAULT_THERMAL)) trip(c, LITE_FAULT_THERMAL, now_ms);
    }

    out.act_en = c->state == LITE_ARMED || c->state == LITE_DRIVING;
    if (c->state != LITE_DRIVING) {
        memset(out.duty_permil, 0, sizeof out.duty_permil);
        c->target_mm_s[0] = c->target_mm_s[1] = 0;
    }
    /* M3 review: the servo rails follow ACT_EN, so the arm goes limp and droops when it drops. Settled at stow it
       rests on the fender (swept limp rest); anywhere else its pose is unknown afterwards: latch it limp. */
    if (c->act_was && !out.act_en &&
        !(lite_core_arm_settled(c) && ugv_arm_path_at_node(&c->arm, UGV_ARM_STOW) && claw_closed(c)))
        c->arm_limp = 1, c->grip_empty = 0;  /* DD94: the claw too - what it held or where it went is unknown until 0x123 */
    c->act_was = out.act_en;
    ugv_servo_enable(&c->servo, out.act_en, now_ms);
    /* N1: the arm advances along its edge only while the actuators are enabled; all five joint targets come
       from one path point per tick (<= 45 deg/s, below every joint's own rate, so the servos track it). */
    if (out.act_en && !c->arm_limp) ugv_arm_path_tick(&c->arm, dt);
    else c->arm.target = c->arm.frac;  /* disarm, lease loss or E-stop cancels the move: no resume on re-arm */
    int32_t arm_cdeg[UGV_ARM_JOINTS];
    ugv_arm_path_cdeg(&c->arm, arm_cdeg);
    for (int j = 0; j < UGV_ARM_JOINTS; ++j) ugv_servo_set_target(&c->servo, UGV_SERVO_SHOULDER + j, arm_cdeg[j]);
    ugv_servo_tick(&c->servo, now_ms, 0, out.act_en && !in->estop_level);  /* Lite: no servo current sense */
    for (int j = 0; j < UGV_SERVO_COUNT; ++j) out.servo_us[j] = ugv_servo_pulse_us(&c->servo, j);
    if (!c->arm_limp && c->servo.target_cdeg[UGV_SERVO_GRIPPER] == UGV_GRIP_OPEN_CDEG &&
        c->servo.pos_cdeg[UGV_SERVO_GRIPPER] == UGV_GRIP_OPEN_CDEG)
        c->grip_empty = 1;  /* DD93: fully open (and driven: not limp), nothing can be held */
    if (c->arm_limp)  /* no pulse: the powered arm servos stay limp; head and gripper still run */
        for (int j = 0; j <= UGV_ARM_JOINTS; ++j) out.servo_us[UGV_SERVO_SHOULDER + j] = 0;  /* DD94: claw too */

    static const uint8_t MODE[] = {UGV_LIGHT_IDLE, UGV_LIGHT_ARMED, UGV_LIGHT_DRIVING, UGV_LIGHT_ESTOP, UGV_LIGHT_FAULT};
    uint8_t mode = MODE[c->state];
    if (c->state == LITE_DRIVING && c->servo_cmd.ai_mode) mode = UGV_LIGHT_AI;
    const float pct = clampf((vbat - LITE_VBAT_LOW_MV) * 100.0f / (12600.0f - LITE_VBAT_LOW_MV), 0.0f, 100.0f);
    ugv_light_frame(out.light, mode, (uint8_t)pct, now_ms);

    out.state = c->state;
    out.faults = c->faults;
    out.forward_blocked = blocked;
    out.forward_blind = blind;
    c->flags = (uint8_t)(c->need_idle | blocked << 1 | out.act_en << 2 | !arm_ok << 3 | c->grip_empty << 4 | blind << 5);
    c->last = *in;
    return out;
}

int lite_core_arm_settled(const LiteCore *c) {
    if (c->arm.frac != c->arm.target) return 0;
    for (int j = 0; j < UGV_ARM_JOINTS; ++j)
        if (c->servo.pos_cdeg[UGV_SERVO_SHOULDER + j] != c->servo.target_cdeg[UGV_SERVO_SHOULDER + j]) return 0;
    return 1;
}

int lite_core_arm_allows_drive(const LiteCore *c) {
    const int node = settled_node(c);  /* A04/DD93: and the claw closed and empty */
    return node >= 0 && ((UGV_ARM_DRIVE_MASK >> node) & 1) && claw_closed(c) && c->grip_empty;
}

int lite_core_telemetry(LiteCore *c, uint32_t now_ms, uint8_t out[4][UGV_LITE_DGRAM_LEN]) {
    if (c->key_len != LITE_KEY_LEN || now_ms - c->tlm_at < LITE_TLM_PERIOD_MS) return 0;
    c->tlm_at = now_ms;
    const uint32_t s = c->bound ? c->tlm_session : 0, e = c->bound ? c->lease_ext : 0;  /* lease binding */
    uint8_t p[8];
    p[0] = (uint8_t)c->state;
    p[1] = c->faults;
    put16(p + 2, c->tlm_seq++);
    put32(p + 4, now_ms);
    ugv_lite_pack_bound(out[0], UGV_LITE_TLM, 0x190, p, c->key, c->key_len, s, e);
    put16(p, c->last.vbat_mv);
    put16(p + 2, c->flags);  /* bit0 needs IDLE handshake, bit1 forward blocked, bit2 ACT_EN, bit3 arm/claw blocks drive,
                                bit4 claw empty (DD93), bit5 forward blind (DD94) */
    put16(p + 4, c->last.tof_mm[0]);
    put16(p + 6, c->last.tof_mm[1]);
    ugv_lite_pack_bound(out[1], UGV_LITE_TLM, 0x1A0, p, c->key, c->key_len, s, e);
    put32(p, (uint32_t)((c->odo[LITE_FL] + c->odo[LITE_RL]) / 2));  /* channel-A edges, signed by direction */
    put32(p + 4, (uint32_t)((c->odo[LITE_FR] + c->odo[LITE_RR]) / 2));
    ugv_lite_pack_bound(out[2], UGV_LITE_TLM, 0x1A1, p, c->key, c->key_len, s, e);
    p[0] = c->arm.from;  /* N1: the MacBook moves on only when the core reports the arm settled */
    p[1] = c->arm.to;
    put16(p + 2, c->arm.frac);
    put16(p + 4, c->arm.target);
    const int g = UGV_SERVO_GRIPPER;
    const int live = !c->arm_limp;  /* DD94 recheck: a limp claw gets no pulse, so the model is no evidence */
    p[6] = (uint8_t)((live && lite_core_arm_settled(c)) | c->arm_limp << 1 |          /* bit0 settled, bit1 limp */
                     (live && c->servo.target_cdeg[g] == 0) << 2 |                     /* bit2 claw closed */
                     (live && c->servo.pos_cdeg[g] == c->servo.target_cdeg[g]) << 3 |  /* bit3 gripper settled */
                     (c->path_ack >> 8 & 0x0F) << 4);                                    /* echo bits 8-11 */
    p[7] = (uint8_t)c->path_ack;  /* N3/A06: the last 0x122 the arm took, low byte */
    ugv_lite_pack_bound(out[3], UGV_LITE_TLM, 0x1A2, p, c->key, c->key_len, s, e);
    return 4;
}
