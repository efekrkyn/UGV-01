"""Board interface drafts keep J-PWR/J-SIG and PCA9615 nets aligned."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CLI = os.environ.get("UGV_KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
CONTRACT = json.loads((ROOT / "config/pwr_mcu_connector.json").read_text())

for side, u, jsig, jpwr in (("mcu", "U1", "J1", "J2"), ("pwr", "U501", "J501", "J502")):
    sheet = ROOT / f"electronics/ugv_{side}_01/pwr_mcu_interface.kicad_sch"
    assert sheet.exists(), f"Missing {side.upper()} board interface sheet"
    with tempfile.TemporaryDirectory() as tmp:
        netlist = Path(tmp) / "interface.xml"
        report = Path(tmp) / "erc.txt"
        subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(netlist), str(sheet)], check=True)
        root = ET.parse(netlist).getroot()
        values = {c.attrib["ref"]: c.findtext("value") for c in root.findall("./components/comp")}
        nets = {
            n.attrib["name"].removeprefix("/"): {(p.attrib["ref"], p.attrib["pin"]) for p in n.findall("node")}
            for n in root.findall("./nets/net")
        }
        assert values[u] == "PCA9615DP"
        for row in CONTRACT["signal_connector"]["pins"]:
            assert (jsig, str(row["pad"])) in nets[row["net"]]
        for pin, net in (("1", "ACT_BUS"), ("2", "PGND"), ("3", "PGND"), ("4", "5V_CONTROL")):
            assert (jpwr, pin) in nets[net]
        for pin, net in {"1": f"{side.upper()}_3V3", "3": f"{side.upper()}_PGOOD",
                         "5": "PGND", "10": "5V_CONTROL"}.items():
            assert (u, pin) in nets[net]
        for pin, net in {"6": "DI2C_SCL_N", "7": "DI2C_SCL_P",
                         "8": "DI2C_SDA_P", "9": "DI2C_SDA_N"}.items():
            assert (u, pin) in nets[net]
        subprocess.run([CLI, "sch", "erc", "-o", str(report), str(sheet)], check=True)
        text = report.read_text()
        assert "Errors 0  Warnings 9" in text, text
        assert text.count("[isolated_pin_label]") == 9, text
        for net in [row["net"] for row in CONTRACT["signal_connector"]["pins"][:8]] + ["ACT_BUS"]:
            assert f"'{net}'" in text, net

print("PASS: both board interface drafts match connector and PCA9615 pin contract; ERC has only 9 expected external-net warnings per sheet")
