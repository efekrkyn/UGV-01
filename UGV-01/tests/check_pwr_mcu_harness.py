"""The real KiCad netlist must match the power/control link contract."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCHEMATIC = ROOT / "electronics/interconnect/pwr_mcu_harness.kicad_sch"
KICAD_CLI = os.environ.get("UGV_KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
contract = json.loads((ROOT / "config/pwr_mcu_connector.json").read_text())
assert len(contract["pins"]) == 4
assert len(contract["signal_connector"]["pins"]) == 12
assert contract["housing_mpn"] == "1700010104"
assert contract["signal_connector"]["header_mpn"] == "BM12B-GHS-TBT"
assert contract["signal_connector"]["housing_mpn"] == "GHR-12V-S"
assert contract["signal_connector"]["footprint"] == "Connector_JST:JST_GH_BM12B-GHS-TBT_1x12-1MP_P1.25mm_Vertical"
assert {row["pad"]: row["net"] for row in contract["signal_connector"]["pins"] if row["pad"] >= 9} == {
    9: "DI2C_SCL_P", 10: "DI2C_SCL_N", 11: "DI2C_SDA_P", 12: "DI2C_SDA_N",
}
assert SCHEMATIC.exists(), "KiCad harness schematic is missing"

with tempfile.TemporaryDirectory() as tmp:
    netlist = Path(tmp) / "harness.xml"
    erc = Path(tmp) / "harness_erc.txt"
    subprocess.run([KICAD_CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(netlist), str(SCHEMATIC)], check=True)
    root = ET.parse(netlist).getroot()
    nets = {
        net.attrib["name"].removeprefix("/"): {(node.attrib["ref"], int(node.attrib["pin"])) for node in net.findall("node")}
        for net in root.findall("./nets/net")
    }
    assert len(nets) == 16, nets
    for row in contract["pins"]:
        assert nets[row["net"]] == {("J1", row["pad"]), ("J2", row["pad"])}, row
    for row in contract["signal_connector"]["pins"]:
        assert nets[row["net"]] == {("J3", row["pad"]), ("J4", row["pad"])}, row
    subprocess.run([KICAD_CLI, "sch", "erc", "--exit-code-violations", "-o", str(erc), str(SCHEMATIC)], check=True)
print("PASS: 16 KiCad harness nets match contract; ERC clean")
