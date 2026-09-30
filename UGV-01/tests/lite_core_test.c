#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../firmware/lite/lite_core.h"
#include "../firmware/lite/arm_graph.h"

/* Host test of the A3 Lite core with signed datagrams and a first-order motor model (ballast path,
   back-EMF, load current, channel-A encoder edges). Numbers are model results, not measurements. */
static uint8_t KEY[32];

typedef struct {
    LiteCore c;
    LiteInputs in;
    LiteOutputs out;
    uint32_t now;
    uint16_t lseq, cseq, aseq;
    uint8_t mode, deadman, send, manual;
    int16_t left, right;
    float rpm[LITE_MOTORS], frac[LITE_MOTORS], load_a[LITE_MOTORS], imax[LITE_MOTORS];
    uint8_t stalled[LITE_MOTORS];
} Rig;

static void send(Rig *r, uint16_t id, const uint8_t p[8]) {
    uint8_t d[UGV_LITE_DGRAM_LEN];
    ugv_lite_pack(d, UGV_LITE_CMD, id, p, KEY, sizeof KEY);
    lite_core_receive(&r->c, d, sizeof d, r->now);
}

static void traffic(Rig *r) {
    const uint16_t ls = r->lseq++;
    const uint8_t lease[8] = {0x78,0x56,0x34,0x12, (uint8_t)ls, (uint8_t)(ls >> 8), (uint8_t)(0x10 | r->mode), r->deadman};
    send(r, 0x110, lease);
    if (r->mode == UGV_CAN_MODE_IDLE) return;
    const uint16_t l = (uint16_t)(r->mode == UGV_CAN_MODE_DRIVE ? r->left : 0);
    const uint16_t rr = (uint16_t)(r->mode == UGV_CAN_MODE_DRIVE ? r->right : 0);
    const uint16_t cs = r->cseq++;
    const uint8_t drive[8] = {(uint8_t)l, (uint8_t)(l >> 8), (uint8_t)rr, (uint8_t)(rr >> 8),
                              (uint8_t)cs, (uint8_t)(cs >> 8), 0x78, 0x56};
    send(r, 0x100, drive);
    if (r->manual) {  /* manual 0x121 (shoulder 180.00 deg, open, AI flag 0) lifts the 200 mm/s AI cap */
        const uint16_t as = r->aseq++;
        const uint8_t arm[8] = {0x50,0x46, 0, 0, (uint8_t)as, (uint8_t)(as >> 8), 0x78, 0x56};
        send(r, 0x121, arm);
    }
}

/* First-order motor through winding + ballast + bridge: real current from the applied voltage and
   back-EMF, a friction/load current opposing motion, 80 ms mechanical time constant. */
static void motors(Rig *r) {
    const float dt = LITE_TICK_MS / 1000.0f;
    for (int m = 0; m < LITE_MOTORS; ++m) {
        const int driven = r->out.act_en && r->out.duty_permil[m];
        const float v = driven ? r->out.duty_permil[m] / 1000.0f * r->in.vbat_mv : 0.0f;
        const float amps = driven ? (v - LITE_KE_MV_PER_RPM * r->rpm[m]) / 1000.0f / LITE_PATH_OHM : 0.0f;
        if (fabsf(amps) > r->imax[m]) r->imax[m] = fabsf(amps);
        const float drag = (0.07f + r->load_a[m]) * LITE_PATH_OHM * 1000.0f;
        const float ss = v > drag ? (v - drag) / LITE_KE_MV_PER_RPM : v < -drag ? (v + drag) / LITE_KE_MV_PER_RPM : 0.0f;
        r->rpm[m] = r->stalled[m] ? 0.0f : r->rpm[m] + (ss - r->rpm[m]) * dt / 0.08f;
        r->frac[m] += fabsf(r->rpm[m]) * LITE_COUNTS_PER_REV / 60.0f * dt;
        const uint32_t edges = (uint32_t)r->frac[m];
        r->frac[m] -= (float)edges;
        r->in.enc[m] += edges;
    }
}

static void run(Rig *r, uint32_t ms) {
    for (uint32_t t = 0; t < ms; t += LITE_TICK_MS) {
        r->now += LITE_TICK_MS;
        motors(r);
        if (r->send) traffic(r);
        r->out = lite_core_tick(&r->c, &r->in, r->now);
        r->in.estop_edge = 0;  /* the driver clears the ISR latch after each tick */
    }
}

static void rig_init(Rig *r) {
    memset(r, 0, sizeof *r);
    r->in.vbat_mv = 12000;
    r->in.tof_mm[0] = r->in.tof_mm[1] = 2000;
    r->now = 1000;
    r->send = 1;
    lite_core_init(&r->c, KEY, sizeof KEY, r->now);
}

static void handshake(Rig *r, uint32_t ms) {  /* IDLE lease, deadman released */
    r->mode = UGV_CAN_MODE_IDLE;
    r->deadman = 0;
    run(r, ms);
}

static void arm(Rig *r) {
    handshake(r, 60);
    r->mode = UGV_CAN_MODE_ARM;
    r->deadman = 1;
    run(r, 600);
    assert(r->out.state == LITE_ARMED && r->out.act_en);
}

static void drive(Rig *r, int16_t left, int16_t right, uint32_t ms) {
    r->mode = UGV_CAN_MODE_DRIVE;
    r->deadman = 1;
    r->left = left;
    r->right = right;
    run(r, ms);
}

static uint16_t arm_seq;
static int arm_cmd(Rig *r, uint8_t from, uint8_t to, uint16_t target) {  /* 0x122 path frame */
    const uint16_t sq = arm_seq++;
    const uint8_t p[8] = {from, to, (uint8_t)target, (uint8_t)(target >> 8), (uint8_t)sq, (uint8_t)(sq >> 8), 0x78, 0x56};
    uint8_t d[UGV_LITE_DGRAM_LEN];
    ugv_lite_pack(d, UGV_LITE_CMD, 0x122, p, KEY, sizeof KEY);
    return lite_core_receive(&r->c, d, sizeof d, r->now);
}

static void claw(Rig *r, int close) {  /* 0x121: claw close/open, AI flag */
    const uint16_t sq = r->aseq++;
    const uint8_t p[8] = {0, 0, (uint8_t)close, 1, (uint8_t)sq, (uint8_t)(sq >> 8), 0x78, 0x56};
    send(r, 0x121, p);
}

static int claw_there(const Rig *r, int32_t cdeg) {
    return r->c.servo.target_cdeg[UGV_SERVO_GRIPPER] == cdeg && r->c.servo.pos_cdeg[UGV_SERVO_GRIPPER] == cdeg;
}

static uint16_t park_seq;
static int park(Rig *r, uint16_t session) {  /* 0x123: operator parked the arm at stow by hand */
    const uint16_t sq = park_seq++;
    const uint8_t p[8] = {1, 1, 0, 0, (uint8_t)sq, (uint8_t)(sq >> 8), (uint8_t)session, (uint8_t)(session >> 8)};  /* DD94: + claw closed, empty */
    uint8_t d[UGV_LITE_DGRAM_LEN];
    ugv_lite_pack(d, UGV_LITE_CMD, 0x123, p, KEY, sizeof KEY);
    return lite_core_receive(&r->c, d, sizeof d, r->now);
}

static void rig_parked(Rig *r) {  /* fresh core whose arm the operator has parked (0x123) */
    rig_init(r);
    handshake(r, 60);
    assert(park(r, 0x5678));
}

static int arm_pulses_off(const Rig *r) {
    for (int j = 0; j < UGV_ARM_JOINTS; ++j) if (r->out.servo_us[UGV_SERVO_SHOULDER + j]) return 0;
    return 1;
}

static void arm_joints(const Rig *r, int32_t q[UGV_ARM_JOINTS]) {  /* servo positions, arm joints */
    for (int j = 0; j < UGV_ARM_JOINTS; ++j) q[j] = r->c.servo.pos_cdeg[UGV_SERVO_SHOULDER + j];
}

static int on_edge(const int32_t q[UGV_ARM_JOINTS], int a, int b) {  /* one common fraction, +-1 cdeg */
    int best = 0;
    for (int j = 1; j < UGV_ARM_JOINTS; ++j)
        if (abs(UGV_ARM_POSE_CDEG[b][j] - UGV_ARM_POSE_CDEG[a][j]) > abs(UGV_ARM_POSE_CDEG[b][best] - UGV_ARM_POSE_CDEG[a][best])) best = j;
    const double f = (double)(q[best] - UGV_ARM_POSE_CDEG[a][best]) / (UGV_ARM_POSE_CDEG[b][best] - UGV_ARM_POSE_CDEG[a][best]);
    if (f < -1e-6 || f > 1 + 1e-6) return 0;
    for (int j = 0; j < UGV_ARM_JOINTS; ++j)
        if (fabs(UGV_ARM_POSE_CDEG[a][j] + f * (UGV_ARM_POSE_CDEG[b][j] - UGV_ARM_POSE_CDEG[a][j]) - q[j]) > 1.5) return 0;
    return 1;
}

static int at_pose(const Rig *r, int n) {
    int32_t q[UGV_ARM_JOINTS];
    arm_joints(r, q);
    for (int j = 0; j < UGV_ARM_JOINTS; ++j) if (q[j] != UGV_ARM_POSE_CDEG[n][j]) return 0;
    return 1;
}

static int arm_settled(const Rig *r) {
    return lite_core_arm_settled(&r->c);
}

static float mm_s(const Rig *r) {  /* mean wheel surface speed of the model */
    float sum = 0.0f;
    for (int m = 0; m < LITE_MOTORS; ++m) sum += r->rpm[m];
    return sum / LITE_MOTORS * LITE_WHEEL_MM / 60.0f;
}

static int all(const Rig *r, int sign) {
    for (int m = 0; m < LITE_MOTORS; ++m)
        if ((sign > 0 && r->out.duty_permil[m] <= 0) || (sign < 0 && r->out.duty_permil[m] >= 0) ||
            (sign == 0 && r->out.duty_permil[m] != 0)) return 0;
    return 1;
}

int main(void) {
    for (int i = 0; i < 32; ++i) KEY[i] = (uint8_t)i;
    Rig r;

    /* Boot: actuators off, no motion, no servo pulses, even without any traffic. */
    rig_init(&r);
    r.send = 0;
    run(&r, 100);
    assert(r.out.state == LITE_IDLE && !r.out.act_en && all(&r, 0) && r.out.servo_us[UGV_SERVO_PAN] == 0);

    /* A01 (full review): a missing or wrong-size link key (NVS with Wi-Fi but no link_key) never becomes a usable
       HMAC key: the core refuses every datagram, even ones signed with that same key, and sends no telemetry. */
    static const size_t bad_len[] = {0, 16, 31, 33};
    uint8_t bad_key[33];
    memcpy(bad_key, KEY, 32);
    bad_key[32] = 0xAA;
    for (int k = 0; k < 4; ++k) {
        rig_init(&r);
        lite_core_init(&r.c, bad_key, bad_len[k], r.now);
        r.send = 0;
        for (int t = 0; t < 60; ++t) {  /* IDLE handshake, 0.7 s of ARM, then DRIVE: all refused */
            const uint8_t mode = t < 5 ? UGV_CAN_MODE_IDLE : t < 40 ? UGV_CAN_MODE_ARM : UGV_CAN_MODE_DRIVE;
            const uint8_t lease[8] = {0x78, 0x56, 0x34, 0x12, (uint8_t)t, 0, (uint8_t)(0x10 | mode), mode != UGV_CAN_MODE_IDLE};
            const uint8_t drv[8] = {200, 0, 200, 0, (uint8_t)t, 0, 0x78, 0x56};
            uint8_t d[UGV_LITE_DGRAM_LEN];
            ugv_lite_pack(d, UGV_LITE_CMD, 0x110, lease, bad_key, bad_len[k]);
            assert(!lite_core_receive(&r.c, d, sizeof d, r.now));
            ugv_lite_pack(d, UGV_LITE_CMD, 0x100, drv, bad_key, bad_len[k]);
            assert(!lite_core_receive(&r.c, d, sizeof d, r.now));
            run(&r, LITE_TICK_MS);
        }
        assert(r.out.state == LITE_IDLE && !r.out.act_en && all(&r, 0));
        uint8_t none[4][UGV_LITE_DGRAM_LEN];
        assert(lite_core_telemetry(&r.c, r.now + LITE_TLM_PERIOD_MS, none) == 0);
    }

    /* Arming needs an IDLE handshake then 500 ms of fresh neutral ARM traffic; servo PWM after 100 ms. */
    rig_init(&r);
    handshake(&r, 60);
    r.mode = UGV_CAN_MODE_ARM;
    r.deadman = 1;
    run(&r, 480);
    assert(r.out.state == LITE_IDLE && !r.out.act_en);
    run(&r, 60);
    assert(r.out.state == LITE_ARMED && r.out.act_en && all(&r, 0));
    run(&r, 120);
    /* M3 review: from power-on the core cannot know where the arm is: no arm pulses, no path moves, until the
       operator parks it by hand and confirms (0x123) with the actuators off. The head runs meanwhile. */
    assert(r.out.servo_us[UGV_SERVO_PAN] == 1500 && arm_pulses_off(&r));
    assert(!arm_cmd(&r, UGV_ARM_STOW, UGV_ARM_LIFT, 65535) && !park(&r, 0x5678));  /* refused while armed */
    handshake(&r, 60);
    assert(!r.out.act_en && !park(&r, 0x5679));                                 /* wrong session tag */
    assert(park(&r, 0x5678));
    --park_seq;
    assert(!park(&r, 0x5678));                                                  /* replayed sequence */
    arm(&r);
    run(&r, 120);
    assert(r.out.servo_us[UGV_SERVO_SHOULDER] == 2333);                         /* stow park */

    /* N1 (M3 review): the arm moves only along the swept pose graph (arm_graph.h, from config). 0x122 = (from
       pose, to pose, target fraction). All five joints move together on the edge's straight line, the fastest
       at <= the path rate; off-graph or discontinuous commands are refused; one accepted command is enough
       (later datagrams may be lost); a reversal returns along the same edge; a hold stops mid-edge. */
    assert(arm_cmd(&r, UGV_ARM_STOW, UGV_ARM_LIFT, 65535));
    int32_t last[UGV_ARM_JOINTS];
    arm_joints(&r, last);
    for (int t = 0; t < 150; ++t) {
        run(&r, LITE_TICK_MS);
        int32_t q[UGV_ARM_JOINTS];
        arm_joints(&r, q);
        assert(on_edge(q, UGV_ARM_STOW, UGV_ARM_LIFT));
        for (int j = 0; j < UGV_ARM_JOINTS; ++j)
            assert(abs(q[j] - last[j]) <= UGV_ARM_RATE_CDEG_S * LITE_TICK_MS / 1000 + 1);
        memcpy(last, q, sizeof q);
    }
    assert(at_pose(&r, UGV_ARM_LIFT) && arm_settled(&r));
    assert(!arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_REACH_LOW, 65535));        /* not an edge */
    assert(!arm_cmd(&r, UGV_ARM_UP, UGV_ARM_READY, 65535));              /* edge, but not from here */
    run(&r, 400);
    assert(at_pose(&r, UGV_ARM_LIFT));
    assert(arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_UP, 65535));
    run(&r, 600);                                                         /* part way: twist 90 -> 63 */
    assert(!at_pose(&r, UGV_ARM_LIFT) && !at_pose(&r, UGV_ARM_UP) && !arm_settled(&r));
    assert(!arm_cmd(&r, UGV_ARM_UP, UGV_ARM_READY, 65535));              /* not at UP yet */
    assert(arm_cmd(&r, UGV_ARM_UP, UGV_ARM_LIFT, 65535));                /* reversal: back along the edge */
    for (int t = 0; t < 60; ++t) {
        run(&r, LITE_TICK_MS);
        int32_t q[UGV_ARM_JOINTS];
        arm_joints(&r, q);
        assert(on_edge(q, UGV_ARM_LIFT, UGV_ARM_UP));
    }
    assert(at_pose(&r, UGV_ARM_LIFT));
    assert(arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_UP, 65535));
    run(&r, 600);
    uint8_t tl[4][UGV_LITE_DGRAM_LEN];
    uint16_t tid, frac;
    uint8_t tp[8];
    r.now += LITE_TLM_PERIOD_MS;
    assert(lite_core_telemetry(&r.c, r.now, tl) == 4);
    /* Telemetry is bound to the last accepted lease: session + the lease sequence extended to 32 bits. */
    assert(r.c.lease_ext == (uint32_t)(r.lseq - 1) && !ugv_lite_unpack(tl[3], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &tid, tp, KEY, sizeof KEY));
    assert(!ugv_lite_unpack_bound(tl[3], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &tid, tp, KEY, sizeof KEY, 0x12345678u, r.c.lease_ext - 1));
    assert(ugv_lite_unpack_bound(tl[3], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &tid, tp, KEY, sizeof KEY, 0x12345678u, r.c.lease_ext) && tid == 0x1A2);
    frac = (uint16_t)(tp[2] | tp[3] << 8);
    assert(tp[0] == UGV_ARM_LIFT && tp[1] == UGV_ARM_UP && frac > 0 && frac < 65535 && !(tp[6] & 1));
    /* N3 (M3 review): byte 7 echoes the low byte of the last 0x122 sequence the core took, so the MacBook can tell a
       sample that answers its latest command from one taken before it. A refused 0x122 leaves the echo alone. */
    const uint16_t next_seq = arm_seq;
    assert(tp[7] == (uint8_t)(next_seq - 1));
    arm_seq = (uint16_t)(next_seq - 2);
    assert(!arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_UP, 0));                   /* an older sequence, late */
    arm_seq = next_seq;
    r.now += LITE_TLM_PERIOD_MS;
    assert(lite_core_telemetry(&r.c, r.now, tl) == 4);
    assert(ugv_lite_unpack_bound(tl[3], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &tid, tp, KEY, sizeof KEY, 0x12345678u, r.c.lease_ext));
    assert(tp[7] == (uint8_t)(next_seq - 1));
    /* A06 (full review): a new-sequence command the arm refuses (off-graph edge) burns its sequence against replay but
       leaves the echo alone: the echo reports only commands the arm took. */
    assert(!arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_REACH_LOW, 65535));
    run(&r, 60);                                                          /* leases stay fresh */
    assert(lite_core_telemetry(&r.c, r.now, tl) == 4);
    assert(ugv_lite_unpack_bound(tl[3], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &tid, tp, KEY, sizeof KEY, 0x12345678u, r.c.lease_ext));
    assert(tp[7] == (uint8_t)(next_seq - 1) && !(tp[6] >> 4));
    --arm_seq;
    assert(!arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_UP, 0));                   /* its sequence cannot be replayed */
    /* The echo is 12 bits (A05): byte 7 low byte, byte 6 bits 4-7 the rest. */
    arm_seq = 0x2A5;
    frac = (uint16_t)(tp[2] | tp[3] << 8);
    assert(arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_UP, 65535));
    run(&r, 60);
    assert(lite_core_telemetry(&r.c, r.now, tl) == 4);
    assert(ugv_lite_unpack_bound(tl[3], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &tid, tp, KEY, sizeof KEY, 0x12345678u, r.c.lease_ext));
    assert(tp[7] == 0xA5 && tp[6] >> 4 == 0x2);
    frac = (uint16_t)(tp[2] | tp[3] << 8);
    assert(arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_UP, frac));                 /* hold where it is */
    run(&r, 400);
    assert(arm_settled(&r) && !at_pose(&r, UGV_ARM_UP));
    assert(arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_UP, 65535));                /* one command; the rest "lost" */
    run(&r, 2500);
    assert(at_pose(&r, UGV_ARM_UP) && arm_settled(&r));
    /* 0x121 carries only the claw and the AI flag in M3: its shoulder field no longer moves the arm. */
    const uint8_t old_shoulder[8] = {0x88, 0x13, 1, 1, 0, 0, 0x78, 0x56};  /* shoulder 50 deg, close, AI */
    send(&r, 0x121, old_shoulder);
    run(&r, 600);
    assert(at_pose(&r, UGV_ARM_UP) && claw_there(&r, 0));                 /* closed = 0 = the park */
    /* A lease loss (or E-stop) mid-move cancels the move: re-arming never resumes an old arm command. M3 review:
       the rails went off with the arm away from stow, so it drooped: after re-arming it stays limp (no pulse, no
       path, telemetry bit1) instead of jumping back to the old path point, until it is parked by hand. */
    assert(arm_cmd(&r, UGV_ARM_UP, UGV_ARM_LIFT, 65535));
    run(&r, 600);
    r.send = 0;
    run(&r, 140);
    assert(!r.out.act_en);
    r.send = 1;
    arm(&r);
    run(&r, 1500);
    assert(r.out.act_en && arm_pulses_off(&r) && !arm_cmd(&r, UGV_ARM_UP, UGV_ARM_LIFT, 65535));
    r.now += LITE_TLM_PERIOD_MS;
    assert(lite_core_telemetry(&r.c, r.now, tl) == 4);
    assert(ugv_lite_unpack_bound(tl[3], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &tid, tp, KEY, sizeof KEY, 0x12345678u, r.c.lease_ext));
    assert((tp[6] & 3) == 2);                                             /* limp, not settled */
    handshake(&r, 60);
    assert(park(&r, 0x5678));
    arm(&r);
    run(&r, 200);
    assert(at_pose(&r, UGV_ARM_STOW) && r.out.servo_us[UGV_SERVO_SHOULDER] == 2333);
    r.send = 0;                                                            /* settled at stow: no latch */
    run(&r, 140);
    r.send = 1;
    arm(&r);
    run(&r, 200);
    assert(r.out.servo_us[UGV_SERVO_SHOULDER] == 2333 && arm_cmd(&r, UGV_ARM_STOW, UGV_ARM_LIFT, 65535));
    run(&r, 2500);
    assert(arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_STOW, 65535));
    run(&r, 2500);
    assert(at_pose(&r, UGV_ARM_STOW));

    /* DD84: the core itself refuses to drive unless the arm is settled at a drive pose (UGV_ARM_DRIVE_MASK in
       arm_graph.h, from config), so no host bug can drive with the arm out; 0x1A0 flags bit3 says why. N4 (M3
       review): only stow is a drive pose now; raised poses put the loaded CG past the x/z limits (check_body_mass). */
    drive(&r, 200, 200, 600);
    assert(at_pose(&r, UGV_ARM_STOW) && all(&r, 1) && !(r.c.flags & 8));       /* stow drives */
    assert(arm_cmd(&r, UGV_ARM_STOW, UGV_ARM_LIFT, 65535));                   /* arm leaves it while driving */
    drive(&r, 200, 200, 20);
    assert(r.c.target_mm_s[0] > 0 && (r.c.flags & 8));                         /* ramped stop, not a jolt */
    drive(&r, 200, 200, 600);
    assert(all(&r, 0) && r.c.target_mm_s[0] == 0);
    drive(&r, 0, 0, 3000);
    const uint8_t legs[][2] = {{UGV_ARM_STOW, UGV_ARM_LIFT}, {UGV_ARM_LIFT, UGV_ARM_UP}, {UGV_ARM_UP, UGV_ARM_READY},
                               {UGV_ARM_READY, UGV_ARM_REACH_MID}};
    for (int k = 0; k < 4; ++k) {  /* lift, up, ready (drive poses before N4) and reach_mid all refuse */
        if (k) assert(arm_cmd(&r, legs[k][0], legs[k][1], 65535));
        drive(&r, 0, 0, 3000);
        assert(at_pose(&r, legs[k][1]));
        drive(&r, 200, 200, 600);
        assert(r.out.state == LITE_DRIVING && all(&r, 0) && (r.c.flags & 8));
    }
    const uint8_t back[][2] = {{UGV_ARM_REACH_MID, UGV_ARM_READY}, {UGV_ARM_READY, UGV_ARM_UP}, {UGV_ARM_UP, UGV_ARM_LIFT},
                               {UGV_ARM_LIFT, UGV_ARM_STOW}};
    for (int k = 0; k < 4; ++k) {
        assert(arm_cmd(&r, back[k][0], back[k][1], 65535));
        drive(&r, 0, 0, 3000);
    }
    assert(at_pose(&r, UGV_ARM_STOW));

    /* DD93 (M01, A04): the twin geared claw. Closed and empty at stow the wheels go (0x1A0 bit4 = empty). It cannot open
       at stow or lift (the jaws would hit the body): an "open" there is ignored. At an OPEN pose it opens; while it is
       open the arm moves only between OPEN poses. A close at a GRASP pose may hold an object: the wheels refuse at stow
       until the claw has been fully open again (at store, over the cargo bin); a lost "open" never lets them go. */
    drive(&r, 200, 200, 600);
    assert(all(&r, 1) && !(r.c.flags & 8) && (r.c.flags & 16) && claw_there(&r, 0));
    drive(&r, 0, 0, 600);
    r.aseq = 1;
    claw(&r, 0);
    drive(&r, 0, 0, 300);
    assert(claw_there(&r, 0));                                                /* not at stow */
    const uint8_t to_ready[][2] = {{UGV_ARM_STOW, UGV_ARM_LIFT}, {UGV_ARM_LIFT, UGV_ARM_UP}, {UGV_ARM_UP, UGV_ARM_READY}};
    for (int k = 0; k < 3; ++k) {
        assert(arm_cmd(&r, to_ready[k][0], to_ready[k][1], 65535));
        drive(&r, 0, 0, 3000);
        if (k == 0) {
            claw(&r, 0);
            drive(&r, 0, 0, 300);
            assert(claw_there(&r, 0));                                        /* nor at lift */
        }
    }
    claw(&r, 0);
    drive(&r, 0, 0, 600);
    assert(at_pose(&r, UGV_ARM_READY) && claw_there(&r, UGV_GRIP_OPEN_CDEG) && r.out.servo_us[UGV_SERVO_GRIPPER] == 2167);
    r.now += LITE_TLM_PERIOD_MS;
    assert(lite_core_telemetry(&r.c, r.now, tl) == 4);
    assert(ugv_lite_unpack_bound(tl[3], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &tid, tp, KEY, sizeof KEY, 0x12345678u, r.c.lease_ext));
    assert((tp[6] & 0x0C) == 8);                                              /* commanded open, and there */
    assert(!arm_cmd(&r, UGV_ARM_READY, UGV_ARM_UP, 65535));                   /* open: UP is not an open pose */
    assert(arm_cmd(&r, UGV_ARM_READY, UGV_ARM_REACH_LOW, 65535));             /* READY-REACH_LOW is swept open */
    drive(&r, 0, 0, 3000);
    assert(at_pose(&r, UGV_ARM_REACH_LOW));
    claw(&r, 1);                                                              /* grasp */
    drive(&r, 0, 0, 600);
    assert(claw_there(&r, 0) && !r.c.grip_empty);
    const uint8_t home[][2] = {{UGV_ARM_REACH_LOW, UGV_ARM_READY}, {UGV_ARM_READY, UGV_ARM_UP}, {UGV_ARM_UP, UGV_ARM_LIFT},
                               {UGV_ARM_LIFT, UGV_ARM_STOW}};
    for (int k = 0; k < 4; ++k) {
        assert(arm_cmd(&r, home[k][0], home[k][1], 65535));
        drive(&r, 0, 0, 3000);
    }
    drive(&r, 200, 200, 600);
    assert(at_pose(&r, UGV_ARM_STOW) && all(&r, 0) && (r.c.flags & 8) && !(r.c.flags & 16));  /* may hold an object */
    drive(&r, 0, 0, 100);
    assert(arm_cmd(&r, UGV_ARM_STOW, UGV_ARM_LIFT, 65535));
    drive(&r, 0, 0, 3000);
    assert(arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_STORE, 65535));
    drive(&r, 0, 0, 4000);
    assert(at_pose(&r, UGV_ARM_STORE));
    claw(&r, 0);                                                              /* over the cargo bin: let go */
    drive(&r, 0, 0, 600);
    assert(claw_there(&r, UGV_GRIP_OPEN_CDEG) && r.c.grip_empty);
    claw(&r, 1);                                                              /* close empty, not at a grasp pose */
    drive(&r, 0, 0, 600);
    assert(claw_there(&r, 0) && r.c.grip_empty);
    assert(arm_cmd(&r, UGV_ARM_STORE, UGV_ARM_LIFT, 65535));
    drive(&r, 0, 0, 4000);
    assert(arm_cmd(&r, UGV_ARM_LIFT, UGV_ARM_STOW, 65535));
    drive(&r, 0, 0, 3000);
    drive(&r, 200, 200, 600);
    assert(at_pose(&r, UGV_ARM_STOW) && all(&r, 1) && !(r.c.flags & 8) && (r.c.flags & 16));
    drive(&r, 0, 0, 600);

    /* DD94 (R02): a close anywhere but a release pose (store) may hold an object, READY included. */
    for (int k = 0; k < 3; ++k) {
        assert(arm_cmd(&r, to_ready[k][0], to_ready[k][1], 65535));
        drive(&r, 0, 0, 3000);
    }
    claw(&r, 0);
    drive(&r, 0, 0, 600);
    claw(&r, 1);
    drive(&r, 0, 0, 600);
    assert(claw_there(&r, 0) && !r.c.grip_empty);
    /* R02: open at READY, then the actuators drop (IDLE): the arm is out of stow and the claw open, so both are latched
       unknown: no arm and no claw pulse (not the old open PWM), until 0x123 says "parked at stow, claw closed and
       empty" - then closed at stow, not open against the side wall. A park without the claw statement is refused. */
    claw(&r, 0);
    drive(&r, 0, 0, 600);
    assert(claw_there(&r, UGV_GRIP_OPEN_CDEG));
    handshake(&r, 60);
    assert(!r.out.act_en && r.c.arm_limp);
    r.mode = UGV_CAN_MODE_ARM;
    r.deadman = 1;
    run(&r, 700);
    assert(r.out.act_en && arm_pulses_off(&r) && !r.out.servo_us[UGV_SERVO_GRIPPER]);
    /* DD94 recheck #2: a close while limp moves nothing (no pulse), so the model takes no target and the telemetry
       claims neither "closed" nor "settled" nor "empty": the claw stays unknown until 0x123. */
    claw(&r, 1);
    run(&r, 600);
    assert(!r.out.servo_us[UGV_SERVO_GRIPPER] && claw_there(&r, UGV_GRIP_OPEN_CDEG) && !r.c.grip_empty && !(r.c.flags & 16));
    r.now += LITE_TLM_PERIOD_MS;
    assert(lite_core_telemetry(&r.c, r.now, tl) == 4);
    assert(ugv_lite_unpack_bound(tl[3], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &tid, tp, KEY, sizeof KEY, 0x12345678u, r.c.lease_ext));
    assert((tp[6] & 0x0F) == 2);                                              /* limp only: bits 0, 2, 3 clear */
    handshake(&r, 60);
    const uint16_t ps = park_seq++;
    const uint8_t arm_only[8] = {1, 0, 0, 0, (uint8_t)ps, (uint8_t)(ps >> 8), 0x78, 0x56};
    send(&r, 0x123, arm_only);
    assert(r.c.arm_limp);                                                     /* the claw was not confirmed */
    assert(park(&r, 0x5678) && claw_there(&r, 0) && r.c.grip_empty);
    arm(&r);
    run(&r, 200);
    assert(at_pose(&r, UGV_ARM_STOW) && r.out.servo_us[UGV_SERVO_GRIPPER] == 1500);
    /* R02: grasp at REACH_LOW, park, then a watchdog reset: "empty" is not regained by a reset. The vehicle drives
       only after the operator's closed-and-empty park confirmation. */
    for (int k = 0; k < 3; ++k) {
        assert(arm_cmd(&r, to_ready[k][0], to_ready[k][1], 65535));
        drive(&r, 0, 0, 3000);
    }
    claw(&r, 0);
    drive(&r, 0, 0, 600);
    assert(arm_cmd(&r, UGV_ARM_READY, UGV_ARM_REACH_LOW, 65535));
    drive(&r, 0, 0, 3000);
    claw(&r, 1);
    drive(&r, 0, 0, 600);
    for (int k = 0; k < 4; ++k) {
        assert(arm_cmd(&r, home[k][0], home[k][1], 65535));
        drive(&r, 0, 0, 3000);
    }
    assert(at_pose(&r, UGV_ARM_STOW) && !r.c.grip_empty);
    lite_core_init(&r.c, KEY, sizeof KEY, r.now);                             /* watchdog reset */
    park_seq = 0;
    arm_seq = 0;
    r.aseq = 1;
    arm(&r);
    drive(&r, 200, 200, 600);
    assert(!r.c.grip_empty && all(&r, 0) && (r.c.flags & 8));                /* limp and not empty: no wheels */
    handshake(&r, 60);
    assert(park(&r, 0x5678) && r.c.grip_empty);
    arm(&r);
    drive(&r, 200, 200, 600);
    assert(all(&r, 1));
    drive(&r, 0, 0, 600);

    /* DD94 (R01): a front ToF that saw nothing in range (0xFFFF) is no clear road: forward only at a 100 mm/s creep
       (0x1A0 bit5), reverse as usual; an invalid reading (0) still stops forward at once. */
    r.in.tof_mm[1] = 0xFFFF;
    drive(&r, 200, 200, 2000);
    assert(all(&r, 1) && fabsf(mm_s(&r) - LITE_TOF_BLIND_MM_S) < 12.0f && r.out.forward_blind && !r.out.forward_blocked);
    assert(r.c.flags & 32);
    drive(&r, -200, -200, 2000);
    assert(all(&r, -1) && mm_s(&r) < -150.0f);
    r.in.tof_mm[0] = 0;
    drive(&r, 200, 200, 600);
    assert(r.out.forward_blocked && all(&r, 0));
    r.in.tof_mm[0] = r.in.tof_mm[1] = 2000;
    drive(&r, 100, 100, 1500);                                                /* forward again, as before */
    drive(&r, 0, 0, 1200);

    /* Drive: 0.5 m/s2 ramp, feed-forward + PI speed loop per motor, same sign front/rear. */
    drive(&r, 200, 200, 20);  /* first tick: one ramp step (10 mm/s), not the 200 mm/s voltage */
    assert(r.out.state == LITE_DRIVING && all(&r, 1) && r.out.duty_permil[LITE_FL] < 300);
    drive(&r, 200, 100, 1500);
    assert(all(&r, 1) && r.out.duty_permil[LITE_FL] == r.out.duty_permil[LITE_RL]);
    assert(r.out.duty_permil[LITE_FL] > r.out.duty_permil[LITE_FR] + 100);

    /* AI cap: without a fresh manual 0x121, 300 mm/s is held at 200; a manual frame lifts it to 300.
       N2: the speed loop holds the commanded wheel speed (was open-loop feed-forward). */
    drive(&r, 300, 300, 1500);
    assert(fabsf(mm_s(&r) - 200.0f) < 12.0f);
    r.manual = 1;
    drive(&r, 300, 300, 1500);
    assert(fabsf(mm_s(&r) - 300.0f) < 12.0f);

    /* Reversal crosses zero through a coast tick; braking stays under the back-EMF limit. 295 mm/s makes
       the 10 mm/s ramp step from +5 straight to -5, so the coast must come from the core, not the ramp. */
    drive(&r, 295, 295, 1500);
    for (int m = 0; m < LITE_MOTORS; ++m) r.imax[m] = 0;
    int16_t prev[LITE_MOTORS];
    memcpy(prev, r.out.duty_permil, sizeof prev);
    int coast_seen = 0;
    r.left = r.right = -295;
    for (int t = 0; t < 150; ++t) {
        run(&r, LITE_TICK_MS);
        for (int m = 0; m < LITE_MOTORS; ++m) {
            assert(!(prev[m] > 0 && r.out.duty_permil[m] < 0) && !(prev[m] < 0 && r.out.duty_permil[m] > 0));
            coast_seen |= prev[m] > 0 && r.out.duty_permil[m] == 0;
            prev[m] = r.out.duty_permil[m];
        }
    }
    assert(coast_seen && all(&r, -1) && r.rpm[LITE_FL] < -20.0f);
    for (int m = 0; m < LITE_MOTORS; ++m) assert(r.imax[m] <= LITE_I_LIMIT_A);
    /* The limiter itself: a hard reverse request against +10 V of back-EMF is held to I_LIMIT * R_min. */
    assert(fabsf(lite_core_limit_mv(-12600.0f, 10000.0f) - (10000.0f - LITE_I_LIMIT_A * LITE_PATH_OHM_MIN * 1000.0f)) < 1.0f);
    assert(lite_core_limit_mv(9000.0f, 0.0f) == 9000.0f);

    /* Front ToF: forward is cut at once below 250 mm or with an invalid reading; reverse stays allowed. */
    drive(&r, 200, 200, 1500);
    r.in.tof_mm[0] = 200;
    run(&r, LITE_TICK_MS);
    assert(r.out.state == LITE_DRIVING && r.out.forward_blocked && all(&r, 0));
    drive(&r, -100, -100, 600);
    assert(all(&r, -1));
    r.in.tof_mm[0] = 0;
    drive(&r, 100, 100, 600);
    assert(r.out.forward_blocked && all(&r, 0));
    r.in.tof_mm[0] = 2000;

    /* Lease loss: stopped with ACT_EN Low within one freshness window; ARM traffic alone does not
       re-arm, an IDLE handshake is required first. */
    drive(&r, 200, 200, 600);
    r.send = 0;
    run(&r, 140);
    assert(r.out.state == LITE_IDLE && !r.out.act_en && all(&r, 0) && r.out.servo_us[UGV_SERVO_PAN] == 0);
    r.send = 1;
    r.mode = UGV_CAN_MODE_ARM;
    run(&r, 1000);
    assert(r.out.state == LITE_IDLE && !r.out.act_en);
    arm(&r);

    /* E-stop: a short press (edge only) latches; release does not restart; a held press stays ESTOP. */
    drive(&r, 200, 200, 600);
    r.in.estop_edge = 1;
    run(&r, LITE_TICK_MS);
    assert(r.out.state == LITE_ESTOP && !r.out.act_en && all(&r, 0));
    drive(&r, 200, 200, 400);
    assert(r.out.state == LITE_IDLE && !r.out.act_en && all(&r, 0));
    arm(&r);
    r.in.estop_level = 1;
    drive(&r, 200, 200, 400);
    assert(r.out.state == LITE_ESTOP && !r.out.act_en);
    r.in.estop_level = 0;
    run(&r, 100);
    assert(r.out.state == LITE_IDLE);
    arm(&r);

    /* STOP frame: back to IDLE at once. */
    drive(&r, 200, 200, 600);
    const uint8_t stop[8] = {1, 0, 0, 0, 0, 0, 0, 0};
    send(&r, 0x080, stop);
    run(&r, LITE_TICK_MS);
    assert(r.out.state == LITE_IDLE && !r.out.act_en && all(&r, 0));
    arm(&r);

    /* Low battery below 9.6 V for 1 s: FAULT; recovers only above 9.9 V with an IDLE handshake. */
    drive(&r, 100, 100, 400);
    r.in.vbat_mv = 9400;
    run(&r, 900);
    assert(r.out.state == LITE_DRIVING);
    run(&r, 200);
    assert(r.out.state == LITE_FAULT && (r.out.faults & LITE_FAULT_LOW_BATTERY) && !r.out.act_en);
    r.in.vbat_mv = 12000;
    handshake(&r, 100);
    assert(r.out.state == LITE_IDLE && r.out.faults == 0);
    arm(&r);

    /* R4: a stalled rear wheel is caught by its own encoder within 300 ms while the others turn. */
    drive(&r, 200, 200, 1500);
    r.stalled[LITE_RL] = 1;
    run(&r, 260);
    assert(r.out.state == LITE_DRIVING);
    run(&r, 100);
    assert(r.out.state == LITE_FAULT && r.out.faults == (LITE_FAULT_STALL_FL << LITE_RL) && !r.out.act_en);
    r.stalled[LITE_RL] = 0;
    handshake(&r, 5000);
    assert(r.out.state == LITE_FAULT);  /* cooldown */
    handshake(&r, 5200);
    assert(r.out.state == LITE_IDLE && r.out.faults == 0);

    /* Recheck F1: a heavy load that still turns (no stall) is limited in time by the TB6612 thermal budget
       (conservative current estimate); a moderate load runs on. */
    rig_parked(&r);
    arm(&r);
    r.manual = 1;
    drive(&r, 300, 300, 2000);  /* up to speed, then the load arrives (a heavy pivot or a push) */
    r.load_a[LITE_FL] = r.load_a[LITE_RL] = 0.53f;
    drive(&r, 300, 300, 5000);
    assert(r.out.state == LITE_DRIVING);
    drive(&r, 300, 300, 30000);
    assert(r.out.state == LITE_FAULT && r.out.faults == LITE_FAULT_THERMAL && !r.out.act_en);
    rig_parked(&r);
    arm(&r);
    r.manual = 1;
    r.load_a[LITE_FL] = r.load_a[LITE_RL] = 0.3f;
    drive(&r, 300, 300, 60000);
    assert(r.out.state == LITE_DRIVING && r.out.faults == 0);

    /* Telemetry: signed 'T' datagrams at 20 Hz, bound to the last lease; a command-direction or wrong-key datagram is
       refused. */
    uint8_t tlm[4][UGV_LITE_DGRAM_LEN];
    assert(lite_core_telemetry(&r.c, r.now, tlm) == 4 && lite_core_telemetry(&r.c, r.now + 10, tlm) == 0);
    uint16_t id;
    uint8_t p[8];
    assert(ugv_lite_unpack_bound(tlm[0], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &id, p, KEY, sizeof KEY, 0x12345678u, r.c.lease_ext) && id == 0x190);
    assert(p[0] == LITE_DRIVING && p[1] == 0);
    assert(ugv_lite_unpack_bound(tlm[1], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &id, p, KEY, sizeof KEY, 0x12345678u, r.c.lease_ext) && id == 0x1A0);
    assert((p[0] | p[1] << 8) == 12000 && (p[2] & 4));  /* vbat, ACT_EN flag */
    assert(ugv_lite_unpack_bound(tlm[2], UGV_LITE_DGRAM_LEN, UGV_LITE_TLM, &id, p, KEY, sizeof KEY, 0x12345678u, r.c.lease_ext) && id == 0x1A1);
    const int32_t left = (int32_t)((uint32_t)p[0] | (uint32_t)p[1] << 8 | (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24);
    assert(left > LITE_COUNTS_PER_REV);  /* forward odometry counted */
    assert(!lite_core_receive(&r.c, tlm[0], UGV_LITE_DGRAM_LEN, r.now));  /* telemetry is not a command */
    uint8_t other[32] = {1}, forged[UGV_LITE_DGRAM_LEN];
    const uint8_t stop2[8] = {1, 0, 0, 0, 0, 0, 0, 0};
    ugv_lite_pack(forged, UGV_LITE_CMD, 0x080, stop2, other, sizeof other);
    assert(!lite_core_receive(&r.c, forged, sizeof forged, r.now));

    /* N2 (M3 review): pivot in place at the executor's 0.45 rad/s (wheels +-63 mm/s) against the scrub of a
       mu floor (per-motor load from tools/calculations.py, 5.1 kg). The speed loop turns on mu 0.3 even on a
       9.7 V pack; a floor beyond the drive (mu 0.6) ends in a stall or thermal fault, never a silent overload.
       With no fixed voltage ceiling the estimated current of a stalled wheel stays <= the back-EMF limit. */
    const float kt = 7.6f * 0.0980665f / (1.8f - 0.07f), per_mu = 0.3579f / 0.6f, roll = 0.0237f;
    rig_parked(&r);
    r.in.vbat_mv = 9700;
    arm(&r);
    for (int m = 0; m < LITE_MOTORS; ++m) r.load_a[m] = (0.3f * per_mu + roll) / kt;
    drive(&r, -63, 63, 2500);
    assert(r.out.state == LITE_DRIVING && r.out.faults == 0);
    for (int m = 0; m < LITE_MOTORS; ++m) assert(fabsf(fabsf(r.rpm[m]) - 10.0f) < 2.0f && r.imax[m] <= 1.0f);
    rig_parked(&r);
    arm(&r);
    for (int m = 0; m < LITE_MOTORS; ++m) r.load_a[m] = (0.6f * per_mu + roll) / kt;
    drive(&r, -63, 63, 30000);
    assert(r.out.state == LITE_FAULT && (r.out.faults & (LITE_FAULT_THERMAL | 0xF0)) && !r.out.act_en);
    rig_parked(&r);
    arm(&r);
    r.stalled[LITE_FL] = 1;
    for (int t = 0; t < 14; ++t) {  /* up to the 300 ms stall cut the loop pushes, the limiter bounds */
        run(&r, LITE_TICK_MS);
        r.left = r.right = 200;
        r.mode = UGV_CAN_MODE_DRIVE;
        const float v = r.out.duty_permil[LITE_FL] / 1000.0f * r.in.vbat_mv;
        assert(fabsf(v) / 1000.0f / LITE_PATH_OHM_MIN <= LITE_I_LIMIT_A + 0.01f);
    }

    puts("PASS: Lite core boot-off, no link without a 32-byte key (A01), 500 ms ARM, arm path on the pose graph (N1), ramp, PI speed loop, AI cap, pivot on mu 0.3 at 9.7 V (N2), "
         "zero-crossing coast and back-EMF limit, ToF, lease loss, E-stop latch, STOP, low battery, per-wheel stall, "
         "TB6612 thermal budget, lease-bound signed telemetry, arm limp latch until 0x123 park (M3 review), 12-bit echo of taken arm commands only (A05/A06), twin geared claw: opens only at swept poses, arm on open edges only, drives closed and empty (A04, DD93); blind ToF creep, claw state reconciled on park/reset (DD94); limp claw takes no command, reports nothing (DD95)");
    return 0;
}
