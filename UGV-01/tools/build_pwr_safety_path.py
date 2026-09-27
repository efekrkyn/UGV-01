"""Build UGV-PWR-01 actuator path, safety permit and arming I/O pages plus the board root.

P0 review schematics only: K1 MPN/footprint, F1 family, shunt MPN, power resistor
parts, TVS/regen clamp and PCB thermal design stay open. Not for fabrication.
"""
import json
from uuid import NAMESPACE_URL, uuid5

from pwr_sheet import BOARD, BOARD_DIR, PAGES, ROOT_UUID, Page, sheet_uuid

R0603, C0603 = "Resistor_SMD:R_0603_1608Metric", "Capacitor_SMD:C_0603_1608Metric"
SOT23, SOT235, SOT236 = ("Package_TO_SOT_SMD:SOT-23", "Package_TO_SOT_SMD:SOT-23-5",
                         "Package_TO_SOT_SMD:SOT-23-6")
OPEN = {"Status": "SELECTION-OPEN: no footprint or MPN release"}
NMOS, PMOS = "Transistor_FET:Q_NMOS_GSD", "Transistor_FET:Q_PMOS_GSD"


def fet(page, ref, kind, value, x, y, gate, source, drain):
    page.part(ref, NMOS if kind == "N" else PMOS, value, x, y,
              {"1": gate, "2": source, "3": drain}, SOT23)


def actuator_path():
    p = Page("actuator_path", "UGV-PWR-01 actuator path: F1-K1-MID-K2-ACT_BUS")
    # F1 and K1. K1 coil high side is the physical NC_A channel (ESTOP_A_5V).
    p.part("F1", "Device:Fuse", "15A F1 - family/I2t OPEN", 25.4, 50.8,
           {"1": "MOTOR_FEED", "2": "F1_OUT"}, extra=OPEN)
    p.part("K1", "Relay:Relay_SPST-NO", "K1 relay MPN OPEN",
           76.2, 50.8, {"A1": "ESTOP_A_5V", "A2": "K1_COIL_LO", "13": "F1_OUT", "14": "MID"},
           extra={"Status": "SELECTION-OPEN: T9AS1D17-5 is only a packaging candidate; no 16.8 V DC motor-break "
                         "evidence; footprint deliberately empty"})
    p.part("D201", "Device:D", "1N4148W", 116.84, 38.1, {"1": "K1_CLAMP", "2": "K1_COIL_LO"},
           "Diode_SMD:D_SOD-123")
    p.part("D202", "Device:D_Zener", "BZT52C12 12V", 116.84, 58.42, {"1": "K1_CLAMP", "2": "ESTOP_A_5V"},
           "Diode_SMD:D_SOD-123")
    fet(p, "Q201", "N", "AO3400A", 157.48, 50.8, "K1_GATE", "PGND", "K1_COIL_LO")
    p.two("R201", "R", "100R", 182.88, 50.8, "K1_DRV", "K1_GATE", R0603)
    p.two("R202", "R", "100k", 203.2, 50.8, "K1_GATE", "PGND", R0603)

    # Switched 470 ohm precharge around K2; P-FET source on MID blocks MID->ACT when off.
    fet(p, "Q202", "P", "BSS84", 38.1, 111.76, "PCH_G", "MID", "PCH_D")
    p.two("R205", "R", "470R >=2W pulse", 63.5, 111.76, "PCH_D", "ACT_BUS")
    p.two("R206", "R", "100k", 88.9, 111.76, "MID", "PCH_G", R0603)
    p.part("D203", "Device:D_Zener", "BZT52C12 12V", 111.76, 111.76, {"1": "MID", "2": "PCH_G"},
           "Diode_SMD:D_SOD-123")
    p.two("R207", "R", "10k", 137.16, 111.76, "PCH_G", "PCH_PD", R0603)
    fet(p, "Q203", "N", "2N7002", 162.56, 111.76, "PCH_DRV", "PGND", "PCH_PD")
    p.two("R208", "R", "100k", 187.96, 111.76, "PCH_DRV", "PGND", R0603)

    # 150 ohm ACT bleed; hardware interlock: PWR_ACT_EN High clamps the bleed gate.
    p.two("R209", "R", "150R 5W", 238.76, 111.76, "ACT_BUS", "BLEED_D")
    fet(p, "Q204", "N", "BSS138", 264.16, 111.76, "BLEED_G", "PGND", "BLEED_D")
    p.two("R210", "R", "1k", 289.56, 111.76, "BLEED_CMD", "BLEED_G", R0603)
    p.two("R211", "R", "100k", 309.88, 111.76, "BLEED_G", "PGND", R0603)
    fet(p, "Q205", "N", "2N7002", 335.28, 111.76, "ILK_G", "PGND", "BLEED_G")
    p.two("R228", "R", "1k", 360.68, 111.76, "PWR_ACT_EN", "ILK_G", R0603)

    # Test injection F1_OUT -> S2 permit -> S1 command -> 1k -> MID; either switch blocks alone.
    fet(p, "Q206", "P", "BSS84", 38.1, 172.72, "TSTP_G", "F1_OUT", "TST_A")
    p.two("R212", "R", "100k", 63.5, 172.72, "F1_OUT", "TSTP_G", R0603)
    p.part("D204", "Device:D_Zener", "BZT52C12 12V", 86.36, 172.72, {"1": "F1_OUT", "2": "TSTP_G"},
           "Diode_SMD:D_SOD-123")
    p.two("R213", "R", "10k", 111.76, 172.72, "TSTP_G", "TSTP_PD", R0603)
    fet(p, "Q207", "N", "2N7002", 137.16, 172.72, "TEST_PERMIT_DRV", "PGND", "TSTP_PD")
    p.two("R214", "R", "100k", 162.56, 172.72, "TEST_PERMIT_DRV", "PGND", R0603)
    fet(p, "Q208", "P", "BSS84", 38.1, 215.9, "TSTC_G", "TST_A", "TST_B")
    p.two("R215", "R", "100k", 63.5, 215.9, "TST_A", "TSTC_G", R0603)
    p.part("D205", "Device:D_Zener", "BZT52C12 12V", 86.36, 215.9, {"1": "TST_A", "2": "TSTC_G"},
           "Diode_SMD:D_SOD-123")
    p.two("R216", "R", "10k", 111.76, 215.9, "TSTC_G", "TSTC_PD", R0603)
    fet(p, "Q209", "N", "2N7002", 137.16, 215.9, "TSTC_DRV", "PGND", "TSTC_PD")
    p.two("R229", "R", "100R", 162.56, 215.9, "TEST_CMD", "TSTC_DRV", R0603)
    p.two("R230", "R", "100k", 180.34, 215.9, "TSTC_DRV", "PGND", R0603)
    p.two("R217", "R", "1k >=1W", 187.96, 194.31, "TST_B", "MID")

    # Rail sensing. R218/R219 are also the ~10k MID bleed.
    dividers = [("R218", "8k25 0.1%", "R219", "1k65 0.1%", "C201", "MID", "MID_SENSE"),
                ("R220", "100k 0.1%", "R221", "20k 0.1%", "C202", "F1_OUT", "F1_SENSE"),
                ("R222", "100k 0.1%", "R223", "20k 0.1%", "C203", "ACT_BUS", "ACT_SENSE"),
                ("R224", "105k 0.1%", "R225", "20k 0.1%", "C204", "F1_OUT", "F1_CMP"),
                ("R226", "105k 0.1%", "R227", "20k 0.1%", "C205", "MID", "MID_CMP")]
    for i, (rt, vt, rb, vb, c, node, sense) in enumerate(dividers):
        x = 238.76 + i * 30.48
        p.two(rt, "R", vt, x, 162.56, node, sense, R0603)
        p.two(rb, "R", vb, x, 203.2, sense, "PGND", R0603)
        p.two(c, "C", "100n", x + 12.7, 203.2, sense, "PGND", C0603)
    for i, net in enumerate(("F1_OUT", "MID", "ACT_BUS", "K1_COIL_LO")):
        p.part(f"TP{201 + i}", "Connector:TestPoint", f"TP {net}", 238.76 + i * 25.4, 50.8,
               {"1": net}, "TestPoint:TestPoint_Pad_D1.5mm")

    notes = [
        "P0 REVIEW SHEET - NOT FOR FABRICATION. K1 MPN/footprint, F1 I2t, R205/R209/R217 parts, TVS and regen clamp OPEN.",
        "K2 (LM74900 + 2x CSD18540, Kelvin shunt, 4700uF) is on k2_reference; MID -> K2 -> ACT_BUS.",
        "K1 coil supply = ESTOP_A_5V (NC-A contact); Q201 low side needs SAFE_GATE AND K1_CMD (safety_gate).",
        "Precharge/test FET gates are driven from ESTOP_B_5V via LVC1T45: NC-B open removes the drive physically.",
        "Test path bypasses K1 only; K2/precharge short is detected before K1 closes (MCU sequence, not HW interlock).",
        "Small-signal FET ratings not verified against vendor datasheets in this revision.",
    ]
    for i, text in enumerate(notes):
        p.note(f"note{i}", text, 25.4, 243.84 + i * 6.35)
    return p.write("Actuator path P0: K1 selection open; not a PCB release")


def safety_gate():
    p = Page("safety_gate", "UGV-PWR-01 dual NC E-stop, watchdog and permit chain", "A2")
    # Physical E-stop channels: each NC contact carries its own 5 V energy.
    p.part("J301", "Connector_Generic:Conn_01x06", "J-ESTOP MPN OPEN", 38.1, 50.8,
           {"1": "ESTOP_A_SRC", "2": "ESTOP_A_5V", "3": "ESTOP_B_SRC", "4": "ESTOP_B_5V",
            "5": "RESET_SW", "6": "PGND"}, extra=OPEN)
    for ref, value, x, src in (("F301", "PTC 0.5A hold", 71.12, "ESTOP_A_SRC"), ("F302", "PTC 0.1A hold", 91.44, "ESTOP_B_SRC")):
        p.part(ref, "Device:Polyfuse", value, x, 50.8, {"1": "5V_CONTROL", "2": src}, extra=OPEN)
    rows = [("D301", "C301", "R301", "R303", "C303", "ESTOP_A_5V", "NC_A_OK"),
            ("D302", "C302", "R302", "R304", "C304", "ESTOP_B_5V", "NC_B_OK")]
    for i, (tvs, cap, pull, series, filt, rail, sense) in enumerate(rows):
        y = 40.64 + i * 30.48
        p.part(tvs, "Device:D_TVS", "SMAJ6.0CA", 121.92, y, {"1": rail, "2": "PGND"}, extra=OPEN)
        p.two(cap, "C", "100n", 144.78, y, rail, "PGND", C0603)
        p.two(pull, "R", "10k", 165.1, y, rail, "PGND", R0603)
        p.two(series, "R", "10k", 185.42, y, rail, sense, R0603)
        p.two(filt, "C", "100n", 205.74, y, sense, "PGND", C0603)
    # Local reset: release edge sets the latch (stuck-pressed button cannot re-arm).
    p.part("D303", "Device:D_TVS", "PESD5V0S1BL", 243.84, 40.64,
           {"1": "RESET_SW", "2": "PGND"}, "Diode_SMD:D_SOD-323", extra=OPEN)
    p.two("R309", "R", "10k", 264.16, 40.64, "PWR_3V3", "RESET_SW", R0603)
    p.two("R310", "R", "10k", 284.48, 40.64, "RESET_SW", "RESET_F", R0603)
    p.two("C309", "C", "100n", 304.8, 40.64, "RESET_F", "PGND", C0603)

    def gate(ref, value, lib, x, y, nets, footprint, cap):
        p.part(ref, lib, value, x, y, nets, footprint)
        p.two(cap, "C", "100n", x + 22.86, y + 12.7, "PWR_3V3", "PGND", C0603)

    # Watchdog (100 pF C0G ~62.7 ms) and 3.3 V supervisor; EN/SET1 not MCU-controlled.
    p.part("U301", "UGV:TPS3431SDRB", "TPS3431SDRBR", 50.8, 124.46,
           {"1": "PWR_3V3", "2": "WD_CWD", "3": "RAIL_OK", "4": "PGND", "5": "PWR_3V3",
            "6": "WDI_IN", "7": "WD_OK", "8": "WD_OK", "9": "PGND"},
           "Package_SON:VSON-8-1EP_3x3mm_P0.65mm_EP1.65x2.4mm")
    p.two("C305", "C", "100p C0G 5%", 88.9, 124.46, "WD_CWD", "PGND", C0603)
    p.two("C306", "C", "100n", 104.14, 124.46, "PWR_3V3", "PGND", C0603)
    p.two("R305", "R", "1k", 119.38, 124.46, "MCU_WDI", "WDI_IN", R0603)
    p.two("R306", "R", "100k", 134.62, 124.46, "WDI_IN", "PGND", R0603)
    p.two("R307", "R", "10k", 149.86, 124.46, "PWR_3V3", "WD_OK", R0603)
    p.part("U302", "Power_Supervisor:TPS3808DBV", "TPS3808G33DBVR", 198.12, 124.46,
           {"1": "RAIL_OK", "2": "PGND", "3": "PWR_3V3", "4": None, "5": "PWR_3V3", "6": "PWR_3V3"},
           SOT236)
    p.two("R308", "R", "10k", 228.6, 124.46, "PWR_3V3", "RAIL_OK", R0603)
    p.two("C307", "C", "100n", 243.84, 124.46, "PWR_3V3", "PGND", C0603)
    gate("U303", "SN74LVC1G17DBVR", "74xGxx:74LVC1G17", 297.18, 124.46,
         {"1": None, "2": "RESET_F", "3": "PGND", "4": "RESET_CLK", "5": "PWR_3V3"}, SOT235, "C308")

    # Chain, reset latch and SAFE_GATE.
    and3, and2, buf = "74xGxx:74LVC1G11", "74xGxx:74LVC1G08", "74xGxx:74LVC1G17"
    gate("U304", "SN74LVC1G11DBVR", and3, 50.8, 185.42,
         {"1": "NC_A_OK", "3": "NC_B_OK", "6": "WD_OK", "4": "CHAIN_OK", "2": "PGND", "5": "PWR_3V3"},
         SOT236, "C310")
    gate("U305", "SN74LVC2G74DCUR", "74xGxx:74LVC2G74", 139.7, 185.42,
         {"1": "RESET_CLK", "2": "CHAIN_OK", "3": None, "4": "PGND", "5": "LATCH_OK",
          "6": "CHAIN_OK", "7": "PWR_3V3", "8": "PWR_3V3"}, "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", "C311")
    gate("U306", "SN74LVC1G11DBVR", and3, 228.6, 185.42,
         {"1": "LATCH_OK", "3": "CHAIN_OK", "6": "RUN_REQ_IN", "4": "SAFE_GATE", "2": "PGND", "5": "PWR_3V3"},
         SOT236, "C312")
    p.two("R311", "R", "1k", 279.4, 185.42, "MCU_RUN_REQ", "RUN_REQ_IN", R0603)
    p.two("R312", "R", "100k", 299.72, 185.42, "RUN_REQ_IN", "PGND", R0603)
    # TCA9534A pins are inputs at power-up: command defaults are these consumer-side pulldowns.
    for i, net in enumerate(("K1_CMD", "K2_CMD", "PRECHARGE_CMD", "ACT_ENABLE_REQ")):
        p.two(f"R{318 + i}", "R", "100k", 322.58 + i * 20.32, 185.42, net, "PGND", R0603)

    # Command AND permit. Only SAFE_GATE-qualified requests reach the actuator drivers.
    for i, (ref, cap, cmd, out) in enumerate([("U307", "C313", "K1_CMD", "K1_DRV"),
                                               ("U308", "C314", "K2_CMD", "K2_EN_REQ"),
                                               ("U309", "C315", "PRECHARGE_CMD", "PCH_REQ")]):
        gate(ref, "SN74LVC1G08DBVR", and2, 50.8 + i * 88.9, 243.84,
             {"1": "SAFE_GATE", "2": cmd, "4": out, "3": "PGND", "5": "PWR_3V3"}, SOT235, cap)
    gate("U310", "SN74LVC1G11DBVR", and3, 317.5, 243.84,
         {"1": "SAFE_GATE", "3": "ACT_ENABLE_REQ", "6": "SAFE_EN", "4": "ACT_EN_OUT",
          "2": "PGND", "5": "PWR_3V3"}, SOT236, "C316")
    p.two("R313", "R", "1k", 368.3, 243.84, "ACT_EN_OUT", "PWR_ACT_EN", R0603)
    p.two("R314", "R", "100k", 388.62, 243.84, "PWR_ACT_EN", "PGND", R0603)

    # Level translators powered on the B side from ESTOP_B_5V: NC-B open = outputs Hi-Z.
    for i, (ref, ca, cb, a, b) in enumerate([("U311", "C317", "C318", "K2_EN_REQ", "SAFE_EN"),
                                              ("U312", "C319", "C320", "PCH_REQ", "PCH_DRV"),
                                              ("U313", "C321", "C322", "SAFE_GATE", "TEST_PERMIT_DRV")]):
        x = 50.8 + i * 88.9
        p.part(ref, "Logic_LevelTranslator:SN74LVC1T45DBV", "SN74LVC1T45DBVR", x, 302.26,
               {"1": "PWR_3V3", "2": "PGND", "3": a, "4": b, "5": "PWR_3V3", "6": "ESTOP_B_5V"}, SOT236)
        p.two(ca, "C", "100n", x + 22.86, 314.96, "PWR_3V3", "PGND", C0603)
        p.two(cb, "C", "100n", x + 38.1, 314.96, "ESTOP_B_5V", "PGND", C0603)

    # Buffered status to J-SIG (Ioff; 1k series into the MCU receiver) and PCA9615 EN.
    for i, (ref, cap, rin, mid, res, out) in enumerate([
            ("U314", "C323", "NC_A_OK", "STA_A", "R315", "ESTOP_A_CLOSED"),
            ("U315", "C324", "NC_B_OK", "STA_B", "R316", "ESTOP_B_CLOSED"),
            ("U316", "C325", "WD_OK", "STA_WD", "R317", "PWR_WD_OK")]):
        x = 50.8 + i * 88.9
        gate(ref, "SN74LVC1G17DBVR", buf, x, 360.68,
             {"1": None, "2": rin, "3": "PGND", "4": mid, "5": "PWR_3V3"}, SOT235, cap)
        p.two(res, "R", "1k", x + 43.18, 360.68, mid, out, R0603)
    gate("U317", "SN74LVC1G17DBVR", buf, 317.5, 360.68,
         {"1": None, "2": "RAIL_OK", "3": "PGND", "4": "PWR_PGOOD", "5": "PWR_3V3"}, SOT235, "C326")

    # One PWR_FLAG per net in the merged board: rails are flagged on pwr_mcu_interface (board entry).
    p.flag(303, 452.12, 40.64, "ESTOP_B_5V")  # driven only through the NC-B contact
    notes = [
        "P0 REVIEW SHEET - NOT FOR FABRICATION; not a functional-safety certification.",
        "CHAIN_OK = NC_A AND NC_B AND WD_OK; WD_OK = TPS3431 WDO AND ENOUT (wired); TPS3808 RAIL_OK drives TPS3431 EN.",
        "SAFE_GATE = LATCH_OK AND CHAIN_OK AND MCU_RUN_REQ. Latch sets only on reset-button release with CHAIN_OK High.",
        "NC-A carries K1 coil energy; NC-B powers the LVC1T45 B side (K2 EN, precharge, test permit). Logic cannot veto an open NC.",
        "LM74900 SLEEP is not an E-stop: SLEEP=EN=SAFE_EN, driven Low by hardware. K2_FLT is read by MCU only (latch input OPEN).",
        "J-ESTOP, PTC, TVS MPNs OPEN. T01/T03/T13 physical evidence NOT_RUN.",
    ]
    for i, text in enumerate(notes):
        p.note(f"note{i}", text, 406.4, 284.48 + i * 5.08)
    return p.write("Safety permit P0: not a PCB or functional-safety release")


def arming_io():
    p = Page("arming_io", "UGV-PWR-01 arming commands, rail ADC and K1/K2 feedback")
    p.part("U401", "Interface_Expansion:TCA9534", "TCA9534APWR", 63.5, 76.2,
           {"1": "PGND", "2": "PGND", "3": "PGND", "4": "TEST_CMD", "5": "PRECHARGE_CMD",
            "6": "BLEED_CMD", "7": "K1_CMD", "8": "PGND", "9": "K2_CMD", "10": "ACT_ENABLE_REQ",
            "11": "K2_FLT", "12": "LATCH_OK", "13": None, "14": "PWR_I2C_SCL", "15": "PWR_I2C_SDA",
            "16": "PWR_3V3"}, "Package_SO:TSSOP-16_4.4x5mm_P0.65mm")
    p.two("C401", "C", "100n", 127, 76.2, "PWR_3V3", "PGND", C0603)
    p.part("U402", "Analog_ADC:ADS1115IDGS", "ADS1115IDGSR", 63.5, 157.48,
           {"1": "PGND", "2": None, "3": "PGND", "4": "F1_ADC", "5": "MID_ADC", "6": "ACT_ADC",
            "7": "IMON_ADC", "8": "PWR_3V3", "9": "PWR_I2C_SDA", "10": "PWR_I2C_SCL"},
           "Package_SO:TSSOP-10_3x3mm_P0.5mm")
    p.two("C402", "C", "100n", 104.14, 157.48, "PWR_3V3", "PGND", C0603)
    # 1k series: limits injection into an unpowered ADS1115 (AIN <= VDD+0.3 V).
    for i, (net, adc) in enumerate((("F1_SENSE", "F1_ADC"), ("MID_SENSE", "MID_ADC"),
                                    ("ACT_SENSE", "ACT_ADC"), ("K2_IMON", "IMON_ADC"))):
        p.two(f"R{401 + i}", "R", "1k", 25.4 + i * 17.78, 200.66, net, adc, R0603)
    # Independent comparators: K1_FB = MID > 0.96*F1_OUT, K2_FB = ACT > 0.96*MID (+~0.16 V offset).
    comp, so8 = "Comparator:LM2903", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
    p.part("U403", comp, "LM2903 (Q1 candidate)", 175.26, 142.24,
           {"1": "K1_FB_OC", "2": "F1_CMP", "3": "MID_SENSE"}, so8, unit=1)
    p.part("U403", comp, "LM2903 (Q1 candidate)", 175.26, 175.26,
           {"7": "K2_FB_OC", "6": "MID_CMP", "5": "ACT_SENSE"}, so8, unit=2)
    p.part("U403", comp, "LM2903 (Q1 candidate)", 144.78, 208.28,
           {"4": "PGND", "8": "5V_CONTROL"}, so8, unit=3)
    p.two("C403", "C", "100n", 165.1, 208.28, "5V_CONTROL", "PGND", C0603)
    for i, (up, oc, series, out, bias, node) in enumerate([
            ("R407", "K1_FB_OC", "R409", "PWR_K1_FB", "R411", "F1_CMP"),
            ("R408", "K2_FB_OC", "R410", "PWR_K2_FB", "R412", "MID_CMP")]):
        x = 213.36 + i * 60.96
        p.two(up, "R", "10k", x, 142.24, "PWR_3V3", oc, R0603)
        p.two(series, "R", "1k", x + 17.78, 142.24, oc, out, R0603)
        p.two(bias, "R", "2M2", x + 35.56, 142.24, "PWR_3V3", node, R0603)
    notes = [
        "P0 REVIEW SHEET - NOT FOR FABRICATION. TCA9534A 0x38, ADS1115 0x48 on PWR_I2C behind PCA9615.",
        "TCA outputs power up as inputs; consumer-side 100k pulldowns hold commands Low. Stuck-High commands are gated by SAFE_GATE.",
        "ADS1115 is for ARMING diagnosis only - never the E-stop or OV cut path. AIN3 = K2 IMON.",
        "LM2903 feedback reports measured state across K1 and K2; MCU compares with command and time.",
    ]
    for i, text in enumerate(notes):
        p.note(f"note{i}", text, 25.4, 243.84 + i * 6.35)
    return p.write("Arming I/O P0: not a PCB release")


def root():
    """Board root: one sheet symbol per page; global labels join them."""
    sheets = []
    for i, page in enumerate(PAGES):
        x, y = 25.4 + (i % 3) * 91.44, 50.8 + (i // 3) * 50.8
        sheets.append(f'''  (sheet (at {x} {y}) (size 76.2 25.4) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid "{sheet_uuid(page)}")
    (property "Sheetname" "{page}" (at {x} {y - 1.27} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "{page}.kicad_sch" (at {x} {y + 26.67} 0) (effects (font (size 1.27 1.27)) (justify left top)))
    (instances (project "{BOARD}" (path "/{ROOT_UUID}" (page "{i + 2}")))))''')
    note_uid = uuid5(NAMESPACE_URL, f"ugv-01/{BOARD}/note")
    (BOARD_DIR / f"{BOARD}.kicad_sch").write_text(f'''(kicad_sch
  (version 20250114) (generator "eeschema") (generator_version "10.0")
  (uuid "{ROOT_UUID}") (paper "A4")
  (title_block (title "UGV-PWR-01 partial board hierarchy") (date "2026-09-24") (rev "P0")
    (comment 1 "INA228, regulators, TVS/regen clamp and PCB missing: not a full board"))
  (lib_symbols)
  (text "Partial PWR hierarchy for merged ERC/netlist. NOT a full board, PCB or fabrication release." (exclude_from_sim no)
    (at 25.4 25.4 0) (effects (font (size 2 2)) (justify left)) (uuid "{note_uid}"))
{chr(10).join(sheets)}
  (sheet_instances (path "/" (page "1")))
  (embedded_fonts no)
)
''')
    (BOARD_DIR / f"{BOARD}.kicad_pro").write_text(json.dumps(
        {"meta": {"filename": f"{BOARD}.kicad_pro", "version": 3},
         "sheets": [[ROOT_UUID, "Root"]] + [[sheet_uuid(pg), pg] for pg in PAGES]}, indent=2) + "\n")


if __name__ == "__main__":
    for build in (actuator_path, safety_gate, arming_io):
        print(build())
    root()
    print(BOARD_DIR / f"{BOARD}.kicad_sch")
