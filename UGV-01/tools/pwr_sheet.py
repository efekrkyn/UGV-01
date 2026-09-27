"""Pin-accurate KiCad 10 page writer shared by the UGV-PWR-01 safety-path sheets.

Every symbol pin gets a short wire and a net label, so the drawing is a labelled
netlist rather than a routed diagram. Pages carry two instance paths: their own
(standalone ERC/netlist) and the ugv_pwr_01 root hierarchy (merged ERC).
"""
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from build_differential_i2c_reference import LIB, global_label, num
from build_pwr_mcu_harness import form_at

ROOT = Path(__file__).resolve().parents[1]
BOARD_DIR = ROOT / "electronics/ugv_pwr_01"
BOARD = "ugv_pwr_01"
CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
ROOT_UUID = str(uuid5(NAMESPACE_URL, f"ugv-01/{BOARD}/root"))
PAGES = ("pwr_mcu_interface", "k2_reference", "actuator_path", "safety_gate", "arming_io")

# Nets that cross PWR pages. Everything else stays a page-local label.
GLOBAL_NETS = {
    "PGND", "PWR_3V3", "5V_CONTROL", "MOTOR_FEED", "F1_OUT", "MID", "ACT_BUS",
    "SAFE_EN", "K2_FLT", "K2_IMON", "ESTOP_A_5V", "ESTOP_B_5V",
    "K1_DRV", "PCH_DRV", "TEST_PERMIT_DRV", "PWR_ACT_EN", "LATCH_OK",
    "TEST_CMD", "PRECHARGE_CMD", "BLEED_CMD", "K1_CMD", "K2_CMD", "ACT_ENABLE_REQ",
    "F1_SENSE", "MID_SENSE", "ACT_SENSE", "F1_CMP", "MID_CMP",
    "PWR_I2C_SCL", "PWR_I2C_SDA", "PWR_PGOOD",
    "MCU_RUN_REQ", "MCU_WDI", "PWR_K1_FB", "PWR_K2_FB",
    "ESTOP_A_CLOSED", "ESTOP_B_CLOSED", "PWR_WD_OK",
    "DI2C_SCL_P", "DI2C_SCL_N", "DI2C_SDA_P", "DI2C_SDA_N",
}


def sheet_uuid(page, board=BOARD):
    return str(uuid5(NAMESPACE_URL, f"ugv-01/{board}/sheet/{page}"))


def board_path(page, board=BOARD):
    root = str(uuid5(NAMESPACE_URL, f"ugv-01/{board}/root"))
    return f"/{root}/{sheet_uuid(page, board)}"


def _property(body, name):
    start = body.find(f'(property "{name}"')
    return form_at(body, start) if start >= 0 else None


def lib_symbol(lib, name, source=None, prefix=True):
    """Library symbol text; `extends` children are flattened onto the parent body."""
    source = source or (LIB / f"{lib}.kicad_sym").read_text()
    body = form_at(source, source.index(f'(symbol "{name}"'))
    parent = re.search(r'\(extends "([^"]+)"\)', body)
    if parent:
        base = lib_symbol(lib, parent.group(1), source, prefix=False)
        base = base.replace(f'(symbol "{parent.group(1)}', f'(symbol "{name}')
        for prop in re.findall(r'\(property "([^"]+)"', body):
            old, new = _property(base, prop), _property(body, prop)
            base = base.replace(old, new) if old else base.replace("\n", f"\n    {new}\n", 1)
        body = base
    return body.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1) if prefix else body


def pin_table(text):
    """{unit: [(number, x, y, angle)]}; unit 0 pins belong to every unit."""
    units = {}
    for sub in re.finditer(r'\(symbol "[^"]*_(\d+)_\d+"', text):
        body = form_at(text, sub.start())
        for pin in re.finditer(r"\(pin ", body):
            form = form_at(body, pin.start())
            x, y, angle = re.search(r"\(at ([-\d.]+) ([-\d.]+) (\d+)\)", form).groups()
            number = re.search(r'\(number "([^"]*)"', form).group(1)
            units.setdefault(int(sub.group(1)), []).append((number, float(x), float(y), int(angle)))
    return units


class Page:
    def __init__(self, name, title, paper="A3", board=BOARD, board_dir=BOARD_DIR, globals_=GLOBAL_NETS):
        self.name, self.title, self.paper = name, title, paper
        self.board, self.board_dir, self.globals = board, board_dir, globals_
        self.items, self.symbols = [], {}

    def uid(self, key):
        return str(uuid5(NAMESPACE_URL, f"ugv-01/{self.name}/{key}"))

    def label(self, key, x, y, net, angle):
        """Wire-end label; global for cross-page nets."""
        uid = self.uid(f"{key}/label")
        if net in self.globals:
            return global_label(uid, x, y, net, angle)
        justify = "left bottom" if angle in (0, 90) else "right bottom"
        return (f'  (label "{net}" (at {num(x)} {num(y)} {angle})\n'
                f'    (effects (font (size 1 1)) (justify {justify})) (uuid "{uid}"))')

    def stub(self, key, x, y, net, angle):
        """Wire from a pin end away from the body, then a label. `angle` is the pin's own angle."""
        dx, dy, text_angle = {0: (-2.54, 0, 180), 180: (2.54, 0, 0),
                              90: (0, 2.54, 270), 270: (0, -2.54, 90)}[angle]
        self.items.append(
            f'  (wire (pts (xy {num(x)} {num(y)}) (xy {num(x+dx)} {num(y+dy)}))\n'
            f'    (stroke (width 0) (type default)) (uuid "{self.uid(f"{key}/wire")}"))')
        self.items.append(self.label(key, x + dx, y + dy, net, text_angle))

    def part(self, ref, lib_id, value, x, y, nets, footprint="", unit=1, board=True, extra=None):
        """Place one symbol unit; `nets` maps every pin number to a net name or None (no-connect)."""
        lib, name = lib_id.split(":")
        if lib_id not in self.symbols:
            self.symbols[lib_id] = LOCAL[name] if lib == "UGV" else lib_symbol(lib, name)
        table = pin_table(self.symbols[lib_id])
        pins = table.get(unit, []) + table.get(0, [])
        numbers = {p[0] for p in pins}
        assert set(nets) == numbers, (ref, sorted(numbers ^ set(nets)))
        fields = "".join(
            f'\n    (property "{k}" "{v}" (at {num(x)} {num(y)} 0)\n'
            f'      (effects (font (size 1.27 1.27)) (hide yes)))' for k, v in (extra or {}).items())
        pin_uuids = "\n".join(f'    (pin "{n}" (uuid "{self.uid(f"{ref}/{unit}/{n}")}"))'
                              for n in sorted(numbers))
        paths = (f'(project "{self.name}" (path "/{self.uid("root")}" (reference "{ref}") (unit {unit})))\n'
                 f'      (project "{self.board}" (path "{board_path(self.name, self.board)}" (reference "{ref}") (unit {unit})))')
        flag = "yes" if board else "no"
        self.items.append(f'''  (symbol (lib_id "{lib_id}") (at {num(x)} {num(y)} 0) (unit {unit})
    (exclude_from_sim no) (in_bom {flag}) (on_board {flag}) (dnp no) (uuid "{self.uid(f"{ref}/{unit}")}")
    (property "Reference" "{ref}" (at {num(x+2.54)} {num(y-3.81)} 0)
      (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "{value}" (at {num(x+2.54)} {num(y+3.81)} 0)
      (effects (font (size 1 1)) (justify left)))
    (property "Footprint" "{footprint}" (at {num(x)} {num(y)} 0)
      (effects (font (size 1.27 1.27)) (hide yes))){fields}
{pin_uuids}
    (instances {paths}))''')
        for number, px, py, angle in pins:
            ex, ey = x + px, y - py  # symbol y axis points up, schematic y points down
            if nets[number] is None:
                self.items.append(f'  (no_connect (at {num(ex)} {num(ey)}) (uuid "{self.uid(f"{ref}/{unit}/{number}/nc")}"))')
            else:
                self.stub(f"{ref}/{unit}/{number}", ex, ey, nets[number], angle)

    def two(self, ref, kind, value, x, y, top, bottom, footprint=""):
        """Vertical two-pin part (R, C, fuse, TVS...); pin 1 on top."""
        self.part(ref, kind if ":" in kind else f"Device:{kind}", value, x, y,
                  {"1": top, "2": bottom}, footprint)

    def flag(self, index, x, y, net):
        self.part(f"#FLG{index}", "power:PWR_FLAG", "PWR_FLAG", x, y, {"1": net}, board=False)

    def note(self, key, text, x, y, size=1.27):
        self.items.append(f'  (text "{text}" (exclude_from_sim no) (at {num(x)} {num(y)} 0)\n'
                          f'    (effects (font (size {num(size)} {num(size)})) (justify left)) (uuid "{self.uid(key)}"))')

    def write(self, comment):
        path = self.board_dir / f"{self.name}.kicad_sch"
        path.write_text(f'''(kicad_sch
  (version 20250114) (generator "eeschema") (generator_version "10.0")
  (uuid "{self.uid('root')}") (paper "{self.paper}")
  (title_block (title "{self.title}") (date "2026-09-24") (rev "P0")
    (comment 1 "{comment}"))
  (lib_symbols
{chr(10).join(self.symbols.values())}
  )
{chr(10).join(self.items)}
  (sheet_instances (path "/" (page "1")))
  (embedded_fonts no)
)
''')
        return path


def _tps3431():
    """TI TPS3431 DRB VSON-8 (SNVSB66A Table 5-1); pad 9 is the GND-connected thermal pad."""
    left = [("1", "VDD", "power_in"), ("2", "CWD", "passive"), ("3", "EN", "input"), ("5", "SET1", "input")]
    right = [("6", "WDI", "input"), ("7", "WDO", "open_collector"), ("8", "ENOUT", "open_collector")]
    pins = [(n, nm, t, -12.7, 5.08 - 2.54 * i, 0) for i, (n, nm, t) in enumerate(left)]
    pins += [(n, nm, t, 12.7, 5.08 - 2.54 * i, 180) for i, (n, nm, t) in enumerate(right)]
    pins += [("4", "GND", "power_in", 0, -10.16, 90), ("9", "EP", "passive", 2.54, -10.16, 90)]
    body = "\n".join(
        f'''      (pin {t} line (at {num(x)} {num(y)} {a}) (length 2.54)
        (name "{nm}" (effects (font (size 1.27 1.27)))) (number "{n}" (effects (font (size 1.27 1.27)))))'''
        for n, nm, t, x, y, a in pins)
    return f'''    (symbol "UGV:TPS3431SDRB"
      (property "Reference" "U" (at 0 8.89 0) (effects (font (size 1.27 1.27))))
      (property "Value" "TPS3431SDRBR" (at 0 -13.97 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SON:VSON-8-1EP_3x3mm_P0.65mm_EP1.65x2.4mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet" "https://www.ti.com/lit/ds/symlink/tps3431.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "TPS3431SDRB_0_1"
        (rectangle (start -10.16 7.62) (end 10.16 -7.62) (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "TPS3431SDRB_1_1"
{body}
      ))'''


LOCAL = {"TPS3431SDRB": _tps3431()}


def netlist(sheet):
    """(values, nets, footprints) from kicad-cli; net names without the leading '/'."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "net.xml"
        subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(out), str(sheet)],
                       check=True, capture_output=True)
        root = ET.parse(out).getroot()
    comps = root.findall("./components/comp")
    values = {c.attrib["ref"]: c.findtext("value") for c in comps}
    footprints = {c.attrib["ref"]: c.findtext("footprint") or "" for c in comps}
    raw = root.findall("./nets/net")
    nets = {n.attrib["name"].split("/")[-1]: {(p.attrib["ref"], p.attrib["pin"]) for p in n.findall("node")}
            for n in raw}
    assert len(nets) == len(raw), "two sheets use the same local net name"
    return values, nets, footprints


def ohms(value):
    """'8k25 0.1%' -> 8250.0, '470R >=2W' -> 470.0, '2M2' -> 2.2e6."""
    token = value.split()[0]
    for mark, scale in (("M", 1e6), ("k", 1e3), ("R", 1.0)):
        if mark in token:
            whole, frac = token.split(mark)
            return float(f"{whole or 0}.{frac or 0}") * scale
    return float(token)


def pins(nets):
    """{(ref, pin): net} inverse of a netlist."""
    return {node: name for name, nodes in nets.items() for node in nodes}


def erc(sheet):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "erc.txt"
        subprocess.run([CLI, "sch", "erc", "-o", str(out), str(sheet)], check=True, capture_output=True)
        return out.read_text()


def violations(report):
    """{check_name: count} from a kicad-cli ERC report."""
    counts = {}
    for name in re.findall(r"^\[(\w+)\]", report, re.M):
        counts[name] = counts.get(name, 0) + 1
    return counts


def _blocks(report, check):
    return re.findall(rf"^\[{check}\]:.*?(?=^\[|^\s*\*\*)", report, re.M | re.S)


def flagged(report, check):
    """Quoted names in every `check` violation block, e.g. isolated label net names."""
    return sorted(name for block in _blocks(report, check) for name in re.findall(r"'([^']+)'", block))


def flagged_nets(report, check, nets):
    """Net names of the symbol pins cited by `check` violations (e.g. power_pin_not_driven)."""
    at = pins(nets)
    return sorted({at[hit] for block in _blocks(report, check)
                   for hit in re.findall(r"Symbol (\S+) Pin (\S+)", block)})
