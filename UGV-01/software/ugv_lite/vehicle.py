"""Executor-facing vehicle over the signed Wi-Fi UDP link to the ESP32-S3 Lite core (runs on the MacBook).

`pump()` runs every 20 ms (a thread in real use, a clock hook in tests): it reads telemetry and sends the
lease, the drive command and the head/arm frames. M3/N1: the 5-axis arm walks the pose graph one edge at a time;
the core itself moves all five joints along the edge (the path the CAD swept) and reports 0x1A2. A leg counts as
done only when that telemetry says the arm settled at the pose, so lost datagrams delay but never fake arrival. The deadman follows the AI-mode permit; after any loss
the vehicle only re-arms on an explicit `request_arm()`, which starts with the IDLE handshake the core
requires. Stale or invalid telemetry reads as NaN, never as zero or an old value (review R1).
M3 review: telemetry counts only when its tag is bound to a lease this vehicle sent within STALE_S, and its age is
measured from that lease, so recorded, delayed or other-session telemetry never reads as current. An arm the core
reports limp (pose unknown after a power drop, or since power-on) stays unusable until `confirm_arm_parked()`.
N3: inside that window a sample still counts only when it is bound to a newer lease than the last one taken for its
frame id (late or repeated datagrams are dropped), and a goal or hold ends only on a sample whose 0x1A2 echo shows the
core took a path command sent for it, never on one taken before the command.
"""
import json
import math
import os
from pathlib import Path
import threading

from ugv_ai.executor import pose_path
from . import frames

_CFG = json.loads((Path(__file__).resolve().parents[2] / "config/vehicle.json").read_text())
WHEEL_M = _CFG["geometry"]["wheel_diameter_mm"] / 1000
TRACK_M = _CFG["geometry"]["track_mm"] / 1000
COUNTS_PER_REV = _CFG["motor"]["gear_ratio"] * _CFG["motor"]["encoder_counts_motor_rev"]
MAX_MM_S = round(_CFG["motion"]["maximum_speed_m_s"] * 1000)  # the core rejects frames above its ceiling
STALE_S = 0.2
HANDSHAKE_PUMPS = 3
POSE_NAMES = list(_CFG["geometry"]["arm"]["poses_deg"])  # pose numbers = firmware/lite/arm_graph.h
POSE_INDEX = {name: k for k, name in enumerate(POSE_NAMES)}
AT_END = 65535


class LiteVehicle:
    def __init__(self, link, key, clock, permit_ok=lambda: True, session=None, cameras=()):
        self.link, self.key, self.clock, self.permit_ok = link, key, clock, permit_ok
        self.session = int.from_bytes(os.urandom(4), "little") if session is None else session
        self.cameras = list(cameras)
        self.lock = threading.Lock()
        self.seq = {"cmd": 0, "head": 0, "arm": 0, "path": 0, "park": 0}
        self.lease_ext, self.leases = 0, []  # 32-bit lease count; (lease_ext, sent at) within STALE_S
        self.want_arm, self.handshake, self.pumps = False, 0, 0
        self.left = self.right = 0
        self.head, self.gripper = (0, 0), "open"
        self.goal, self.hold, self.arm_visits, self.cmd_from = None, False, [], 0
        self.last_ext = {}  # frame id -> lease the newest accepted sample was bound to (N3)
        self.status = self.sense = self.odo = self.arm = None
        self.seen = {"status": None, "sense": None, "odo": None, "arm": None}

    # ---- link
    def _send(self, frame_id, payload):
        self.link.send(frames.pack(frames.CMD, frame_id, payload, self.key))

    def _next(self, name):
        value = self.seq[name]
        self.seq[name] = (value + 1) & 0xFFFF
        return value

    def _fresh(self, name):
        at = self.seen[name]
        return at is not None and self.clock.monotonic() - at <= STALE_S

    def _verify(self, data):
        """(id, payload, lease, lease sent at) when the tag binds to one of our recent leases, newest first."""
        for ext, at in reversed(self.leases):
            got = frames.unpack(data, frames.TLM, self.key, frames.bind(self.session, ext))
            if got:
                return (*got, ext, at)
        return None

    def pump(self):
        now = self.clock.monotonic()
        self.leases = [(ext, at) for ext, at in self.leases if now - at <= STALE_S]
        for data in self.link.recv():
            got = self._verify(data)
            if got is None:
                continue
            frame_id, payload, ext, at = got
            last = self.last_ext.get(frame_id)
            if last is not None and not 0 < (ext - last) & 0xFFFFFFFF < 1 << 31:
                continue  # N3: not newer than the sample already taken (late, reordered or repeated)
            self.last_ext[frame_id] = ext
            if frame_id == 0x190:
                self.status, self.seen["status"] = frames.status(payload), at
            elif frame_id == 0x1A0:
                self.sense, self.seen["sense"] = frames.sense(payload), at
            elif frame_id == 0x1A1:
                self.odo, self.seen["odo"] = frames.odometry(payload), at
            elif frame_id == 0x1A2:
                self.arm, self.seen["arm"] = frames.arm_state(payload), at
        with self.lock:
            if self.want_arm and not self.permit_ok():
                self.want_arm = False  # permit lost: disarm; only an explicit request re-arms
            if not self.want_arm or self.handshake:
                mode = frames.MODE_IDLE
                self.handshake = max(self.handshake - 1, 0)
            else:
                mode = frames.MODE_DRIVE if self.armed() else frames.MODE_ARM
            self._send(0x110, frames.lease(self.session, self.lease_ext, mode, mode != frames.MODE_IDLE))
            self.leases.append((self.lease_ext, now))
            self.lease_ext = (self.lease_ext + 1) & 0xFFFFFFFF
            if mode != frames.MODE_IDLE:
                left, right = (self.left, self.right) if mode == frames.MODE_DRIVE else (0, 0)
                self._send(0x100, frames.drive(left, right, self._next("cmd"), self.session))
                if self.pumps % 3 == 0:  # head <= 20 Hz
                    pan, tilt = self.head
                    self._send(0x120, frames.head(round(pan * 100), round(tilt * 100), self._next("head"), self.session))
                if self.pumps % 2 == 0:  # 25 Hz: gripper + AI flag (keeps the core's 200 mm/s cap), arm path
                    self._send(0x121, frames.arm(0, self.gripper == "close", True, self._next("arm"), self.session))
                    path = self._arm_command() if mode == frames.MODE_DRIVE else None
                    if path:
                        self._send(0x122, frames.arm_path(*path, self._next("path"), self.session))
            self.pumps += 1

    def request_arm(self):
        with self.lock:
            self.want_arm, self.handshake = True, HANDSHAKE_PUMPS

    def confirm_arm_parked(self):
        """Panel: the operator put the arm at stow by hand. The core takes it only while disarmed; three copies
        (forward sequence) ride out a lost datagram."""
        with self.lock:
            for _ in range(3):
                self._send(0x123, frames.arm_parked(self._next("park"), self.session))

    def disarm(self):
        with self.lock:
            self.want_arm = False

    def send_stop(self):
        """Local STOP: the 0x080 frame is latched by the core regardless of the session."""
        with self.lock:
            self.want_arm, self.left, self.right = False, 0, 0
        self._send(0x080, frames.stop())

    def armed(self):
        return self._fresh("status") and self.status["state"] in ("ARMED", "DRIVING")

    # ---- executor interface
    def set_velocity(self, v, w):
        def mm(x):
            return max(-MAX_MM_S, min(MAX_MM_S, round(x * 1000)))
        with self.lock:
            self.left, self.right = mm(v - w * TRACK_M / 2), mm(v + w * TRACK_M / 2)

    def stop(self):
        self.set_velocity(0.0, 0.0)

    def odometry(self):
        """(signed distance m, yaw rad) from the wheel edges, or NaN when telemetry is stale."""
        if not self._fresh("odo"):
            return math.nan, math.nan
        left, right = (count / COUNTS_PER_REV * math.pi * WHEEL_M for count in self.odo)
        return (left + right) / 2, (right - left) / TRACK_M

    def front_tof_m(self):
        if not self._fresh("sense") or min(self.sense["tof_mm"]) == 0:
            return math.nan
        return min(self.sense["tof_mm"]) / 1000

    def set_head(self, pan_deg, tilt_deg):
        self.head = (pan_deg, tilt_deg)

    @staticmethod
    def _node(arm):
        """Pose name when the reported path point is a pose, else None."""
        if arm["frac"] == AT_END:
            return POSE_NAMES[arm["to"]]
        return POSE_NAMES[arm["from"]] if arm["frac"] == 0 else None

    def _answers(self, arm):
        """N3: the sample was taken after the core took a 0x122 sent for the current goal or hold. The core echoes
        the low byte of the last path sequence it took and takes them only forward, so older commands cannot land
        later; sequences from cmd_from on belong to this goal (a window across the 16-bit wrap)."""
        sent = (self.seq["path"] - self.cmd_from) & 0xFFFF
        return sent > 0 and (arm["echo"] - self.cmd_from) & 0xFF < min(sent, 256)

    def _arm_command(self):
        """Next 0x122 (from, to, target) from the latest core telemetry, or None (caller holds the lock)."""
        if not self._fresh("arm") or self.arm["limp"]:
            return None
        arm = self.arm
        node = self._node(arm) if arm["settled"] else None
        if node and (not self.arm_visits or self.arm_visits[-1] != node):
            self.arm_visits.append(node)
        if self.hold:
            if arm["settled"] and self._answers(arm):
                self.hold = False
                return None
            return arm["from"], arm["to"], arm["frac"]  # stop where it is
        if self.goal is None:
            return None
        if node == self.goal:
            if self._answers(arm):
                self.goal = None
                return None
            return arm["from"], arm["to"], arm["frac"]  # pin it there until a sample answers this goal
        if node is not None:  # at a pose: next leg of the swept route
            return POSE_INDEX[node], POSE_INDEX[pose_path(node, self.goal)[0]], AT_END
        if not arm["settled"]:  # on a leg: let the core finish it along the same line
            return arm["from"], arm["to"], arm["target"]
        return arm["to"], arm["from"], AT_END  # held mid-edge: back along it to where it started

    def set_arm(self, pose):
        with self.lock:
            self.goal, self.hold, self.cmd_from = pose, False, self.seq["path"]

    def arm_moving(self):
        return self.goal is not None

    def hold_arm(self):
        with self.lock:
            self.goal, self.hold, self.cmd_from = None, True, self.seq["path"]

    def arm_pose(self):
        """From core telemetry: a pose name, "moving", "partial" (held mid-edge), "limp" (pose unknown to the core
        until the operator parks it) or "unknown" (stale)."""
        if not self._fresh("arm"):
            return "unknown"
        if self.arm["limp"]:
            return "limp"
        if not self.arm["settled"]:
            return "moving"
        return self._node(self.arm) or "partial"

    def set_gripper(self, action):
        self.gripper = action

    def images(self):
        shots = []
        for camera in self.cameras:  # ESP32-CAM /capture callables; a dead eye is skipped, not faked
            try:
                shots.append(("image/jpeg", camera()))
            except OSError:
                continue
        return shots

    def state(self):
        tof = self.front_tof_m()
        vbat = self.sense["vbat_mv"] if self._fresh("sense") else None
        return {"head_pan_deg": self.head[0], "head_tilt_deg": self.head[1], "arm": self.arm_pose(),
                "gripper": self.gripper, "front_tof_m": None if math.isnan(tof) else round(tof, 3),
                "battery_pct": None if vbat is None else max(0, min(100, round((vbat - 9600) / 30))),
                "moving": bool(self.left or self.right),
                "core": self.status["state"] if self._fresh("status") else "NO_TELEMETRY",
                "faults": self.status["faults"] if self._fresh("status") else None}
