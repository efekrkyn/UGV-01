"""A3 Lite MacBook side end to end: Python frames = C frames; LiteVehicle + SkillExecutor drive the real
C core (built as a shared library, loaded with ctypes) over an in-memory link with a small motor/pose
model; the panel gateway maps messages to permit/stop/instruction. No network, no hardware, no API key."""
import ctypes
import math
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "software"))
from ugv_ai.executor import Permit, SkillExecutor  # noqa: E402
from ugv_ai.sim import SimClock  # noqa: E402
from ugv_lite import frames  # noqa: E402
from ugv_lite.gateway import Gateway, local_origin, serve  # noqa: E402
from ugv_lite.vehicle import ARM_UNANSWERED, COUNTS_PER_REV, TRACK_M, WHEEL_M, LiteVehicle  # noqa: E402

KEY = bytes(range(32))
SOURCES = ["firmware/lite/lite_core.c", "firmware/lite/arm_path.c", "firmware/lite/lite_link.c", "firmware/lite/hmac_sha256.c",
           "firmware/stm32/can_protocol.c", "firmware/stm32/servo_control.c", "firmware/stm32/light_bar.c"]
build = Path(tempfile.mkdtemp()) / "liblitecore.so"
subprocess.run(["cc", "-std=c11", "-shared", "-fPIC", "-O1", *[str(ROOT / s) for s in SOURCES], "-lm", "-o", str(build)],
               check=True)
lib = ctypes.CDLL(str(build))


class Inputs(ctypes.Structure):
    _fields_ = [("vbat_mv", ctypes.c_uint16), ("estop_edge", ctypes.c_uint8), ("estop_level", ctypes.c_uint8),
                ("tof_mm", ctypes.c_uint16 * 2), ("enc", ctypes.c_uint32 * 4)]


class Rgb(ctypes.Structure):
    _fields_ = [("r", ctypes.c_uint8), ("g", ctypes.c_uint8), ("b", ctypes.c_uint8)]


class Outputs(ctypes.Structure):
    _fields_ = [("state", ctypes.c_int), ("act_en", ctypes.c_uint8), ("faults", ctypes.c_uint8),
                ("forward_blocked", ctypes.c_uint8), ("forward_blind", ctypes.c_uint8), ("duty", ctypes.c_int16 * 4),
                ("servo_us", ctypes.c_uint16 * 8),
                ("light", Rgb * 8)]


lib.lite_core_sizeof.restype = ctypes.c_size_t
lib.lite_core_tick.restype = Outputs
lib.lite_core_tick.argtypes = [ctypes.c_void_p, ctypes.POINTER(Inputs), ctypes.c_uint32]
lib.lite_core_receive.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32]
lib.lite_core_init.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32]
lib.lite_core_telemetry.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
lib.ugv_lite_pack.argtypes = [ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint16, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]
lib.ugv_lite_pack_bound.argtypes = [ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint16, ctypes.c_char_p, ctypes.c_char_p,
                                    ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32]
assert (lib.lite_core_sizeof(1), lib.lite_core_sizeof(2)) == (ctypes.sizeof(Inputs), ctypes.sizeof(Outputs))

# Python datagrams are byte-identical to the C ones (and to the vector in tests/lite_link_test.c).
lease = frames.lease(0x12345678, 0, frames.MODE_ARM, 1)
assert frames.pack(frames.CMD, 0x110, lease, KEY).hex() == "554301100178563412000011014fd3dde0206c7b81"
for n, payload in enumerate((frames.drive(-300, 250, 77, 0x12345678), frames.arm(-5500, 1, 1, 9, 0x12345678),
                             frames.head(9000, -3000, 65535, 0x12345678), frames.stop(),
                             frames.arm_path(0, 1, 65535, 3, 0x12345678))):
    c_out = ctypes.create_string_buffer(21)
    lib.ugv_lite_pack(c_out, frames.TLM if n % 2 else frames.CMD, 0x100 + n, payload, KEY, len(KEY))
    assert frames.pack(frames.TLM if n % 2 else frames.CMD, 0x100 + n, payload, KEY) == c_out.raw
    lib.ugv_lite_pack_bound(c_out, frames.TLM, 0x1A0 + n, payload, KEY, len(KEY), 0x12345678, 70000 + n)
    assert frames.pack(frames.TLM, 0x1A0 + n, payload, KEY, frames.bind(0x12345678, 70000 + n)) == c_out.raw
# M3: the firmware servo table matches config (arm joint limits, stow park) and the PCA9685 channel order.
import json  # noqa: E402
import re  # noqa: E402
arm_cfg = json.loads((ROOT / "config/vehicle.json").read_text())["geometry"]["arm"]
pinmap = json.loads((ROOT / "config/esp32_pinmap.json").read_text())
JOINTS = {n: tuple(map(int, v)) for n, *v in re.findall(
    r"\[UGV_SERVO_(\w+)\] = \{(-?\d+), (-?\d+), (-?\d+), (\d+), (\d+), (\d+)\}",
    (ROOT / "firmware/stm32/servo_control.c").read_text())}
order = re.search(r"enum \{ (UGV_SERVO_PAN.*?), UGV_SERVO_COUNT \}", (ROOT / "firmware/stm32/servo_control.h").read_text(), re.S)
assert ["SERVO_" + n.strip().removeprefix("UGV_SERVO_") for n in order.group(1).split(",")] == pinmap["pca9685"]["channels"]
for j, (lo, hi), park in zip(arm_cfg["joints"], arm_cfg["limits_deg"], arm_cfg["poses_deg"]["stow"]):
    lo_c, hi_c, park_c, rate, _, _ = JOINTS[j.upper()]
    assert (lo_c, hi_c, park_c) == (lo * 100, hi * 100, park * 100) and rate >= 6000, j


# N1: the firmware's pose graph header is generated from config and must match it exactly.
sys.path.insert(0, str(ROOT / "tools"))
from gen_arm_graph import render  # noqa: E402
assert (ROOT / "firmware/lite/arm_graph.h").read_text() == render(json.loads((ROOT / "config/vehicle.json").read_text())), \
    "firmware/lite/arm_graph.h is stale: python3 tools/gen_arm_graph.py"


def pulse(joint, deg):
    lo_c, hi_c, _, _, us_lo, us_hi = JOINTS[joint]
    return us_lo + (round(deg * 100) - lo_c) * (us_hi - us_lo) // (hi_c - lo_c)


good = frames.pack(frames.CMD, 0x110, lease, KEY)
assert frames.unpack(good, frames.CMD, KEY) == (0x110, lease)
assert frames.unpack(good, frames.TLM, KEY) is None  # direction is authenticated
assert frames.unpack(good[:-1] + bytes([good[-1] ^ 1]), frames.CMD, KEY) is None
assert frames.unpack(good, frames.CMD, bytes(32)) is None


class Robot:
    """The ESP32 side: the real C core ticked every 20 ms, plus wheels, pose and a front obstacle."""

    def __init__(self, clock):
        self.clock, self.inbox, self.outbox = clock, [], []
        self.core = ctypes.create_string_buffer(lib.lite_core_sizeof(0))
        self.now_ms = 1000
        lib.lite_core_init(self.core, KEY, len(KEY), self.now_ms)
        self.inp = Inputs(vbat_mv=11500, tof_mm=(2000, 2000))
        self.out = Outputs()
        self.rpm, self.frac = [0.0] * 4, [0.0] * 4
        self.x = self.yaw = 0.0
        self.obstacle_x = None
        self.radio = True  # telemetry reaches the MacBook
        self.tof = None  # a fixed front ToF reading instead of the obstacle model (0xFFFF: nothing in range)

    def step(self):
        self.now_ms += 20
        ke, path = (12000 - 70 * 12 / 1.8) / 77, 12 / 1.8 + 7.5 + 0.7
        for m in range(4):
            v = self.out.duty[m] / 1000 * self.inp.vbat_mv if self.out.act_en else 0.0
            drag = 0.135 * path * 1000
            ss = (v - drag) / ke if v > drag else (v + drag) / ke if v < -drag else 0.0
            self.rpm[m] += (ss - self.rpm[m]) * 0.02 / 0.08
            self.frac[m] += abs(self.rpm[m]) * COUNTS_PER_REV / 60 * 0.02
            edges = int(self.frac[m])
            self.frac[m] -= edges
            self.inp.enc[m] = (self.inp.enc[m] + edges) & 0xFFFFFFFF
        left = (self.rpm[0] + self.rpm[2]) / 2 / 60 * WHEEL_M * math.pi
        right = (self.rpm[1] + self.rpm[3]) / 2 / 60 * WHEEL_M * math.pi
        self.x += (left + right) / 2 * math.cos(self.yaw) * 0.02
        self.yaw += (right - left) / TRACK_M * 0.02
        gap = 2.0 if self.obstacle_x is None else self.obstacle_x - self.x
        self.inp.tof_mm[0] = self.inp.tof_mm[1] = max(1, min(2000, int(gap * 1000))) if self.tof is None else self.tof
        for d in self.inbox:
            lib.lite_core_receive(self.core, d, len(d), self.now_ms)
        self.inbox.clear()
        self.out = lib.lite_core_tick(self.core, ctypes.byref(self.inp), self.now_ms)
        self.inp.estop_edge = 0
        tlm = (ctypes.c_uint8 * 84)()
        if lib.lite_core_telemetry(self.core, self.now_ms, tlm) and self.radio:
            raw = bytes(tlm)
            self.outbox += [raw[i:i + 21] for i in range(0, 84, 21)]


class Link:
    """In-memory UDP: the vehicle sends to the robot inbox and reads the robot outbox."""

    def __init__(self, robot):
        self.robot, self.up = robot, True

    def send(self, data):
        if self.up:
            self.robot.inbox.append(data)

    def recv(self):
        got, self.robot.outbox[:] = list(self.robot.outbox), []
        return got


def park(clock, vehicle):
    """Operator check at power-on (and after a limp drop): arm put at stow by hand, confirmed with actuators off."""
    clock.sleep(0.05)  # the first leases carry the session to the core
    vehicle.confirm_arm_parked()
    clock.sleep(0.05)


def rig(obstacle_x=None, parked=True):
    clock = SimClock()
    robot = Robot(clock)
    robot.obstacle_x = obstacle_x
    link = Link(robot)
    permit = Permit(clock)
    permit.set(ai_switch=True, visible_focused=True)
    permit.renew()
    vehicle = LiteVehicle(link, KEY, clock, permit_ok=permit.ok, session=0x12345678,
                          cameras=[lambda: b"\xff\xd8left\xff\xd9", lambda: b"\xff\xd8right\xff\xd9"])

    def hook(t):  # 50 ms executor tick: panel heartbeat, then 20 ms vehicle pump + robot steps
        permit.renew()
        while robot.now_ms - 1000 + 20 <= t * 1000 + 1e-6:
            vehicle.pump()
            robot.step()
    clock.hooks.append(hook)
    ex = SkillExecutor(vehicle, permit, clock, panel=lambda text: None)
    if parked:
        park(clock, vehicle)
        assert vehicle.state()["arm"] == "stow", vehicle.state()
    return clock, robot, link, permit, vehicle, ex


# Arming over the link: IDLE handshake, then 500 ms of neutral ARM traffic; telemetry reports it.
clock, robot, link, permit, vehicle, ex = rig(parked=False)
assert math.isnan(vehicle.odometry()[0]) and math.isnan(vehicle.front_tof_m())  # no telemetry yet (R1)
park(clock, vehicle)
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
assert vehicle.armed() and robot.out.act_en and robot.out.state in (1, 2), (robot.out.state, vehicle.status)
assert vehicle.state()["core"] in ("ARMED", "DRIVING") and vehicle.state()["battery_pct"] > 50

# The executor drives 0.2 m on the real core: odometry comes back from the telemetry.
ex.new_task()
result = ex.execute("drive", {"distance_m": 0.2, "speed_mps": 0.15})
assert result.ok, result
assert abs(robot.x - 0.2) < 0.03 and robot.out.faults == 0, (robot.x, robot.out.faults)
for _ in range(10):
    clock.sleep(0.05)
assert all(d == 0 for d in robot.out.duty) and robot.out.act_en  # stopped, still armed
turn = ex.execute("turn", {"angle_deg": 30})
assert turn.ok and abs(math.degrees(robot.yaw) - 30) < 6, (turn, math.degrees(robot.yaw))
look = ex.execute("look", {"pan_deg": 30, "tilt_deg": -20})
assert look.ok and len(vehicle.images()) == 2
for _ in range(10):
    clock.sleep(0.05)
assert robot.out.servo_us[0] > 1500  # pan moved on the core

# M3 arm on the real core: the vehicle walks the pose graph (joint-space lines the CAD swept), the executor waits
# for it, and the core ends at the pose's pulses. A permit loss mid-move holds the arm where it is.
ex.new_task()
reach = ex.execute("arm", {"pose": "reach_low"})
assert reach.ok and vehicle.arm_visits[-4:] == ["lift", "up", "ready", "reach_low"], (reach, vehicle.arm_visits)
for _ in range(10):
    clock.sleep(0.05)
target = arm_cfg["poses_deg"]["reach_low"]
got = [robot.out.servo_us[k] for k in range(2, 7)]
assert all(abs(g - pulse(j.upper(), q)) <= 1 for g, j, q in zip(got, arm_cfg["joints"], target)), (got, target)
assert vehicle.state()["arm"] == "reach_low" and not vehicle.arm_moving()
turn_blocked = ex.execute("turn", {"angle_deg": 10})
assert not turn_blocked.ok and "arm" in turn_blocked.text
assert vehicle.sense["arm_blocks_drive"], vehicle.sense  # DD84: the core refuses too, and says so
clock.hooks.append(lambda t: permit.set(ai_switch=clock.t < stop_at, visible_focused=True))
stop_at = clock.t + 1.0
home = ex.execute("arm", {"pose": "stow"})
assert home.abort and not vehicle.arm_moving() and vehicle.state()["arm"] != "stow", home
clock.hooks.pop()

# N1 (M3 review) regressions: with half of the 0x122 path datagrams lost the arm still ends exactly at the pose
# (the core walks the edge on its own); with every 0x122 lost the executor must NOT report arrival and the core
# arm stays parked (before N1 it reported "reach_low" while the core sat in an unswept joint mix).
import random  # noqa: E402
stow_pulses = [pulse(j.upper(), q) for j, q in zip(arm_cfg["joints"], arm_cfg["poses_deg"]["stow"])]
for loss, expect_ok in ((0.5, True), (1.0, False)):
    clock, robot, link, permit, vehicle, ex = rig()
    rng, send = random.Random(7), link.send
    link.send = lambda d, send=send, rng=rng, loss=loss: None if d[3:5] == b"\x22\x01" and rng.random() < loss else send(d)
    vehicle.request_arm()
    for _ in range(20):
        clock.sleep(0.05)
    ex.new_task()
    result = ex.execute("arm", {"pose": "reach_low"})
    for _ in range(10):
        clock.sleep(0.05)
    got = [robot.out.servo_us[k] for k in range(2, 7)]
    if expect_ok:
        assert result.ok and vehicle.state()["arm"] == "reach_low", (loss, result)
        assert all(abs(g - pulse(j.upper(), q)) <= 1 for g, j, q in zip(got, arm_cfg["joints"], target)), (loss, got)
    else:
        assert not result.ok and "took none" in result.text and vehicle.state()["arm"] == "stow", (loss, result)
        assert got == stow_pulses, got

# M3 review (Codex, 26.09.2026). (1) Telemetry is bound to the lease it answers: authentic telemetry recorded
# earlier (or delayed, or from another session) is dropped, so a replayed "settled at stow" cannot unlock driving
# while the arm is out. (2) The servo rails follow ACT_EN, so the arm goes limp and droops whenever it drops. Unless
# the arm was settled at stow (its swept limp rest on the fender), the core latches it limp: no arm pulses and no
# path moves after re-arming until the operator parks it by hand and confirms with the actuators off. Power-on too.
clock, robot, link, permit, vehicle, ex = rig(parked=False)
clock.sleep(0.2)
assert vehicle.state()["arm"] == "limp", vehicle.state()  # power-on: the core cannot know where the arm is
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
ex.new_task()
limp = ex.execute("arm", {"pose": "reach_low"})
assert not limp.ok and "limp" in limp.text, limp
assert robot.out.act_en and robot.out.servo_us[0] > 0 and all(robot.out.servo_us[k] == 0 for k in range(2, 7))
assert not ex.execute("turn", {"angle_deg": 10}).ok
vehicle.confirm_arm_parked()  # refused while the actuators are on
for _ in range(4):
    clock.sleep(0.05)
assert vehicle.state()["arm"] == "limp" and all(robot.out.servo_us[k] == 0 for k in range(2, 7))

clock, robot, link, permit, vehicle, ex = rig()
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
recorded, recv = [], link.recv
link.recv = lambda recv=recv: (lambda got: recorded.extend(got) or got)(recv())
for _ in range(4):
    clock.sleep(0.05)
link.recv = recv
assert vehicle.state()["arm"] == "stow" and len(recorded) >= 8
ex.new_task()
assert ex.execute("arm", {"pose": "reach_low"}).ok and vehicle.state()["arm"] == "reach_low"
robot.outbox += recorded  # the authentic stow telemetry, sent again
vehicle.pump()
assert vehicle.state()["arm"] == "reach_low", vehicle.state()
assert not ex.execute("turn", {"angle_deg": 10}).ok and abs(robot.yaw) < 0.01
permit.set(ai_switch=False, visible_focused=True)  # ACT_EN drops with the arm out: it falls limp
for _ in range(4):
    clock.sleep(0.05)
assert not robot.out.act_en
permit.set(ai_switch=True, visible_focused=True)
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
assert robot.out.act_en and vehicle.state()["arm"] == "limp", vehicle.state()
assert all(robot.out.servo_us[k] == 0 for k in range(2, 7)), list(robot.out.servo_us)  # no jump from the droop
vehicle.disarm()
for _ in range(4):
    clock.sleep(0.05)
park(clock, vehicle)
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
assert vehicle.state()["arm"] == "stow" and [robot.out.servo_us[k] for k in range(2, 7)] == stow_pulses
permit.set(ai_switch=False, visible_focused=True)  # settled at stow: the limp rest is swept, no latch
for _ in range(4):
    clock.sleep(0.05)
permit.set(ai_switch=True, visible_focused=True)
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
assert vehicle.state()["arm"] == "stow" and [robot.out.servo_us[k] for k in range(2, 7)] == stow_pulses

# N3 (M3 review, 26.09.2026): inside the 0.2 s lease window telemetry can still arrive late or out of order, and a
# sample taken before the latest 0x122 says nothing about it. A delayed "settled at stow" sample handed over after
# newer "moving" ones must neither end an `arm stow` request early nor clear a hold, and arrival or hold release
# counts only from a sample whose 0x1A2 echo shows the core took a path command sent for that goal or hold.
def armed_rig():
    clock, robot, link, permit, vehicle, ex = rig()
    vehicle.request_arm()
    for _ in range(20):
        clock.sleep(0.05)
    return clock, robot, link, permit, vehicle, ex


def late_stow():
    """Armed at stow; keep one authentic stow 0x1A2, start `lift`, then hand that sample back last in one pump."""
    clock, robot, link, permit, vehicle, ex = armed_rig()
    kept, recv = [], link.recv
    link.recv = lambda: (lambda got: kept.extend(d for d in got if d[3:5] == b"\xa2\x01") or got)(recv())
    clock.sleep(0.1)
    assert kept and vehicle.state()["arm"] == "stow", vehicle.state()
    vehicle.set_arm("lift")
    link.recv = recv
    clock.sleep(0.1)
    assert vehicle.state()["arm"] == "moving", vehicle.state()
    late = [kept[-1]] * 2  # two pumps in a row, so one of them also sends arm frames (every other pump)
    link.recv = lambda: recv() + [late.pop()] if late else recv()
    return clock, robot, vehicle, ex


clock, robot, vehicle, ex = late_stow()
ex.new_task()
home = ex.execute("arm", {"pose": "stow"})
for _ in range(60):
    clock.sleep(0.05)
got = [robot.out.servo_us[k] for k in range(2, 7)]
assert home.ok and got == stow_pulses and vehicle.state()["arm"] == "stow", (home, got, vehicle.state())
clock, robot, vehicle, ex = late_stow()
vehicle.hold_arm()
for _ in range(60):
    clock.sleep(0.05)
lift_pulses = [pulse(j.upper(), q) for j, q in zip(arm_cfg["joints"], arm_cfg["poses_deg"]["lift"])]
got = [robot.out.servo_us[k] for k in range(2, 7)]
assert vehicle.state()["arm"] == "partial" and not vehicle.hold, vehicle.state()
assert got not in (stow_pulses, lift_pulses), got
# A sample from before the latest command: `lift` goes out, its "moving" answers are lost, then `stow` is asked
# while the last sample still says "settled at stow". The goal stays open until an answering sample arrives.
clock, robot, link, permit, vehicle, ex = armed_rig()
vehicle.set_arm("lift")
while not any(d[3:5] == b"\x22\x01" for d in robot.inbox):
    vehicle.pump()
robot.step()
robot.outbox.clear()
vehicle.set_arm("stow")
vehicle.pump()
assert vehicle.state()["arm"] == "stow" and vehicle.arm_moving()
for _ in range(100):
    clock.sleep(0.05)
    if not vehicle.arm_moving():
        break
for _ in range(20):
    clock.sleep(0.05)
got = [robot.out.servo_us[k] for k in range(2, 7)]
assert not vehicle.arm_moving() and got == stow_pulses and vehicle.state()["arm"] == "stow", (got, vehicle.state())
# The other frames must not rewind either: a 0x1A1 delayed inside the window (odometry from ~0.1 s earlier, while
# driving) is dropped, so the executor never sees the distance shrink (nor an older, clearer ToF on 0x1A0).
clock, robot, link, permit, vehicle, ex = armed_rig()
vehicle.set_velocity(0.15, 0.0)
clock.sleep(0.3)
kept, recv = [], link.recv
link.recv = lambda: (lambda got: kept.extend(d for d in got if d[3:5] == b"\xa1\x01") or got)(recv())
clock.sleep(0.1)
link.recv = recv
clock.sleep(0.06)
before = vehicle.odometry()[0]
late = [kept[-1]]
link.recv = lambda: recv() + [late.pop()] if late else recv()
vehicle.pump()
assert not late and vehicle.odometry()[0] >= before > 0.02, (before, vehicle.odometry())
vehicle.stop()
# The echo is 12 bits against a 16-bit sequence (A05, DD94): the vehicle tracks the last sequence the core took (`ack`)
# and never runs more than ARM_UNANSWERED past it, so an echo names exactly one command in flight, across the wrap;
# a goal is answered once `ack` reaches its first sequence; an echo that names nothing in flight moves nothing.
for ack, now, cmd_from, echo, want_ack, answered in ((65530, 65534, 65531, 0xFFD, 65533, True),
                                                     (65534, 2, 65535, 0x001, 1, True),
                                                     (65534, 2, 1, 0x000, 0, False),
                                                     (65534, 2, 65535, 0x003, 65534, False),     # not sent yet
                                                     (100, 104, 102, 100 & 0xFFF, 100, False)):  # nothing new
    vehicle.ack, vehicle.seq["path"], vehicle.cmd_from = ack, now, cmd_from
    assert vehicle._answers({"echo": echo}) == answered and vehicle.ack == want_ack, (ack, now, echo, vehicle.ack)

# Full review (29.09.2026). Every counter-example of docs/review_full_2026-09-29.md now ends safe.
def drop(link, frame_id):
    """Lose every command datagram with this id on the way to the core."""
    send, tag = link.send, frame_id.to_bytes(2, "little")
    link.send = lambda d: None if d[3:5] == tag else send(d)
    return send


# A04 / DD93: the twin geared claw on the real core. It opens only at a swept open pose; a close at a grasp pose may
# hold an object, so the vehicle then drives only after the claw has let go over the cargo bin (store) and closed. With
# every 0x121 "open" lost there, the claw stays closed in telemetry, the gripper call fails, the executor refuses to
# drive, and even a host that sends drive frames anyway gets no motion from the core.
clock, robot, link, permit, vehicle, ex = armed_rig()
ex.new_task()
assert vehicle.state()["gripper"] == "closed" and vehicle.state()["gripper_empty"] and robot.out.servo_us[7] == 1500
assert not ex.execute("gripper", {"action": "open"}).ok and robot.out.servo_us[7] == 1500  # not at stow
assert ex.execute("arm", {"pose": "reach_low"}).ok and ex.execute("gripper", {"action": "open"}).ok
assert vehicle.state()["gripper"] == "open" and robot.out.servo_us[7] == 2167
assert ex.execute("gripper", {"action": "close"}).ok and not vehicle.state()["gripper_empty"]  # grasp
assert ex.execute("arm", {"pose": "store"}).ok
send = drop(link, 0x121)
opened = ex.execute("gripper", {"action": "open"})
assert not opened.ok and "did not report open" in opened.text and vehicle.state()["gripper"] == "closed", opened
assert robot.out.servo_us[7] == 1500 and not vehicle.state()["gripper_empty"]  # still holding, as far as anyone knows
link.send = send
for _ in range(10):
    clock.sleep(0.05)
assert robot.out.servo_us[7] == 1500 and vehicle.gripper == "close"  # the failed request was withdrawn: no late open
assert ex.execute("arm", {"pose": "stow"}).ok
refused = ex.execute("drive", {"distance_m": 0.1, "speed_mps": 0.1})
assert not refused.ok and "empty" in refused.text and robot.x < 0.005, (refused, robot.x)
vehicle.set_velocity(0.1, 0.0)  # a host bug driving anyway
for _ in range(20):
    clock.sleep(0.05)
assert robot.x < 0.005 and all(d == 0 for d in robot.out.duty) and vehicle.sense["arm_blocks_drive"], robot.x
vehicle.stop()
assert ex.execute("arm", {"pose": "store"}).ok and ex.execute("gripper", {"action": "open"}).ok
assert vehicle.state()["gripper_empty"] and ex.execute("gripper", {"action": "close"}).ok
assert ex.execute("arm", {"pose": "stow"}).ok and vehicle.state()["gripper_empty"]
assert ex.execute("drive", {"distance_m": 0.1, "speed_mps": 0.1}).ok and robot.x > 0.08

# A05: every hold 0x122 lost while the arm walks to lift: after ARM_UNANSWERED sends the hold ends as a fault, never as
# a success read off the old echo (before: "cleared" after 256 sends while the core went on to lift). Across the
# 16-bit sequence wrap too: a goal still completes normally there, a lost hold still faults.
for wrap in (False, True):
    clock, robot, link, permit, vehicle, ex = armed_rig()
    if wrap:  # the core takes any first path sequence of a session; start just below the wrap
        vehicle.seq["path"] = vehicle.cmd_from = 65400
        vehicle.ack = 65399
        ex.new_task()
        assert ex.execute("arm", {"pose": "up"}).ok and ex.execute("arm", {"pose": "stow"}).ok
        assert vehicle.seq["path"] < 65400, vehicle.seq  # wrapped while both goals completed
    vehicle.set_arm("lift")
    clock.sleep(0.2)
    assert vehicle.state()["arm"] == "moving"
    send = drop(link, 0x122)
    vehicle.hold_arm()
    for _ in range(300):
        clock.sleep(0.05)
        if not vehicle.hold:
            break
    sent = (vehicle.seq["path"] - vehicle.cmd_from) & 0xFFFF
    assert not vehicle.hold and "took none" in vehicle.arm_fault and sent <= ARM_UNANSWERED, (vehicle.arm_fault, sent)
    assert vehicle.state()["arm"] == "lift"  # telemetry still says where the arm really went
    link.send = send

# R03 (DD94): 17 failed goals in a row with every 0x122 lost never turn into a success: after the first fault the arm
# fault stays for the session and no arm command goes out, so the 12-bit echo can never alias an old one (before: the
# 17th goal read "ok" off echo 0 at sequence 4097). Unanswered sends are bounded across goals too, not per goal:
# goals halted early before 255 each still fault at 255 in total. request_arm() (a new session) recovers.
clock, robot, link, permit, vehicle, ex = armed_rig()
send = drop(link, 0x122)
ex.new_task()
results = [ex.execute("arm", {"pose": "up"}) for _ in range(17)]
assert not any(r.ok for r in results) and all("re-arm" in r.text for r in results), results[-1]
assert vehicle._unanswered() <= ARM_UNANSWERED and vehicle.ack == 0 and vehicle.state()["arm"] == "stow"
clock, robot, link, permit, vehicle, ex = armed_rig()
send = drop(link, 0x122)
for _ in range(8):  # goals that each stop after 40 sends (a halt), 320 unanswered in all
    vehicle.set_arm("up")
    start = vehicle.seq["path"]
    while (vehicle.seq["path"] - start) & 0xFFFF < 40 and not vehicle.arm_fault:
        clock.sleep(0.05)
    vehicle.hold_arm()
assert vehicle.arm_fault and vehicle._unanswered() <= ARM_UNANSWERED, (vehicle.arm_fault, vehicle._unanswered())
link.send = send
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
ex.new_task()
assert vehicle.arm_fault is None and ex.execute("arm", {"pose": "up"}).ok and ex.execute("arm", {"pose": "stow"}).ok

# R02 (DD94): open at ready, then the actuators drop (permit loss). After re-arming the arm and the claw stay limp (no
# pulse: not the old open PWM against the side wall at stow) until the operator confirms "parked, claw closed and
# empty"; then the claw is closed and the vehicle's own request is "close", so no stale open follows.
clock, robot, link, permit, vehicle, ex = armed_rig()
ex.new_task()
assert ex.execute("arm", {"pose": "ready"}).ok and ex.execute("gripper", {"action": "open"}).ok
permit.set(ai_switch=False, visible_focused=True)
for _ in range(4):
    clock.sleep(0.05)
permit.set(ai_switch=True, visible_focused=True)
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
assert robot.out.act_en and vehicle.state()["arm"] == "limp" and robot.out.servo_us[7] == 0, list(robot.out.servo_us)
# DD94 recheck #2: a close asked while limp is no success: the claw gets no pulse, the core takes no target, the vehicle
# reads it "unknown" (not empty), and the executor says so at once (before: "gripper close" ok with the PWM at 0).
ex.new_task()
limp_close = ex.execute("gripper", {"action": "close"})
for _ in range(10):
    clock.sleep(0.05)
assert not limp_close.ok and "limp" in limp_close.text and robot.out.servo_us[7] == 0, limp_close
assert vehicle.state()["gripper"] == "unknown" and vehicle.state()["gripper_empty"] is False, vehicle.state()
vehicle.disarm()
for _ in range(4):
    clock.sleep(0.05)
park(clock, vehicle)
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
assert vehicle.state()["arm"] == "stow" and robot.out.servo_us[7] == 1500 and vehicle.gripper == "close"
assert vehicle.state()["gripper"] == "closed" and vehicle.state()["gripper_empty"]

# R01 (DD94): front ToF sees nothing in range (0xFFFF): no clear road. The core creeps forward at <= 100 mm/s and the
# executor stops after 0.3 m blind to look again; an invalid reading (0) stops at once.
clock, robot, link, permit, vehicle, ex = armed_rig()
robot.tof = 0xFFFF
clock.sleep(0.2)
assert vehicle.front_blind() and vehicle.front_tof_m() == math.inf and vehicle.sense["forward_blind"]
notes = []  # DD95: the operator watching the creep sees it start and end on the panel, once each
gw_blind = Gateway(permit, ex, vehicle, run_task=None, send=notes.append)
gw_blind.notice()
gw_blind.notice()
assert len(notes) == 1 and notes[0]["type"] == "status" and "kör" in notes[0]["text"] and "0,3 m" in notes[0]["text"]
ex.new_task()
blind = ex.execute("drive", {"distance_m": 1.0, "speed_mps": 0.2})
assert not blind.ok and "nothing in range" in blind.text and 0.28 < robot.x < 0.36, (blind, robot.x)
vehicle.set_velocity(0.3, 0.0)  # a host asking for more than the creep
for _ in range(30):
    clock.sleep(0.05)
speed = sum(robot.rpm) / 4 / 60 * WHEEL_M * math.pi
assert 0.08 < speed < 0.12, speed
robot.tof = 0
for _ in range(6):
    clock.sleep(0.05)
assert all(d == 0 for d in robot.out.duty) and robot.out.forward_blocked
gw_blind.notice()
assert len(notes) == 2 and "bitti" in notes[1]["text"], notes
vehicle.stop()

# A06: a new-sequence 0x122 the core refuses (stow -> reach_low is no edge) leaves the echo alone.
clock, robot, link, permit, vehicle, ex = armed_rig()
before = vehicle.arm["echo"]
bad = frames.pack(frames.CMD, 0x122, frames.arm_path(0, 5, AT_END := 65535, 99, vehicle.session), KEY)
assert lib.lite_core_receive(robot.core, bad, len(bad), robot.now_ms) == 0
clock.sleep(0.15)
assert vehicle.arm["echo"] == before != 99 and vehicle.state()["arm"] == "stow", vehicle.arm

# A07: an ESP32 reset binds the core's telemetry to the low 16 bits of the first lease it takes. Before and past
# 65536 leases in a session, request_arm() (a new session) recovers the link; telemetry recorded in the old session
# is dropped in the new one.
for start_ext in (100, 65500):
    clock, robot, link, permit, vehicle, ex = rig()
    vehicle.request_arm()
    vehicle.lease_ext = start_ext  # the session's first lease, as if it had run that long
    for _ in range(20):
        clock.sleep(0.05)
    assert vehicle.armed() and (start_ext < 65536 or vehicle.lease_ext > 65536)
    recorded, recv = [], link.recv
    link.recv = lambda recv=recv: (lambda got: recorded.extend(got) or got)(recv())
    for _ in range(4):
        clock.sleep(0.05)
    link.recv = recv
    assert vehicle.lease_ext > 65536 or start_ext < 65536, vehicle.lease_ext
    lib.lite_core_init(robot.core, KEY, len(KEY), robot.now_ms)  # watchdog reset: the core starts over
    for _ in range(10):
        clock.sleep(0.05)
    assert not vehicle.armed() and not robot.out.act_en  # no telemetry verifies, nothing moves
    vehicle.request_arm()
    for _ in range(20):
        clock.sleep(0.05)
    assert vehicle.armed() and robot.out.act_en, (start_ext, vehicle.status)
    status = dict(vehicle.status)
    robot.outbox += recorded  # old-session telemetry, authentic, handed back
    vehicle.pump()
    assert vehicle.status["seq"] >= status["seq"] and vehicle.armed()  # nothing older taken
park(clock, vehicle)  # the limp latch after the reset still needs the operator
assert vehicle.state()["arm"] in ("stow", "limp")

# DD94 recheck #3: pump() verifies and takes telemetry under the lock request_arm() resets the session with, so a
# sample verified for the old session cannot land in the new one (before: an old DRIVING status read "armed" in the
# new session and its own first samples were dropped as older). The gateway pumps and runs tasks on two threads.
class _Clock:
    t = 0.0

    def monotonic(self):
        return self.t


class _Link:
    inbox = ()

    def recv(self):
        got, self.inbox = list(self.inbox), []
        return got

    def send(self, data):
        pass


race_clock, race_link = _Clock(), _Link()
race = LiteVehicle(race_link, KEY, race_clock, session=0x12345678)
race.lease_ext, race.leases, old_session = 70001, [(70000, 0.0)], race.session
race_link.inbox = [frames.pack(frames.TLM, 0x190, struct.pack("<BBHI", 2, 0, 10, 1000), KEY, frames.bind(old_session, 70000))]
verified, resume, verify = threading.Event(), threading.Event(), race._verify


def paused_verify(data):
    got = verify(data)
    verified.set()
    resume.wait(2)
    return got


race._verify = paused_verify
pumping = threading.Thread(target=race.pump)
pumping.start()
assert verified.wait(2)
rearm = threading.Thread(target=race.request_arm)
rearm.start()
rearm.join(0.1)
assert rearm.is_alive()  # the reset waits: the verified sample is taken (or not) in the session it was verified in
resume.set()
pumping.join(2)
rearm.join(2)
race._verify = verify
assert race.session != old_session and race.status is None and 0x190 not in race.last_ext and not race.armed()
race_clock.t = 0.02
race.leases = [(0, 0.0), (1, 0.02)]
race_link.inbox = [frames.pack(frames.TLM, 0x190, struct.pack("<BBHI", 0, 0, 11, 1020), KEY, frames.bind(race.session, e))
                   for e in (0, 1)]
race.pump()
assert race.status["state"] == "IDLE" and race.last_ext[0x190] == 1 and not race.armed(), (race.status, race.last_ext)
# DD95 (Codex note, older than DD94): disarm and re-arm drop the wheel targets, so a re-arm never resumes old motion.
race.set_velocity(0.2, 0.0)
race.disarm()
assert race.left == race.right == 0
race.set_velocity(0.2, 0.0)
race.request_arm()
assert race.left == race.right == 0

# A03: the panel socket takes only this server's own page, one controlling connection at a time; the answers go to
# it alone; when it goes the permit goes with it; a reconnecting panel takes over again.
assert local_origin({"Host": "127.0.0.1:8765", "Origin": "http://127.0.0.1:8765"}, 8765)
assert local_origin({"Host": "localhost:8765", "Origin": "http://localhost:8765"}, 8765)
for headers in ({"Host": "127.0.0.1:8765", "Origin": "https://untrusted.example"},
                {"Host": "127.0.0.1:8765"},                                            # no Origin (not a browser page)
                {"Host": "evil.example:8765", "Origin": "http://evil.example:8765"},  # DNS rebinding
                {"Host": "127.0.0.1:9999", "Origin": "http://127.0.0.1:9999"}):
    assert not local_origin(headers, 8765), headers
clock, robot, link, permit, vehicle, ex = rig()
gw = Gateway(permit, ex, vehicle, run_task=lambda text: None, send=lambda msg: None)
first, second = [], []
assert gw.attach(first.append) and not gw.attach(second.append)
gw.handle({"type": "bogus"})
assert first and not second
gw.detach(second.append)  # not the owner: nothing happens
assert permit.ok()
gw.detach(first.append)
assert not permit.ok() and gw.attach(second.append)

try:
    import asyncio
    import json
    import socket
    import threading
    from websockets.asyncio.client import connect
    from websockets.exceptions import ConnectionClosed, InvalidStatus
except ImportError:
    print("SKIP: live panel socket test (pip install websockets)")
else:
    class WallClock:
        monotonic, sleep = staticmethod(__import__("time").monotonic), staticmethod(__import__("time").sleep)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    live_permit, ran = Permit(WallClock()), []
    live = Gateway(live_permit, SkillExecutor(vehicle, live_permit, WallClock()), vehicle, run_task=ran.append,
                   send=lambda msg: None)
    threading.Thread(target=serve, args=(live,), kwargs={"port": port}, daemon=True).start()
    url, page = f"ws://127.0.0.1:{port}/ai", f"http://127.0.0.1:{port}"

    async def live_test():
        for _ in range(50):
            try:
                owner = await connect(url, origin=page)
                break
            except OSError:
                await asyncio.sleep(0.05)
        try:
            await connect(url, origin="https://untrusted.example")
            raise AssertionError("foreign Origin accepted")
        except InvalidStatus as err:
            assert err.response.status_code == 403
        other = await connect(url, origin=page)  # a second panel: closed at once, takes nothing over
        try:
            await asyncio.wait_for(other.recv(), 1.0)
            raise AssertionError("second panel kept")
        except ConnectionClosed as err:
            assert err.rcvd.code == 1008
        await owner.send(json.dumps({"type": "lease", "ai": True}))
        await owner.send(json.dumps({"type": "bogus"}))
        reply = json.loads(await asyncio.wait_for(owner.recv(), 1.0))  # the answer comes back to the owner
        assert reply["type"] == "status" and "unknown" in reply["text"], reply
        assert live_permit.ai_switch
        await owner.close()
        await asyncio.sleep(0.2)
        assert not live_permit.ai_switch and live.owner is None  # the permit went with its panel
        again = await connect(url, origin=page)  # the panel reconnects and is in control again
        await again.send(json.dumps({"type": "instruction", "text": "küpü al"}))
        await asyncio.sleep(0.2)
        assert ran == ["küpü al"], ran
        await again.close()
    asyncio.run(live_test())

# Front obstacle: the executor and the core both stop short of it.
clock, robot, link, permit, vehicle, ex = rig(obstacle_x=0.6)
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
ex.new_task()
result = ex.execute("drive", {"distance_m": 1.0, "speed_mps": 0.2})
assert not result.ok and "obstacle" in result.text and robot.x < 0.6 - 0.2, (result, robot.x)

# Link loss (MacBook stops sending): the core drops ACT_EN within the 100 ms lease window.
clock, robot, link, permit, vehicle, ex = rig()
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
link.up = False
for _ in range(4):
    clock.sleep(0.05)
assert robot.out.state == 0 and not robot.out.act_en, robot.out.state

# Permit loss drops the deadman, so the core disarms too; re-arming needs an explicit request.
clock, robot, link, permit, vehicle, ex = rig()
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
permit.set(ai_switch=False, visible_focused=True)
for _ in range(4):
    clock.sleep(0.05)
assert robot.out.state == 0 and not robot.out.act_en and not vehicle.armed()
permit.set(ai_switch=True, visible_focused=True)
for _ in range(20):
    clock.sleep(0.05)
assert robot.out.state == 0, "no silent re-arm"

# Stale telemetry: odometry and range become NaN (R1 contract), so the executor refuses to move.
clock, robot, link, permit, vehicle, ex = rig()
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
robot.radio = False
for _ in range(6):
    clock.sleep(0.05)
assert math.isnan(vehicle.odometry()[0]) and math.isnan(vehicle.front_tof_m())
ex.new_task()
assert not ex.execute("drive", {"distance_m": 0.1, "speed_mps": 0.1}).ok and robot.x < 0.01
# A late datagram is as old as the lease it is bound to, not its arrival: telemetry held 100 ms on the way reads
# stale 200 ms after its lease even though it arrived only moments ago.
clock, robot, link, permit, vehicle, ex = rig()
held, recv = [], link.recv
link.recv = lambda recv=recv: (held.extend((clock.t, d) for d in recv()),
                               [d for t, d in held if clock.t - t >= 0.1], held.__setitem__(
                                   slice(None), [(t, d) for t, d in held if clock.t - t < 0.1]))[1]
for _ in range(10):
    clock.sleep(0.05)
assert not math.isnan(vehicle.odometry()[0])  # 100 ms late still counts
robot.radio = False
for _ in range(4):
    clock.sleep(0.05)
assert math.isnan(vehicle.odometry()[0]), "late telemetry aged from its arrival"

# Panel gateway: lease -> permit, stop -> local stop + STOP frame, instruction -> task runner.
clock, robot, link, permit, vehicle, ex = rig()
permit.set(ai_switch=False, visible_focused=False)
said, ran = [], []
gw = Gateway(permit, ex, vehicle, run_task=ran.append, send=said.append)
gw.handle({"type": "lease", "ai": True})
assert permit.ok()
gw.handle({"type": "lease", "ai": False})
assert not permit.ok()
gw.handle({"type": "lease", "ai": True})
vehicle.request_arm()
for _ in range(20):
    clock.sleep(0.05)
gw.handle({"type": "instruction", "text": "Kırmızı küpe git."})
assert ran == ["Kırmızı küpe git."]
gw.handle({"type": "stop", "source": "button"})
for _ in range(2):
    clock.sleep(0.05)
assert ex.stop_reason == "button" and robot.out.state == 0 and not robot.out.act_en
gw.handle({"type": "instruction", "text": "hemen dur"})  # stop word inside an instruction: stop, not AI
assert ran == ["Kırmızı küpe git."] and ex.stop_reason == "instruction"
gw.handle({"type": "bogus"})
assert said[-1]["type"] == "status" and "unknown" in said[-1]["text"]
gw.handle({"type": "arm_parked"})  # DD94: without the claw statement it is refused
assert said[-1]["type"] == "status" and "eksik" in said[-1]["text"], said[-1]
gw.handle({"type": "arm_parked", "claw_closed_empty": True})  # panel: parked by hand, claw closed and empty
assert said[-1]["type"] == "status" and "park" in said[-1]["text"].lower(), said[-1]
print("PASS: Python frames byte-identical to C; LiteVehicle arms the real C core over the signed link, drives "
      "0.2 m and turns 30 deg from telemetry odometry, walks the arm pose graph to reach_low (core pulses; 50 % 0x122 "
      "loss still arrives, 100 % loss never claims arrival), holds the "
      "arm on permit loss, stops before the ToF obstacle, loses ACT_EN on link or "
      "permit loss (no silent re-arm), NaN on stale telemetry; replayed telemetry dropped (lease-bound tags), arm "
      "limp from power-on and after an off-stow ACT_EN drop until parked by hand; N3: late/reordered telemetry "
      "dropped per frame (odometry never rewinds), arm goal/hold end only on samples echoing their 0x122; "
      "full review: twin claw opens only at swept poses, lost open over the bin blocks driving (A04, DD93), no false hold after 256+ lost 0x122 incl. wrap (A05), "
      "refused 0x122 leaves the echo (A06), new session re-binds after an ESP32 reset past 65536 leases (A07), "
      "panel socket: own Origin/Host, one owner, permit follows it (A03); no ACK alias over 17 failed goals, blind ToF creep, claw reconciled on park (DD94); limp claw no success, re-arm race, blind notice (DD95); gateway lease/stop/instruction/"
      "stop-word/arm_parked")
