"""A3 Lite mass screen: printed estimates stay inside the mass budget; filament fits the spools (M3: 3 PETG)."""
import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('body_mass_screen', root/'tools/body_mass_screen.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result = module.screen(root)
groups = result['groups']
assert result['revision'] == 'A3'
assert {k: v['parts'] for k, v in groups.items()} == {
    'base': 12, 'body': 21, 'bumpers': 3, 'wheels': 8, 'head': 15, 'arms': 42}, groups  # DD93: claw jaws, pads, washer; DD94: left stand-ins (R04), jaw B spacers (R05)
for name, group in groups.items():
    assert group['printed_kg'] <= group['solid_kg'] + 1e-9, (name, group)
    assert group['printed_margin_kg'] > 0, (name, group)  # print estimate inside its allocation
filament = result['filament_g']
assert 2100 < filament['PETG']['printed'] < 2400 and 250 < filament['TPU']['printed'] < 320, filament  # M3 body + arm
# With 25 % waste/supports: three 1 kg PETG spools and one TPU spool (M3; A3 had two PETG).
assert filament['PETG']['printed']*1.25 <= 3000 and filament['TPU']['printed']*1.25 <= 1000, filament
# N4 (M3 review): the CG for every arm pose the core lets the vehicle drive in and every payload placement allowed
# while driving, not one stow budget. The arms allocation sits at the CAD centroid of the arms group (printed-estimate
# weights) moved to the pose; the same 0.5 kg payload is only redistributed (lid / 0.15 kg in the cargo bin / 0.15 kg
# in the gripper), never added twice. The budget's arm entry is that centroid at stow, y included.
import json  # noqa: E402
config = json.loads((root/'config/vehicle.json').read_text())
motion, arm = config['motion'], config['geometry']['arm']
entry = next(b for b in config['mass_budget'] if b['name'].startswith('arms'))
stow_c = result['arm_centroid_stow']
assert all(abs(e - c) <= 3 for e, c in zip((entry['x_mm'], entry.get('y_mm', 0), entry['z_mm']), stow_c)), (entry, stow_c)
cg = result['cg']


def inside(c):
    return (abs(c['x']) <= motion['cg_max_abs_x_mm'] and abs(c['y']) <= motion['cg_max_abs_y_mm']
            and c['z'] <= motion['loaded_cg_max_z_mm'] and c['pitch_tip_deg'] >= 30 and c['roll_tip_deg'] >= 30)


for pose in arm['drive_poses']:
    for case in ('lid', 'bin'):
        assert inside(cg[pose][case]), (pose, case, cg[pose][case])
# Teeth: the raised poses the review found (lift/up z ~139, ready x ~26) fail the same test, and a 150 g object held
# in the gripper at ready tips at < 30 deg; that is why driving needs the arm at stow (core and executor).
assert not any(inside(cg[p]['lid']) for p in ('lift', 'up', 'ready')), {p: cg[p]['lid'] for p in ('lift', 'up', 'ready')}
assert cg['ready']['gripper']['pitch_tip_deg'] < 30, cg['ready']['gripper']
# Held at stow (at the real grasp datum, R06): since the left arm's stand-ins (R04) balance the arms, it stays inside
# the y target and >= 30 deg; the claw still drives closed and empty (DD93/94: its envelope, objects ride in the bin).
held = cg['stow']['gripper']
assert abs(held['y']) <= motion['cg_max_abs_y_mm'] and held['pitch_tip_deg'] >= 30 and held['roll_tip_deg'] >= 30, held
print('PASS: A3 printed mass estimates inside allocations; filament fits 3 PETG + 1 TPU spools; N4: CG inside '
      'x/y/z limits and >= 30 deg static tip for every drive pose and payload placement (arm entry = CAD stow '
      'centroid); raised poses shown to break it')
