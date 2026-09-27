"""A3 Lite ESP32-S3-DevKitC-1 pin map: only free pins, ADC1 for analog, peripheral capacity, PCA9685 servos (M3)."""
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from esp32_pinmap import REQUIRED, header_pin, validate  # noqa: E402

m = json.loads((ROOT / "config/esp32_pinmap.json").read_text())
assert validate(m) == [], validate(m)
assert len(m["assignments"]) == 20 and {a["signal"] for a in m["assignments"]} == REQUIRED
# Every exposed, unreserved GPIO is either used or listed as a spare (M3: the servos moved to the PCA9685).
exposed = {int(n) for pins in m["headers"].values() for n in pins if n.isdigit()}
free = exposed - {int(g) for g in m["unavailable"]}
used = {a["gpio"] for a in m["assignments"]}
assert free - used == {int(g) for g in m["spare"]} == {40, 41, 42}, free ^ used
# M3 (DD75): eight servos on a PCA9685 (I2C0, shared with the ToF sensors) in firmware joint order; /OE is an ESP32
# GPIO with a pull-up so every PWM output is off through reset and boot; two 5 V servo rails.
pca = m["pca9685"]
assert pca["channels"] == [c["signal"] for c in pca["servos"]] == [
    "SERVO_PAN", "SERVO_TILT", "SERVO_SHOULDER", "SERVO_TWIST", "SERVO_ELBOW", "SERVO_WRIST", "SERVO_ROLL", "SERVO_GRIPPER"]
assert int(pca["address"], 16) not in {int(a, 16) for a in m["tof_addresses"]} and int(pca["address"], 16) == 0x40
assert {c["rail"] for c in pca["servos"]} == {"A", "B"}
assert next(a for a in m["assignments"] if a["signal"] == pca["oe_signal"])["peripheral"] == "GPIO"
assert header_pin(m, 4) == "J1-4" and header_pin(m, 1) == "J3-4" and header_pin(m, 47) == "J3-17"
# R4: every motor, rear included, has its own encoder (single channel A, one PCNT unit each).
kind = {a["signal"]: a["peripheral"] for a in m["assignments"]}
assert {s for s, p in kind.items() if p == "PCNT"} == {f"ENC_{w}_A" for w in ("FL", "FR", "RL", "RR")}, kind
# R6: the E-stop is read from its own NC contact as a digital, edge-latched input, not an ADC level.
assert kind["ESTOP_SENSE"] == "GPIO" and kind["VBAT_SENSE"] == "ADC1", kind


def broken(change):
    bad = deepcopy(m)
    change(bad)
    return validate(bad)


def signal(mm, name):
    return next(a for a in mm["assignments"] if a["signal"] == name)


for gpio in (0, 3, 19, 20, 35, 36, 37, 38, 43, 44, 45, 46, 48):  # strap, USB, console, PSRAM, RGB LED
    errors = broken(lambda mm, g=gpio: signal(mm, "ACT_EN").update(gpio=g))
    assert any(f"GPIO{gpio} " in e for e in errors), (gpio, errors)
assert any("ADC1" in e for e in broken(lambda mm: signal(mm, "VBAT_SENSE").update(gpio=11)))  # ADC2 vs Wi-Fi
assert any("duplicate" in e for e in broken(lambda mm: signal(mm, "ESTOP_SENSE").update(gpio=1)))
assert any("missing" in e for e in broken(lambda mm: mm["assignments"].pop()))
assert any("LEDC" in e for e in broken(lambda mm: mm["assignments"].extend(
    {"signal": f"SPARE{i}", "gpio": 21, "peripheral": "LEDC"} for i in range(9))))
# L4a (DD86): the ESP-IDF board layer takes its pins from a header generated from this map, never by hand.
from gen_pins import render  # noqa: E402
assert (ROOT / "firmware/lite/esp32/main/pins.h").read_text() == render(m), \
    "firmware/lite/esp32/main/pins.h is stale: python3 tools/gen_pins.py"
print("PASS: ESP32-S3 DevKitC-1 pin map: 20 GPIOs + 3 listed spares, 8 servos on the PCA9685 (/OE pulled up); "
      "reserved pins, ADC2 and peripheral overflow rejected; pins.h generated from it")
