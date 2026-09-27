"""Generate the UGV-MCU-01 A2 servo rail, servo header and light bar partial sheet (KiCad 10).

P0 review schematic. The 6 V / 4 A servo buck (fed from ACT_BUS), the MCU itself and
the board supplies are other sheets (sub-project 5). Not for fabrication.
"""
import subprocess

from pwr_sheet import CLI, ROOT, Page

BOARD_DIR = ROOT / "electronics/ugv_mcu_01"
R0603, C0603, SOT235 = ("Resistor_SMD:R_0603_1608Metric", "Capacitor_SMD:C_0603_1608Metric",
                        "Package_TO_SOT_SMD:SOT-23-5")
HEADER = "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical"
SERVOS = ("SERVO_PAN", "SERVO_TILT", "SERVO_SHOULDER", "SERVO_GRIPPER")
# Nets that will cross MCU sheets once the board hierarchy exists.
GLOBALS = {"MCU_3V3", "PGND", "5V_CONTROL", "ACT_PERMIT_BUF", "SERVO_PWR_REQ", "SERVO_I_SENSE",
           "LIGHT_DATA", "SERVO_6V_BUCK", "SERVO_BUCK_EN", *SERVOS}

p = Page("servo_light", "UGV-MCU-01 A2 servo rail, servo headers and light bar",
         board="ugv_mcu_01", board_dir=BOARD_DIR, globals_=GLOBALS)

# Servo rail enable: PWR hardware permit AND MCU request; both default Low.
p.part("U701", "74xGxx:74LVC1G08", "74LVC1G08", 38.1, 50.8,
       {"1": "SERVO_PWR_REQ", "2": "ACT_PERMIT_BUF", "3": "PGND", "4": "SERVO_BUCK_EN", "5": "MCU_3V3"},
       SOT235)
p.two("R701", "R", "10k", 76.2, 50.8, "SERVO_PWR_REQ", "PGND", R0603)
p.two("R702", "R", "100k", 101.6, 50.8, "SERVO_BUCK_EN", "PGND", R0603)
p.two("C704", "C", "100n", 127, 50.8, "MCU_3V3", "PGND", C0603)

# Servo rail current: 10 mohm high side, INA180A2 50 V/V -> 0.5 V/A, 6.6 A at 3.3 V; RC to ADC2.
p.two("R703", "R", "0R01 1% 1W", 38.1, 101.6, "SERVO_6V_BUCK", "SERVO_6V", "Resistor_SMD:R_2512_6332Metric")
p.part("U702", "Amplifier_Current:INA180A2", "INA180A2", 76.2, 101.6,
       {"1": "SERVO_I_AMP", "2": "PGND", "3": "SERVO_6V_BUCK", "4": "SERVO_6V", "5": "MCU_3V3"},
       SOT235)
p.two("R704", "R", "1k", 114.3, 101.6, "SERVO_I_AMP", "SERVO_I_SENSE", R0603)
p.two("C701", "C", "10n", 139.7, 101.6, "SERVO_I_SENSE", "PGND", C0603)
p.two("C705", "C", "100n", 165.1, 101.6, "MCU_3V3", "PGND", C0603)

# Four servo headers (signal, +6 V, GND); 1 k limits back-feed into an unpowered servo.
for n, signal in enumerate(SERVOS):
    x = 38.1 + n * 63.5
    p.two(f"R{705 + n}", "R", "1k", x, 152.4, signal, f"{signal}_OUT", R0603)
    p.part(f"J{701 + n}", "Connector_Generic:Conn_01x03", signal.replace("_", " "), x + 38.1, 152.4,
           {"1": f"{signal}_OUT", "2": "SERVO_6V", "3": "PGND"}, HEADER)
p.two("C702", "C_Polarized", "470u 16V", 304.8, 152.4, "SERVO_6V", "PGND", "Capacitor_SMD:CP_Elec_8x10")

# Light bar: PTC keeps a shorted strip off 5V_CONTROL; 74AHCT1G125 gives 5 V data (VIH 2 V).
p.part("F701", "Device:Polyfuse", "PTC 0.2A hold", 38.1, 215.9,
       {"1": "5V_CONTROL", "2": "LIGHT_5V"}, "Fuse:Fuse_1206_3216Metric",
       extra={"Status": "SELECTION-OPEN: PTC MPN"})
p.part("U703", "74xGxx:74AHCT1G125", "74AHCT1G125", 88.9, 215.9,
       {"1": "PGND", "2": "LIGHT_DATA", "3": "PGND", "4": "LIGHT_DOUT", "5": "LIGHT_5V"}, SOT235)
p.two("R709", "R", "100k", 127, 215.9, "LIGHT_DATA", "PGND", R0603)
p.two("R710", "R", "33R", 152.4, 215.9, "LIGHT_DOUT", "LIGHT_DIN", R0603)
p.part("J705", "Connector_Generic:Conn_01x03", "LIGHT BAR", 190.5, 215.9,
       {"1": "LIGHT_5V", "2": "LIGHT_DIN", "3": "PGND"},
       "Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical")
p.two("C703", "C_Polarized", "100u 10V", 228.6, 215.9, "LIGHT_5V", "PGND", "Capacitor_SMD:CP_Elec_6.3x7.7")
p.two("C706", "C", "100n", 254, 215.9, "LIGHT_5V", "PGND", C0603)
p.flag(701, 279.4, 215.9, "LIGHT_5V")  # local rail derived through F701; never flagged elsewhere

for n, text in enumerate((
    "PARTIAL MCU sheet. 6 V/4 A servo buck (input ACT_BUS), MCU and supplies are other sheets.",
    "SERVO_BUCK_EN = SERVO_PWR_REQ AND ACT_PERMIT_BUF; both pulled Low. E-stop also removes ACT_BUS.",
    "Servo relax = rail off: digital servos may hold position without PWM pulses.",
    "INA180A2 50 V/V x 10 mohm = 0.5 V/A; 6.6 A full scale at 3.3 V; RC 1k/10n to ADC2_IN5.",
    "Firmware drives servo PWM Low before SERVO_PWR_REQ Low; 1k series limits back-feed.",
    "Light bar: 8 addressable LEDs, firmware brightness cap <=0.5 W; F701 PTC MPN open.",
)):
    p.note(f"note{n}", text, 38.1, 250 + n * 5.08)

sheet = p.write("A2 servo/light P0: servo buck and board ERC open; not a PCB release")
subprocess.run([CLI, "sch", "export", "pdf", "-o", str(sheet.with_suffix(".pdf")), str(sheet)],
               check=True, capture_output=True)
print(sheet)
