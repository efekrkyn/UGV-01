"""Netlist/ERC gate for the UGV-MCU-01 A2 servo rail, servo headers and light bar partial sheet."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from pwr_sheet import erc, flagged, flagged_nets, netlist, ohms, pins, violations  # noqa: E402

SHEET = ROOT / "electronics/ugv_mcu_01/servo_light.kicad_sch"
assert SHEET.exists(), "MCU servo/light schematic missing"
values, nets, footprints = netlist(SHEET)
at = pins(nets)


def on(ref, pin, net):
    assert at.get((ref, pin)) == net, (ref, pin, at.get((ref, pin)), net)


# Servo rail enable: hardware AND of the PWR permit and the MCU request, both default off.
assert values["U701"] == "74LVC1G08"
for pin, net in {"1": "SERVO_PWR_REQ", "2": "ACT_PERMIT_BUF", "4": "SERVO_BUCK_EN",
                 "5": "MCU_3V3", "3": "PGND"}.items():
    on("U701", pin, net)
on("R701", "1", "SERVO_PWR_REQ"); on("R701", "2", "PGND")
on("R702", "1", "SERVO_BUCK_EN"); on("R702", "2", "PGND")

# Servo rail current: 10 mohm high-side shunt, INA180A2 (50 V/V) from 3.3 V -> ADC-safe output.
assert values["U702"] == "INA180A2"
for pin, net in {"3": "SERVO_6V_BUCK", "4": "SERVO_6V", "5": "MCU_3V3", "2": "PGND",
                 "1": "SERVO_I_AMP"}.items():
    on("U702", pin, net)
on("R703", "1", "SERVO_6V_BUCK"); on("R703", "2", "SERVO_6V")
shunt, gain, adc_full_scale = ohms(values["R703"]), 50, 3.3
assert shunt == 0.01, values["R703"]
assert adc_full_scale / (gain * shunt) >= 1.5 * 4.0, "full scale must cover 1.5 x 4 A servo buck"
on("R704", "1", "SERVO_I_AMP"); on("R704", "2", "SERVO_I_SENSE")
on("C701", "1", "SERVO_I_SENSE"); on("C701", "2", "PGND")

# Four servo headers: signal via 1 k series resistor, +6 V centre pin, ground.
for n, signal in enumerate(("SERVO_PAN", "SERVO_TILT", "SERVO_SHOULDER", "SERVO_GRIPPER")):
    j, r = f"J{701 + n}", f"R{705 + n}"
    on(r, "1", signal); on(r, "2", f"{signal}_OUT")
    assert ohms(values[r]) == 1000, values[r]
    on(j, "1", f"{signal}_OUT"); on(j, "2", "SERVO_6V"); on(j, "3", "PGND")
on("C702", "1", "SERVO_6V"); on("C702", "2", "PGND")

# Light bar: PTC-isolated 5 V branch, 74AHCT1G125 3.3 V -> 5 V data, always enabled.
on("F701", "1", "5V_CONTROL"); on("F701", "2", "LIGHT_5V")
assert values["U703"] == "74AHCT1G125"
for pin, net in {"1": "PGND", "2": "LIGHT_DATA", "4": "LIGHT_DOUT", "5": "LIGHT_5V", "3": "PGND"}.items():
    on("U703", pin, net)
on("R709", "1", "LIGHT_DATA"); on("R709", "2", "PGND")
on("R710", "1", "LIGHT_DOUT"); on("R710", "2", "LIGHT_DIN")
on("J705", "1", "LIGHT_5V"); on("J705", "2", "LIGHT_DIN"); on("J705", "3", "PGND")
on("C703", "1", "LIGHT_5V"); on("C703", "2", "PGND")
for cap, rail in (("C704", "MCU_3V3"), ("C705", "MCU_3V3"), ("C706", "LIGHT_5V")):
    on(cap, "1", rail); on(cap, "2", "PGND")
for ref in values:
    if not ref.startswith("#"):
        assert footprints[ref], f"{ref} has no footprint"

# Standalone ERC: only nets driven on other MCU sheets may be reported.
report = erc(SHEET)
counts = violations(report)
assert set(counts) <= {"power_pin_not_driven", "pin_not_driven", "isolated_pin_label"}, counts
assert flagged_nets(report, "power_pin_not_driven", nets) == ["MCU_3V3", "PGND"], report
assert flagged_nets(report, "pin_not_driven", nets) == ["ACT_PERMIT_BUF"], report
assert flagged(report, "isolated_pin_label") == sorted(
    ["5V_CONTROL", "ACT_PERMIT_BUF", "SERVO_GRIPPER", "SERVO_PAN", "SERVO_SHOULDER", "SERVO_TILT"]), report
print("PASS: servo rail AND-gate enable, 6.6 A INA180 full scale, four 1 k servo headers, "
      "PTC light bar with 5 V data buffer; ERC only off-sheet drivers")
