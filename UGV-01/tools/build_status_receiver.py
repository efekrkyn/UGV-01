"""Generate the UGV-MCU-01 powered-off status receiver draft (KiCad 10)."""
from pathlib import Path

import build_differential_i2c_reference as sch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electronics/ugv_mcu_01/status_receiver.kicad_sch"
sch.OUTPUT, sch.PROJECT = OUT, OUT.stem

lib = sch.symbol("74xx", "74HC244")
lib = lib.replace("74HC244", "SN74LVC244APWR").replace(
    "74xx:SN74LVC244APWR", "UGV:SN74LVC244APWR"
).replace(
    "https://assets.nexperia.com/documents/data-sheet/74HC_HCT244.pdf",
    "https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf",
)
(OUT.parent / "UGV.kicad_sym").write_text(
    '(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor")\n'
    + lib.replace('"UGV:SN74LVC244APWR"', '"SN74LVC244APWR"', 1) + '\n)\n'
)
(OUT.parent / "sym-lib-table").write_text(
    '(sym_lib_table (lib (name "UGV") (type "KiCad") '
    '(uri "${KIPRJMOD}/UGV.kicad_sym") (options "") (descr "UGV-01 local symbols")))\n'
)
libs = "\n".join((lib, sch.symbol("Device", "R"), sch.symbol("power", "PWR_FLAG")))
items = [sch.instance("U1", "UGV", "SN74LVC244APWR", "SN74LVC244APWR",
                      101.6, 101.6, 20, "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm")]

inputs = [
    (2, 88.9, 88.9, "PWR_ACT_EN"),
    (4, 88.9, 91.44, "PWR_K1_FB"),
    (6, 88.9, 93.98, "PWR_K2_FB"),
    (8, 88.9, 96.52, "ESTOP_A_CLOSED"),
    (11, 88.9, 106.68, "ESTOP_B_CLOSED"),
    (13, 88.9, 104.14, "PWR_WD_OK"),
]
outputs = [
    (18, 114.3, 88.9, "ACT_PERMIT_BUF"),
    (16, 114.3, 91.44, "K1_FB_BUF"),
    (14, 114.3, 93.98, "K2_FB_BUF"),
    (12, 114.3, 96.52, "ESTOP_A_BUF"),
    (9, 114.3, 106.68, "ESTOP_B_BUF"),
    (7, 114.3, 104.14, "WD_OK_BUF"),
]
for pin, x, y, net in inputs:
    items.append(sch.wire_label(f"U1/{pin}", x, y, net, -5.08, 0))
for pin, x, y, net in outputs:
    items.append(sch.wire_label(f"U1/{pin}", x, y, net, 5.08, 0))
for pin, x, y, net in (
    (1, 88.9, 111.76, "MCU_RAILS_OK_N"),
    (19, 88.9, 114.3, "MCU_RAILS_OK_N"),
    (15, 88.9, 101.6, "PGND"),
    (17, 88.9, 99.06, "PGND"),
    (20, 101.6, 81.28, "MCU_3V3"),
    (10, 101.6, 121.92, "PGND"),
):
    items.append(sch.wire_label(f"U1/{pin}", x, y, net, -5.08 if x < 100 else 0, -2.54 if x >= 100 else 0))
for pin, x, y in ((3, 114.3, 99.06), (5, 114.3, 101.6)):
    items.append(f'  (no_connect (at {sch.num(x)} {sch.num(y)}) (uuid "{sch.uid(f"U1/{pin}/nc")}"))')

for n, (_, _, _, net) in enumerate(outputs, 1):
    x, y = 30.48 + (n - 1) * 30.48, 157.48
    ref = f"R{n}"
    items.append(sch.instance(ref, "Device", "R", "10k", x, y, 2, "Resistor_SMD:R_0603_1608Metric"))
    items.append(sch.wire_label(f"{ref}/1", x, y-3.81, net))
    items.append(sch.wire_label(f"{ref}/2", x, y+3.81, "PGND", 0, 2.54))
items.append(sch.instance("R7", "Device", "R", "10k", 30.48, 193.04, 2,
                          "Resistor_SMD:R_0603_1608Metric"))
items.append(sch.wire_label("R7/1", 30.48, 189.23, "MCU_3V3"))
items.append(sch.wire_label("R7/2", 30.48, 196.85, "MCU_RAILS_OK_N", 0, 2.54))

for n, net in enumerate(("MCU_3V3", "PGND"), 1):
    x = 60.96 + (n - 1) * 30.48
    items.append(sch.instance(f"#FLG{n:02d}", "power", "PWR_FLAG", "PWR_FLAG",
                              x, 215.9, 1, board=False))
    items.append(sch.wire_label(f"#FLG{n:02d}/1", x, 215.9, net, 2.54, 0))
items.append(sch.text_note("scope", "PARTIAL MCU receiver: PWR source, rail supervisor and nSLEEP fanout on other sheets", 170, 226))
items.append(sch.text_note("oe", "OE1/OE2: 10k pullup; MCU_RAILS_OK_N is external open-drain, defaults released", 170, 233))
items.append(sch.text_note("safety", "Ioff at VCC=0 is not brownout proof. K1/K2 and local nSLEEP pulldown stay independent.", 170, 240))

OUT.write_text(f'''(kicad_sch
  (version 20250114) (generator "eeschema") (generator_version "10.0")
  (uuid "{sch.uid('root')}") (paper "A3")
  (title_block (title "UGV-MCU-01 status receiver draft") (date "2026-09-23") (rev "P1")
    (comment 1 "Partial circuit; not a complete board or safety release"))
  (lib_symbols
{libs}
  )
{"\n".join(items)}
  (sheet_instances (path "/" (page "1")))
  (embedded_fonts no)
)\n''')
print(OUT)
