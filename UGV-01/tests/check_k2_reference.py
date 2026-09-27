"""Pin-level regression for the conditional K2 power-path schematic."""
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / "electronics/ugv_pwr_01/k2_reference.kicad_sch"
CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"

with tempfile.TemporaryDirectory() as directory:
    netlist = Path(directory) / "k2.xml"
    erc = Path(directory) / "k2_erc.txt"
    subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadxml",
                    "-o", str(netlist), str(SHEET)], check=True)
    root = ET.parse(netlist).getroot()
    parts = {part.attrib["ref"]: part.findtext("value")
             for part in root.findall("./components/comp")}
    nets = {net.attrib["name"].removeprefix("/"):
            {(node.attrib["ref"], node.attrib["pin"]) for node in net.findall("node")}
            for net in root.findall("./nets/net")}
    assert parts["U1"] == "LM74900QRGERQ1"
    assert parts["Q1"] == parts["Q2"] == "CSD18540Q5BT"
    assert parts["R1"] == "1m 1% Kelvin"
    assert parts["R2"] == "49R9", parts
    assert parts["R3"] == "31k6", parts
    assert parts["R4"] == "100k", parts
    assert parts["R7"] == "5k6", parts
    assert parts["C1"] == "68n", parts
    for net, required in {
        "MID": {("Q1", "1"), ("U1", "2")},
        "K2_DRAIN_A": {("Q1", "5"), ("R1", "1"), ("U1", "22"), ("U1", "24"), ("U1", "18")},
        "K2_DRAIN_B": {("R1", "4"), ("Q2", "5")},
        "ACT_BUS": {("Q2", "1"), ("U1", "15")},
        "DGATE": {("U1", "1"), ("Q1", "4")},
        "HGATE": {("U1", "14"), ("Q2", "4")},
        "SAFE_EN": {("U1", "6"), ("U1", "7")},
        "CS_PLUS": {("U1", "20"), ("R2", "2")},
        "K2_SENSE_P": {("R1", "2"), ("R2", "1")},
        "K2_SENSE_N": {("R1", "3"), ("U1", "19")},
        "K2_FLT": {("U1", "12")},
        "PGND": {("U1", "13")},
    }.items():
        assert required <= nets[net], (net, required - nets.get(net, set()))
    assert ("U1", "25") in nets["unconnected-(U1-RTN-Pad25)"], "thermal pad must float"
    assert ("U1", "25") not in nets["PGND"], "thermal pad must not join ground"
    assert {("R5", "1"), ("U1", "6"), ("U1", "7")} <= nets["SAFE_EN"]
    assert {("R4", "1"), ("C1", "1"), ("U1", "9")} <= nets["K2_TMR"]
    assert {("R8", "2"), ("R9", "1"), ("U1", "4")} <= nets["K2_UVLO"]
    assert {("R10", "2"), ("R11", "1"), ("U1", "5")} <= nets["K2_OV"]
    subprocess.run([CLI, "sch", "erc", "-o", str(erc), str(SHEET)], check=True,
                   capture_output=True, text=True)
    report = erc.read_text()
    # PGND is PWR_FLAGged once on pwr_mcu_interface; standalone, only U1 GND sees it undriven.
    assert "Errors 1" in report and report.count("[power_pin_not_driven]") == 1, report
    assert "Symbol U1 Pin 13" in report, report
    assert report.count("[lib_symbol_issues]") == 3, report
    assert report.count("[isolated_pin_label]") == 1, report

print("PASS: K2 controller, FETs, Kelvin shunt, EN/SLEEP and gate path")
