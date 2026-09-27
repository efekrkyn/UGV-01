"""J-PWR must match KiCad's actual 2x2 pads, with positive rails diagonal."""
import json
import os
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOOTPRINT = Path(os.environ.get(
    "UGV_J_PWR_FOOTPRINT",
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_Molex.pretty/"
    "Molex_Mega-Fit_76825-0004_2x02_P5.70mm_Horizontal.kicad_mod",
))


def check(manifest, pads):
    pins = manifest["pins"]
    errors = []
    if manifest["mpn"] != "768250004" or manifest["footprint"] != (
        "Connector_Molex:Molex_Mega-Fit_76825-0004_2x02_P5.70mm_Horizontal"
    ):
        errors.append("wrong connector or footprint")
    if {p["pad"] for p in pins} != {1, 2, 3, 4} or len(pins) != 4:
        errors.append("missing or duplicate pad")
    if {p["net"] for p in pins} != {"ACT_BUS", "PGND_A", "PGND_B", "5V_CONTROL"}:
        errors.append("missing or duplicate net")
    if pads != {1: (0.0, 0.0), 2: (5.7, 0.0), 3: (0.0, 5.5), 4: (5.7, 5.5)}:
        errors.append("not the expected 2x2 footprint")
    if not errors:
        by_net = {p["net"]: pads[p["pad"]] for p in pins}
        a, b = by_net["ACT_BUS"], by_net["5V_CONTROL"]
        if a[0] == b[0] or a[1] == b[1]:
            errors.append("positive rails are adjacent")
        if any(p["awg"] != (16 if p["net"] == "5V_CONTROL" else 12) for p in pins):
            errors.append("wire gauge differs from current budget")
    return errors


manifest = json.loads((ROOT / "config/pwr_mcu_connector.json").read_text())
footprint_text = FOOTPRINT.read_text()
pads = {
    int(number): (float(x), float(y))
    for number, x, y in re.findall(
        r'\(pad "(\d+)"\s+thru_hole\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)',
        footprint_text,
    )
}
assert check(manifest, pads) == []

adjacent = deepcopy(manifest)
next(p for p in adjacent["pins"] if p["net"] == "5V_CONTROL")["pad"] = 2
next(p for p in adjacent["pins"] if p["net"] == "PGND_A")["pad"] = 4
assert "positive rails are adjacent" in check(adjacent, pads)

missing_ground = deepcopy(manifest)
next(p for p in missing_ground["pins"] if p["net"] == "PGND_B")["net"] = "PGND_A"
assert "missing or duplicate net" in check(missing_ground, pads)

duplicate_pad = deepcopy(manifest)
next(p for p in duplicate_pad["pins"] if p["net"] == "PGND_B")["pad"] = 2
assert "missing or duplicate pad" in check(duplicate_pad, pads)

wrong_footprint = dict(pads)
wrong_footprint[4] = (11.4, 0.0)
assert "not the expected 2x2 footprint" in check(manifest, wrong_footprint)
print("PASS: J-PWR footprint is 2x2; power rails diagonal; missing ground rejected")
