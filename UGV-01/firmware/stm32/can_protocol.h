#ifndef UGV_CAN_PROTOCOL_H
#define UGV_CAN_PROTOCOL_H

#include <stdint.h>

enum { UGV_CAN_MODE_IDLE = 0, UGV_CAN_MODE_ARM = 1, UGV_CAN_MODE_DRIVE = 2 };

/* have_command: a command is valid for the current mode (a mode change clears it).
   have_command_seq: command_seq holds this session's history (only a new session clears it), so a
   mode change can never re-admit an older signed command. */
typedef struct {
    uint32_t session, lease_at_ms, command_at_ms;
    uint16_t lease_seq, command_seq, max_speed_mm_s;
    int16_t left_mm_s, right_mm_s;
    uint8_t mode, deadman, have_session, have_lease, have_command, have_command_seq, stop_pending;
} UgvCanCommand;

void ugv_can_command_init(UgvCanCommand *c, uint16_t max_speed_mm_s);
int ugv_can_command_receive(UgvCanCommand *c, uint16_t id, const uint8_t data[8],
                            uint8_t dlc, uint32_t now_ms, uint8_t may_start_session);
uint8_t ugv_can_command_fresh(const UgvCanCommand *c, uint32_t now_ms);
uint8_t ugv_can_take_stop(UgvCanCommand *c);

/* A2: 0x120 head (pan, tilt cdeg) and 0x121 arm (shoulder cdeg, gripper, flags bit0 = AI mode; the Lite M3
   core ignores the shoulder field). M3/N1: 0x122 arm path (from pose u8, to pose u8, target fraction u16 of the
   edge, 65535 = at `to`); the pose graph is enforced by firmware/lite/arm_path.c.
   Accepted only with a fresh armed lease + deadman, the session tag and a forward seq (one space per id). */
enum { UGV_CAN_AI_SPEED_MM_S = 200, UGV_CAN_ARM_FRAME_TIMEOUT_MS = 300 };

typedef struct {
    uint32_t head_at_ms, arm_at_ms;
    int16_t pan_cdeg, tilt_cdeg, shoulder_cdeg;
    uint16_t head_seq, arm_seq, path_seq, path_target, tag;
    uint8_t gripper, ai_mode, have_head, have_arm, have_path, path_from, path_to;
} UgvCanServo;

void ugv_can_servo_init(UgvCanServo *s);
int ugv_can_servo_receive(UgvCanServo *s, const UgvCanCommand *c, uint16_t id,
                          const uint8_t data[8], uint8_t dlc, uint32_t now_ms);
/* Wheel speed ceiling: 200 mm/s in AI mode or while 0x121 is missing/stale, else base. */
uint16_t ugv_can_speed_cap_mm_s(const UgvCanServo *s, uint16_t base_mm_s, uint32_t now_ms);

#endif
