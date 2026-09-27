"""Pin assignment must agree with the real KiCad LQFP100 symbol."""
import json
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_mcu_pinmap import read_kicad_pins, validate  # noqa: E402

library = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/MCU_ST_STM32G4.kicad_sym")
manifest = json.loads((ROOT / "config/mcu_pinmap.json").read_text())
pins = read_kicad_pins(library, "STM32G474V_B-C-E_Tx")

assert validate(manifest, pins) == []
assert any(x["signal"] == "I2C2_SDA" and x["gpio"] == "PA8" for x in manifest["assignments"])
assert {f"PWM_{wheel}_{side}" for wheel in ("FL", "FR", "RL", "RR") for side in ("IN1", "IN2")} <= {
    x["signal"] for x in manifest["assignments"]
}
assert {"SAFETY_BKIN_TIM1", "SAFETY_BKIN_TIM8"} <= {x["signal"] for x in manifest["assignments"]}
assert {"MCU_RUN_REQ", "MCU_WDI", "PWR_ACT_EN_FB", "PWR_K1_FB", "PWR_K2_FB", "ESTOP_A_CLOSED", "ESTOP_B_CLOSED", "PWR_WD_OK"} <= {
    x["signal"] for x in manifest["assignments"]
}

old_map = deepcopy(manifest)
next(x for x in old_map["assignments"] if x["signal"] == "I2C2_SDA")["gpio"] = "PB10"
assert any("I2C2_SDA" in error for error in validate(old_map, pins)), "Old PB10 assignment must fail"

duplicate = deepcopy(manifest)
next(x for x in duplicate["assignments"] if x["signal"] == "I2C2_SCL")["gpio"] = "PA8"
assert any("duplicate" in error for error in validate(duplicate, pins))

missing = deepcopy(manifest)
missing["assignments"] = [x for x in missing["assignments"] if x["signal"] != "PWM_RR_IN2"]
assert any("PWM_RR_IN2" in error for error in validate(missing, pins)), "Fourth motor second input is required"

missing_wdi = deepcopy(manifest)
missing_wdi["assignments"] = [x for x in missing_wdi["assignments"] if x["signal"] != "MCU_WDI"]
assert any("MCU_WDI" in error for error in validate(missing_wdi, pins)), "External watchdog path is required"

# A2: four 50 Hz servos, light bar data, servo rail current and enable request.
a2 = {"SERVO_PAN", "SERVO_TILT", "SERVO_SHOULDER", "SERVO_GRIPPER", "LIGHT_DATA", "SERVO_I_SENSE", "SERVO_PWR_REQ"}
assert a2 <= {x["signal"] for x in manifest["assignments"]}
for signal in sorted(a2):
    missing_a2 = deepcopy(manifest)
    missing_a2["assignments"] = [x for x in missing_a2["assignments"] if x["signal"] != signal]
    assert any(signal in error for error in validate(missing_a2, pins)), signal

boot0 = deepcopy(manifest)
boot0["assignments"].append({"signal": "SPARE_TIM16", "gpio": "PB8", "package_pin": 95, "function": "TIM16_CH1"})
assert any("BOOT0" in error for error in validate(boot0, pins)), "PB8 is BOOT0 and must stay unused"

shared = deepcopy(manifest)
shared["assignments"].append({"signal": "SPARE_TIM20", "gpio": "PF2", "package_pin": 19, "function": "TIM20_CH3"})
assert any("TIM20" in error for error in validate(shared, pins)), "servo timers run at 50 Hz; no other users"

reused_name = deepcopy(manifest)
next(x for x in reused_name["assignments"] if x["signal"] == "FAULT_FR")["signal"] = "FAULT_FL"
assert any("duplicate signal FAULT_FL" in error for error in validate(reused_name, pins))
print("PASS: MCU pinmap matches KiCad G474 LQFP100; A2 servo/light pins present; bad I2C, duplicates, BOOT0 and shared servo timer rejected")
