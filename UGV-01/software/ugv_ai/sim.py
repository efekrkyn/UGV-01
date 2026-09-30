"""Deterministic clock and kinematic vehicle for host tests (no hardware, no network)."""


class SimClock:
    """Simulated monotonic time; hooks run after every sleep (panel heartbeat, test events)."""

    def __init__(self):
        self.t = 0.0
        self.hooks = []

    def monotonic(self):
        return self.t

    def sleep(self, seconds):
        self.t = round(self.t + seconds, 9)
        for hook in list(self.hooks):
            hook(self.t)


class SimVehicle:
    """Integrates the last commanded velocity lazily up to the clock's current time."""

    def __init__(self, clock, obstacle_x=None):
        self.clock, self.obstacle_x = clock, obstacle_x
        self.x = self.yaw = self.dist = self.v = self.w = self.max_abs_speed = 0.0
        self.head, self.arm, self.gripper, self.empty = (0, 0), "stow", "close", True  # DD93: claw parks closed
        self._at = clock.t

    def _advance(self):
        dt, self._at = self.clock.t - self._at, self.clock.t
        self.x += self.v * dt
        self.dist += abs(self.v) * dt
        self.yaw += self.w * dt

    def set_velocity(self, v, w):
        self._advance()
        self.v, self.w = v, w
        self.max_abs_speed = max(self.max_abs_speed, abs(v))

    def stop(self):
        self.set_velocity(0.0, 0.0)

    def odometry(self):
        self._advance()
        return self.dist, self.yaw

    def front_tof_m(self):
        self._advance()
        return 4.0 if self.obstacle_x is None else self.obstacle_x - self.x

    def set_head(self, pan_deg, tilt_deg):
        self.head = (pan_deg, tilt_deg)

    def set_arm(self, pose):
        self.arm = pose

    def arm_moving(self):
        return False

    def hold_arm(self):
        pass

    def set_gripper(self, action):
        """As the core (DD93/94): opens only at an open pose; a close anywhere but a release pose may hold an object."""
        from .executor import _ARM
        grip = _ARM["gripper"]
        if action == "open" and self.arm in grip["open_poses"]:
            self.gripper, self.empty = "open", True
        elif action == "close":
            if self.gripper == "open" and self.arm not in grip["release_poses"]:
                self.empty = False
            self.gripper = "close"

    def images(self):
        return [("image/jpeg", b"\xff\xd8sim-left\xff\xd9"), ("image/jpeg", b"\xff\xd8sim-right\xff\xd9")]

    def state(self):
        self._advance()
        return {"head_pan_deg": self.head[0], "head_tilt_deg": self.head[1], "arm": self.arm,
                "gripper": "closed" if self.gripper == "close" else "open", "gripper_empty": self.empty,
                "front_tof_m": round(self.front_tof_m(), 3),
                "battery_pct": 80, "moving": self.v != 0 or self.w != 0}
