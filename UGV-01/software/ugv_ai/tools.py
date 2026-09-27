"""Claude tool definitions for UGV-01 supervised AI mode.

Order and wording are frozen: the tool list is part of the cached prompt prefix.
Strict schemas cannot carry minimum/maximum, so the numeric bounds live in the
descriptions and are enforced by executor.py, which is the authority.
"""


def _tool(name, description, properties):
    return {"name": name, "description": description, "strict": True,
            "input_schema": {"type": "object", "properties": properties,
                             "required": list(properties), "additionalProperties": False}}


_NUM = {"type": "number"}
_ARM_POSES = ["stow", "up", "ready", "reach_mid", "reach_low", "reach_center", "store"]  # = executor.ARM_POSES

TOOLS = [
    _tool("look", "Point the head with both eye cameras. pan_deg -90..90 (positive = left), "
          "tilt_deg -60..30 (positive = up). Returns fresh images of both eyes.",
          {"pan_deg": _NUM, "tilt_deg": _NUM}),
    _tool("drive", "Drive straight. distance_m -1.0..1.0 (negative = reverse), speed_mps 0.02..0.2. "
          "Stops early if a front obstacle is closer than 0.25 m. Allowed only with the arm in stow and the "
          "gripper open. Returns fresh images.",
          {"distance_m": _NUM, "speed_mps": _NUM}),
    _tool("turn", "Turn in place. angle_deg -180..180 (positive = left). Allowed only with the arm in "
          "stow and the gripper open. Returns fresh images.",
          {"angle_deg": _NUM}),
    _tool("arm", "Move the right arm (5 joints + gripper, out of the body side) to a named pose: stow "
          "(lying on the fender along the body), up (raised straight up), ready (raised in front), "
          "reach_mid (straight ahead, level, right side), reach_low (gripper pointing down just above "
          "the ground about 7 cm in front of the right wheel), reach_center (gripper low in front of the "
          "robot's centre, below both cameras), store (gripper above the cargo slot on the lid: open it "
          "there to drop the object into the body bin). The arm follows checked paths and the vehicle "
          "stays stopped while it moves. Returns fresh images.",
          {"pose": {"type": "string", "enum": _ARM_POSES}}),
    _tool("gripper", "Open or close the right gripper. Objects up to 150 g only. Returns fresh images.",
          {"action": {"type": "string", "enum": ["open", "close"]}}),
    _tool("wait", "Stay still for seconds 0..10.", {"seconds": _NUM}),
    _tool("say", "Show a short Turkish message (max 200 characters) to the operator on the web panel.",
          {"text": {"type": "string"}}),
    _tool("ask_operator", "Ask the operator a Turkish question (max 200 characters) and wait for the "
          "answer. Use it before any uncertain or risky action.",
          {"question": {"type": "string"}}),
    _tool("finish", "End the task with a short Turkish summary (max 500 characters).",
          {"summary": {"type": "string"}}),
]
