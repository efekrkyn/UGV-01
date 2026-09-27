"""UGV-PWR-01 actuator path + arming I/O pages: pin nets, open K1 selection, diagnostic windows, ERC."""
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from pwr_sheet import BOARD_DIR, erc, flagged, flagged_nets, netlist, ohms, pins, violations  # noqa: E402

values, nets, footprints = netlist(BOARD_DIR / "actuator_path.kicad_sch")
at = pins(nets)


def wired(table, ref, **by_pin):
    for pin, net in by_pin.items():
        got = table.get((ref, pin.removeprefix("p")))
        assert got == net, (ref, pin, got, net)


# F1 -> K1 contact -> MID. K1 stays an open selection: no footprint, MPN flagged.
wired(at, "F1", p1="MOTOR_FEED", p2="F1_OUT")
wired(at, "K1", p13="F1_OUT", p14="MID", pA1="ESTOP_A_5V", pA2="K1_COIL_LO")
assert "MPN OPEN" in values["K1"] and footprints["K1"] == "", "K1 must not look released"
assert footprints["F1"] == "" and "OPEN" in values["F1"]
wired(at, "Q201", p1="K1_GATE", p2="PGND", p3="K1_COIL_LO")
wired(at, "R201", p1="K1_DRV", p2="K1_GATE")
wired(at, "R202", p1="K1_GATE", p2="PGND")
wired(at, "D201", p1="K1_CLAMP", p2="K1_COIL_LO")  # anode on coil low side
wired(at, "D202", p1="K1_CLAMP", p2="ESTOP_A_5V")  # zener cathode away from the supply

# Precharge: P-FET source on MID, 470R to ACT_BUS, 12 V gate clamp, off by default.
wired(at, "Q202", p1="PCH_G", p2="MID", p3="PCH_D")
wired(at, "R205", p1="PCH_D", p2="ACT_BUS")
wired(at, "R206", p1="MID", p2="PCH_G")
wired(at, "D203", p1="MID", p2="PCH_G")
wired(at, "R207", p1="PCH_G", p2="PCH_PD")
wired(at, "Q203", p1="PCH_DRV", p2="PGND", p3="PCH_PD")
wired(at, "R208", p1="PCH_DRV", p2="PGND")
assert ohms(values["R205"]) == 470 and ">=2W" in values["R205"]

# ACT bleed with hardware interlock against PWR_ACT_EN.
wired(at, "R209", p1="ACT_BUS", p2="BLEED_D")
wired(at, "Q204", p1="BLEED_G", p2="PGND", p3="BLEED_D")
wired(at, "R210", p1="BLEED_CMD", p2="BLEED_G")
wired(at, "R211", p1="BLEED_G", p2="PGND")
wired(at, "Q205", p1="ILK_G", p2="PGND", p3="BLEED_G")
wired(at, "R228", p1="PWR_ACT_EN", p2="ILK_G")

# Test injection: two P-FETs in series, both sourced toward F1_OUT, then 1k into MID.
wired(at, "Q206", p1="TSTP_G", p2="F1_OUT", p3="TST_A")
wired(at, "Q208", p1="TSTC_G", p2="TST_A", p3="TST_B")
wired(at, "R217", p1="TST_B", p2="MID")
wired(at, "Q207", p1="TEST_PERMIT_DRV", p2="PGND", p3="TSTP_PD")
wired(at, "Q209", p1="TSTC_DRV", p2="PGND", p3="TSTC_PD")
wired(at, "R229", p1="TEST_CMD", p2="TSTC_DRV")
wired(at, "R230", p1="TSTC_DRV", p2="PGND")
wired(at, "D204", p1="F1_OUT", p2="TSTP_G")
wired(at, "D205", p1="TST_A", p2="TSTC_G")

# Dividers from the netlist values drive the diagnostic calculation below.
r = {ref: ohms(values[ref]) for ref in values if ref.startswith("R")}
for top, bottom, node, sense in (("R218", "R219", "MID", "MID_SENSE"), ("R220", "R221", "F1_OUT", "F1_SENSE"),
                                 ("R222", "R223", "ACT_BUS", "ACT_SENSE"), ("R224", "R225", "F1_OUT", "F1_CMP"),
                                 ("R226", "R227", "MID", "MID_CMP")):
    wired(at, top, p1=node, p2=sense)
    wired(at, bottom, p1=sense, p2="PGND")


def par(*rs):
    return 1 / sum(1 / x for x in rs)


mid_load = par(r["R218"] + r["R219"], r["R226"] + r["R227"])
act_div = r["R222"] + r["R223"]
lo, hi = 12.4, 16.8
# Test injection with K1/K2 open and ACT bleed on: healthy vs K2-or-precharge short.
healthy = (lo * mid_load * 0.99 / (r["R217"] * 1.05 + mid_load * 0.99),
           hi * mid_load * 1.01 / (r["R217"] * 0.95 + mid_load * 1.01))


def fault_load(k):
    return par(mid_load * k, r["R209"] * k, act_div)


fault = (lo * fault_load(0.95) / (r["R217"] * 1.05 + fault_load(0.95)),
         hi * fault_load(1.05) / (r["R217"] * 0.95 + fault_load(1.05)))
adc_err = 0.3
assert healthy[0] - adc_err > 8.0 > fault[1] + adc_err, (healthy, fault)

# K1_FB comparator (arming_io U403A): MID_SENSE vs F1_CMP + 3.3 V/2M2 offset.
av, anets, _ = netlist(BOARD_DIR / "arming_io.kicad_sch")
a = pins(anets)
r_mid = r["R219"] / (r["R218"] + r["R219"])
r_cmp = r["R225"] / (r["R224"] + r["R225"])
offset = 3.3 * par(r["R224"], r["R225"]) / (ohms(av["R411"]) + par(r["R224"], r["R225"]))


def threshold(f1):
    return (f1 * r_cmp + offset) / r_mid


error_budget = 0.2  # V at rail: LM2903 offset/bias + 0.1% ratio error, see docs/pwr_safety_path.md
for f1 in (lo, hi):
    test_mid = f1 * mid_load * 1.01 / (r["R217"] * 0.95 + mid_load * 1.01)
    assert test_mid < threshold(f1) - error_budget, ("test injection must read K1 open", f1)
    assert f1 - 0.05 > threshold(f1) + error_budget, ("closed K1 must read High", f1, threshold(f1))
assert offset > 0.015 and threshold(0) > 0.1, "0 V/0 V must read Low beyond LM2903 input offset"

# Precharge/bleed timing and power with +20% C and +/-5% R (C6 4700u lives on k2_reference).
c_bulk = 4700e-6 * 1.2
t_pch = r["R205"] * 1.05 * c_bulk * math.log(hi / 1.0)
t_bleed = r["R209"] * 1.05 * c_bulk * math.log(hi / 1.0)
assert t_pch + t_bleed < 13.0, (t_pch, t_bleed)  # 15 s ARMING budget minus test/K1 steps
assert hi**2 / (r["R209"] * 0.95) < 5 * 0.5 and "5W" in values["R209"]
assert hi**2 / (r["R217"] * 0.95) < 1 * 0.5 and ">=1W" in values["R217"]
assert 5.25 + 1.0 + 12 * 1.05 < 30 * 0.8, "K1 driver Vds with 12 V zener clamp"

# Arming I/O page wiring.
tca = {"1": "PGND", "2": "PGND", "3": "PGND", "4": "TEST_CMD", "5": "PRECHARGE_CMD", "6": "BLEED_CMD",
       "7": "K1_CMD", "8": "PGND", "9": "K2_CMD", "10": "ACT_ENABLE_REQ", "11": "K2_FLT", "12": "LATCH_OK",
       "14": "PWR_I2C_SCL", "15": "PWR_I2C_SDA", "16": "PWR_3V3"}
wired(a, "U401", **{f"p{k}": v for k, v in tca.items()})
assert av["U401"] == "TCA9534APWR" and av["U402"] == "ADS1115IDGSR"
for pin, adc, sense, res in (("4", "F1_ADC", "F1_SENSE", "R401"), ("5", "MID_ADC", "MID_SENSE", "R402"),
                             ("6", "ACT_ADC", "ACT_SENSE", "R403"), ("7", "IMON_ADC", "K2_IMON", "R404")):
    wired(a, "U402", **{f"p{pin}": adc})
    wired(a, res, p1=sense, p2=adc)
wired(a, "U402", p1="PGND")  # ADS1115 address 0x48
wired(a, "U403", p1="K1_FB_OC", p2="F1_CMP", p3="MID_SENSE", p5="ACT_SENSE", p6="MID_CMP",
      p7="K2_FB_OC", p4="PGND", p8="5V_CONTROL")
for res, top, bottom in (("R407", "PWR_3V3", "K1_FB_OC"), ("R409", "K1_FB_OC", "PWR_K1_FB"),
                         ("R408", "PWR_3V3", "K2_FB_OC"), ("R410", "K2_FB_OC", "PWR_K2_FB"),
                         ("R411", "PWR_3V3", "F1_CMP"), ("R412", "PWR_3V3", "MID_CMP")):
    wired(a, res, p1=top, p2=bottom)

# Standalone ERC: only nets that continue on other PWR pages.
report = erc(BOARD_DIR / "actuator_path.kicad_sch")
assert violations(report) == {"isolated_pin_label": 5}, report
assert flagged(report, "isolated_pin_label") == ["BLEED_CMD", "K1_DRV", "MOTOR_FEED", "PWR_ACT_EN", "TEST_CMD"]
report = erc(BOARD_DIR / "arming_io.kicad_sch")
assert violations(report) == {"isolated_pin_label": 12, "pin_not_driven": 1, "power_pin_not_driven": 3}, report
assert flagged_nets(report, "pin_not_driven", anets) == ["PWR_I2C_SCL"], "SCL pull-ups live on pwr_mcu_interface"
assert flagged_nets(report, "power_pin_not_driven", anets) == ["5V_CONTROL", "PGND", "PWR_3V3"]

print("PASS: F1-K1-MID path, switched precharge/bleed/test injection, open K1 selection; "
      f"test window {healthy[0]:.2f}-{healthy[1]:.2f} V vs fault {fault[0]:.2f}-{fault[1]:.2f} V; "
      f"K1_FB threshold {threshold(lo):.2f}/{threshold(hi):.2f} V; precharge <= {t_pch:.2f} s")
