"""AI bridge (DeepSeek default, Claude optional) with a mock client: no network, no API key, no cost."""
import json
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace as NS
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "software"))
from ugv_ai.bridge import DEFAULT_PROVIDER, PROVIDERS, AiBridge  # noqa: E402
from ugv_ai.executor import Permit, SkillExecutor  # noqa: E402
from ugv_ai.sim import SimClock, SimVehicle  # noqa: E402
from ugv_ai.tools import TOOLS  # noqa: E402


def usage(i=1000, o=200, read=0, write=0):
    return NS(input_tokens=i, output_tokens=o, cache_read_input_tokens=read, cache_creation_input_tokens=write)


def tool(uid, name, args):
    return NS(type="tool_use", id=uid, name=name, input=args)


def reply(stop, *blocks, u=None):
    return NS(stop_reason=stop, content=[NS(type="thinking", thinking="", signature="sig"), *blocks],
              usage=u or usage())


class MockClient:
    def __init__(self, replies, on_call=None):
        self.replies, self.calls, self.on_call = list(replies), [], on_call
        self.messages = self

    def create(self, **request):
        self.calls.append(request)
        if self.on_call:
            self.on_call(len(self.calls))
        return self.replies.pop(0)


def rig(replies, **kw):
    clock = SimClock()
    vehicle = SimVehicle(clock)
    permit = Permit(clock)
    permit.set(ai_switch=True, visible_focused=True)
    permit.renew()
    clock.hooks.append(lambda t: permit.renew())
    said = []
    ex = SkillExecutor(vehicle, permit, clock, panel=said.append, operator=lambda q: "evet")
    client = MockClient(replies, kw.pop("on_call", None))
    return AiBridge(ex, vehicle, client=client, **kw), client, vehicle, permit, said


# Happy path: look -> drive -> finish. Request shape, observation and tool_result pairing.
bridge, client, vehicle, permit, said = rig([
    reply("tool_use", tool("t1", "look", {"pan_deg": 20, "tilt_deg": -30})),
    reply("tool_use", NS(type="text", text="Küpe gidiyorum."), tool("t2", "drive", {"distance_m": 0.3, "speed_mps": 0.1})),
    reply("tool_use", tool("t3", "finish", {"summary": "Küpün önündeyim."})),
])
out = bridge.run("Kırmızı küpün önüne git.")
assert out.status == "finished" and out.steps == 3 and said[-1] == "Küpün önündeyim.", out
assert abs(vehicle.x - 0.3) < 1e-6 and vehicle.head == (20, -30) and vehicle.v == 0
first = client.calls[0]
# Default provider: DeepSeek V4.1 Flash (vision + tools) on its Anthropic-compatible endpoint.
assert DEFAULT_PROVIDER == "deepseek" and first["model"] == "deepseek-flash"
assert PROVIDERS["deepseek"]["base_url"] == "https://api.deepseek.com/anthropic"
assert "thinking" not in first and "cache_control" not in first  # not verified on DeepSeek; ignored there anyway
assert first["output_config"] == {"effort": "medium"} and bridge.max_usd == 0.10
assert [t["name"] for t in first["tools"]] == [t["name"] for t in TOOLS]
assert all("strict" not in t and t["input_schema"] == s["input_schema"] for t, s in zip(first["tools"], TOOLS))
assert isinstance(first["system"], str) and first["max_tokens"] >= 8000
opening = first["messages"][0]
assert opening["role"] == "user"
kinds = [b["type"] for b in opening["content"]]
assert kinds.count("image") == 2 and "Kırmızı küpün önüne git." in opening["content"][0]["text"], kinds
assert '"front_tof_m"' in opening["content"][0]["text"]  # vehicle state JSON rides along
second = client.calls[1]["messages"]
assert second[1]["role"] == "assistant" and second[1]["content"] is not None
result = second[2]["content"][0]
assert second[2]["role"] == "user" and result["type"] == "tool_result" and result["tool_use_id"] == "t1"
assert [b["type"] for b in result["content"]] == ["text", "image", "image"] and not result["is_error"]
assert client.calls[0]["system"] == client.calls[2]["system"]  # frozen prefix for the cache

# Claude stays available as an option with its own request shape.
bridge, client, vehicle, permit, said = rig([reply("tool_use", tool("t1", "finish", {"summary": "tamam"}))],
                                            provider="anthropic")
assert bridge.run("bitir").status == "finished" and bridge.max_usd == 0.30
claude = client.calls[0]
assert claude["model"] == "claude-sonnet-5" and claude["thinking"] == {"type": "adaptive"}
assert claude["cache_control"] == {"type": "ephemeral"} and claude["tools"] is TOOLS

# Keys come only from the environment (git-ignored secret file), checked before any SDK import.
os.environ.pop("DEEPSEEK_API_KEY", None)
try:
    AiBridge(bridge.executor, vehicle)
except RuntimeError as error:
    assert "DEEPSEEK_API_KEY" in str(error)
else:
    raise AssertionError("missing DeepSeek key must fail loudly")

# Out-of-bounds tool input comes back as an error result, the loop continues.
bridge, client, vehicle, permit, said = rig([
    reply("tool_use", tool("t1", "drive", {"distance_m": 5, "speed_mps": 0.1})),
    reply("end_turn", NS(type="text", text="Yapamıyorum.")),
])
out = bridge.run("5 metre git.")
bad = client.calls[1]["messages"][2]["content"][0]
assert bad["is_error"] and "distance_m" in bad["content"][0]["text"] and vehicle.max_abs_speed == 0
assert out.status == "end_turn" and out.text == "Yapamıyorum."

# refusal / max_tokens: the turn's tools are never executed.
for stop in ("refusal", "max_tokens"):
    bridge, client, vehicle, permit, said = rig([reply(stop, tool("t1", "drive", {"distance_m": 0.5, "speed_mps": 0.2}))])
    out = bridge.run("git")
    assert out.status == stop and vehicle.max_abs_speed == 0 and len(client.calls) == 1, out

# Step and dollar caps.
looping = [reply("tool_use", tool(f"t{n}", "wait", {"seconds": 0})) for n in range(10)]
bridge, client, vehicle, permit, said = rig(looping, max_steps=3)
assert bridge.run("bekle").status == "step_limit" and len(client.calls) == 3
pricey = [reply("tool_use", tool(f"t{n}", "wait", {"seconds": 0}), u=usage(i=40000, o=2000)) for n in range(10)]
bridge, client, vehicle, permit, said = rig(pricey, max_usd=0.20, provider="anthropic")
out = bridge.run("bekle")
assert out.status == "cost_limit" and 0.20 < out.usd < 0.40 and len(client.calls) == 3, out  # $0.1 per call
huge = [reply("tool_use", tool(f"t{n}", "wait", {"seconds": 0}), u=usage(i=400000, o=100000)) for n in range(3)]
bridge, client, vehicle, permit, said = rig(huge)  # DeepSeek peak prices: $0.12 + $0.12 per call > $0.10 cap
out = bridge.run("bekle")
assert out.status == "cost_limit" and abs(out.usd - 0.24) < 1e-9 and len(client.calls) == 1, out

# Permit lost while the model is thinking: no further call, vehicle stopped.
bridge, client, vehicle, permit, said = rig(
    [reply("tool_use", tool("t1", "look", {"pan_deg": 0, "tilt_deg": 0})) for _ in range(3)],
    on_call=lambda n: n == 2 and permit.set(ai_switch=False, visible_focused=True))
out = bridge.run("etrafa bak")
assert out.status == "permit_lost" and len(client.calls) == 2 and vehicle.v == 0, out

# R2: the lease lapses (or focus drops) while the model is thinking and comes back before the reply is
# handled: the old reply must not move anything.
def lapse(n):
    if n == 1:
        bridge.executor.clock.t += 0.2  # 200 ms model call without a heartbeat
        permit.renew()


def refocus(n):
    if n == 1:
        permit.set(ai_switch=True, visible_focused=False)
        permit.set(ai_switch=True, visible_focused=True)


for event in (lapse, refocus):
    bridge, client, vehicle, permit, said = rig(
        [reply("tool_use", tool("t1", "drive", {"distance_m": 0.1, "speed_mps": 0.2}))], on_call=event)
    out = bridge.run("biraz ilerle")
    assert out.status == "permit_lost" and vehicle.max_abs_speed == 0 and len(client.calls) == 1, (event, out)

# R10: two tasks logged to the same directory keep their own images, and each log line points at them.
with tempfile.TemporaryDirectory() as tmp:
    frames = iter([b"\xff\xd8task-one\xff\xd9", b"\xff\xd8task-two\xff\xd9"])
    for text in ("birinci", "ikinci"):
        bridge, client, vehicle, permit, said = rig([reply("tool_use", tool("t1", "finish", {"summary": text}))],
                                                    log_dir=tmp)
        frame = next(frames)
        vehicle.images = lambda f=frame: [("image/jpeg", f)]
        assert bridge.run(text).status == "finished"
    lines = [json.loads(line) for line in (Path(tmp) / "ai_steps.jsonl").read_text().splitlines()]
    assert len(lines) == 2 and lines[0]["task"] != lines[1]["task"], lines
    saved = [(Path(tmp) / line["images"][0]).read_bytes() for line in lines]
    assert saved == [b"\xff\xd8task-one\xff\xd9", b"\xff\xd8task-two\xff\xd9"], saved

# Local stop word between steps ends the task without another API call.
bridge, client, vehicle, permit, said = rig(
    [reply("tool_use", tool("t1", "wait", {"seconds": 0})) for _ in range(3)],
    on_call=lambda n: n == 1 and bridge.executor.request_stop("dur"))
assert bridge.run("bekle").status == "stopped" and len(client.calls) == 1

# API failure is fail-safe.
class Broken(MockClient):
    def create(self, **request):
        raise ConnectionError("offline")


bridge, client, vehicle, permit, said = rig([])
bridge.client = Broken([])
out = bridge.run("git")
assert out.status == "api_error" and "offline" in out.text and vehicle.v == 0
print("PASS: deepseek-flash default + claude option request shapes, env-only keys, observation images/state, tool_result pairing, "
      "error results, refusal/max_tokens, step/cost caps, permit loss, lapsed-lease/refocus stale replies (R2), "
      "per-task image logs (R10), stop word, API failure")
