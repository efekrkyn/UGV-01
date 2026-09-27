"""Generate the PWR↔MCU cable-only KiCad schematic from the pin contract."""
import json
import os
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "config/pwr_mcu_connector.json").read_text())
LIBRARY = Path(os.environ.get(
    "UGV_KICAD_CONNECTOR_LIBRARY",
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector_Generic.kicad_sym",
))
OUTPUT = ROOT / "electronics/interconnect/pwr_mcu_harness.kicad_sch"
PROJECT = OUTPUT.stem


def uid(key):
    return str(uuid5(NAMESPACE_URL, f"ugv-01/{PROJECT}/{key}"))


def number(value):
    return f"{value:.3f}".rstrip("0").rstrip(".")


def form_at(source, start):
    depth = 0
    quoted = False
    escaped = False
    for end in range(start, len(source)):
        char = source[end]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return source[start:end + 1]
    raise ValueError("Unbalanced KiCad symbol library")


def library_symbol(source, name):
    start = source.index(f'(symbol "{name}"')
    return form_at(source, start).replace(
        f'(symbol "{name}"', f'(symbol "Connector_Generic:{name}"', 1,
    )


def instance(reference, name, value, x, y, count):
    top = 10 if count == 4 else 20
    bottom = 10 if count == 4 else 22
    pins = "\n".join(
        f'    (pin "{pin}" (uuid "{uid(f"{reference}/pin/{pin}")}"))'
        for pin in range(1, count + 1)
    )
    return f'''  (symbol
    (lib_id "Connector_Generic:{name}")
    (at {number(x)} {number(y)} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board no)
    (dnp no)
    (uuid "{uid(reference)}")
    (property "Reference" "{reference}" (at {number(x)} {number(y-top)} 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "{value}" (at {number(x)} {number(y+bottom)} 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at {number(x)} {number(y)} 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at {number(x)} {number(y)} 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
{pins}
    (instances (project "{PROJECT}" (path "/{uid('root')}"
      (reference "{reference}") (unit 1))))
  )'''


def connection(reference, pin, net, x, y, count):
    offset = (2.54 if count == 4 else 12.7) - 2.54 * (pin - 1)
    pin_x = x - 5.08
    label_x = pin_x - 5.08
    pin_y = y - offset
    return f'''  (wire (pts (xy {number(label_x)} {number(pin_y)})
      (xy {number(pin_x)} {number(pin_y)}))
    (stroke (width 0) (type default)) (uuid "{uid(f"{reference}/wire/{pin}")}"))
  (label "{net}" (at {number(label_x)} {number(pin_y)} 0)
    (effects (font (size 1.27 1.27)) (justify right bottom))
    (uuid "{uid(f"{reference}/label/{pin}")}"))'''


def heading(value, x):
    return f'''  (text "{value}"
    (exclude_from_sim no)
    (at {number(x)} 27.94 0)
    (effects (font (size 2 2)))
    (uuid "{uid(f"heading/{value}")}"))'''


def main():
    symbol_source = LIBRARY.read_text()
    symbols = "\n".join(library_symbol(symbol_source, name) for name in ("Conn_01x04", "Conn_01x12"))
    groups = (
        ("J1", "Conn_01x04", f"Mega-Fit_{CONTRACT['housing_mpn']}", 63.5, 48.26, CONTRACT["pins"]),
        ("J2", "Conn_01x04", f"Mega-Fit_{CONTRACT['housing_mpn']}", 177.8, 48.26, CONTRACT["pins"]),
        ("J3", "Conn_01x12", f"GH_{CONTRACT['signal_connector']['housing_mpn']}", 63.5, 111.76, CONTRACT["signal_connector"]["pins"]),
        ("J4", "Conn_01x12", f"GH_{CONTRACT['signal_connector']['housing_mpn']}", 177.8, 111.76, CONTRACT["signal_connector"]["pins"]),
    )
    items = [heading("PWR board end - cable receptacles", 63.5),
             heading("MCU board end - cable receptacles", 177.8)]
    for reference, name, value, x, y, rows in groups:
        count = len(rows)
        items.append(instance(reference, name, value, x, y, count))
        items.extend(connection(reference, row["pad"], row["net"], x, y, count) for row in rows)
    body = "\n".join(items)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(f'''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "10.0")
  (uuid "{uid('root')}")
  (paper "A4")
  (title_block
    (title "UGV-01 PWR-MCU cable link")
    (date "2026-09-23") (rev "P0")
    (comment 1 "Harness continuity only; board safety circuits not shown"))
  (lib_symbols
{symbols}
  )
{body}
  (sheet_instances (path "/" (page "1")))
  (embedded_fonts no)
)\n''')
    print(OUTPUT)


if __name__ == "__main__":
    main()
