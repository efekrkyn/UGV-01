"""Signed A3 Lite UDP datagrams, byte-identical to firmware/lite/lite_link.c.

'U' + direction ('C' command / 'T' telemetry) + version 1 + id16 LE + 8-byte payload + first 8 bytes of
HMAC-SHA256 over the first 13 bytes. Payloads keep the A2 CAN layouts (docs/communication_architecture.md).
M3 review: telemetry tags also cover `bind(session, lease_ext)`, the lease the core last accepted, so the MacBook
accepts telemetry only for a lease it sent within its staleness window (no replayed or delayed telemetry).
"""
import hashlib
import hmac
import struct

CMD, TLM = ord("C"), ord("T")
MODE_IDLE, MODE_ARM, MODE_DRIVE = 0, 1, 2
STATES = ("IDLE", "ARMED", "DRIVING", "ESTOP", "FAULT")


def bind(session, lease_ext):
    """Telemetry binding: lease session and extended (32-bit) lease sequence, as lite_link.c."""
    return struct.pack("<II", session & 0xFFFFFFFF, lease_ext & 0xFFFFFFFF)


def pack(direction, frame_id, payload, key, binding=b""):
    body = bytes([ord("U"), direction, 1]) + struct.pack("<H", frame_id) + bytes(payload)
    return body + hmac.new(key, body + binding, hashlib.sha256).digest()[:8]


def unpack(data, direction, key, binding=b""):
    """(id, payload) for an authentic datagram of this direction (and binding), else None."""
    if len(data) != 21 or data[0] != ord("U") or data[1] != direction or data[2] != 1:
        return None
    if not hmac.compare_digest(hmac.new(key, data[:13] + binding, hashlib.sha256).digest()[:8], data[13:]):
        return None
    return struct.unpack("<H", data[3:5])[0], data[5:13]


def lease(session, seq, mode, deadman):
    return struct.pack("<IHBB", session & 0xFFFFFFFF, seq & 0xFFFF, 0x10 | mode, 1 if deadman else 0)


def drive(left_mm_s, right_mm_s, seq, session):
    return struct.pack("<hhHH", left_mm_s, right_mm_s, seq & 0xFFFF, session & 0xFFFF)


def head(pan_cdeg, tilt_cdeg, seq, session):
    return struct.pack("<hhHH", pan_cdeg, tilt_cdeg, seq & 0xFFFF, session & 0xFFFF)


def arm(shoulder_cdeg, gripper_closed, ai_mode, seq, session):
    return struct.pack("<hBBHH", shoulder_cdeg, 1 if gripper_closed else 0, 1 if ai_mode else 0,
                       seq & 0xFFFF, session & 0xFFFF)


def arm_path(from_pose, to_pose, target, seq, session):
    """0x122 (M3/N1): move along the swept edge from_pose -> to_pose up to `target` (65535 = at to_pose).
    Pose numbers are config order (firmware/lite/arm_graph.h); the core refuses anything off the graph."""
    return struct.pack("<BBHHH", from_pose, to_pose, target & 0xFFFF, seq & 0xFFFF, session & 0xFFFF)


def arm_parked(seq, session):
    """0x123 (M3 review, DD94): the operator parked the arm at stow by hand and closed and emptied the claw (bytes 0 and
    1 both 1). The core accepts it only with the actuators off, and only then trusts the stow pose and a closed, empty
    claw again (it latches both unknown after a power drop away from stow or with the claw not closed, and at power-on)."""
    return struct.pack("<BBBBHH", 1, 1, 0, 0, seq & 0xFFFF, session & 0xFFFF)


def stop(reason=0):
    return bytes([1, reason & 0xFF, 0, 0, 0, 0, 0, 0])


def status(p):
    """0x190: core state, fault bits, telemetry sequence, core milliseconds."""
    state, faults, seq, ms = struct.unpack("<BBHI", p)
    return {"state": STATES[state] if state < len(STATES) else f"?{state}", "faults": faults, "seq": seq, "ms": ms}


def sense(p):
    """0x1A0: pack voltage, flags (needs IDLE handshake, forward blocked, ACT_EN, arm or claw blocks drive, claw empty:
    fully open since its last close away from store, DD93/94; forward blind: a ToF saw nothing in range, DD94), front
    ToF (0 invalid, 0xFFFF nothing in range)."""
    vbat, flags, left, right = struct.unpack("<HHHH", p)
    return {"vbat_mv": vbat, "needs_idle": bool(flags & 1), "forward_blocked": bool(flags & 2),
            "act_en": bool(flags & 4), "arm_blocks_drive": bool(flags & 8), "gripper_empty": bool(flags & 16),
            "forward_blind": bool(flags & 32),
            "tof_mm": (left, right)}


def arm_state(p):
    """0x1A2 (M3/N1): the core's arm path: from/to pose numbers, fraction, target, settled, limp (needs parking),
    gripper commanded closed and at its target (A04), echo = the last 0x122 sequence the arm took, 12 bits: byte 7 and
    flag bits 4-7 (N3, A05/A06; 0 = none yet in this lease session)."""
    frm, to, frac, target, flags, low = struct.unpack("<BBHHBB", p)
    return {"from": frm, "to": to, "frac": frac, "target": target, "settled": bool(flags & 1),
            "limp": bool(flags & 2), "gripper_closed": bool(flags & 4), "gripper_settled": bool(flags & 8),
            "echo": low | (flags >> 4) << 8}


def odometry(p):
    """0x1A1: left and right encoder edges (channel A, signed by the commanded direction)."""
    return struct.unpack("<ii", p)
