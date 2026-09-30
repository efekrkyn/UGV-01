"""Onboard skill executor: the only path from an AI tool call to the vehicle.

Works offline. Every call is validated against local bounds, motion is ticked at
20 Hz and interrupted by the stop word, a dropped AI-mode permit or a close front
obstacle, and every motion ends with the vehicle stopped. The MCU keeps its own
freshness timeout and 200 mm/s AI-mode speed cap underneath this layer.
"""
from dataclasses import dataclass
import json
import math
from pathlib import Path

TICK_S = 0.05
FRONT_STOP_M = 0.25
TURN_RATE_RAD_S = 0.45
ARM_TIMEOUT_S = 20.0
BLIND_MPS = 0.1    # DD94: the core's forward creep while a front ToF sees nothing in range
BLIND_MAX_M = 0.3  # then stop and look again
GRIPPER_TIMEOUT_S = 2.0  # A04: the claw needs 0.33 s; the rest is telemetry and a lost datagram or two
# M3 (DD73): named poses of the 5-axis arm, joint degrees [shoulder, twist, elbow, wrist, roll], and the pose graph
# whose edges the CAD swept for collisions. "lift" is a planner-only waypoint (stow <-> up without twisting beside
# the body), not a pose the AI can ask for.
_ARM = json.loads((Path(__file__).resolve().parents[2] / "config/vehicle.json").read_text())["geometry"]["arm"]
ARM_POSES = {name: q for name, q in _ARM["poses_deg"].items() if name != "lift"}
ARM_EDGES = [tuple(e) for e in _ARM["pose_edges"]]
REACH_POSES = {"reach_mid", "reach_low", "reach_center", "store"}  # arm out in front or over the lid
DRIVE_POSES = set(_ARM["drive_poses"])  # driving and turning allowed only here; the core enforces it too (DD84)
DRIVE_TEXT = " or ".join(_ARM["drive_poses"])  # N4: only stow, where the loaded CG stays inside its limits
OPEN_POSES = set(_ARM["gripper"]["open_poses"])  # DD93: the claw opens only here (CAD-swept); the core enforces it
OPEN_TEXT = ", ".join(_ARM["gripper"]["open_poses"])


def pose_path(start, goal):
    """Shortest route start -> goal over the swept pose-graph edges, without start (breadth first)."""
    prev, todo = {start: None}, [start]
    while todo:
        node = todo.pop(0)
        for a, b in ARM_EDGES:
            for u, v in ((a, b), (b, a)):
                if u == node and v not in prev:
                    prev[v] = node
                    todo.append(v)
    if goal not in prev:
        raise ValueError(f"no swept path {start} -> {goal}")
    path = []
    while goal != start:
        path.insert(0, goal)
        goal = prev[goal]
    return path
SPEC = {
    "look": {"pan_deg": (-90, 90), "tilt_deg": (-60, 30)},
    "drive": {"distance_m": (-1.0, 1.0), "speed_mps": (0.02, 0.2)},
    "turn": {"angle_deg": (-180, 180)},
    "arm": {"pose": tuple(ARM_POSES)},
    "gripper": {"action": ("open", "close")},
    "wait": {"seconds": (0, 10)},
    "say": {"text": 200},
    "ask_operator": {"question": 200},
    "finish": {"summary": 500},
}


@dataclass
class Result:
    ok: bool
    text: str
    images: bool = False
    done: bool = False
    abort: bool = False


class Permit:
    """AI mode is allowed only with the panel switch on, the page visible and focused, and a fresh lease.

    `generation` counts every loss (switch or focus off, or a lease that ran out before it was renewed),
    so a task started under one generation can never be authorised again by a later renewal."""
    LEASE_S = 0.1

    def __init__(self, clock):
        self.clock, self.ai_switch, self.visible_focused, self.lease_at = clock, False, False, None
        self.generation = 0

    def set(self, ai_switch, visible_focused):
        self.ai_switch, self.visible_focused = ai_switch, visible_focused
        if not (ai_switch and visible_focused):
            self.generation += 1

    def renew(self):
        now = self.clock.monotonic()
        if self.lease_at is None or now - self.lease_at > self.LEASE_S:
            self.generation += 1  # the previous lease had already lapsed
        self.lease_at = now

    def ok(self):
        return (self.ai_switch and self.visible_focused and self.lease_at is not None
                and self.clock.monotonic() - self.lease_at <= self.LEASE_S)


def finite_number(value):
    """A real int/float a float can hold and that is finite; bools, NaN, inf and huge ints are not."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def validate(name, args):
    """Error text, or None when the call is inside the local bounds."""
    if name not in SPEC:
        return f"unknown tool {name!r}"
    spec = SPEC[name]
    if not isinstance(args, dict) or set(args) != set(spec):
        return f"{name} needs exactly {sorted(spec)}"
    for key, rule in spec.items():
        value = args[key]
        if isinstance(rule, int):
            if not isinstance(value, str) or not 1 <= len(value) <= rule:
                return f"{key} must be text of 1..{rule} characters"
        elif isinstance(rule[0], str):
            if value not in rule:
                return f"{key} must be one of {list(rule)}"
        elif not finite_number(value) or not rule[0] <= value <= rule[1]:
            return f"{key} must be a number in {rule[0]}..{rule[1]}"
    return None


class SkillExecutor:
    def __init__(self, vehicle, permit, clock, panel=None, operator=None):
        self.vehicle, self.permit, self.clock = vehicle, permit, clock
        self.panel = panel or (lambda text: None)
        self.operator = operator or (lambda question: None)
        self.stop_reason = None
        self.task_generation = permit.generation

    def request_stop(self, reason):
        """Local stop word / STOP button: never waits for the network or the model."""
        self.stop_reason = reason
        self.vehicle.stop()

    def new_task(self):
        """An explicitly started task; it is valid only while the permit keeps this generation."""
        self.stop_reason = None
        self.task_generation = self.permit.generation

    def halt_reason(self):
        """Why motion must end now, or None."""
        if self.stop_reason:
            return f"stopped by operator ({self.stop_reason})"
        if not self.permit.ok() or self.permit.generation != self.task_generation:
            return "AI mode permit lost (switch, page focus or lease)"
        return None

    def execute(self, name, args):
        halt = self.halt_reason()
        if halt:
            self.vehicle.stop()
            return Result(False, halt, abort=True)
        error = validate(name, args)
        if error:
            return Result(False, error)
        if name in ("drive", "turn"):
            state = self.vehicle.state()
            if state["arm"] not in DRIVE_POSES:
                return Result(False, f"arm must be {DRIVE_TEXT} before driving or turning")
            # N4/DD93: a held object moves the CG sideways; it rides in the cargo bin, and the claw drives closed
            if state["gripper"] != "closed" or not state.get("gripper_empty"):
                return Result(False, "the gripper must be closed and empty before driving or turning: put a held "
                                     "object in the cargo bin first (arm store, gripper open, gripper close)")
        return getattr(self, f"_{name}")(**args)

    def _move(self, target, rate, axis, forward_check):
        """Tick until `target` (m or rad) is covered on odometry `axis`; always ends stopped.

        Every odometry and front range sample is checked before use: a NaN/inf reading is a sensor
        fault, so motion does not start, or stops at once, with an explicit error."""
        sign, goal = (1 if target >= 0 else -1), abs(target)
        deadline = self.clock.monotonic() + goal / min(rate, BLIND_MPS) + 2.0
        blind_from = None  # DD94: where the front view went blind in this motion
        try:
            start = self.vehicle.odometry()[axis]
            if not finite_number(start):
                return Result(False, "odometry reading invalid (not a finite number); not moving", images=True)
            while True:
                halt = self.halt_reason()
                if halt:
                    return Result(False, halt, images=True, abort=True)
                position = self.vehicle.odometry()[axis]
                if not finite_number(position):
                    return Result(False, "odometry reading invalid (not a finite number); stopped", images=True)
                covered = abs(position - start)
                if covered >= goal - 1e-9:
                    return Result(True, f"done ({covered:.3f})", images=True)
                speed = rate
                if forward_check and sign > 0:
                    front = self.vehicle.front_tof_m()
                    blind = getattr(self.vehicle, "front_blind", lambda: False)()  # DD94: said so by the vehicle
                    if not (finite_number(front) or (front == math.inf and blind)):  # R1: any other inf is invalid
                        return Result(False, "front ToF reading invalid (not a finite number); stopped", images=True)
                    if front < FRONT_STOP_M:
                        return Result(False, f"obstacle ahead, stopped after {covered:.2f} m", images=True)
                    if blind:
                        blind_from = covered if blind_from is None else blind_from
                        if covered - blind_from >= BLIND_MAX_M:  # DD94: nothing seen is not a clear road
                            return Result(False, f"front ToF sees nothing in range: stopped after {covered:.2f} m, "
                                                 f"{BLIND_MAX_M} m of it blind; look before driving on", images=True)
                        speed = min(rate, BLIND_MPS)
                    else:
                        blind_from = None
                if self.clock.monotonic() > deadline:
                    return Result(False, "motion timeout", images=True)
                step = sign * min(speed, (goal - covered) / TICK_S)
                if axis == 0:
                    self.vehicle.set_velocity(step, 0.0)
                else:
                    self.vehicle.set_velocity(0.0, step)
                self.clock.sleep(TICK_S)
        finally:
            self.vehicle.stop()

    def _drive(self, distance_m, speed_mps):
        return self._move(distance_m, speed_mps, 0, True)

    def _turn(self, angle_deg):
        return self._move(math.radians(angle_deg), TURN_RATE_RAD_S, 1, False)

    def _look(self, pan_deg, tilt_deg):
        self.vehicle.set_head(pan_deg, tilt_deg)
        return Result(True, "head moved", images=True)

    def _arm(self, pose):
        """Walk the pose graph; wait until the arm arrives. A halt holds the arm where it is."""
        fault = getattr(self.vehicle, "arm_fault", None)
        if fault:  # DD94: latched for the session; the next task re-arms with a new one
            return Result(False, fault, images=True)
        state = self.vehicle.state()
        if state["arm"] == "limp":  # M3 review: pose unknown to the core after a power drop
            return Result(False, "arm is limp (servo power dropped away from stow): park it by hand, confirm on "
                                 "the panel, then re-arm", images=True)
        if state["gripper"] != "closed":  # DD93: open jaws are swept only between the open poses
            if state["arm"] not in OPEN_POSES or pose not in OPEN_POSES or \
                    any(p not in OPEN_POSES for p in pose_path(state["arm"], pose)):
                return Result(False, f"close the gripper first: with it open the arm moves only between {OPEN_TEXT}",
                              images=True)
        self.vehicle.set_arm(pose)
        deadline = self.clock.monotonic() + ARM_TIMEOUT_S
        while self.vehicle.arm_moving():
            halt = self.halt_reason()
            if halt or self.clock.monotonic() > deadline:
                self.vehicle.hold_arm()
                return Result(False, halt or "arm timeout (is the vehicle armed?)", images=True, abort=bool(halt))
            self.clock.sleep(TICK_S)
        fault = getattr(self.vehicle, "arm_fault", None)  # A05: the core never took the commands
        if fault:
            return Result(False, fault, images=True)
        return Result(True, f"arm {pose}", images=True)

    def _gripper(self, action):
        """A04: done only when the vehicle reports the gripper there (core telemetry), not when it was asked."""
        want = "open" if action == "open" else "closed"
        state = self.vehicle.state()
        if state["arm"] == "limp":  # DD94 recheck: no pulse reaches the claw until the operator parks the arm
            return Result(False, "the arm and gripper are limp (position unknown) until the operator parks them",
                          images=True)
        if action == "open" and state["arm"] not in OPEN_POSES:  # DD93: jaws would hit the body
            return Result(False, f"the gripper opens only with the arm at {OPEN_TEXT}", images=True)
        self.vehicle.set_gripper(action)
        deadline = self.clock.monotonic() + GRIPPER_TIMEOUT_S
        while self.vehicle.state()["gripper"] != want:
            halt = self.halt_reason()
            if halt or self.clock.monotonic() > deadline:
                if state["gripper"] in ("open", "closed"):  # withdraw the request: no late move after a failure
                    self.vehicle.set_gripper("open" if state["gripper"] == "open" else "close")
                return Result(False, halt or f"gripper did not report {want} (is the vehicle armed?)", images=True,
                              abort=bool(halt))
            self.clock.sleep(TICK_S)
        return Result(True, f"gripper {action}", images=True)

    def _wait(self, seconds):
        end = self.clock.monotonic() + seconds
        while self.clock.monotonic() < end:
            halt = self.halt_reason()
            if halt:
                return Result(False, halt, abort=True)
            self.clock.sleep(TICK_S)
        return Result(True, "waited")

    def _say(self, text):
        self.panel(text)
        return Result(True, "shown to operator")

    def _ask_operator(self, question):
        answer = self.operator(question)
        return Result(True, f"operator answer: {answer}" if answer else "operator did not answer")

    def _finish(self, summary):
        self.panel(summary)
        return Result(True, "task finished", done=True)
