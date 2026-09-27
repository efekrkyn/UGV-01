"""Build the PCA9615 reference and two board-interface draft sheets."""
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from build_pwr_mcu_harness import form_at

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "config/pwr_mcu_connector.json").read_text())
LIB = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
OUTPUT = ROOT / "electronics/interconnect/differential_i2c_reference.kicad_sch"
PROJECT = OUTPUT.stem
GLOBALS = set()    # nets written as KiCad global labels (PWR board hierarchy only)
EXTRA_PATH = None  # (project, path) of a board root hierarchy that also instantiates this page


def uid(key):
    return str(uuid5(NAMESPACE_URL, f"ugv-01/{PROJECT}/{key}"))


def num(value):
    return f"{value:.3f}".rstrip("0").rstrip(".")


def symbol(library, name):
    source = (LIB / f"{library}.kicad_sym").read_text()
    start = source.index(f'(symbol "{name}"')
    return form_at(source, start).replace(f'(symbol "{name}"', f'(symbol "{library}:{name}"', 1)


def instance(ref, library, name, value, x, y, pin_count, footprint="", board=True):
    pins = "\n".join(f'    (pin "{n}" (uuid "{uid(f"{ref}/{n}")}"))' for n in range(1, pin_count + 1))
    reference_y = y - (25.4 if name == "PCA9615DP" else 20.32 if name == "Conn_01x12" else 10.16 if name == "Conn_01x04" else 2.54)
    value_y = y - (22.86 if name == "PCA9615DP" else -20.32 if name == "Conn_01x12" else -10.16 if name == "Conn_01x04" else 0)
    return f'''  (symbol
    (lib_id "{library}:{name}") (at {num(x)} {num(y)} 0) (unit 1)
    (exclude_from_sim no) (in_bom {'yes' if board else 'no'})
    (on_board {'yes' if board else 'no'}) (dnp no) (uuid "{uid(ref)}")
    (property "Reference" "{ref}" (at {num(x+20.32 if name == 'PCA9615DP' else x+3)} {num(reference_y)} 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "{value}" (at {num(x+20.32 if name == 'PCA9615DP' else x+3)} {num(value_y)} 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "{footprint}" (at {num(x)} {num(y)} 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
{pins}
    (instances (project "{PROJECT}" (path "/{uid('root')}"
      (reference "{ref}") (unit 1))){extra_path(ref)})
  )'''


def extra_path(ref):
    if not EXTRA_PATH:
        return ""
    project, path = EXTRA_PATH
    return f'\n      (project "{project}" (path "{path}" (reference "{ref}") (unit 1)))'


def global_label(uid_value, x, y, net, angle=0):
    justify = "left" if angle in (0, 90) else "right"
    return (f'  (global_label "{net}" (shape passive) (at {num(x)} {num(y)} {angle})\n'
            f'    (effects (font (size 1 1)) (justify {justify})) (uuid "{uid_value}"))')


def wire_label(key, x, y, net, dx=0, dy=-2.54):
    ex, ey = x + dx, y + dy
    wire = f'''  (wire (pts (xy {num(x)} {num(y)}) (xy {num(ex)} {num(ey)}))
    (stroke (width 0) (type default)) (uuid "{uid(f"{key}/wire")}"))'''
    if net in GLOBALS:
        return wire + "\n" + global_label(uid(f"{key}/label"), ex, ey, net, 180 if dx < 0 else 0)
    return wire + f'''
  (label "{net}" (at {num(ex)} {num(ey)} 0)
    (effects (font (size 1 1)) (justify {'right' if dx < 0 else 'left'} bottom))
    (uuid "{uid(f"{key}/label")}"))'''


def text_note(key, value, x, y, size=1.27):
    return f'''  (text "{value}" (exclude_from_sim no) (at {num(x)} {num(y)} 0)
    (effects (font (size {num(size)} {num(size)}))) (uuid "{uid(key)}"))'''


def build(output, sides, board=False, ref_base=0):
    global OUTPUT, PROJECT
    OUTPUT, PROJECT = output, output.stem
    symbols = [("Interface", "PCA9615DP"), ("Device", "R"), ("Device", "C"), ("power", "PWR_FLAG")]
    if board:
        symbols += [("Connector_Generic", "Conn_01x12"), ("Connector_Generic", "Conn_01x04")]
    libs = "\n".join(symbol(lib, name) for lib, name in symbols)
    items = []
    rail_flags = 0
    resistor_no = 0
    cap_no = 0
    for side, offset, chip in sides:
        cx, cy = 88.9 + offset, 60.96
        base = 25.4 + offset
        rail_5v = "5V_CONTROL" if board else f"{side}_5V"
        ground = "PGND" if board else f"{side}_GND"
        items.append(text_note(f"heading/{side}", f"{side} board - local PCA9615", cx, 27.94, 2))
        items.append(instance(chip, "Interface", "PCA9615DP", "PCA9615DP", cx, cy, 10,
                              "Package_SO:TSSOP-10_3x3mm_P0.5mm"))
        chip_nets = {
            1: (cx-2.54, cy-10.16, f"{side}_3V3", -12.7, 0),
            2: (cx-12.7, cy, f"{side}_I2C_SDA", -2.54, 0),
            3: (cx-12.7, cy-5.08, f"{side}_PGOOD", -2.54, 0),
            4: (cx-12.7, cy+5.08, f"{side}_I2C_SCL", -2.54, 0),
            5: (cx, cy+10.16, ground, 0, 2.54),
            6: (cx+12.7, cy+5.08, "DI2C_SCL_N", 2.54, 0),
            7: (cx+12.7, cy+2.54, "DI2C_SCL_P", 2.54, 0),
            8: (cx+12.7, cy-5.08, "DI2C_SDA_P", 2.54, 0),
            9: (cx+12.7, cy-2.54, "DI2C_SDA_N", 2.54, 0),
            10: (cx, cy-10.16, rail_5v, 0, -5.08),
        }
        for pin, (x, y, net, dx, dy) in chip_nets.items():
            items.append(wire_label(f"{chip}/{pin}", x, y, net, dx, dy))

        def resistor(x, y, value, top, bottom):
            nonlocal resistor_no
            resistor_no += 1
            ref = f"R{ref_base + resistor_no}"
            items.append(instance(ref, "Device", "R", value, x, y, 2, "Resistor_SMD:R_0603_1608Metric"))
            items.append(wire_label(f"{ref}/1", x, y-3.81, top))
            items.append(wire_label(f"{ref}/2", x, y+3.81, bottom, 0, 2.54))

        for line, y in (("SCL", 121.92), ("SDA", 162.56)):
            plus, minus = f"DI2C_{line}_P", f"DI2C_{line}_N"
            resistor(base, y, "600R", rail_5v, plus)
            resistor(base+30.48, y, "120R", plus, minus)
            resistor(base+60.96, y, "600R", minus, ground)
        resistor(base+91.44, 121.92, "4k7", f"{side}_3V3", f"{side}_I2C_SCL")
        resistor(base+121.92, 121.92, "4k7", f"{side}_3V3", f"{side}_I2C_SDA")
        resistor(base+91.44, 162.56, "10k", f"{side}_PGOOD", ground)
        for x, rail in ((base+121.92, f"{side}_3V3"), (base+152.4, rail_5v)):
            cap_no += 1
            ref = f"C{ref_base + cap_no}"
            items.append(instance(ref, "Device", "C", "100n", x, 162.56, 2, "Capacitor_SMD:C_0603_1608Metric"))
            items.append(wire_label(f"{ref}/1", x, 162.56-3.81, rail))
            items.append(wire_label(f"{ref}/2", x, 162.56+3.81, ground, 0, 2.54))

        for n, net in enumerate((f"{side}_3V3", rail_5v, ground)):
            rail_flags += 1
            x = base + 30.48*n
            ref = f"#FLG{ref_base + rail_flags:02d}"
            items.append(instance(ref, "power", "PWR_FLAG", "PWR_FLAG", x, 205.74, 1, board=False))
            items.append(wire_label(f"{ref}/1", x, 205.74, net, 2.54, 0))
        if board:
            for ref, name, y, rows, footprint, value in (
                (f"J{ref_base + 1}", "Conn_01x12", 60.96, CONTRACT["signal_connector"]["pins"],
                 CONTRACT["signal_connector"]["footprint"], CONTRACT["signal_connector"]["header_mpn"]),
                (f"J{ref_base + 2}", "Conn_01x04", 119.38, CONTRACT["pins"],
                 CONTRACT["footprint"], CONTRACT["mpn"]),
            ):
                x = 228.6
                items.append(instance(ref, "Connector_Generic", name, value, x, y, len(rows), footprint))
                for row in rows:
                    net = "PGND" if name == "Conn_01x04" and row["net"].startswith("PGND") else row["net"]
                    py = y - (12.7 if len(rows) == 12 else 2.54) + 2.54*(row["pad"]-1)
                    items.append(wire_label(f"{ref}/{row['pad']}", x-5.08, py, net, -5.08, 0))
    if board:
        items.append(text_note("scope", "BOARD INTERFACE DRAFT: safety nets 1-8 and ACT_BUS continue on other sheets", 190, 228))
        items.append(text_note("ground", "J2 pins 2/3 join at PGND; routing/current sharing and mating CAD remain open", 190, 236))
        items.append(text_note("power", "3V3 regulator and PGOOD source are external; not a release-to-fab schematic", 190, 244))
    else:
        items.append(text_note("scope", "REFERENCE ONLY: J-SIG pins 9-12 use the four DI2C nets; other safety pins omitted", 190, 228))
        items.append(text_note("ground", "MCU_GND and PWR_GND meet only through J-PWR; no galvanic isolation", 190, 236))
        items.append(text_note("power", "MCU_PGOOD / PWR_PGOOD sources and board regulators are external to this sheet", 190, 244))
    OUTPUT.write_text(f'''(kicad_sch
  (version 20250114) (generator "eeschema") (generator_version "10.0")
  (uuid "{uid('root')}") (paper "A3")
  (title_block (title "UGV-01 {'board interface draft' if board else 'differential I2C reference'}") (date "2026-09-23") (rev "P1")
    (comment 1 "{'Partial interface sheet; not a production board schematic' if board else 'Reference circuit only; not production board schematics'}"))
  (lib_symbols
{libs}
  )
{"\n".join(items)}
  (sheet_instances (path "/" (page "1")))
  (embedded_fonts no)
)\n''')
    print(OUTPUT)


def main():
    global GLOBALS, EXTRA_PATH
    build(ROOT / "electronics/interconnect/differential_i2c_reference.kicad_sch",
          (("MCU", 0, "U1"), ("PWR", 213.36, "U2")))
    build(ROOT / "electronics/ugv_mcu_01/pwr_mcu_interface.kicad_sch", (("MCU", 0, "U1"),), board=True)
    # PWR copy joins the ugv_pwr_01 hierarchy: global labels, 5xx refs, second instance path.
    from pwr_sheet import BOARD, GLOBAL_NETS, board_path
    GLOBALS, EXTRA_PATH = GLOBAL_NETS, (BOARD, board_path("pwr_mcu_interface"))
    build(ROOT / "electronics/ugv_pwr_01/pwr_mcu_interface.kicad_sch", (("PWR", 0, "U501"),),
          board=True, ref_base=500)
    GLOBALS, EXTRA_PATH = set(), None


if __name__ == "__main__":
    main()
