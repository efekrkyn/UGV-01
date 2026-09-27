"""Generate a conditional LM74900-Q1 K2 reference circuit for KiCad 10."""
from pathlib import Path

import build_differential_i2c_reference as sch
from pwr_sheet import BOARD, GLOBAL_NETS, LOCAL, board_path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electronics/ugv_pwr_01/k2_reference.kicad_sch"
sch.OUTPUT, sch.PROJECT = OUT, OUT.stem
sch.GLOBALS, sch.EXTRA_PATH = GLOBAL_NETS, (BOARD, board_path("k2_reference"))
UX, UY = 243.84, 111.76
FET_Y = 81.28

PINS = [
    "DGATE", "A", "SW", "UVLO", "OV", "EN", "SLEEP", "NC", "TMR", "IMON", "ILIM", "FLT",
    "GND", "HGATE", "OUT", "SLEEP_OV", "NC", "ISCP", "CS-", "CS+", "NC", "VS", "CAP", "C",
]


def controller_symbol():
    pins = []
    for index, name in enumerate(PINS, 1):
        left = index <= 12
        x = -35.56 if left else 35.56
        y = 27.94 - ((index - 1) % 12) * 5.08
        direction = 0 if left else 180
        kind = "no_connect" if name == "NC" else "power_in" if name == "GND" else "passive"
        pins.append(f'''      (pin {kind} line (at {sch.num(x)} {sch.num(y)} {direction}) (length 5.08)
        (name "{name}" (effects (font (size 1.27 1.27))))
        (number "{index}" (effects (font (size 1.27 1.27)))))''')
    pins.append('''      (pin passive line (at 0 -40.64 90) (length 5.08)
        (name "RTN" (effects (font (size 1.27 1.27))))
        (number "25" (effects (font (size 1.27 1.27)))))''')
    return f'''    (symbol "UGV:LM74900QRGERQ1"
      (property "Reference" "U" (at 0 0 0) (effects (font (size 1.27 1.27))))
      (property "Value" "LM74900QRGERQ1" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_DFN_QFN:Texas_RGE0024C_VQFN-24-1EP_4x4mm_P0.5mm_EP2.1x2.1mm"
        (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet" "https://www.ti.com/lit/ds/symlink/lm74900-q1.pdf"
        (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "LM74900QRGERQ1_0_1"
        (rectangle (start -30.48 30.48) (end 30.48 -35.56)
          (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "LM74900QRGERQ1_1_1"
{chr(10).join(pins)}
      ))'''


def fet_symbol():
    parent = sch.symbol("Transistor_FET", "Q_NMOS_SSSGD_AvalancheRated")
    parent = parent.replace("Q_NMOS_SSSGD_AvalancheRated", "CSD18540Q5BT")
    parent = parent.replace('"Transistor_FET:CSD18540Q5BT"', '"UGV:CSD18540Q5BT"', 1)
    parent = parent.replace('(property "Footprint" ""',
                            '(property "Footprint" "Package_TO_SOT_SMD:TDSON-8-1"')
    return parent


items = [sch.instance("U1", "UGV", "LM74900QRGERQ1", "LM74900QRGERQ1", UX, UY, 25,
                      "Package_DFN_QFN:Texas_RGE0024C_VQFN-24-1EP_4x4mm_P0.5mm_EP2.1x2.1mm")]
for pin, name in enumerate(PINS, 1):
    if name == "NC" or pin == 16:
        x = UX + (-35.56 if pin <= 12 else 35.56)
        y = UY - (27.94 - ((pin - 1) % 12) * 5.08)
        items.append(f'  (no_connect (at {sch.num(x)} {sch.num(y)}) (uuid "{sch.uid(f"U1/{pin}/nc")}"))')
        continue
    nets = {
        1: "DGATE", 2: "MID", 3: "K2_SW", 4: "K2_UVLO", 5: "K2_OV",
        6: "SAFE_EN", 7: "SAFE_EN", 9: "K2_TMR", 10: "K2_IMON", 11: "K2_ILIM",
        12: "K2_FLT", 13: "PGND", 14: "HGATE", 15: "ACT_BUS",
        18: "K2_DRAIN_A", 19: "K2_SENSE_N", 20: "CS_PLUS",
        22: "K2_DRAIN_A", 23: "K2_CAP", 24: "K2_DRAIN_A",
    }
    x = UX + (-35.56 if pin <= 12 else 35.56)
    y = UY - (27.94 - ((pin - 1) % 12) * 5.08)
    items.append(sch.wire_label(f"U1/{pin}", x, y, nets[pin], -5.08 if pin <= 12 else 5.08, 0))
items.append(f'  (no_connect (at {sch.num(UX)} {sch.num(UY+40.64)}) (uuid "{sch.uid("U1/25/nc")}"))')

for ref, x, drain, source, gate in (
    ("Q1", 71.12, "K2_DRAIN_A", "MID", "DGATE"),
    ("Q2", 152.4, "K2_DRAIN_B", "ACT_BUS", "HGATE"),
):
    items.append(sch.instance(ref, "UGV", "CSD18540Q5BT", "CSD18540Q5BT",
                              x, FET_Y, 5, "Package_TO_SOT_SMD:TDSON-8-1"))
    items.append(sch.wire_label(f"{ref}/D", x+2.54, FET_Y-5.08, drain, 0, -2.54))
    items.append(sch.wire_label(f"{ref}/S", x+2.54, FET_Y+5.08, source, 0, 2.54))
    items.append(sch.wire_label(f"{ref}/G", x-5.08, FET_Y, gate, -2.54, 0))

items.append(sch.instance("R1", "Device", "R_Shunt", "1m 1% Kelvin", 111.76, FET_Y, 4))
for pin, x, y, net, dx, dy in (
    (1, 111.76, FET_Y-5.08, "K2_DRAIN_A", 0, -2.54),
    (2, 114.3, FET_Y-2.54, "K2_SENSE_P", 2.54, 0),
    (3, 114.3, FET_Y+2.54, "K2_SENSE_N", 2.54, 0),
    (4, 111.76, FET_Y+5.08, "K2_DRAIN_B", 0, 2.54),
):
    items.append(sch.wire_label(f"R1/{pin}", x, y, net, dx, dy))


def two_pin(ref, kind, value, x, y, top, bottom, footprint=""):
    items.append(sch.instance(ref, "Device", kind, value, x, y, 2, footprint))
    items.append(sch.wire_label(f"{ref}/1", x, y-3.81, top, 0, -2.54))
    items.append(sch.wire_label(f"{ref}/2", x, y+3.81, bottom, 0, 2.54))


resistors = [
    ("R2", "49R9", "K2_SENSE_P", "CS_PLUS"),
    ("R3", "31k6", "K2_ILIM", "PGND"),
    ("R4", "100k", "K2_TMR", "PGND"),
    ("R5", "10k", "SAFE_EN", "PGND"),
    ("R6", "10k", "PWR_3V3", "K2_FLT"),
    ("R7", "5k6", "K2_IMON", "PGND"),
    ("R8", "200k", "K2_SW", "K2_UVLO"),
    ("R9", "10k", "K2_UVLO", "PGND"),
    ("R10", "300k", "K2_SW", "K2_OV"),
    ("R11", "10k", "K2_OV", "PGND"),
]
for index, (ref, value, top, bottom) in enumerate(resistors):
    two_pin(ref, "R", value, 30.48+index*30.48, 195.58, top, bottom, "Resistor_SMD:R_0603_1608Metric")

capacitors = [
    ("C1", "68n", "K2_TMR", "PGND"),
    ("C2", "100n", "K2_CAP", "K2_DRAIN_A"),
    ("C3", "100n", "K2_DRAIN_A", "PGND"),
    ("C4", "10n", "CS_PLUS", "K2_SENSE_N"),
    ("C5", "100n", "MID", "PGND"),
    ("C6", "4700u 25V", "ACT_BUS", "PGND"),
]
for index, (ref, value, top, bottom) in enumerate(capacitors):
    two_pin(ref, "C", value, 45.72+index*48.26, 233.68, top, bottom)

# PGND is flagged once, on pwr_mcu_interface (board entry); a second PWR_FLAG conflicts in the merged ERC.

items.extend([
    sch.text_note("title", "K2 dual-FET separator - reference circuit, NOT for fabrication", 205, 28, 2),
    sch.text_note("scope", "K1/precharge/bleed/test: actuator_path; SAFE_EN driver: safety_gate; K2_FLT/IMON: arming_io. Clamp/TVS, FLT latch input, shunt MPN OPEN", 205, 260),
    sch.text_note("pad", "U1 pad 25: solder to isolated copper island; NO PGND connection (TI Rev C, Table 5-1)", 205, 267),
    sch.text_note("power", "MID -> Q1 -> R1 Kelvin shunt -> Q2 -> ACT_BUS; power nets are labels, not wire-width proof", 205, 274),
])

libraries = "\n".join((controller_symbol(), fet_symbol(), sch.symbol("Device", "R_Shunt"),
                       sch.symbol("Device", "R"), sch.symbol("Device", "C")))
(OUT.parent / "UGV.kicad_sym").write_text(
    '(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor")\n'
    + controller_symbol().replace('"UGV:LM74900QRGERQ1"', '"LM74900QRGERQ1"', 1)
    + '\n' + fet_symbol().replace('"UGV:CSD18540Q5BT"', '"CSD18540Q5BT"', 1)
    + ''.join('\n' + text.replace(f'"UGV:{name}"', f'"{name}"', 1) for name, text in LOCAL.items()) + '\n)\n'
)
(OUT.parent / "sym-lib-table").write_text(
    '(sym_lib_table (lib (name "UGV") (type "KiCad") '
    '(uri "${KIPRJMOD}/UGV.kicad_sym") (options "") (descr "UGV-01 PWR symbols")))\n'
)
OUT.write_text(f'''(kicad_sch
  (version 20250114) (generator "eeschema") (generator_version "10.0")
  (uuid "{sch.uid('root')}") (paper "A3")
  (title_block (title "UGV-PWR-01 K2 reference") (date "2026-09-24") (rev "P0")
    (comment 1 "Conditional circuit only; no PWR board or safety release"))
  (lib_symbols
{libraries}
  )
{chr(10).join(items)}
  (sheet_instances (path "/" (page "1")))
  (embedded_fonts no)
)\n''')
print(OUT)
