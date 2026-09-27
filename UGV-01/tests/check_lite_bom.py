"""A3 Lite parts list: total within the budget and quantities consistent with config/pin map.

M3 (DD75): the cap moved from 10,000 to 13,500 TL for the character body and the 5-axis arm (user: cost may rise).
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / "manufacturing/bom/lite_bom_A3.csv").open(encoding="utf-8")))
vehicle = json.loads((ROOT / "config/vehicle.json").read_text())
pinmap = json.loads((ROOT / "config/esp32_pinmap.json").read_text())
BUDGET_TL = 13_500


def qty(*categories):
    return sum(int(r["quantity"]) for r in rows if r["category"] in categories)


total = sum(int(r["quantity"]) * float(r["unit_tl"]) for r in rows)
assert total <= BUDGET_TL, total
assert len({r["id"] for r in rows}) == len(rows), "duplicate BOM id"
assert all(r["source"].startswith("http") or r["source"] == "tahmin" for r in rows), "every price has a source or says tahmin"
assert qty("motor", "motor_encoder") == vehicle["motor"]["quantity"]
assert qty("motor_encoder") == vehicle["motor"]["encoder_quantity"] == vehicle["motor"]["quantity"]  # R4
assert qty("ballast") == vehicle["motor"]["quantity"]  # one series ballast per motor (R4)
assert qty("driver") == vehicle["motor_driver"]["quantity"]
text = " ".join(r["item"] for r in rows)
assert "2 NC" in text, "2-NC E-stop (R6/R8)"
# M3 arm: 6804-2RS in the neck and both shoulder bosses, 6704-2RS on the twist, 624ZZ + M4 idlers on elbow and wrist.
bearings = {r["item"].split()[0]: int(r["quantity"]) for r in rows if r["category"] == "mechanical" and "rulman" in r["item"]}
assert bearings == {"6804-2RS": 3, "6704-2RS": 1, "624ZZ": 2}, bearings
assert "M4" in text and "PCA9685" in text
# One servo per PCA9685 channel, and each arm joint's servo model is in the BOM.
assert qty("servo") == len(pinmap["pca9685"]["channels"]) == 8
servo_rows = {r["item"].split()[0]: int(r["quantity"]) for r in rows if r["category"] == "servo"}
arm = vehicle["geometry"]["arm"]["servos"]
assert servo_rows == {"MG90S": 2 + sum(v == "MG90S" for v in arm.values()), "MG996R": sum(v == "MG996R" for v in arm.values()),
                      "DS3218MG": 1}, servo_rows
assert qty("power") >= 3 and sum(int(r["quantity"]) for r in rows if r["item"].startswith("Mini560")) == 3  # logic + 2 servo rails
assert qty("camera") == 2 and qty("tof") == 2
assert qty("cell") == vehicle["battery"]["series"] * vehicle["battery"]["parallel"]
assert qty("filament") == 4  # M3: 3 PETG + 1 TPU spools from the CAD filament estimate (check_body_mass)
# N7 (M3 review): the active summaries quote this total and margin, not an older one.
tl = lambda x: f"{x:,.0f}".replace(",", ".")  # noqa: E731
for doc in ("README.md", "docs/lite_electronics_A3.md"):
    text = (ROOT / doc).read_text()
    assert f"{tl(total)} TL" in text and f"{tl(BUDGET_TL - total)} TL pay" in text, (doc, tl(total))
print(f"PASS: A3 Lite BOM {total:,.0f} TL <= {BUDGET_TL:,} TL ({BUDGET_TL - total:,.0f} TL margin); "
      "quantities match config and pin map")
