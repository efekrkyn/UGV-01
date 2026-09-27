"""Check the PCA9615 reference sheet against the PWR-MCU cable contract."""
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCHEMATIC = ROOT / "electronics/interconnect/differential_i2c_reference.kicad_sch"
CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
contract = json.loads((ROOT / "config/pwr_mcu_connector.json").read_text())
assert SCHEMATIC.exists(), "Differential I2C reference schematic missing"

with tempfile.TemporaryDirectory() as tmp:
    xml = Path(tmp) / "link.xml"
    erc = Path(tmp) / "erc.txt"
    subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(xml), str(SCHEMATIC)], check=True)
    root = ET.parse(xml).getroot()
    components = {c.attrib["ref"]: c.findtext("value") for c in root.findall("./components/comp")}
    assert components["U1"] == components["U2"] == "PCA9615DP"
    nets = {
        n.attrib["name"].removeprefix("/"): {(node.attrib["ref"], node.attrib["pin"]) for node in n.findall("node")}
        for n in root.findall("./nets/net")
    }
    pin_net = {pin: name for name, nodes in nets.items() for pin in nodes}
    for pin, net in {"6": "DI2C_SCL_N", "7": "DI2C_SCL_P", "8": "DI2C_SDA_P", "9": "DI2C_SDA_N"}.items():
        assert {("U1", pin), ("U2", pin)} <= nets[net]
    assert [p["net"] for p in contract["signal_connector"]["pins"][8:]] == [
        "DI2C_SCL_P", "DI2C_SCL_N", "DI2C_SDA_P", "DI2C_SDA_N",
    ]
    for ref, prefix in (("U1", "MCU"), ("U2", "PWR")):
        for pin, net in {"1": "3V3", "2": "I2C_SDA", "3": "PGOOD", "4": "I2C_SCL", "5": "GND", "10": "5V"}.items():
            assert (ref, pin) in nets[f"{prefix}_{net}"]
    for side, start in (("MCU", 1), ("PWR", 10)):
        expected = []
        for line in ("SCL", "SDA"):
            plus, minus = f"DI2C_{line}_P", f"DI2C_{line}_N"
            expected += [("600R", f"{side}_5V", plus), ("120R", plus, minus),
                         ("600R", minus, f"{side}_GND")]
        expected += [("4k7", f"{side}_3V3", f"{side}_I2C_SCL"),
                     ("4k7", f"{side}_3V3", f"{side}_I2C_SDA"),
                     ("10k", f"{side}_PGOOD", f"{side}_GND")]
        for number, (value, upper, lower) in enumerate(expected, start):
            ref = f"R{number}"
            assert components[ref] == value
            assert (pin_net[(ref, "1")], pin_net[(ref, "2")]) == (upper, lower)
    subprocess.run([CLI, "sch", "erc", "--exit-code-violations", "-o", str(erc), str(SCHEMATIC)], check=True)
print("PASS: two PCA9615s, four differential lines, local rails and ERC clean")
