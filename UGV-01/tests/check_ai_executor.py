"""Onboard skill executor: every AI tool call is bounded and interruptible locally."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "software"))
from ugv_ai.executor import ARM_POSES, REACH_POSES, Permit, SkillExecutor, pose_path  # noqa: E402
from ugv_ai.sim import SimClock, SimVehicle  # noqa: E402
from ugv_ai.tools import TOOLS  # noqa: E402


def rig(obstacle_x=None):
    clock = SimClock()
    vehicle = SimVehicle(clock, obstacle_x=obstacle_x)
    permit = Permit(clock)
    permit.set(ai_switch=True, visible_focused=True)
    permit.renew()
    clock.hooks.append(lambda t: permit.renew())  # panel heartbeat every tick
    said, asked = [], []
    ex = SkillExecutor(vehicle, permit, clock, panel=said.append,
                       operator=lambda q: asked.append(q) or "evet")
    return clock, vehicle, permit, ex, said, asked


# Tool schemas: fixed order, strict, closed objects; numeric bounds are enforced locally.
names = [t["name"] for t in TOOLS]
assert names == ["look", "drive", "turn", "arm", "gripper", "wait", "say", "ask_operator", "finish"], names
for tool in TOOLS:
    schema = tool["input_schema"]
    assert tool["strict"] is True and schema["additionalProperties"] is False, tool["name"]
    assert set(schema["required"]) == set(schema["properties"]), tool["name"]
    assert "minimum" not in str(schema) and "maximum" not in str(schema), tool["name"]

# Out-of-range, unknown and malformed calls are rejected without motion.
clock, vehicle, permit, ex, said, asked = rig()
for name, args in [("drive", {"distance_m": 1.5, "speed_mps": 0.1}),
                   ("drive", {"distance_m": 0.5, "speed_mps": 0.3}),
                   ("drive", {"distance_m": 0.5}),
                   ("drive", {"distance_m": 0.5, "speed_mps": 0.1, "extra": 1}),
                   ("drive", {"distance_m": True, "speed_mps": 0.1}),
                   ("look", {"pan_deg": 120, "tilt_deg": 0}),
                   ("look", {"pan_deg": 0, "tilt_deg": -70}),
                   ("arm", {"pose": "wave"}),
                   ("wait", {"seconds": 11}),
                   ("say", {"text": "x" * 201}),
                   ("self_destruct", {})]:
    result = ex.execute(name, args)
    assert not result.ok and not result.done, (name, args, result)
assert vehicle.max_abs_speed == 0 and vehicle.head == (0, 0) and vehicle.arm == "stow"

# A valid drive goes the distance at <= 0.2 m/s and ends stopped.
result = ex.execute("drive", {"distance_m": 0.5, "speed_mps": 0.2})
assert result.ok and result.images, result
assert abs(vehicle.x - 0.5) <= 0.011 and vehicle.v == 0 and vehicle.max_abs_speed <= 0.2 + 1e-9, vehicle.x

# Losing the AI-mode permit stops motion and aborts the task.
clock, vehicle, permit, ex, said, asked = rig()
clock.hooks.append(lambda t: t >= 1.0 and permit.set(ai_switch=True, visible_focused=False))
result = ex.execute("drive", {"distance_m": 1.0, "speed_mps": 0.2})
assert not result.ok and result.abort and vehicle.v == 0 and vehicle.x < 0.25, (result, vehicle.x)
assert not ex.execute("look", {"pan_deg": 10, "tilt_deg": 0}).ok  # no new tool without the permit

# A stale lease (panel heartbeat stopped) is the same as a dropped permit.
clock, vehicle, permit, ex, said, asked = rig()
clock.hooks.clear()
permit.renew()
clock.sleep(0.15)
assert not permit.ok() and not ex.execute("turn", {"angle_deg": 30}).ok and vehicle.max_abs_speed == 0

# The local stop word halts within one tick and aborts.
clock, vehicle, permit, ex, said, asked = rig()
clock.hooks.append(lambda t: t >= 0.5 and ex.request_stop("dur"))
result = ex.execute("drive", {"distance_m": 1.0, "speed_mps": 0.2})
assert result.abort and vehicle.v == 0 and vehicle.x <= 0.5 * 0.2 + 0.05 * 0.2 + 1e-9, vehicle.x

# Front ToF reflex: forward drive stops short of the obstacle, reverse is still allowed.
clock, vehicle, permit, ex, said, asked = rig(obstacle_x=0.6)
result = ex.execute("drive", {"distance_m": 1.0, "speed_mps": 0.2})
assert not result.ok and not result.abort and "obstacle" in result.text, result
assert vehicle.v == 0 and 0.6 - vehicle.x >= 0.25 - 0.011, vehicle.x
assert ex.execute("drive", {"distance_m": -0.2, "speed_mps": 0.1}).ok

# R1: a NaN/inf odometry or front range sample never lets motion start or continue.
nan, inf = float("nan"), float("inf")
for bad_tof in (nan, inf, -inf):
    clock, vehicle, permit, ex, said, asked = rig()
    vehicle.front_tof_m = lambda v=bad_tof: v
    result = ex.execute("drive", {"distance_m": 1.0, "speed_mps": 0.2})
    assert not result.ok and "ToF" in result.text and vehicle.max_abs_speed == 0, (bad_tof, result)
for bad_odo in (nan, inf):
    clock, vehicle, permit, ex, said, asked = rig()
    vehicle.odometry = lambda v=bad_odo: (v, v)
    for name, args in (("drive", {"distance_m": 0.1, "speed_mps": 0.2}), ("turn", {"angle_deg": 30})):
        result = ex.execute(name, args)
        assert not result.ok and "odometry" in result.text and vehicle.max_abs_speed == 0, (bad_odo, name, result)
clock, vehicle, permit, ex, said, asked = rig()  # sensor fails mid-motion: stop at once
real_tof = vehicle.front_tof_m
vehicle.front_tof_m = lambda: nan if clock.t >= 0.5 else real_tof()
result = ex.execute("drive", {"distance_m": 1.0, "speed_mps": 0.2})
assert not result.ok and "ToF" in result.text and vehicle.v == 0 and vehicle.x <= 0.1 + 0.011, (result, vehicle.x)
clock, vehicle, permit, ex, said, asked = rig()
real_odo = vehicle.odometry
vehicle.odometry = lambda: (nan, 0.0) if clock.t >= 0.5 else real_odo()
result = ex.execute("drive", {"distance_m": 1.0, "speed_mps": 0.2})
assert not result.ok and "odometry" in result.text and vehicle.v == 0 and vehicle.x <= 0.1 + 0.011, (result, vehicle.x)

# R2: a lapsed lease or a switch/focus drop voids the running task, even after the permit comes back.
clock, vehicle, permit, ex, said, asked = rig()
ex.new_task()
clock.hooks.clear()
clock.sleep(0.2)  # heartbeat lost while the model was thinking
permit.renew()    # heartbeat back before the reply is handled
assert permit.ok()
result = ex.execute("drive", {"distance_m": 0.1, "speed_mps": 0.2})
assert not result.ok and result.abort and vehicle.max_abs_speed == 0, result
clock.hooks.append(lambda t: permit.renew())
ex.new_task()  # only an explicitly started new task may move again
assert ex.execute("drive", {"distance_m": 0.1, "speed_mps": 0.2}).ok
clock, vehicle, permit, ex, said, asked = rig()
ex.new_task()
permit.set(ai_switch=True, visible_focused=False)
permit.set(ai_switch=True, visible_focused=True)
result = ex.execute("look", {"pan_deg": 30, "tilt_deg": 0})
assert permit.ok() and result.abort and vehicle.head == (0, 0), result

# R9: numbers a float cannot hold, NaN/inf and bools are ordinary errors, never exceptions or motion.
clock, vehicle, permit, ex, said, asked = rig()
for value in (10**400, -10**400, nan, inf, True):
    result = ex.execute("drive", {"distance_m": value, "speed_mps": 0.2})
    assert not result.ok and "distance_m" in result.text, (value, result)
assert vehicle.max_abs_speed == 0

# M3 (DD73): the AI picks named poses of the 5-axis arm; they come from config (the poses CAD swept), without the
# planner-only "lift" waypoint. Moves follow the pose graph, never a straight line across it.
import json  # noqa: E402
arm_cfg = json.loads((ROOT / "config/vehicle.json").read_text())["geometry"]["arm"]
assert ARM_POSES == {k: v for k, v in arm_cfg["poses_deg"].items() if k != "lift"}
arm_tool = next(t for t in TOOLS if t["name"] == "arm")
assert arm_tool["input_schema"]["properties"]["pose"]["enum"] == list(ARM_POSES)
assert pose_path("stow", "reach_low") == ["lift", "up", "ready", "reach_low"]
assert pose_path("reach_low", "store") == ["ready", "up", "lift", "store"]
assert pose_path("ready", "ready") == [] and REACH_POSES == {"reach_mid", "reach_low", "reach_center", "store"}

# Arm out: no driving or turning until it is stowed (N4: stow is the only drive pose, raised poses put the loaded CG
# past its limits) and the claw is closed and empty (DD93: a held object goes to the cargo bin first).
clock, vehicle, permit, ex, said, asked = rig()
assert ex.execute("arm", {"pose": "reach_low"}).ok and vehicle.arm == "reach_low"
assert not ex.execute("drive", {"distance_m": 0.2, "speed_mps": 0.1}).ok
assert not ex.execute("turn", {"angle_deg": 20}).ok and vehicle.max_abs_speed == 0
assert ex.execute("arm", {"pose": "store"}).ok and not ex.execute("drive", {"distance_m": 0.1, "speed_mps": 0.1}).ok
for pose in ("ready", "up"):
    assert ex.execute("arm", {"pose": pose}).ok
    refused = ex.execute("turn", {"angle_deg": 20})
    assert not refused.ok and "stow" in refused.text and vehicle.max_abs_speed == 0, refused
# DD93 claw: opens only at the swept open poses; while open the arm stays between them; after a grasp the vehicle drives
# only once the claw has let go over the cargo bin (store) and closed again.
assert ex.execute("arm", {"pose": "stow"}).ok
at_stow = ex.execute("gripper", {"action": "open"})
assert not at_stow.ok and "opens only" in at_stow.text and vehicle.gripper == "close", at_stow
assert ex.execute("arm", {"pose": "ready"}).ok and ex.execute("gripper", {"action": "open"}).ok
off = ex.execute("arm", {"pose": "up"})
assert not off.ok and "close the gripper" in off.text and vehicle.arm == "ready", off
assert ex.execute("arm", {"pose": "reach_low"}).ok and ex.execute("gripper", {"action": "close"}).ok  # grasp
assert ex.execute("arm", {"pose": "stow"}).ok
held = ex.execute("turn", {"angle_deg": 20})
assert not held.ok and "empty" in held.text and vehicle.max_abs_speed == 0, held
assert ex.execute("arm", {"pose": "store"}).ok and ex.execute("gripper", {"action": "open"}).ok
assert ex.execute("gripper", {"action": "close"}).ok and ex.execute("arm", {"pose": "stow"}).ok
assert ex.execute("turn", {"angle_deg": 20}).ok

# Talking, asking and finishing.
assert ex.execute("say", {"text": "Kırmızı küpü görüyorum."}).ok and said == ["Kırmızı küpü görüyorum."]
answer = ex.execute("ask_operator", {"question": "Küpü alayım mı?"})
assert answer.ok and "evet" in answer.text and asked == ["Küpü alayım mı?"]
done = ex.execute("finish", {"summary": "Küp taşındı."})
assert done.ok and done.done
print("PASS: strict tool schemas, local bounds, permit/lease loss, stale-task permit generations (R2), "
      "NaN/inf sensor samples (R1), huge-int/NaN/bool inputs (R9), stop word, ToF reflex, arm pose graph and "
      "arm-drive interlock")
