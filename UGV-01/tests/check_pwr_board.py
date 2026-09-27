"""Merged UGV-PWR-01 partial hierarchy: cross-page nets, J-SIG sources, permit logic from the netlist, ERC.

The permit check evaluates the real KiCad netlist (gate pins, series resistors, pulls) for every
combination of NC/watchdog/rail/MCU/latch/command inputs, and again with all logic stuck High.
It proves connectivity and Boolean intent only; T01/T03/T13 physical tests remain NOT_RUN.
"""
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from pwr_sheet import BOARD_DIR, erc, flagged, netlist, pins, violations  # noqa: E402

SHEET = BOARD_DIR / "ugv_pwr_01.kicad_sch"
values, nets, footprints = netlist(SHEET)
at = pins(nets)

for ref in ("U1", "Q1", "Q2", "K1", "U301", "U401", "U501", "J501", "J502"):
    assert ref in values, f"{ref} missing from merged hierarchy"

# K2 page joins the permit chain; LM74900 pad 25 still floats in the merged board.
assert nets["SAFE_EN"] == {("U1", "6"), ("U1", "7"), ("R5", "1"), ("U311", "4"), ("U310", "6")}, nets["SAFE_EN"]
assert at[("U1", "25")].startswith("unconnected"), "LM74900 RTN pad must not join PGND"
assert ("U1", "2") in nets["MID"] and ("K1", "14") in nets["MID"] and ("Q1", "1") in nets["MID"]
assert {("Q2", "1"), ("R205", "2"), ("R209", "1"), ("J502", "1"), ("C6", "1")} <= nets["ACT_BUS"]
assert nets["K2_FLT"] >= {("U1", "12"), ("R6", "2"), ("U401", "11")}

# Physical NC channels: nothing but the E-stop contact feeds K1's coil or the LVC1T45 B side.
assert {r for r, _ in nets["ESTOP_A_5V"]} == {"J301", "K1", "D202", "D301", "C301", "R301", "R303"}
assert {r for r, _ in nets["ESTOP_B_5V"]} == {"J301", "D302", "C302", "R302", "R304", "U311", "U312",
                                              "U313", "C318", "C320", "C322"}  # PWR_FLAGs are not netlist parts

# J-SIG: each contract pin has exactly one defined PWR-side element.
contract = json.loads((ROOT / "config/pwr_mcu_connector.json").read_text())
expected = {"MCU_RUN_REQ": {("R311", "1")}, "MCU_WDI": {("R305", "1")},
            "PWR_ACT_EN": {("R313", "2"), ("R314", "1"), ("R228", "1")},
            "PWR_K1_FB": {("R409", "2")}, "PWR_K2_FB": {("R410", "2")},
            "ESTOP_A_CLOSED": {("R315", "2")}, "ESTOP_B_CLOSED": {("R316", "2")}, "PWR_WD_OK": {("R317", "2")}}
for row in contract["signal_connector"]["pins"]:
    net = row["net"]
    assert ("J501", str(row["pad"])) in nets[net], net
    if net in expected:
        assert nets[net] - {("J501", str(row["pad"]))} == expected[net], (net, nets[net])

RAILS = {"PGND": 0, "PWR_3V3": 1, "5V_CONTROL": 1}
MODELS = {"SN74LVC1G08DBVR": ("4", "and", ("1", "2")), "SN74LVC1G11DBVR": ("4", "and", ("1", "3", "6")),
          "SN74LVC1G17DBVR": ("4", "and", ("2",)), "SN74LVC2G74DCUR": ("5", "latch", ("6",)),
          "SN74LVC1T45DBVR": ("4", "xlate", ("3", "6"))}


def other(ref, pin):
    return at[(ref, "2" if pin == "1" else "1")]


def strong(net, env, seen):
    """Actively driven level reachable through series resistors, else None."""
    if net in env:
        return env[net]
    if net in RAILS:
        return RAILS[net]
    for ref, pin in nets[net]:
        model = MODELS.get(values[ref])
        if model and model[0] == pin:
            _, kind, inputs = model
            vals = [level(at[(ref, i)], env, seen | {net}) for i in inputs]
            if kind == "xlate":  # B = A only while VCCB (NC-B channel) is present
                return int((env["_stuck"] or vals[0]) and vals[1])
            if env["_stuck"]:
                return 1
            if kind == "latch":  # Q = set-by-reset AND /CLR
                return int(env["_latched"] and vals[0])
            return int(all(vals))
    for ref, pin in nets[net]:
        if ref.startswith("R") and other(ref, pin) not in seen | set(RAILS):
            found = strong(other(ref, pin), env, seen | {net})
            if found is not None:
                return found
    return None


def level(net, env, seen=frozenset()):
    found = strong(net, env, seen)
    if found is not None:
        return found
    pulls = {other(r, p) for r, p in nets[net] if r.startswith("R")}
    assert pulls & set(RAILS), f"{net} floats with no pull resistor"
    return int(bool(pulls & {"PWR_3V3", "5V_CONTROL"}))


INPUTS = ("nc_a", "nc_b", "wd", "rail", "run", "latched", "k1", "k2", "pch", "test", "act")
checked = 0
for bits in product((0, 1), repeat=len(INPUTS)):
    s = dict(zip(INPUTS, bits))
    for stuck in (0, 1):
        env = {"ESTOP_A_5V": s["nc_a"], "ESTOP_B_5V": s["nc_b"], "WD_OK": s["wd"] & s["rail"],
               "RAIL_OK": s["rail"], "MCU_RUN_REQ": s["run"], "K1_CMD": s["k1"], "K2_CMD": s["k2"],
               "PRECHARGE_CMD": s["pch"], "TEST_CMD": s["test"], "ACT_ENABLE_REQ": s["act"],
               "_latched": s["latched"], "_stuck": stuck}
        k1 = level("ESTOP_A_5V", env) and level("K1_GATE", env)
        k2, pch, act = level("SAFE_EN", env), level("PCH_DRV", env), level("PWR_ACT_EN", env)
        test = level("TEST_PERMIT_DRV", env) and level("TSTC_DRV", env)
        if stuck:  # logic may be wrong; an open NC contact alone must still remove energy
            assert not (not s["nc_a"] and k1), s
            assert not (not s["nc_b"] and (k2 or pch or level("TEST_PERMIT_DRV", env))), s
            assert not ((not s["nc_a"] or not s["nc_b"]) and k1 and (k2 or pch)), s
        else:
            permit = all(s[k] for k in ("nc_a", "nc_b", "wd", "rail", "run", "latched"))
            assert k1 == (permit and s["k1"]), s
            assert k2 == (permit and s["k2"]), s
            assert pch == (permit and s["pch"]), s
            assert test == (permit and s["test"]), s
            assert act == (permit and s["act"] and s["k2"]), s
        checked += 1

report = erc(SHEET)
assert "Errors 0" in report, report
assert violations(report) == {"isolated_pin_label": 1}, report
assert flagged(report, "isolated_pin_label") == ["MOTOR_FEED"], "only the undrawn STAR/INA228 feed is external"
print(f"PASS: 5-page PWR hierarchy, 12 J-SIG sources, {checked} permit scenarios incl. stuck-High logic; "
      "merged ERC 0 errors, 1 external-net warning (MOTOR_FEED). Not a full board or PCB release.")
