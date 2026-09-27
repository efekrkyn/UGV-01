"""Generate the A3 Lite module-level wiring schematic (KiCad 10) from config/esp32_pinmap.json.

Bought modules are drawn as their header rows (pin order of the common breakouts;
verify against the purchased modules). Wiring diagram for a perfboard build, not a PCB.
"""
import json
import subprocess

from pwr_sheet import CLI, ROOT, Page

BOARD_DIR = ROOT / "electronics/ugv_lite_01"
BOARD_DIR.mkdir(parents=True, exist_ok=True)
PINMAP = json.loads((ROOT / "config/esp32_pinmap.json").read_text())
SIGNAL = {a["gpio"]: a["signal"] for a in PINMAP["assignments"]}
PCA = PINMAP["pca9685"]
C = "Connector_Generic:Conn_01x"

p = Page("lite_wiring", "UGV-01 A3 Lite module wiring", board="ugv_lite_01", board_dir=BOARD_DIR, globals_=set())


def snap(v):
    """Place on the 2.54 mm connection grid (ERC endpoint_off_grid)."""
    return round(round(v / 2.54) * 2.54, 2)


def part(ref, lib_id, value, x, y, nets, footprint=""):
    p.part(ref, lib_id, value, snap(x), snap(y), nets, footprint)


def two(ref, kind, value, x, y, top, bottom):
    p.two(ref, kind, value, snap(x), snap(y), top, bottom)


def header_net(name):
    if name == "3V3":
        return "3V3"
    if name == "5V":
        return "5V_LOGIC"
    if name == "G":
        return "GND"
    return SIGNAL.get(int(name)) if name.isdigit() else None  # RST and reserved GPIOs: not connected


for ref, header, y in (("J101", "J1", 75), ("J103", "J3", 175)):
    names = PINMAP["headers"][header]
    part(ref, f"{C}22", f"ESP32-S3-DevKitC-1 {header}", 55, y,
           {str(i + 1): header_net(n) for i, n in enumerate(names)})

# TB6612FNG breakouts: 1 PWMA 2 AIN2 3 AIN1 4 STBY 5 BIN1 6 BIN2 7 PWMB 8 GND 9 VM 10 VCC 11 GND
# 12 AO1 13 AO2 14 BO2 15 BO1 16 GND. PWMx tied high: speed is MCPWM on IN1/IN2 (drive/coast).
for ref, (a, b), y in (("U201", ("FL", "RL"), 60), ("U202", ("FR", "RR"), 120)):
    part(ref, f"{C}16", f"TB6612FNG module (A={a}, B={b})", 150, y, {
        "1": "3V3", "2": f"M_{a}_IN2", "3": f"M_{a}_IN1", "4": "ACT_EN", "5": f"M_{b}_IN1", "6": f"M_{b}_IN2",
        "7": "3V3", "8": "GND", "9": "VM_ACT", "10": "3V3", "11": "GND",
        "12": f"MOT_{a}_1", "13": f"MOT_{a}_2", "14": f"MOT_{b}_2", "15": f"MOT_{b}_1", "16": "GND"})
# Mini560 5 V / 5 A bucks: 1 IN+ 2 GND 3 OUT+ 4 EN. Two servo rails after the E-stop (M3), logic rail before it.
part("U501", f"{C}04", "Mini560 5V 5A servo rail A (EN)", 150, 160,
       {"1": "VM_ACT", "2": "GND", "3": "5V_SERVO_A", "4": "ACT_EN"})
part("U503", f"{C}04", "Mini560 5V 5A servo rail B (EN)", 150, 177.8,
       {"1": "VM_ACT", "2": "GND", "3": "5V_SERVO_B", "4": "ACT_EN"})
part("U502", f"{C}04", "Mini560 5V logic rail (EN open = on)", 150, 195,
       {"1": "VBAT_SW", "2": "GND", "3": "5V_LOGIC", "4": None})

# R4: every JGA25 has its Hall encoder (channel A to PCNT; B unused, direction comes from the command) and
# a 7.5 ohm 10 W series ballast that bounds the stall current below the TB6612 1.0 A operating limit.
for n, motor in enumerate(("FL", "FR", "RL", "RR")):
    y = 40 + 22 * n
    two(f"R{301 + n}", "R", "7R5 10W", 212, y, f"MOT_{motor}_1", f"MOTB_{motor}_1")
    part(f"J{301 + n}", f"{C}06", f"JGA25-370 {motor} + encoder", 245, y, {
        "1": f"MOTB_{motor}_1", "2": f"MOT_{motor}_2", "3": "GND", "4": "3V3",
        "5": f"ENC_{motor}_A", "6": None})

# M3: PCA9685 16-channel PWM module on I2C0 (common breakout: 1 GND 2 OE 3 SCL 4 SDA 5 VCC 6 V+; 220R series on each
# output). /OE pulled up: PWM off through ESP32 reset/boot. Servo power from the rails, never the module V+ terminal.
part("U601", f"{C}06", f"PCA9685 module logic header ({PCA['address']})", 205, 135,
       {"1": "GND", "2": "SERVO_OE", "3": "I2C_SCL", "4": "I2C_SDA", "5": "3V3", "6": None})
two("R401", "R", "10k", 190, 120, "3V3", "SERVO_OE")
part("U602", f"{C}08", "PCA9685 PWM0-7 signal pins", 205, 165,
       {str(k + 1): c["signal"] for k, c in enumerate(PCA["servos"])})
for k, c in enumerate(PCA["servos"]):
    part(f"J{401 + k}", f"{C}03", f"{c['signal'].replace('_', ' ')} (rail {c['rail']})", 262, 125 + 12.7 * k,
           {"1": c["signal"], "2": f"5V_SERVO_{c['rail']}", "3": "GND"})

for ref, side, y in (("J601", "L", 45), ("J602", "R", 60)):
    part(ref, f"{C}02", f"ESP32-CAM eye {side} power", 310, y, {"1": "5V_LOGIC", "2": "GND"})
# VL53L0X breakouts: 1 VIN 2 GND 3 SCL 4 SDA 5 GPIO1 6 XSHUT (module pull-ups on SDA/SCL/XSHUT).
for ref, side, y, xshut in (("J701", "L", 85, "TOF_XSHUT"), ("J702", "R", 115, None)):
    part(ref, f"{C}06", f"VL53L0X ToF {side}", 310, y,
           {"1": "3V3", "2": "GND", "3": "I2C_SCL", "4": "I2C_SDA", "5": None, "6": xshut})

part("U801", "74xGxx:74AHCT1G125", "74AHCT1G125", 320, 165,
       {"1": "GND", "2": "LIGHT_DATA", "3": "GND", "4": "LIGHT_DOUT", "5": "5V_LOGIC"}, "Package_TO_SOT_SMD:SOT-23-5")
two("R801", "R", "33R", 350, 165, "LIGHT_DOUT", "LIGHT_DIN")
part("J801", f"{C}03", "WS2812B x8 light bar", 385, 165, {"1": "5V_LOGIC", "2": "LIGHT_DIN", "3": "GND"})

# Power path: pack -> fuse -> main switch -> VBAT_SW -> NC E-stop -> VM_ACT.
part("J901", f"{C}02", "3S1P 18650 + BMS (P+/P-)", 40, 240, {"1": "VBAT", "2": "GND"})
part("F901", "Device:Fuse", "15A blade fuse", 70, 240, {"1": "VBAT", "2": "VBAT_F"})
part("SW901", "Switch:SW_SPST", "main switch", 100, 240, {"1": "VBAT_F", "2": "VBAT_SW"})
part("SW902", "Switch:SW_Push_Open", "E-STOP mushroom NC (power)", 140, 240, {"1": "VBAT_SW", "2": "VM_ACT"})
# R5: 100k/22k keeps a full pack (worst case 2.33 V) inside the ESP32-S3 ATTEN3 0-2.9 V calibrated range.
two("R911", "R", "100k", 180, 240, "VBAT_SW", "VBAT_SENSE")
two("R912", "R", "22k", 195, 240, "VBAT_SENSE", "GND")
two("C911", "C", "100n", 210, 240, "VBAT_SENSE", "GND")
# R6: second NC contact block on the same button reads it directly: released = Low, pressed/open wire = High.
part("SW903", "Switch:SW_Push_Open", "E-STOP 2nd NC block (sense)", 140, 262, {"1": "ESTOP_SW", "2": "GND"})
two("R921", "R", "10k", 230, 240, "3V3", "ESTOP_SW")
two("R922", "R", "1k", 245, 240, "ESTOP_SW", "ESTOP_SENSE")
two("C921", "C", "100n", 260, 240, "ESTOP_SENSE", "GND")
two("R931", "R", "10k", 280, 240, "ACT_EN", "GND")
two("C941", "C_Polarized", "470u 25V", 300, 240, "VM_ACT", "GND")
two("C942", "C_Polarized", "470u 10V", 315, 240, "5V_SERVO_A", "GND")
two("C944", "C_Polarized", "470u 10V", 287, 262, "5V_SERVO_B", "GND")
two("C943", "C_Polarized", "100u 10V", 330, 240, "5V_LOGIC", "GND")
two("C801", "C", "100n", 345, 240, "5V_LOGIC", "GND")
p.flag(901, snap(365), snap(235), "5V_LOGIC")  # rails come from bought modules drawn as passive headers
p.flag(902, snap(380), snap(235), "GND")

for n, text in enumerate((
    "A3 Lite module wiring for a perfboard build; NOT a PCB. Verify each breakout pin order before soldering.",
    "E-stop (NC) cuts both TB6612 VM and both servo buck inputs; ESP32, eyes and ToF stay powered and report.",
    "ACT_EN (10k pulldown) = TB6612 STBY x2 + both servo buck EN; PCA9685 /OE pulled up: actuators off in reset.",
    "E-stop sense = its own 2nd NC contact (fail-safe High), edge-latched; 7.5R ballast bounds motor stall < 1.0 A.",
    "Motor speed: MCPWM on IN1/IN2 with PWMA/PWMB high (drive/coast). Servo /OE High before ACT_EN Low.",
)):
    p.note(f"note{n}", text, 280, 190 + n * 5.08)

sheet = p.write("A3 Lite wiring P0 (M3): breakout pin orders, Mini560 EN level and PCA9685 header to verify")
subprocess.run([CLI, "sch", "export", "pdf", "-o", str(sheet.with_suffix(".pdf")), str(sheet)],
               check=True, capture_output=True)
print(sheet)
