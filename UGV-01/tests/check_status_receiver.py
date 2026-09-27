"""Netlist gate for the powered-off-tolerant MCU status receiver draft."""
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / "electronics/ugv_mcu_01/status_receiver.kicad_sch"
CLI = os.environ.get("UGV_KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
assert SHEET.exists(), "MCU status receiver schematic missing"

with tempfile.TemporaryDirectory() as tmp:
    netlist = Path(tmp) / "receiver.xml"
    erc = Path(tmp) / "erc.txt"
    subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(netlist), str(SHEET)], check=True)
    root = ET.parse(netlist).getroot()
    parts = {c.attrib["ref"]: c.findtext("value") for c in root.findall("./components/comp")}
    nets = {
        n.attrib["name"].removeprefix("/"): {(p.attrib["ref"], p.attrib["pin"]) for p in n.findall("node")}
        for n in root.findall("./nets/net")
    }
    assert parts["U1"] == "SN74LVC244APWR"
    for pin, net in {
        "2": "PWR_ACT_EN", "4": "PWR_K1_FB", "6": "PWR_K2_FB",
        "8": "ESTOP_A_CLOSED", "11": "ESTOP_B_CLOSED", "13": "PWR_WD_OK",
        "18": "ACT_PERMIT_BUF", "16": "K1_FB_BUF", "14": "K2_FB_BUF",
        "12": "ESTOP_A_BUF", "9": "ESTOP_B_BUF", "7": "WD_OK_BUF",
        "20": "MCU_3V3", "10": "PGND",
    }.items():
        assert ("U1", pin) in nets[net], (pin, net)
    assert {("U1", "1"), ("U1", "19")} <= nets["MCU_RAILS_OK_N"]
    assert {("U1", "15"), ("U1", "17")} <= nets["PGND"]
    assert ("R7", "1") in nets["MCU_3V3"]
    assert ("R7", "2") in nets["MCU_RAILS_OK_N"]
    for n, net in enumerate(("ACT_PERMIT_BUF", "K1_FB_BUF", "K2_FB_BUF",
                             "ESTOP_A_BUF", "ESTOP_B_BUF", "WD_OK_BUF"), 1):
        assert (f"R{n}", "1") in nets[net]
        assert (f"R{n}", "2") in nets["PGND"]
    subprocess.run([CLI, "sch", "erc", "-o", str(erc), str(SHEET)], check=True)
    report = erc.read_text()
    # This is a partial sheet: the six PWR drivers are not yet present.
    assert "Errors 6  Warnings 7" in report, report
    assert report.count("[pin_not_driven]") == 6, report
    assert report.count("[isolated_pin_label]") == 6, report
    assert report.count("[lib_symbol_issues]") == 1, report

print("PASS: six power-off-tolerant status channels, output pulldowns and OE default-off netlist")
