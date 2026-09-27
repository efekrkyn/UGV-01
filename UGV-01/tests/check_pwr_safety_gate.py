"""UGV-PWR-01 safety permit page: dual NC energy channels, TPS3431/TPS3808, reset latch, AND fan-out, ERC."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from pwr_sheet import BOARD_DIR, erc, flagged, flagged_nets, netlist, pins, violations  # noqa: E402

values, nets, footprints = netlist(BOARD_DIR / "safety_gate.kicad_sch")
at = pins(nets)


def wired(ref, **by_pin):
    for pin, net in by_pin.items():
        got = at.get((ref, pin.removeprefix("p")))
        assert got == net, (ref, pin, got, net)


# NC-A / NC-B: each contact returns its own 5 V; open contact = pulled Low.
wired("J301", p1="ESTOP_A_SRC", p2="ESTOP_A_5V", p3="ESTOP_B_SRC", p4="ESTOP_B_5V", p5="RESET_SW", p6="PGND")
assert footprints["J301"] == "" and "OPEN" in values["J301"]
wired("F301", p1="5V_CONTROL", p2="ESTOP_A_SRC")
wired("F302", p1="5V_CONTROL", p2="ESTOP_B_SRC")
for pull, series, rail, sense in (("R301", "R303", "ESTOP_A_5V", "NC_A_OK"), ("R302", "R304", "ESTOP_B_5V", "NC_B_OK")):
    wired(pull, p1=rail, p2="PGND")
    wired(series, p1=rail, p2=sense)

# TPS3431 DRB pins (TI SNVSB66A Table 5-1); EN/SET1 never reach an MCU net or connector.
wired("U301", p1="PWR_3V3", p2="WD_CWD", p3="RAIL_OK", p4="PGND", p5="PWR_3V3", p6="WDI_IN",
      p7="WD_OK", p8="WD_OK", p9="PGND")
wired("C305", p1="WD_CWD", p2="PGND")
assert values["C305"].startswith("100p") and "C0G" in values["C305"]
assert (55 + 77.4 * 0.1 * 1.05) * 1.095 < 70.0, "TI tWD(max) with +5% C must stay <= ~69 ms"
wired("R305", p1="MCU_WDI", p2="WDI_IN")
wired("R306", p1="WDI_IN", p2="PGND")
wired("R307", p1="PWR_3V3", p2="WD_OK")
wired("U302", p1="RAIL_OK", p2="PGND", p3="PWR_3V3", p5="PWR_3V3", p6="PWR_3V3")
assert values["U302"] == "TPS3808G33DBVR" and at[("U302", "4")].startswith("unconnected"), "CT open = 20 ms"
for pin in ("3", "5"):
    net = at[("U301", pin)]
    assert not net.startswith("MCU_") and not any(r.startswith("J") for r, _ in nets[net]), pin

# Reset: button release (Schmitt) clocks the latch; CHAIN_OK clears it asynchronously.
wired("R309", p1="PWR_3V3", p2="RESET_SW")
wired("R310", p1="RESET_SW", p2="RESET_F")
wired("U303", p2="RESET_F", p4="RESET_CLK", p3="PGND", p5="PWR_3V3")
wired("U304", p1="NC_A_OK", p3="NC_B_OK", p6="WD_OK", p4="CHAIN_OK")
wired("U305", p1="RESET_CLK", p2="CHAIN_OK", p6="CHAIN_OK", p7="PWR_3V3", p5="LATCH_OK")
wired("U306", p1="LATCH_OK", p3="CHAIN_OK", p6="RUN_REQ_IN", p4="SAFE_GATE")
wired("R311", p1="MCU_RUN_REQ", p2="RUN_REQ_IN")
wired("R312", p1="RUN_REQ_IN", p2="PGND")

# Every actuator request is ANDed with SAFE_GATE; TCA commands default Low at the consumer.
for ref, cmd, out in (("U307", "K1_CMD", "K1_DRV"), ("U308", "K2_CMD", "K2_EN_REQ"),
                      ("U309", "PRECHARGE_CMD", "PCH_REQ")):
    wired(ref, p1="SAFE_GATE", p2=cmd, p4=out)
wired("U310", p1="SAFE_GATE", p3="ACT_ENABLE_REQ", p6="SAFE_EN", p4="ACT_EN_OUT")
wired("R313", p1="ACT_EN_OUT", p2="PWR_ACT_EN")
wired("R314", p1="PWR_ACT_EN", p2="PGND")
for i, cmd in enumerate(("K1_CMD", "K2_CMD", "PRECHARGE_CMD", "ACT_ENABLE_REQ")):
    wired(f"R{318 + i}", p1=cmd, p2="PGND")
assert nets["PWR_ACT_EN"] == {("R313", "2"), ("R314", "1")}, "PWR_ACT_EN is not a copy of an MCU pin"

# LVC1T45 B side is powered by the NC-B channel: NC-B open leaves K2 EN/precharge/test permit Hi-Z.
for ref, a, b in (("U311", "K2_EN_REQ", "SAFE_EN"), ("U312", "PCH_REQ", "PCH_DRV"),
                  ("U313", "SAFE_GATE", "TEST_PERMIT_DRV")):
    wired(ref, p1="PWR_3V3", p2="PGND", p3=a, p4=b, p5="PWR_3V3", p6="ESTOP_B_5V")

# Status to J-SIG through Ioff buffers + 1k; PWR_PGOOD for the PCA9615 EN.
for ref, src, mid, res, out in (("U314", "NC_A_OK", "STA_A", "R315", "ESTOP_A_CLOSED"),
                                ("U315", "NC_B_OK", "STA_B", "R316", "ESTOP_B_CLOSED"),
                                ("U316", "WD_OK", "STA_WD", "R317", "PWR_WD_OK")):
    wired(ref, p2=src, p4=mid)
    wired(res, p1=mid, p2=out)
wired("U317", p2="RAIL_OK", p4="PWR_PGOOD")

# Every logic IC supply rail has a local 100n on this page.
for ref in [r for r in values if r.startswith("U")]:
    for rail in {at.get((ref, p)) for p in ("1", "5", "6", "8")} & {"PWR_3V3", "ESTOP_B_5V"}:
        assert any(c.startswith("C") for c, _ in nets[rail]), (ref, rail)

report = erc(BOARD_DIR / "safety_gate.kicad_sch")
assert violations(report) == {"isolated_pin_label": 9, "lib_symbol_issues": 1, "power_pin_not_driven": 2}, report
assert flagged_nets(report, "power_pin_not_driven", nets) == ["PGND", "PWR_3V3"], "rails are flagged on pwr_mcu_interface"
assert flagged(report, "isolated_pin_label") == sorted([
    "ESTOP_A_CLOSED", "ESTOP_B_CLOSED", "K1_DRV", "MCU_RUN_REQ", "MCU_WDI", "PCH_DRV",
    "PWR_PGOOD", "PWR_WD_OK", "TEST_PERMIT_DRV"]), flagged(report, "isolated_pin_label")
assert "'UGV'" in report, "only the project-local TPS3431 symbol is unresolved standalone"
print("PASS: dual NC energy channels, TPS3431 100 pF + TPS3808 rail gate, release-edge reset latch, "
      "SAFE_GATE-qualified K1/K2/precharge/test/ACT_EN; standalone ERC only off-page rail/label items")
