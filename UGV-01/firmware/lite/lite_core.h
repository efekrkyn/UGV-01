#ifndef UGV_LITE_CORE_H
#define UGV_LITE_CORE_H

#include <stddef.h>
#include <stdint.h>

#include "arm_path.h"
#include "lite_link.h"
#include "../stm32/can_protocol.h"
#include "../stm32/light_bar.h"
#include "../stm32/servo_control.h"

/* A3 Lite vehicle core: pure logic, host-testable. The ESP-IDF layer (L4) feeds inputs every 20 ms and
   applies the outputs (MCPWM duty with per-motor polarity, ACT_EN, LEDC pulses, RMT light bar); its
   E-stop ISR also drops ACT_EN on the edge before this core sees it. Duty is positive = wheel forward. */
typedef enum { LITE_IDLE, LITE_ARMED, LITE_DRIVING, LITE_ESTOP, LITE_FAULT } LiteState;
enum { LITE_FL, LITE_FR, LITE_RL, LITE_RR, LITE_MOTORS };
/* Fault bits (telemetry 0x190 byte 1): low battery, driver thermal budget, stall of FL/FR/RL/RR. */
enum { LITE_FAULT_LOW_BATTERY = 1, LITE_FAULT_THERMAL = 2, LITE_FAULT_STALL_FL = 16 };

enum {
    LITE_TICK_MS = 20,
    LITE_MAX_SPEED_MM_S = 300,  /* DD69: reachable on an empty pack through the ballast */
    LITE_ACCEL_MM_S2 = 500,
    LITE_ARM_NEUTRAL_MS = 500,
    LITE_TOF_STOP_MM = 250,
    LITE_TOF_BLIND_MM_S = 100,   /* DD94: forward creep while a front ToF sees nothing in range (vl53l0x.h) */
    LITE_VBAT_LOW_MV = 9600, LITE_VBAT_OK_MV = 9900, LITE_VBAT_LOW_MS = 1000,
    LITE_STALL_MS = 300, LITE_STALL_MIN_MV = 3000, LITE_FAULT_COOLDOWN_MS = 10000,
    LITE_TLM_PERIOD_MS = 50,
    LITE_COUNTS_PER_REV = 1716,  /* 11 PPR channel A, both edges, 1:78 */
    LITE_KEY_LEN = 32,           /* link key, HMAC-SHA256 (config: 64 hex chars) */
};
/* Motor path model from config/vehicle.json (DD69): 12 V / 1.8 A winding + 7.5 ohm ballast + TB6612 bridge
   (0.7 V max at 1 A). Back-EMF constant from 77 rpm no-load at 12 V. */
#define LITE_BRIDGE_OHM 0.7f
#define LITE_PATH_OHM (12.0f / 1.8f + 7.5f + LITE_BRIDGE_OHM)
/* Conservative path for current estimates: cold winding -10 %, ballast -5 %, bridge typical 0.5 ohm. */
#define LITE_PATH_OHM_MIN (12.0f / 1.8f * 0.9f + 7.5f * 0.95f + 0.5f)
#define LITE_KE_MV_PER_RPM ((12000.0f - 70.0f * 12.0f / 1.8f) / 77.0f)
#define LITE_RUN_A 0.135f       /* no-load + flat rolling current, feed-forward */
#define LITE_I_LIMIT_A 0.9f     /* back-EMF limiter: |V - EMF| / R_min, below the TB6612 1.0 A operating limit */
#define LITE_REVERSE_RPM 2.0f   /* a wheel slower than this may change direction */
/* N2 (M3 review): per-motor PI speed loop on the channel-A encoder speed, on top of the feed-forward. Output
   bounded by the back-EMF limiter and the pack voltage; no fixed voltage ceiling (user decision 25.09.2026):
   the limiter, the 300 ms stall cut and the thermal budget bound the current in time.
   ponytail: gains tuned on the host motor model; retune on the real drive at bring-up (TL2). */
#define LITE_KP_MV_PER_RPM 120.0f
#define LITE_KI_MV_PER_RPM_S 2500.0f
#define LITE_WHEEL_MM 376.99f   /* 120 mm tyre circumference */
/* Recheck F1: two channels share one TB6612. IC-only 0.78 W at 25 C (Tj 150 C) -> ~0.59 W at 55 C inside
   the body; 0.5 W continuous leaves room for PWM loss (tr/tf 24/41 ns) and model error, and equals two
   channels at the 0.6 A motor ceiling. Loss is estimated per module as sum I^2 * 0.7 ohm with I from the
   conservative path; energy above the allowance accumulates and past the budget -> THERMAL fault. */
#define LITE_CHIP_CONT_W 0.5f
#define LITE_CHIP_HEAT_J 2.0f   /* ponytail: package heat capacity unknown; calibrate against TL1 */

typedef struct {
    uint16_t vbat_mv;                /* VBAT_SW through the 100k/22k divider, calibrated */
    uint8_t estop_edge;              /* the ISR saw ESTOP_SENSE rise since the last tick (driver clears it) */
    uint8_t estop_level;             /* ESTOP_SENSE now: 1 = pressed or wire open */
    uint16_t tof_mm[2];              /* front left/right; 0 = no valid reading, 0xFFFF = nothing seen in range (DD94) */
    uint32_t enc[LITE_MOTORS];       /* cumulative channel-A edges (magnitude only) */
} LiteInputs;

typedef struct {
    LiteState state;
    uint8_t act_en, faults, forward_blocked, forward_blind;
    int16_t duty_permil[LITE_MOTORS];
    uint16_t servo_us[UGV_SERVO_COUNT];
    UgvRgb light[UGV_LIGHT_LEDS];
} LiteOutputs;

typedef struct {
    UgvCanCommand cmd;
    UgvCanServo servo_cmd;
    UgvServo servo;
    UgvArmPath arm;                  /* N1: the arm's position on the swept pose graph */
    LiteInputs last;
    LiteState state;
    uint8_t faults, need_idle, arming, low_timing, flags, coasted[LITE_MOTORS];
    int8_t dir[LITE_MOTORS];
    int32_t target_mm_s[2], odo[LITE_MOTORS];
    uint32_t arm_since, low_since, fault_at, moving_at[LITE_MOTORS], last_ms, tlm_at;
    uint16_t tlm_seq, park_seq, path_ack;  /* path_ack (A06): sequence of the last 0x122 the arm actually took */
    /* M3 review: telemetry binding (lease session + extended lease sequence last accepted); arm limp latch. */
    uint32_t tlm_session, lease_ext, park_session;
    uint8_t bound, have_park_seq, arm_limp, act_was;
    uint8_t grip_empty;              /* DD93/94: fully open since its last close away from a release pose; 0 = unknown */
    float heat_j[2];                 /* energy above the allowance, per TB6612: left (FL+RL), right (FR+RR) */
    float integ_mv[LITE_MOTORS];     /* PI speed loop integrators */
    uint8_t key[32];
    size_t key_len;
} LiteCore;

/* A01 (full review): the key must be exactly LITE_KEY_LEN bytes. A missing or wrong-size key (e.g. NVS with Wi-Fi
   but no link_key) leaves the core refusing every datagram and sending no telemetry: never an empty HMAC key. */
void lite_core_init(LiteCore *c, const uint8_t *key, size_t key_len, uint32_t now_ms);
/* 1 = authentic command datagram accepted by the session decoder. */
int lite_core_receive(LiteCore *c, const uint8_t *dgram, size_t len, uint32_t now_ms);
LiteOutputs lite_core_tick(LiteCore *c, const LiteInputs *in, uint32_t now_ms);
/* Due telemetry: 0x190 status, 0x1A0 sense, 0x1A1 odometry, 0x1A2 arm path (from, to, fraction, target, flags,
   echo). 0x1A2 byte 6: bit0 arm settled, bit1 limp, bit2 claw commanded closed, bit3 claw servo at its target,
   bits 4-7 = echo bits 8-11; byte 7 = echo bits 0-7. Echo (N3, A05/A06) = the last 0x122 sequence the arm took (12
   bits; 0 = none yet in this lease session), so a refused or replayed command never looks answered.
   Tags are bound to the lease (lite_link.h). Returns how many datagrams were written.
   Arm limp latch (M3 review): the servo rails follow ACT_EN, so the arm goes limp and droops whenever it drops.
   Unless the arm was settled at stow (its limp rest on the fender is swept), the core no longer knows where it is:
   from power-on and after such a drop the arm servos get no pulse and 0x122 is refused, until 0x123 (the operator
   parked the arm at stow by hand; payload 1,0,0,0, seq16, session16) arrives with the actuators off. */
int lite_core_telemetry(LiteCore *c, uint32_t now_ms, uint8_t out[4][UGV_LITE_DGRAM_LEN]);
/* The arm path has reached its target and every arm servo is at it. */
int lite_core_arm_settled(const LiteCore *c);
/* DD84: the wheels may drive only with the arm known (not limp) and settled at a drive pose (UGV_ARM_DRIVE_MASK) and,
   A04 (full review) / DD93, the claw closed (commanded and there) and empty: fully open since its last close at a grasp
   pose (N4: a held object rides in the cargo bin, not in the claw; a lost "open" never lets the wheels go). Otherwise
   the side targets ramp to zero and 0x1A0 flags bit3 is set; bit4 = empty. The claw position is the servo model's, not
   a sensor: nothing measures that an object was let go.
   DD93 (M01): the claw (0 = closed = park, UGV_GRIP_OPEN_CDEG = open) opens only with the arm settled at an OPEN pose
   (arm_graph.h); while it is not closed and settled the arm moves only on edges between two OPEN poses. */
int lite_core_arm_allows_drive(const LiteCore *c);
/* Back-EMF current limiter: the motor voltage (mV) kept within EMF +/- I_LIMIT * R_min. */
float lite_core_limit_mv(float want_mv, float emf_mv);
/* FFI layout check (host tests over ctypes): 0 = LiteCore, 1 = LiteInputs, 2 = LiteOutputs. */
size_t lite_core_sizeof(int which);

#endif
