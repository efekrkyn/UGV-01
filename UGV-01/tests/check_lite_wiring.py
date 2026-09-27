"""A3 Lite module wiring: ESP32 pins match the pin map, power path, E-stop cut and sense, enables, ballast, ERC."""
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from esp32_pinmap import header_pin  # noqa: E402
from pwr_sheet import erc, netlist, ohms, pins, violations  # noqa: E402

SHEET = ROOT / "electronics/ugv_lite_01/lite_wiring.kicad_sch"
assert SHEET.exists(), "Lite wiring schematic missing"
values, nets, _ = netlist(SHEET)
at = pins(nets)
pinmap = json.loads((ROOT / "config/esp32_pinmap.json").read_text())
vehicle = json.loads((ROOT / "config/vehicle.json").read_text())
HEADER_REF = {"J1": "J101", "J3": "J103"}


def on(ref, pin, net):
    assert at.get((ref, pin)) == net, (ref, pin, at.get((ref, pin)), net)


def unconnected(node):
    """KiCad lists no-connect pins as their own `unconnected-(...)` net."""
    return at.get(node, "unconnected").startswith("unconnected")


def header(gpio):
    h, n = header_pin(pinmap, gpio).split("-")
    return HEADER_REF[h], n


# Every pin-map signal sits on its DevKitC-1 header pin; reserved pins stay unconnected.
for a in pinmap["assignments"]:
    on(*header(a["gpio"]), a["signal"])
for gpio in pinmap["unavailable"]:
    assert unconnected(header(int(gpio))), f"reserved GPIO{gpio} is wired"
for ref, pin, net in (("J101", "1", "3V3"), ("J101", "2", "3V3"), ("J101", "21", "5V_LOGIC"), ("J101", "22", "GND"),
                      ("J103", "1", "GND"), ("J103", "21", "GND"), ("J103", "22", "GND")):
    on(ref, pin, net)

# Power path: pack -> 15 A fuse (M3: two servo rails) -> main switch -> VBAT_SW -> NC E-stop -> VM_ACT (drivers + servo bucks).
on("J901", "1", "VBAT"); on("J901", "2", "GND")
on("F901", "1", "VBAT"); on("F901", "2", "VBAT_F")
assert values["F901"].startswith("15A"), values["F901"]
on("SW901", "1", "VBAT_F"); on("SW901", "2", "VBAT_SW")
on("SW902", "1", "VBAT_SW"); on("SW902", "2", "VM_ACT")
assert "E-STOP" in values["SW902"] and "NC" in values["SW902"], values["SW902"]
on("U502", "1", "VBAT_SW"); on("U502", "3", "5V_LOGIC"); on("U502", "2", "GND")  # logic stays up in E-stop
on("R931", "1", "ACT_EN"); on("R931", "2", "GND")
assert ohms(values["R931"]) == 10_000  # actuators default off through ESP32 reset/boot

# Two TB6612 modules: PWMA/PWMB tied high, speed on IN1/IN2 (MCPWM), STBY = ACT_EN, VM after the E-stop.
for module, (a, b) in {"U201": ("FL", "RL"), "U202": ("FR", "RR")}.items():
    for pin, net in {"1": "3V3", "7": "3V3", "10": "3V3", "4": "ACT_EN", "9": "VM_ACT", "8": "GND",
                     "3": f"M_{a}_IN1", "2": f"M_{a}_IN2", "5": f"M_{b}_IN1", "6": f"M_{b}_IN2"}.items():
        on(module, pin, net)
    for motor, (p1, p2) in ((a, ("12", "13")), (b, ("15", "14"))):
        ref = {"FL": "J301", "FR": "J302", "RL": "J303", "RR": "J304"}[motor]
        ballast = {"FL": "R301", "FR": "R302", "RL": "R303", "RR": "R304"}[motor]
        # R4: series ballast between driver and motor; stall current is bounded by R, not by timing.
        assert at[(module, p1)] == at[(ballast, "1")] and at[(ballast, "2")] == at[(ref, "1")], motor
        assert at[(module, p2)] == at[(ref, "2")], motor
        assert ohms(values[ballast]) == 7.5 and "10W" in values[ballast], values[ballast]
# Worst case at a full pack: charger +1 %, cold winding -10 %, ballast -5 % stays <= the TB6612 1.0 A
# recommended operating current (Toshiba TB6612FNG datasheet, Operating Range) for any duration.
motor_ohm = vehicle["motor"]["nominal_voltage_v"] / vehicle["motor"]["stall_current_a"]
stall_a = 12.6 * 1.01 / (0.9 * motor_ohm + 0.95 * 7.5)
assert stall_a <= vehicle["motor_driver"]["recommended_iout_max_a"], stall_a
for ref, motor in (("J301", "FL"), ("J302", "FR"), ("J303", "RL"), ("J304", "RR")):  # encoder on every motor
    on(ref, "3", "GND"); on(ref, "4", "3V3"); on(ref, "5", f"ENC_{motor}_A")
    assert unconnected((ref, "6")), ref  # channel B unused: direction comes from the command

# M3 (DD75): eight servos on a PCA9685 (I2C0, channel = firmware joint), /OE pulled up so the PWM is off through ESP32
# reset/boot, servo power from two E-stop-cut Mini560 rails (EN = ACT_EN), never from the module V+ terminal.
pca = pinmap["pca9685"]
for pin, net in {"1": "GND", "2": "SERVO_OE", "3": "I2C_SCL", "4": "I2C_SDA", "5": "3V3"}.items():
    on("U601", pin, net)
assert unconnected(("U601", "6")), "servo power comes from the rails, not the PCA9685 V+ terminal"
on("R401", "1", "3V3"); on("R401", "2", "SERVO_OE")
assert ohms(values["R401"]) == 10_000
for k, servo in enumerate(pca["servos"]):
    on("U602", str(k + 1), servo["signal"])
    ref = f"J{401 + k}"
    on(ref, "1", servo["signal"]); on(ref, "2", f"5V_SERVO_{servo['rail']}"); on(ref, "3", "GND")
for ref, rail, cap in (("U501", "A", "C942"), ("U503", "B", "C944")):
    on(ref, "1", "VM_ACT"); on(ref, "2", "GND"); on(ref, "3", f"5V_SERVO_{rail}"); on(ref, "4", "ACT_EN")
    on(cap, "1", f"5V_SERVO_{rail}"); on(cap, "2", "GND")

# Eyes, ToF, light bar.
for ref in ("J601", "J602"):
    on(ref, "1", "5V_LOGIC"); on(ref, "2", "GND")
for ref in ("J701", "J702"):
    on(ref, "1", "3V3"); on(ref, "2", "GND"); on(ref, "3", "I2C_SCL"); on(ref, "4", "I2C_SDA")
on("J701", "6", "TOF_XSHUT")
assert unconnected(("J702", "6"))  # second ToF re-addressed while the first is held in reset
assert values["U801"] == "74AHCT1G125"
for pin, net in {"1": "GND", "2": "LIGHT_DATA", "3": "GND", "4": "LIGHT_DOUT", "5": "5V_LOGIC"}.items():
    on("U801", pin, net)
on("R801", "1", "LIGHT_DOUT"); on("R801", "2", "LIGHT_DIN")
on("J801", "1", "5V_LOGIC"); on("J801", "2", "LIGHT_DIN"); on("J801", "3", "GND")

# R5: battery divider inside the ESP32-S3 calibrated ADC range at 12 dB (datasheet v2.2 Table 5-6:
# ATTEN3 0 ~ 2900 mV), with 0.3 V margin at worst case: charger +1 %, 1 % resistors the wrong way.
ADC_ATTEN3_MAX_V = 2.9
on("R911", "1", "VBAT_SW"); on("R911", "2", "VBAT_SENSE"); on("R912", "1", "VBAT_SENSE"); on("R912", "2", "GND")
on("C911", "1", "VBAT_SENSE"); on("C911", "2", "GND")
top, bottom = ohms(values["R911"]), ohms(values["R912"])
worst = 12.6 * 1.01 * bottom * 1.01 / (top * 0.99 + bottom * 1.01)
assert worst <= ADC_ATTEN3_MAX_V - 0.3 and 9.6 * bottom / (top + bottom) >= 1.5, worst

# R6: the E-stop has a second NC contact block that reads the button directly. Released = closed to GND
# (Low); pressed or a broken wire = open (High through the pull-up): fail-safe.
on("SW902", "1", "VBAT_SW"); on("SW902", "2", "VM_ACT")  # power contact
on("SW903", "1", "ESTOP_SW"); on("SW903", "2", "GND")
assert "E-STOP" in values["SW903"] and "NC" in values["SW903"], values["SW903"]
on("R921", "1", "3V3"); on("R921", "2", "ESTOP_SW"); assert ohms(values["R921"]) == 10_000
on("R922", "1", "ESTOP_SW"); on("R922", "2", "ESTOP_SENSE"); on("C921", "1", "ESTOP_SENSE"); on("C921", "2", "GND")
# Recheck F3: the two edges charge through different paths. Press (contact opens): C921 charges through
# pull-up + series, R921 + R922, up to VIH. Release (contact closes): C921 discharges through R922 alone
# down to VIL. ESP32-S3 datasheet v2.2 Table 5-4: VIH = 0.75 VDD, VIL = 0.25 VDD. Worst case: 1 %
# resistors high, X7R capacitor +10 %. The L4 ISR drops ACT_EN on the edge (budget 0.3 ms latency).
assert values["C921"].split()[0].endswith("n"), values["C921"]
farad = float(values["C921"].split()[0].rstrip("n")) * 1e-9
r_up, r_series, c_max = ohms(values["R921"]) * 1.01, ohms(values["R922"]) * 1.01, farad * 1.10
press_ms = (r_up + r_series) * c_max * math.log(1 / (1 - 0.75)) * 1e3  # Low -> VIH
release_ms = r_series * c_max * math.log(1 / 0.25) * 1e3               # High -> VIL
assert 1.5 < press_ms <= 1.8 and release_ms <= 0.2, (press_ms, release_ms)
assert press_ms + 0.3 <= 2.0, "E-stop press -> ACT_EN Low budget in the ISR"

report = erc(SHEET)
assert violations(report) == {}, report
print("PASS: Lite wiring matches the ESP32 pin map; fused/switched pack, NC E-stop cuts drivers and both servo rails, "
      "8 servos on the PCA9685 with /OE pulled up, "
      "2nd NC contact read directly (fail-safe; press 1.7 ms / release 0.2 ms worst to the GPIO thresholds), ACT_EN default off, 7.5 ohm ballast keeps stall "
      "<= TB6612 1.0 A, encoder on every motor, VBAT divider inside the ESP32-S3 2.9 V ADC range; ERC clean")
