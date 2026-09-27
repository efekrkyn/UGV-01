"""Regression: unit conversions, load scaling and energy/reserve arithmetic."""
from pathlib import Path
import copy
import importlib.util
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
module_path = ROOT / 'tools/calculations.py'
assert module_path.exists(), 'Missing reproducible engineering calculation implementation'
spec = importlib.util.spec_from_file_location('calculations', module_path)
calc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calc)
p = json.loads((ROOT / 'config/vehicle.json').read_text())
r = calc.calculate(p)
assert p['revision'] == 'A3', p['revision']
# A3 Lite: 3S1P 18650 3.0 Ah (min 2.85 Ah), 80 % use, 85 % ageing.
assert math.isclose(r['battery_wh'], 32.4), r
aged = 32.4 * 2.85 / 3.0 * 0.8 * 0.85
assert math.isclose(r['aged_usable_min_wh'], aged), r
assert math.isclose(r['runtime_typical_h'], aged/p['battery']['duty_power_typical_w']), r
assert math.isclose(r['runtime_heavy_h'], aged/p['battery']['duty_power_heavy_w']), r
assert r['runtime_typical_h'] >= 1.0, r  # 60 min target on the typical Lite duty profile
# M3: 5.1 kg gross (character body + 5-axis arm), 5 deg indoor ramp, JGA25-370 12 V 77 rpm 1:78 (1.8 A stall) behind
# a 7.5 ohm ballast.
assert p['motion']['gross_mass_kg'] == 5.1
assert math.isclose(r['flat_rolling_force_n'], 5.1*9.80665*0.03), r
assert 0.138 < r['grade_motor_torque_nm'] < 0.140, r
assert r['grade_motor_current_a'] <= p['motor']['continuous_current_design_ceiling_a'], r
assert math.isclose(r['encoder_counts_output_rev'], 78*22), r  # channel A, both edges, all four motors
assert r['minimum_speed_counts_per_ms'] > 0.1, r
assert math.isclose(r['kinetic_energy_j'], 0.5*5.1*0.3**2), r  # 5.1 kg at 0.3 m/s
# R7: accelerating up the ramp and pivoting in place are in the gate (conservative scrub M = mu m g L / 2).
# M3: the 278 mm track (was 240) offsets part of the heavier robot's scrub (L/B 0.76 instead of 0.88).
assert 3.15 < r['pivot_scrub_moment_nm'] < 3.16 and 0.357 < r['pivot_motor_torque_nm'] < 0.359, r
assert 0.198 < r['accel_grade_motor_torque_nm'] < 0.201, r  # 5 deg + 0.5 m/s2
assert r['accel_grade_motor_current_a'] <= p['motor']['continuous_current_design_ceiling_a'], r
# R4: the ballast bounds a stalled motor at a full pack below the TB6612 1.0 A operating limit.
assert r['stall_current_full_pack_a'] <= p['motor_driver']['recommended_iout_max_a'], r
# Recheck F2 regression: with rolling resistance (and the H-bridge drop) a mu = 0.45 floor does NOT pivot
# on an empty 9.6 V pack even at zero wheel speed; the old scrub-only model claimed it did.
q = copy.deepcopy(p)
q['motion']['friction_nominal'] = 0.45
x = calc.calculate(q)
assert 0.679 < x['pivot_motor_current_a'] and 9.6 / (12/1.8 + 7.5) < x['pivot_motor_current_a'], x
assert r['pivot_friction_limit_empty_pack'] < 0.45, r  # break-away limit, zero speed, empty pack
assert 0.023 < r['pivot_rolling_torque_nm'] < 0.024, r
# Turning at the executor's yaw rate needs back-EMF headroom: the envelope is lower than break-away.
exec_src = (ROOT / 'software/ugv_ai/executor.py').read_text()
assert f"TURN_RATE_RAD_S = {p['motion']['turn_rate_rad_s']}" in exec_src, 'executor turn rate = config'
assert (r['pivot_friction_limit_turning_empty'] < r['pivot_friction_limit_turning_nominal']
        < r['pivot_friction_limit_turning_full'] < p['motion']['friction_nominal']), r
# M3: the executor turns at 0.45 rad/s (was 0.6) to keep back-EMF headroom for the heavier robot.
assert p['motion']['turn_rate_rad_s'] == 0.45
assert 0.29 < r['pivot_friction_limit_turning_empty'] < 0.31 < 0.35 < r['pivot_friction_limit_turning_nominal'] < 0.37, r
# Recheck F1: a per-channel current below 1.0 A is not an unlimited-duration thermal proof. A firmware
# fault at full duty with both channels of one TB6612 stalled exceeds even the 0.89 W board rating; only
# the 300 ms stall cut, the thermal budget and the chip's own shutdown bound it in time.
drv = p['motor_driver']
assert r['tb6612_fault_full_duty_stall_w'] > drv['pd_board_50mm_w'], r
core_h = (ROOT / 'firmware/lite/lite_core.h').read_text()
const = lambda name: float(re.search(rf'#define {name} ([0-9.]+)f', core_h).group(1))
cont, heat = const('LITE_CHIP_CONT_W'), const('LITE_CHIP_HEAT_J')
assert r['tb6612_ceiling_motor_w'] - 0.01 <= cont <= r['tb6612_allowance_w'] - 0.05, (cont, r)  # PWM-loss margin
# N2 (M3 review, user decision 25.09.2026): the core runs a PI speed loop with no fixed voltage ceiling; a stalled
# or overloaded wheel is bounded by the back-EMF limiter (estimate <= I_LIMIT), then the thermal budget trips a
# pair of such wheels within seconds and the 300 ms stall cut stops a wheel that does not turn at all.
assert const('LITE_I_LIMIT_A') == drv['backemf_limit_a'] < drv['recommended_iout_max_a']
assert 'LITE_KP_MV_PER_RPM' in core_h and 'LITE_KI_MV_PER_RPM_S' in core_h and 'CEIL' not in core_h
assert math.isclose(r['tb6612_limited_stall_w'], 2 * drv['backemf_limit_a']**2 * drv['bridge_ohm_max']), r
assert cont < r['tb6612_limited_stall_w'] and heat / (r['tb6612_limited_stall_w'] - cont) <= 5, r
# The pivot model uses the current the limiter allows (the firmware's own bound), not an unbounded path.
assert r['pivot_current_cap_a'] < drv['backemf_limit_a'] and r['pivot_friction_limit_turning_full'] < 0.46, r
# Speed limits are reachable on an empty pack through the ballast (flat, and on the 5 deg ramp).
assert r['flat_speed_empty_pack_m_s'] >= p['motion']['maximum_speed_m_s'], r
assert r['grade_speed_empty_pack_m_s'] >= p['motion']['grade_speed_limit_m_s'], r
assert 'bulk_delta_energy_j' not in r  # A2 PWR-board bulk capacitor, gone in Lite
assert math.isclose(r['plate_gross_mass_kg'], 300*232*5*1.27e-3/1000), r  # printed PETG plate, solid
assert r['curb_mass_kg'] <= p['motion']['curb_mass_limit_kg'], r
assert r['loaded_cg_z_mm'] <= p['motion']['loaded_cg_max_z_mm'] - 2, r
assert r['static_pitch_tip_deg'] >= 30, r  # M3: CG limit 135 mm (taller body, payload on the lid at z250)
assert p['motion']['curb_mass_limit_kg'] + p['motion']['payload_kg'] <= p['motion']['gross_mass_kg'], p['motion']
q = copy.deepcopy(p)
q['motion']['gross_mass_kg'] = 2 * p['motion']['gross_mass_kg']
assert math.isclose(calc.calculate(q)['grade_motor_torque_nm'], 2*r['grade_motor_torque_nm'])
q['geometry']['wheel_diameter_mm'] = 0
try:
    calc.calculate(q)
except ValueError:
    pass
else:
    raise AssertionError('Zero wheel diameter must be rejected')
# N5/N7 (M3 review): TL4 accepts the servo supply and case temperature the config holds (the data-sheet floor the
# torques assume), measured at the servo connector, and quotes the current CAD park -> lift clearance.
tl4 = (ROOT / 'docs/test_plan.md').read_text().split('**TL4')[1].split('- **TL')[0]
arm = p['geometry']['arm']
dec = lambda x: f'{x:g}'.replace('.', ',')  # noqa: E731
assert f"servo konektöründe ≥{dec(arm['servo_supply_min_v'])} V" in tl4 and f"≤{arm['servo_case_max_c']} °C" in tl4, tl4
lift = next(c for c in json.loads((ROOT / 'cad/assembly/manifest.json').read_text())['arm_clearance']
            if c['pose'] == ['stow', 'lift'])
assert f"CAD {dec(lift['moving_mm'])} mm" in tl4, (lift, tl4)
print('PASS: engineering units, load scaling, reserve, pivot envelope with rolling + bridge losses (F2), '
      'TB6612 two-channel thermal allowance vs Lite core constants (F1) and invalid-input checks; TL4 servo supply/'
      'temperature from config and CAD clearance (N5/N7)')
