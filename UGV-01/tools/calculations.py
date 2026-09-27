"""UGV-01 preliminary engineering calculation; not a motor qualification model."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def calculate(p):
    g, motion, motor, battery = (p[k] for k in ('geometry', 'motion', 'motor', 'battery'))
    positive = [g['wheel_diameter_mm'], g['track_mm'], g['wheelbase_mm'],
                motion['gross_mass_kg'], motor['stall_current_a'],
                motor['stall_torque_kg_cm'], motor['external_coupling_efficiency'],
                battery['series'], battery['parallel'], battery['cell_capacity_typ_ah']]
    if any(not math.isfinite(x) or x <= 0 for x in positive):
        raise ValueError('Physical dimensions, mass and ratings must be positive and finite')
    for key in ('energy_use_fraction', 'aging_factor'):
        if not 0 < battery[key] <= 1:
            raise ValueError('Energy factors must be in (0, 1]')
    if not 0 < motor['external_coupling_efficiency'] <= 1:
        raise ValueError('External efficiency must be in (0, 1]')
    radius = g['wheel_diameter_mm'] / 2000
    mass = motion['gross_mass_kg']
    theta = math.radians(motion['grade_deg'])
    gravity = 9.80665
    eta = motor['external_coupling_efficiency']
    stall_torque = motor['stall_torque_kg_cm'] * 0.0980665
    force = mass * gravity * (math.sin(theta) + motion['rolling_resistance_hard']*math.cos(theta))
    torque = force * radius * motion['wheel_load_factor'] / (4*eta)
    i0 = motor['no_load_current_a']
    kt = stall_torque / (motor['stall_current_a'] - i0)  # output N.m per A above no-load, linear model
    amps = lambda t: i0 + t / kt
    current = amps(torque)
    # A3 (R4/R7): series ballast, accelerating up the ramp, and the conservative pivot scrub moment
    # M = mu m g L / 2 shared by four wheels on the track B.
    winding, ballast = motor['nominal_voltage_v'] / motor['stall_current_a'], motor.get('ballast_ohm', 0.0)
    accel_torque = (force + mass*motion['acceleration_m_s2']) * radius * motion['wheel_load_factor'] / (4*eta)
    scrub = motion['friction_nominal'] * mass * gravity * g['wheelbase_mm'] / 1000 / 2
    pivot_torque = scrub * radius / (2 * g['track_mm'] / 1000 * eta)
    full = battery['series'] * battery['cell_voltage_full_v']
    nominal = battery['series'] * battery['cell_voltage_nominal_v']
    empty = battery['series'] * battery['cell_voltage_cutoff_v']
    # Recheck F2: every voltage path also crosses the H-bridge (TB6612 0.7 V max at 1 A), and a pivot also
    # rolls the wheels. The stall-current bound above stays bridge-free (higher current = conservative).
    path = winding + ballast + p['motor_driver']['bridge_ohm_max']
    ke = (motor['nominal_voltage_v'] - i0*winding) / motor['no_load_rpm']  # V per output rpm (back-EMF)
    roll = mass * gravity * motion['rolling_resistance_hard'] * radius / (4*eta)  # per wheel, even share
    per_mu = pivot_torque / motion['friction_nominal']  # scrub torque per unit floor friction
    turn_rpm = motion['turn_rate_rad_s'] * g['track_mm'] / 2000 / (2 * math.pi * radius) * 60

    # N2: the core's PI loop may apply up to the pack voltage, but its back-EMF limiter keeps
    # |V - EMF| / R_min <= I_LIMIT, so the current through the nominal path is capped at I_LIMIT R_min / R.
    drv = p['motor_driver']
    path_min = winding*0.9 + ballast*0.95 + drv['bridge_ohm_typ']
    i_cap = drv['backemf_limit_a'] * path_min / path

    def pivot_mu(volts, rpm):
        """Highest floor friction a pivot sustains at this pack voltage and wheel speed (model)."""
        available = kt * (min((volts - ke*rpm) / path, i_cap) - i0)
        return max(available - roll, 0.0) / per_mu

    def speed(volts, t):
        """Wheel speed at a load torque through winding + ballast + bridge (back-EMF)."""
        rpm = (volts - amps(t)*path) / ke
        return max(rpm, 0.0) * 2 * math.pi * radius / 60
    flat_torque = mass * gravity * motion['rolling_resistance_hard'] * radius * motion['wheel_load_factor'] / (4*eta)
    # Recheck F1: two channels share one TB6612 (loss = 2 I^2 R_bridge). Allowance from the IC-only rating
    # derated to the enclosure; currents through the conservative path (winding -10 %, ballast -5 %, bridge typ).
    allowance = (drv['tj_max_c'] - drv['enclosure_ambient_c']) * drv['pd_ic_only_w'] / (drv['tj_max_c'] - 25)
    chip = lambda amps_each: 2 * amps_each**2 * drv['bridge_ohm_max']
    counts = motor['gear_ratio']*motor['encoder_counts_motor_rev']
    energy = battery['series']*battery['cell_voltage_nominal_v']*battery['parallel']*battery['cell_capacity_typ_ah']
    minimum = energy*battery['cell_capacity_min_ah']/battery['cell_capacity_typ_ah']
    budget = p['mass_budget']
    curb = sum(x['mass_kg'] for x in budget)
    if curb <= 0:
        raise ValueError('Mass budget must be positive')
    aged = minimum*battery['energy_use_fraction']*battery['aging_factor']
    return {
        'battery_wh': energy, 'battery_min_wh': minimum,
        'aged_usable_min_wh': aged,
        'runtime_typical_h': aged/battery['duty_power_typical_w'],
        'runtime_heavy_h': aged/battery['duty_power_heavy_w'],
        'curb_mass_kg': curb,
        'curb_cg_x_mm': sum(x['mass_kg']*x['x_mm'] for x in budget)/curb,
        'curb_cg_z_mm': sum(x['mass_kg']*x['z_mm'] for x in budget)/curb,
        'loaded_cg_z_mm': (sum(x['mass_kg']*x['z_mm'] for x in budget)
                           + motion['payload_kg']*motion['payload_cg_z_mm'])
                          / (curb + motion['payload_kg']),
        'flat_rolling_force_n': mass*gravity*motion['rolling_resistance_hard'],
        'grade_force_n': force, 'grade_motor_torque_nm': torque,
        'grade_motor_current_a': current,
        'accel_grade_motor_torque_nm': accel_torque, 'accel_grade_motor_current_a': amps(accel_torque),
        'pivot_scrub_moment_nm': scrub, 'pivot_motor_torque_nm': pivot_torque,
        'pivot_rolling_torque_nm': roll, 'pivot_motor_current_a': amps(pivot_torque + roll),
        'stall_current_full_pack_a': full / (winding + ballast),
        'stall_current_empty_pack_a': empty / path,
        'pivot_friction_limit_empty_pack': pivot_mu(empty, 0.0),  # zero wheel speed: break-away only
        'pivot_turn_wheel_rpm': turn_rpm,
        'pivot_friction_limit_turning_empty': pivot_mu(empty, turn_rpm),
        'pivot_friction_limit_turning_nominal': pivot_mu(nominal, turn_rpm),
        'pivot_friction_limit_turning_full': pivot_mu(full, turn_rpm),
        'tb6612_allowance_w': allowance,
        'pivot_current_cap_a': i_cap,
        'tb6612_limited_stall_w': chip(drv['backemf_limit_a']),  # the core's estimate at the limiter
        'tb6612_ceiling_motor_w': chip(motor['continuous_current_design_ceiling_a']),
        'tb6612_fault_full_duty_stall_w': chip(full * 1.01 / path_min),
        'no_load_speed_m_s': motor['no_load_rpm']*2*math.pi*radius/60,
        'flat_speed_empty_pack_m_s': speed(empty, flat_torque),
        'grade_speed_empty_pack_m_s': speed(empty, torque),
        'encoder_counts_output_rev': counts,
        'minimum_speed_counts_per_ms': motion['minimum_controlled_speed_m_s']/(2*math.pi*radius)*counts/1000,
        'kinetic_energy_j': 0.5*mass*motion['maximum_speed_m_s']**2,
        'static_pitch_tip_deg': math.degrees(math.atan((g['wheelbase_mm']/2-motion['cg_max_abs_x_mm'])/motion['loaded_cg_max_z_mm'])),
        'plate_gross_mass_kg': g['plate_length_mm']*g['plate_width_mm']*g['plate_thickness_mm']
                               * g['plate_density_g_cm3']*1e-6,
    }


if __name__ == '__main__':
    p = json.loads((ROOT/'config/vehicle.json').read_text())
    result = calculate(p)
    (ROOT/'docs/calculation_results.json').write_text(json.dumps(result, indent=2)+'\n')
    ceiling = p['motor']['continuous_current_design_ceiling_a']
    grade = p['motion']['grade_deg']
    lines = [f"# Tekrar üretilebilir ön hesap raporu — {p['revision']}", '',
             'Kaynak: config/vehicle.json; güç profilleri docs/electrical_architecture.md §6. Üretim/deney onayı değildir.', '',
             '| Metrik (birim isimde) | Değer |', '|---|---:|']
    lines += [f'| {k} | {v:.6f} |' for k,v in result.items()]
    lines += ['', 'Model: F=mg(sinθ+Crr cosθ); T=Fr·k/(4η); I=I0+(Is−I0)T/Tstall.',
              'η yalnız dış kaplin/yatak kaybıdır; üretici gearbox çıkış torkuna ikinci dişli verimi uygulanmaz.',
              'Akım/hız doğrusal taramadır; PWM RMS, sıcak sargı ve lastik kaymasını çözmez.',
              'Çalışma süreleri minimum kapasite ×0,80 kullanım ×0,85 yaşlanma / ölçülmemiş görev gücü ile hesaplanır.',
              f"{p['battery']['duty_power_typical_w']:.1f} W tipik profilde 60 dakika hedefi ön hesapla "
              f"{'desteklenir' if result['runtime_typical_h'] >= 1 else 'DESTEKLENMEZ'}; "
              f"{p['battery']['duty_power_heavy_w']:.1f} W ağır profilde "
              f"{'desteklenir' if result['runtime_heavy_h'] >= 1 else 'desteklenmez'}.",
              'Statik devrilme açısı dinamik saha eğimi veya fren garantisi değildir.', '',
              '## Yük paylaşımı ve zemin duyarlılığı', '',
              f"| Zemin / katsayı | En yüklü motor torku N·m | Tarama akımı A | {ceiling:g} A tavan |",
              '|---|---:|---:|---|']
    for rolling, label in [(0.03,f'Sert {grade:g}°'),(0.08,f'Pürüzlü {grade:g}°')]:
        for factor in (1.5,1.6):
            q=json.loads(json.dumps(p))
            q['motion']['rolling_resistance_hard']=rolling
            q['motion']['wheel_load_factor']=factor
            x=calculate(q)
            lines.append(f"| {label} / {factor} | {x['grade_motor_torque_nm']:.3f} | {x['grade_motor_current_a']:.3f} | {'KOŞULLU' if x['grade_motor_current_a'] <= ceiling else 'AŞIYOR'} |")
    driver = p['motor_driver']['recommended_iout_max_a']
    rate = p['motion']['turn_rate_rad_s']
    lines += ['', '## Balast, ivme ve yerinde dönüş (R4/R7, yeniden kontrol F2)', '',
              f"Her motorun önünde {p['motor']['ballast_ohm']:g} Ω seri direnç var: tam dolu pakette sıkışma akımı "
              f"{result['stall_current_full_pack_a']:.3f} A ≤ TB6612 önerilen {driver:g} A. Bu akım sınırı tek başına "
              "süresiz ısıl uygunluk kanıtı değildir (iki kanal aynı çipte; bkz. Lite çekirdeği ısı bütçesi). "
              f"5° rampada 0,5 m/s² ivme {result['accel_grade_motor_current_a']:.3f} A ister.",
              'Yerinde dönüş kaba, muhafazakâr kayma modeliyle: M=µmgL/2, motor başına T=Mr/(2Bη), artı teker başına '
              'yuvarlanma mgCrr·r/(4η); gerilim yolu sargı + balast + TB6612 köprüsü (en çok 0,7 Ω, 1 A\'de 0,7 V). '
              'N2: çekirdeğin PI hız döngüsü paket gerilimine kadar çıkabilir; akım geri-EMK sınırlayıcıyla '
              f"{result['pivot_current_cap_a']:.3f} A ile kırpılır (sabit gerilim tavanı yok). "
              f"Kopma (0 hız) ile {rate:g} rad/s dönüş ({result['pivot_turn_wheel_rpm']:.1f} dev/dk teker, geri EMK payı) ayrıdır. "
              'Satırlar model duyarlılığıdır; ölçüm değildir.', '',
              '| Zemin µ | Motor torku N·m | Akım A | Kopma, boş 9,6 V | Dönüş, boş 9,6 V | Dönüş, nominal 10,8 V | Dönüş, dolu 12,6 V |',
              '|---:|---:|---:|---|---|---|---|']
    ok = lambda mu, limit: 'döner' if mu <= limit else 'durur'
    for mu in (0.3, 0.4, 0.45, 0.6):
        q = json.loads(json.dumps(p))
        q['motion']['friction_nominal'] = mu
        x = calculate(q)
        lines.append(f"| {mu:g} | {x['pivot_motor_torque_nm'] + x['pivot_rolling_torque_nm']:.3f} | "
                     f"{x['pivot_motor_current_a']:.3f} | {ok(mu, result['pivot_friction_limit_empty_pack'])} | "
                     f"{ok(mu, result['pivot_friction_limit_turning_empty'])} | "
                     f"{ok(mu, result['pivot_friction_limit_turning_nominal'])} | "
                     f"{ok(mu, result['pivot_friction_limit_turning_full'])} |")
    lines += ['', f"Sınır µ: kopma boş pakette {result['pivot_friction_limit_empty_pack']:.3f}; {rate:g} rad/s dönüşte boş "
              f"{result['pivot_friction_limit_turning_empty']:.3f}, nominal {result['pivot_friction_limit_turning_nominal']:.3f}, "
              f"dolu {result['pivot_friction_limit_turning_full']:.3f}. Üstünde teker sınırlı akımda durur, Lite çekirdeğinin "
              'stall/ısı korumaları keser ve yürütücü hata döndürür. Pivot akımı, ısınma ve gerçek µ fiziksel testte ölçülür (NOT_RUN).']
    drv = p['motor_driver']
    lines += ['', '## TB6612 ısıl sınır (yeniden kontrol F1)', '',
              f"İki kanal aynı çipte: kayıp 2·I²·{drv['bridge_ohm_max']:g} Ω. Çip tek başına {drv['pd_ic_only_w']:g} W "
              f"(25 °C, Tj {drv['tj_max_c']} °C), gövde içi {drv['enclosure_ambient_c']} °C varsayımıyla "
              f"{result['tb6612_allowance_w']:.3f} W. Akımlar muhafazakâr yoldan (sargı −%10, balast −%5, köprü tipik).",
              '', '| Durum | Çip kaybı W | Süre |', '|---|---:|---|',
              f"| İki motor 0,6 A sürekli tavanda | {result['tb6612_ceiling_motor_w']:.3f} | sınırda: 0,5 W payının hemen üstü, bütçe ≈8 dakikada dolar |",
              f"| Hız döngüsü: iki teker akım sınırlayıcıda duruk ya da çok yavaş (tahmin {p['motor_driver']['backemf_limit_a']:g} A) | "
              f"{result['tb6612_limited_stall_w']:.3f} | 300 ms stall kesmesi; dönüyorsa ısı bütçesi 2 J → ≈3 s |",
              f"| Firmware arızası: tam görev, iki kanal sıkışık, dolu paket | {result['tb6612_fault_full_duty_stall_w']:.3f} | "
              f"{drv['pd_board_50mm_w']:g} W kart değerini aşar: 300 ms stall kesmesi + çip ısıl kapanması + watchdog |",
              '', 'Kanal akımının 1 A altında olması süresiz ısıl uygunluk kanıtı değildir. Isı bütçesi sabitleri '
              '`firmware/lite/lite_core.h`\'dedir ve `tests/check_design.py` bu tabloyla karşılaştırır. Gerçek ısınma TL1\'de ölçülür (NOT_RUN).']
    (ROOT/'docs/calculation_results.md').write_text('\n'.join(lines)+'\n')
    print('Wrote calculation_results.json and .md')
