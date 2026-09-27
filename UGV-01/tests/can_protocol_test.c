#include <assert.h>
#include <stdio.h>
#include "../firmware/stm32/can_protocol.h"

/* A2 servo/AI frames: fresh armed lease with deadman, matching session tag, forward seq. */
static void servo_frames(void) {
    UgvCanCommand cmd;
    UgvCanServo sv;
    const uint8_t start[8] = {0x78,0x56,0x34,0x12, 0xFF,0xFF, 0x10,0};
    const uint8_t arm_lease[8] = {0x78,0x56,0x34,0x12, 0,0, 0x11,1};
    const uint8_t head[8] = {0xD0,0x07, 0x48,0xF4, 1,0, 0x78,0x56};          /* pan 20.00, tilt -30.00 deg */
    const uint8_t head_bad_tag[8] = {0xD0,0x07, 0x48,0xF4, 2,0, 0x79,0x56};
    const uint8_t arm_ai[8] = {0x88,0x13, 1, 1, 1,0, 0x78,0x56};             /* shoulder 50.00, close, AI */
    const uint8_t arm_manual[8] = {0x88,0x13, 0, 0, 2,0, 0x78,0x56};
    const uint8_t arm_bad_flags[8] = {0x88,0x13, 0, 2, 3,0, 0x78,0x56};
    const uint8_t arm_bad_grip[8] = {0x88,0x13, 2, 0, 3,0, 0x78,0x56};
    ugv_can_command_init(&cmd, 800);
    ugv_can_servo_init(&sv);
    assert(ugv_can_speed_cap_mm_s(&sv, 800, 0) == 200);                      /* no 0x121 yet */
    assert(!ugv_can_servo_receive(&sv, &cmd, 0x120, head, 8, 0));             /* no lease */
    assert(ugv_can_command_receive(&cmd, 0x110, start, 8, 0, 1));
    assert(!ugv_can_servo_receive(&sv, &cmd, 0x120, head, 8, 1));             /* IDLE, no deadman */
    assert(ugv_can_command_receive(&cmd, 0x110, arm_lease, 8, 10, 0));
    assert(ugv_can_servo_receive(&sv, &cmd, 0x120, head, 8, 11));
    assert(sv.pan_cdeg == 2000 && sv.tilt_cdeg == -3000);
    assert(!ugv_can_servo_receive(&sv, &cmd, 0x120, head, 8, 12));            /* replay */
    assert(!ugv_can_servo_receive(&sv, &cmd, 0x120, head_bad_tag, 8, 12));
    assert(!ugv_can_servo_receive(&sv, &cmd, 0x121, arm_ai, 7, 12));          /* DLC */
    assert(!ugv_can_servo_receive(&sv, &cmd, 0x121, arm_bad_flags, 8, 12));
    assert(!ugv_can_servo_receive(&sv, &cmd, 0x121, arm_bad_grip, 8, 12));
    assert(ugv_can_servo_receive(&sv, &cmd, 0x121, arm_ai, 8, 12));
    assert(sv.shoulder_cdeg == 5000 && sv.gripper == 1 && sv.ai_mode);
    assert(ugv_can_speed_cap_mm_s(&sv, 800, 12) == 200);                     /* AI mode */
    assert(ugv_can_servo_receive(&sv, &cmd, 0x121, arm_manual, 8, 13));
    assert(ugv_can_speed_cap_mm_s(&sv, 800, 13) == 800);                     /* manual and fresh */
    assert(ugv_can_speed_cap_mm_s(&sv, 800, 314) == 200);                    /* stale 0x121: conservative */
    assert(!ugv_can_servo_receive(&sv, &cmd, 0x120, head, 8, 200));           /* lease stale */
    /* M3/N1: 0x122 arm path (from pose, to pose, target fraction): same lease/tag rules, its own forward seq;
       0x123 is gone. The pose graph itself is enforced by firmware/lite/arm_path.c. */
    const uint8_t path[8] = {0, 1, 0xFF, 0xFF, 1, 0, 0x78, 0x56};           /* stow -> lift, to the end */
    const uint8_t path_bad_tag[8] = {0, 1, 0xFF, 0xFF, 2, 0, 0x79, 0x56};
    const uint8_t arm_lease2[8] = {0x78,0x56,0x34,0x12, 1,0, 0x11,1};
    assert(ugv_can_command_receive(&cmd, 0x110, arm_lease2, 8, 300, 0));
    assert(ugv_can_servo_receive(&sv, &cmd, 0x122, path, 8, 301));
    assert(sv.path_from == 0 && sv.path_to == 1 && sv.path_target == 0xFFFF && sv.have_path);
    assert(!ugv_can_servo_receive(&sv, &cmd, 0x122, path, 8, 302));           /* replay */
    assert(!ugv_can_servo_receive(&sv, &cmd, 0x122, path_bad_tag, 8, 302));
    assert(!ugv_can_servo_receive(&sv, &cmd, 0x123, path, 8, 302));           /* retired id */
}

/* R3: a mode switch voids command freshness but keeps the session's sequence history, so an old
   signed drive command cannot be replayed after DRIVE -> ARM -> DRIVE. A new session starts over. */
static void mode_switch_replay(void) {
    UgvCanCommand cmd;
    const uint8_t idle0[8] = {0x78,0x56,0x34,0x12, 0,0, 0x10,0};
    const uint8_t drive1[8] = {0x78,0x56,0x34,0x12, 1,0, 0x12,1};
    const uint8_t arm2[8] = {0x78,0x56,0x34,0x12, 2,0, 0x11,1};
    const uint8_t drive3[8] = {0x78,0x56,0x34,0x12, 3,0, 0x12,1};
    const uint8_t go100[8] = {0xC8,0, 0xC8,0, 100,0, 0x78,0x56};   /* 200 mm/s, seq 100 */
    const uint8_t neutral101[8] = {0,0, 0,0, 101,0, 0x78,0x56};
    const uint8_t go102[8] = {0xC8,0, 0xC8,0, 102,0, 0x78,0x56};
    ugv_can_command_init(&cmd, 800);
    assert(ugv_can_command_receive(&cmd, 0x110, idle0, 8, 0, 1));
    assert(ugv_can_command_receive(&cmd, 0x110, drive1, 8, 10, 0));
    assert(ugv_can_command_receive(&cmd, 0x100, go100, 8, 11, 0) && cmd.left_mm_s == 200);
    assert(ugv_can_command_receive(&cmd, 0x110, arm2, 8, 20, 0));
    assert(ugv_can_command_receive(&cmd, 0x100, neutral101, 8, 21, 0));
    assert(ugv_can_command_receive(&cmd, 0x110, drive3, 8, 30, 0));
    assert(!ugv_can_command_receive(&cmd, 0x100, go100, 8, 31, 0));      /* replayed seq 100 */
    assert(!ugv_can_command_fresh(&cmd, 31) && cmd.left_mm_s == 0 && cmd.command_at_ms == 21);
    assert(ugv_can_command_receive(&cmd, 0x100, go102, 8, 32, 0) && ugv_can_command_fresh(&cmd, 32));
    /* A new session (from IDLE, deadman released) starts a fresh sequence history. */
    const uint8_t idle_new[8] = {0x11,0x11,0x11,0x11, 0,0, 0x10,0};
    const uint8_t drive_new[8] = {0x11,0x11,0x11,0x11, 1,0, 0x12,1};
    const uint8_t go5_new[8] = {0x64,0, 0x64,0, 5,0, 0x11,0x11};
    assert(ugv_can_command_receive(&cmd, 0x110, idle_new, 8, 40, 1));
    assert(ugv_can_command_receive(&cmd, 0x110, drive_new, 8, 41, 0));
    assert(ugv_can_command_receive(&cmd, 0x100, go5_new, 8, 42, 0) && cmd.left_mm_s == 100);
}

int main(void) {
    servo_frames();
    mode_switch_replay();
    UgvCanCommand cmd;
    const uint8_t start[8] = {0x78,0x56,0x34,0x12, 0xFF,0xFF, 0x10,0};
    const uint8_t lease[8] = {0x78,0x56,0x34,0x12, 0,0, 0x11,1};
    const uint8_t neutral[8] = {0,0, 0,0, 0xFF,0xFF, 0x78,0x56};
    ugv_can_command_init(&cmd, 800);
    assert(ugv_can_command_receive(&cmd, 0x110, start, 8, 0, 1));
    assert(ugv_can_command_receive(&cmd, 0x110, lease, 8, 20, 0));
    assert(ugv_can_command_receive(&cmd, 0x100, neutral, 8, 21, 0));
    assert(ugv_can_command_fresh(&cmd, 21));
    assert(!ugv_can_command_receive(&cmd, 0x110, lease, 8, 100, 0));
    assert(!ugv_can_command_fresh(&cmd, 121)); /* replay did not refresh lease */
    const uint8_t bad_session[8] = {0,0,0,0, 1,0, 0x10,0};
    const uint8_t drive_lease[8] = {0x78,0x56,0x34,0x12, 1,0, 0x12,1};
    const uint8_t drive_command[8] = {0x20,0x03, 0xE0,0xFC, 0,0, 0x78,0x56};
    const uint8_t over_speed[8] = {0x21,0x03, 0,0, 1,0, 0x78,0x56};
    const uint8_t stop[8] = {1,0,0,0,0,0,0,0};
    assert(!ugv_can_command_receive(&cmd, 0x110, bad_session, 8, 122, 0));
    assert(ugv_can_command_receive(&cmd, 0x110, drive_lease, 8, 123, 0));
    assert(!ugv_can_command_fresh(&cmd, 123)); /* mode switch invalidates old command */
    assert(ugv_can_command_receive(&cmd, 0x100, drive_command, 8, 124, 0));
    assert(ugv_can_command_fresh(&cmd, 124));
    assert(!ugv_can_command_receive(&cmd, 0x100, drive_command, 8, 125, 0));
    assert(!ugv_can_command_receive(&cmd, 0x100, over_speed, 8, 125, 0));
    assert(ugv_can_command_receive(&cmd, 0x080, stop, 8, 126, 0));
    assert(ugv_can_take_stop(&cmd) && !ugv_can_take_stop(&cmd));
    assert(!ugv_can_command_fresh(&cmd, 225));
    puts("PASS: CAN session, replay, range, mode and STOP checks; no replay after a mode switch (R3); "
         "A2 servo/AI frames, M3 0x122 arm path frame and 200 mm/s AI cap");
    return 0;
}
