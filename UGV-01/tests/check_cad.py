"""Check generated A3 Lite solids, shared dimensions, clearances, arm poses and printable envelopes."""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT/'cad/assembly/manifest.json'
assert manifest_path.exists(), 'Missing generated CAD and geometry manifest'
import cadquery as cq
p = json.loads((ROOT/'config/vehicle.json').read_text())
m = json.loads(manifest_path.read_text())
assert m['parameters'] == p, 'CAD stale: regenerate from current vehicle.json'
g = p['geometry']
bounds = []
for part in m['parts']:
    shape = cq.importers.importStep(str(ROOT/part['step'])).val()
    assert shape.isValid() and shape.Volume() > 0, part['name']
    b = shape.BoundingBox()
    bounds.append(b)
    if part['printable']:
        assert max(b.xlen, b.ylen, b.zlen) <= g['print_design_limit_mm'], part['name']
assert not m['unapproved_intersections'], m['unapproved_intersections']
names = {part['name'] for part in m['parts']}
WHEELS = ('FL', 'FR', 'RL', 'RR')
ARM = {f'UGV-MECH-05{k}-{s}' for k in range(5) for s in ('-1', '+1')} | {'UGV-MECH-056--1', 'UGV-MECH-057-+1'}
ARM_REF = {f'REF-SERVO-{j}-R' for j in ('SHOULDER', 'TWIST', 'ELBOW', 'WRIST', 'ROLL', 'GRIPPER')} | {
    'REF-BEARING-SHOULDER--1', 'REF-BEARING-SHOULDER-+1', 'REF-BEARING-TWIST-R'}
required = {'UGV-MECH-040', 'UGV-MECH-041', 'UGV-MECH-042', 'UGV-MECH-043--1', 'UGV-MECH-043-+1',
            'REF-SERVO-PAN', 'REF-SERVO-TILT', 'REF-EYE-CAMERA--1', 'REF-EYE-CAMERA-+1', 'REF-LIGHT-BAR',
            'REF-BEARING-PAN', *ARM, *ARM_REF, *(f'UGV-MECH-015-{w}' for w in WHEELS)}
assert required <= names, required - names
assert not any(n.endswith('-L') and n.startswith('REF-SERVO') for n in names), 'left arm is passive'
assert not {'UGV-MECH-052', 'UGV-MECH-053', 'REF-AXLE-SHOULDER'} & names, 'A3 geared shoulder tower removed (M3)'
assert 'REF-FRONT-CAMERA' not in names and 'REF-MAST-COLUMN' not in names
lite = {'UGV-MECH-001-F', 'UGV-MECH-001-R', 'REF-BATTERY', 'REF-ELECTRONICS', 'REF-ESTOP',
        'REF-TOF--1', 'REF-TOF-+1', *(f'{p}-{w}' for p in ('UGV-MECH-003', 'UGV-MECH-060', 'UGV-MECH-061',
                                                         'REF-MOTOR') for w in WHEELS)}
assert lite <= names, lite - names
assert not names & {'UGV-MECH-001', 'REF-CM5-IO', 'REF-PWR-PCB', 'REF-MCU-PCB'}, 'A2 compute/PWR parts left'
assert not any(n.startswith('REF-WHEEL') for n in names), 'wheels are printed hub + tyre in A3'
assert all(p['printable'] for p in m['parts'] if p['name'].startswith('UGV-MECH')), 'Lite: every own part is printed'
assert m['revision'] == 'A3' and (ROOT/'cad/assembly/generated/UGV-01-A3-concept.step').exists()
step = lambda name: cq.importers.importStep(str(ROOT/f'cad/assembly/generated/{name}.step')).val()
probe = lambda r, length, start, axis: cq.Solid.makeCylinder(r, length, cq.Vector(*start), cq.Vector(*axis))
cube = lambda size, centre: cq.Workplane('XY').box(*size).translate(centre).val()
W, wall, top = g['body_width_mm'], g['wall_thickness_mm'], g['body_top_z_mm']
lid_z = top - g['lid_thickness_mm']
inner_wall = W/2 - wall
fast, axle = g['fasteners'], g['wheel_axle_z_mm']
ins_d, ins_depth = fast['m3_insert_hole_mm']

# M3 Task 1 (DD72): character body 236 wide, top z210; the camera keeps its 122 mm above the body.
assert (W, top, g['track_mm'], g['overall_width_mm']) == (236, 210, 278, 308)
assert g['tilt_axis_z_mm'] - top == 122, 'camera-to-body distance'
assert math.isclose(step('UGV-MECH-040').BoundingBox().zmin, top + 6, abs_tol=1e-3), 'pan base on the flange'
assert max(step(f'UGV-MECH-013-{k}').BoundingBox().zmax for k in (1, 2, 3)) <= top + 1e-3
assert math.isclose(step('UGV-MECH-011-+1').BoundingBox().ymax, W/2, abs_tol=1e-3)
# Motors (gearbox + can) sit wholly inside the side walls; only the bushing and D-shaft reach out.
# JGA25 D-shaft engages the printed hub boss by >= 7 mm on every wheel; the boss crosses the wall in an 18 mm hole.
for w in WHEELS:
    x = g['wheelbase_mm']/2 * (1 if w[0] == 'F' else -1)
    side = 1 if w[1] == 'L' else -1
    motor, hub_shape = step(f'REF-MOTOR-{w}'), step(f'UGV-MECH-060-{w}')
    outside = cube((60, 100, 60), (x, side*(inner_wall + 50), axle)).cut(probe(3.6, 600, (x, -300, axle), (0, 1, 0)))
    assert motor.intersect(outside).Volume() < 0.01, (w, 'motor body outside the wall')
    mb, hb = motor.BoundingBox(), hub_shape.BoundingBox()
    engage = mb.ymax - hb.ymin if side > 0 else hb.ymax - mb.ymin
    assert engage >= 7, (w, engage)
    panel = step(f"UGV-MECH-0{10 if x < 0 else 12}-{side:+d}")
    hole = g['hub_wall_hole_diameter_mm']/2
    assert panel.intersect(probe(hole - 0.2, 20, (x, side*(W/2 - 10), axle), (0, side, 0))).Volume() < 0.01, w
    ring = probe(13, 20, (x, side*(W/2 - 10), axle), (0, side, 0)).cut(probe(hole + 0.5, 20, (x, side*(W/2 - 10), axle), (0, side, 0)))
    assert panel.intersect(ring).Volume() > 100, (w, 'wall hole is only the hub boss, not the gearbox')
    assert hub_shape.intersect(probe(g['hub_boss_radius_mm'] - 0.5, 4, (x, side*(W/2 - 2), axle), (0, side, 0))).Volume() > 50, w

# M2 Task 1: printable drivetrain interfaces. Clamp split at the motor axis into cradle + cap; two M3
# bolts run cap -> cradle -> base plate (nuts under the plate); the hub bore is a D (JGA25 flat) with an
# M3 set screw onto the flat, in the gap between the body wall and the wheel, and a nut slot open toward
# the motor; ribs stop the TPU tyre turning.
face = g['motor_face_abs_y_mm']
hub_in = g['track_mm']/2 - g['wheel_width_mm']/2  # hub rim inner face |y|
for w in WHEELS:
    x = g['wheelbase_mm']/2 * (1 if w[0] == 'F' else -1)
    side = 1 if w[1] == 'L' else -1
    cradle, cap, plate = step(f'UGV-MECH-003-{w}'), step(f'UGV-MECH-004-{w}'), step(f"UGV-MECH-001-{w[0]}")
    assert math.isclose(cradle.BoundingBox().zmax, axle, abs_tol=1e-3) and math.isclose(cap.BoundingBox().zmin, axle, abs_tol=1e-3), w
    yc = side * (face - 38)
    for dx in (-g['motor_bracket_bolt_dx_mm'], g['motor_bracket_bolt_dx_mm']):
        bolt = probe(fast['m3_clear_mm']/2 - 0.2, 60, (x + dx, yc, g['plate_bottom_z_mm'] - 1), (0, 0, 1))
        assert all(part.intersect(bolt).Volume() < 0.01 for part in (cradle, cap, plate)), (w, dx)
    hub = step(f'UGV-MECH-060-{w}')
    boss_end = hub.BoundingBox().ymin if side > 0 else -hub.BoundingBox().ymax
    bore = hub.intersect(probe(p['motor']['shaft_diameter_mm']/2 + 0.05, 7, (x, side*boss_end, axle), (0, side, 0))).Volume()
    assert 1.0 < bore < 0.25 * math.pi * 2.05**2 * 7, (w, bore)  # material only on the D flat side
    ys = side * (face + g['hub_set_screw_mm'])
    assert W/2 + 1.7 < abs(ys) < hub_in - 1.7, (w, 'set screw reachable in the body-wheel gap')
    assert hub.intersect(probe(1.3, 6, (x, ys, axle + 2.2), (0, 0, 1))).Volume() < 0.01, w  # set screw path
    nut_len = abs(ys) - boss_end + 1
    nut = cube((fast['m3_nut_af_mm'] - 0.6, nut_len, fast['m3_nut_t_mm'] - 0.6), (x, side*(boss_end + nut_len/2 - 1), axle + 4.2))
    assert hub.intersect(nut).Volume() < 0.01, w  # nut slot open from the motor-side boss end
    ring = probe(g['tyre_inner_diameter_mm']/2 + 1.5, 20, (x, side*(hub_in + 5), axle), (0, side, 0)).cut(
        probe(g['tyre_inner_diameter_mm']/2, 20, (x, side*(hub_in + 5), axle), (0, side, 0)))
    assert hub.intersect(ring).Volume() > g['hub_ribs'] * 20, w  # anti-rotation ribs into the tyre
    # Fender (track-style top) covers the wheel top and never touches the tyre.
    fender = step(f'UGV-MECH-015-{w}')
    assert fender.intersect(probe(3, 5, (x, side*g['track_mm']/2, 123.5), (0, 0, 1))).Volume() > 50, w
    tyre_3mm = probe(g['wheel_diameter_mm']/2 + 3, g['wheel_width_mm'], (x, side*hub_in if side > 0 else -hub_in - g['wheel_width_mm'], axle), (0, 1, 0))
    assert fender.intersect(tyre_3mm).Volume() < 0.01, w  # >= 3 mm over the tyre

# M2 Task 2: lid screws go into M3 heat-set inserts in the panel bosses; the head is clamped by four M3
# bolts from a beam under the lid, through lid and mast flange into inserts in the pan base, clear of the
# lid seam at x = 50.
seg = g['body_length_mm'] / 3
boss_y = W/2 - 6
for module, cx in ((10, -seg), (11, 0), (12, seg)):
    for side in (-1, 1):
        panel = step(f'UGV-MECH-{module:03d}-{side:+d}')
        for bx in (cx - 38, cx + 38):
            assert panel.intersect(probe(ins_d/2 - 0.05, ins_depth, (bx, side*boss_y, lid_z - ins_depth), (0, 0, 1))).Volume() < 0.01
            assert panel.intersect(probe(ins_d/2 + 1.5, 4, (bx, side*boss_y, lid_z - ins_depth), (0, 0, 1))).Volume() > 20
nx, ny = g['neck_axis_xy_mm']
beam, lid_mid, mast, pan_base = (step(n) for n in ('UGV-MECH-031', 'UGV-MECH-013-2', 'UGV-MECH-030', 'UGV-MECH-040'))
assert math.isclose(beam.BoundingBox().zmax, lid_z, abs_tol=1e-3), 'beam under the lid'
for dx in (-14, 14):
    for dy in (-14, 14):
        bx, by = nx + dx, ny + dy
        assert bx < seg/2 - 3, 'neck bolts clear of the lid seam'
        bolt = probe(fast['m3_clear_mm']/2 - 0.2, 20, (bx, by, lid_z - 9), (0, 0, 1))
        assert all(part.intersect(bolt).Volume() < 0.01 for part in (beam, lid_mid, mast)), (dx, dy)
        assert pan_base.intersect(probe(ins_d/2 - 0.05, ins_depth, (bx, by, top + 6), (0, 0, 1))).Volume() < 0.01

# M2 Task 3: internal fixtures and cable pass-throughs.
it = g['internal']
cradle3, tray, rack = step('UGV-MECH-070'), step('UGV-MECH-071'), step('UGV-MECH-072')
bat, elec = step('REF-BATTERY').BoundingBox(), step('REF-ELECTRONICS').BoundingBox()
cb = cradle3.BoundingBox()
assert cb.xmin < bat.xmin and bat.xmax < cb.xmax and cb.ymin < bat.ymin and bat.ymax < cb.ymax, 'cradle around the pack'
assert math.isclose(tray.BoundingBox().zmax, elec.zmin, abs_tol=1e-3), 'modules sit on the tray standoffs'
plate_half = lambda x: step('UGV-MECH-001-F' if x > g['plate_seam_x_mm'] else 'UGV-MECH-001-R')
for part, mounts in ((cradle3, it['battery_mounts_mm']), (tray, it['tray_mounts_mm']), (rack, it['ballast_mounts_mm'])):
    for x, y in mounts:
        assert abs(x - g['plate_seam_x_mm']) > 4, (x, y)
        bolt = probe(fast['m3_clear_mm']/2 - 0.2, 30, (x, y, g['plate_bottom_z_mm'] - 1), (0, 0, 1))
        assert part.intersect(bolt).Volume() < 0.01 and plate_half(x).intersect(bolt).Volume() < 0.01, (x, y)
for x in it['strap_slots_x_mm']:  # a strap over the pack passes through both side walls
    strap = cube((18, cb.ylen + 2, 2), (x, 0, g['plate_bottom_z_mm'] + g['plate_thickness_mm'] + 4.5))
    assert cradle3.intersect(strap).Volume() < 0.01, x
for x, y in it['tray_standoffs_mm']:
    assert tray.intersect(probe(ins_d/2 - 0.05, ins_depth, (x, y, elec.zmin - ins_depth), (0, 0, 1))).Volume() < 0.01
    assert tray.intersect(probe(ins_d/2 + 1.2, 3, (x, y, elec.zmin - 4), (0, 0, 1))).Volume() > 5
rb = rack.BoundingBox()
for k in range(1, 5):
    res = step(f'REF-BALLAST-{k}').BoundingBox()
    assert rb.xmin <= res.xmin and res.xmax <= rb.xmax and rb.zmin <= res.zmin and res.zmax <= rb.zmax, k
front = step('UGV-MECH-022-+1')
for z in it['front_vents_z_mm']:  # vent slots in the front wall facing the resistors
    assert front.intersect(cube((8, 38, 2), (g['body_length_mm']/2 - 2, 0, z))).Volume() < 0.01, z
    assert rb.zmin < z < rb.zmax
hx, hy = g['head']['cable_hole_xy_mm']  # DD82: behind the pan servo (the servo sits on the neck axis)
hole = probe(it['neck_cable_hole_mm']/2 - 0.3, 30, (hx, hy, lid_z - 9), (0, 0, 1))
assert all(part.intersect(hole).Volume() < 0.01 for part in (beam, lid_mid, mast, pan_base)), 'head cables into the body'
for side in (-1, 1):
    tof_hole = probe(it['tof_cable_hole_mm']/2 - 0.3, 8, (g['body_length_mm']/2 - 5, side*g['tof_center_y_mm'], 105), (1, 0, 0))
    assert front.intersect(tof_hole).Volume() < 0.01, side

# M3 Task 3 (DD74): cargo bay. A drop slot in the front lid under the arm's "store" pose, a TPU slit cover over
# it and a bin hung below (legs bolted to the plate, flange on the front wall); nothing blocks the drop.
cg = it['cargo']
(sw, sl), (scx, scy) = cg['slot_mm'], cg['slot_center_xy_mm']
bin_, cover, lid_front = step('UGV-MECH-073'), step('UGV-MECH-018'), step('UGV-MECH-013-3')
assert lid_front.intersect(cube((sw - 1, sl - 1, 10), (scx, scy, lid_z))).Volume() < 0.01, 'slot open in the front lid'
bb_ = bin_.BoundingBox()
assert bb_.xmin < scx - sw/2 and scx + sw/2 < bb_.xmax and bb_.ymin < scy - sl/2 and scy + sl/2 < bb_.ymax, 'bin under the slot'
assert bb_.zmax < lid_z and cg['bin_z_mm'][0] > it['ballast_resistor_mm'][2] + max(it['front_vents_z_mm']), bb_
column = cube((sw - 2, sl - 2, lid_z - cg['bin_z_mm'][0] - 2.5), (scx, scy, (lid_z + cg['bin_z_mm'][0] + 2.5)/2))
blocked = [part['name'] for part in m['parts'] if part['name'] not in ('UGV-MECH-018',)
           and step(part['name']).BoundingBox().zmax > cg['bin_z_mm'][0] and step(part['name']).intersect(column).Volume() > 0.01]
assert not blocked, ('drop path', blocked)
assert bin_.intersect(cube((sw - 2, sl - 2, 1), (scx, scy, cg['bin_z_mm'][0] + 1))).Volume() > 100, 'bin floor under the slot'
cv = cover.BoundingBox()
assert cv.zmin >= top - 1e-6 and cv.xmin < scx - sw/2 and scx + sw/2 < cv.xmax, 'TPU cover over the slot'
assert cover.intersect(cube((sw - 4, 0.8, 5), (scx, scy, top + 1))).Volume() < 0.01, 'slit through the cover'
for x, y in cg['leg_mounts_mm']:
    bolt = probe(fast['m3_clear_mm']/2 - 0.2, 20, (x, y, g['plate_bottom_z_mm'] - 1), (0, 0, 1))
    assert bin_.intersect(bolt).Volume() < 0.01 and plate_half(x).intersect(bolt).Volume() < 0.01, (x, y)
store = m['arm_poses']['store']['grip_mm']
assert abs(store[0] - scx) <= sw/2 - 5 and abs(store[1] - scy) <= sl/2 - 5 and top + 10 < store[2] < top + 40, store

# M3 print interfaces (DD78). Eye pod: the rear wall is a press-fit cap (the 27 x 40.5 ESP32-CAM board cannot pass a
# hole in it); the board sits between four front stops and the cap's pressing frame; the lens barrel sits in a
# collar on the window axis.
pod_x = nx + g['eye_pod_x_offset_mm']
eb_t, eb_w, eb_l = g['eye_board_mm']
rear = pod_x + g['eye_board_rear_from_pod_x_mm']
lens_d, lens_l = g['eye_lens_mm']
for side in (-1, 1):
    ye, pod, cap = side * g['eye_center_y_mm'], step(f'UGV-MECH-043-{side:+d}'), step(f'UGV-MECH-044-{side:+d}')
    tz = g['tilt_axis_z_mm']
    back = cube((2.4, 30, 36), (pod_x - g['eye_pod_mm'][0]/2 + 1.25, ye, tz))
    assert pod.intersect(back).Volume() < 0.01 and cap.intersect(back).Volume() > 1000, side  # open shell, cap closes it
    assert math.isclose(cap.BoundingBox().xmax, rear, abs_tol=0.05), 'cap frame presses the board rear face'
    board = cube((eb_t, eb_w, eb_l), (rear + eb_t/2, ye, tz))
    assert pod.intersect(board).Volume() < 0.01 and cap.intersect(board).Volume() < 0.01, side
    stops = cube((0.8, eb_w - 2, eb_l - 2), (rear + eb_t + 0.45, ye, tz)).cut(cube((2, eb_w - 8, eb_l - 8), (rear + eb_t + 0.45, ye, tz)))
    assert pod.intersect(stops).Volume() > 4, side  # front stops on the board rim
    lens_bore = probe(lens_d/2 + 0.2, 12, (pod_x + g['eye_pod_mm'][0]/2 - 11, ye, tz), (1, 0, 0))
    assert pod.intersect(lens_bore).Volume() < 0.01, side
    collar = probe(lens_d/2 + 1.6, 3, (pod_x + g['eye_pod_mm'][0]/2 - 6, ye, tz), (1, 0, 0)).cut(
        probe(lens_d/2 + 0.6, 3, (pod_x + g['eye_pod_mm'][0]/2 - 6, ye, tz), (1, 0, 0)))
    assert pod.intersect(collar).Volume() > 20, side
# DD82/DD83 head mechanism. Pan: MG90S on the neck axis (ears on 2 x M2), the neck turns in the 6804 at the top of
# the base and bolts to the pan horn. Tilt (DD83): the MG90S hides in the neck housing (on a plate that slides into
# grooves) and drives the left eye through a pushrod up the neck column; the eyes turn together on a hex axle through
# the blade between them. They sweep -30..60 deg of tilt without touching the column, blade or housing.
H, M9_ = g['head'], g['arm']['mg90s_mm']
tz, bz = g['tilt_axis_z_mm'], H['bearing_z_mm']
hz0, hz1 = H['housing_z_mm']
ry, cr, ct = H['rod_y_mm'], H['tilt_crank_r_mm'], H['column_top_z_mm']
neck, column, axle, plate = (step(n) for n in ('UGV-MECH-041', 'UGV-MECH-042', 'UGV-MECH-045', 'UGV-MECH-046'))
emp = lambda part, pr: part.intersect(pr).Volume() < 0.01
xc9 = nx + M9_['spline_from_end'] - M9_['case'][0] / 2          # servo case centre (spline on x = nx)
z_ear = bz - 1 - 2 - M9_['spline_top'] + M9_['ear_underside']      # pan: horn face = neck bottom = bearing - 1
ts_ear = ry - 1 - M9_['spline_top'] + M9_['ear_underside']         # tilt: spline top 1 mm short of the rod plane
for s_ in (-1, 1):
    # the pan servo goes in from the open bottom of the base; its ears are screwed up into the ledge above them
    assert emp(pan_base, probe(0.75, 4, (xc9 + s_ * M9_['ear_hole_pitch'] / 2, ny, z_ear + M9_['ear_t']), (0, 0, 1))), 'pan ear pilot'
    assert emp(neck, probe(0.75, 6, (nx + s_ * M9_['horn_hole_r'], ny, bz - 1), (0, 0, 1))), 'neck horn pilot'
    assert emp(plate, probe(0.75, 4, (xc9 + s_ * M9_['ear_hole_pitch'] / 2, ts_ear - 4, H['tilt_servo_z_mm']), (0, 1, 0))), 'tilt ear pilot'
assert emp(pan_base, probe(15.95, 6.9, (nx, ny, bz + 0.05), (0, 0, 1))), '6804 seat'
assert pan_base.intersect(probe(15.5, 1.4, (nx, ny, bz - 1.5), (0, 0, 1)).cut(probe(12.5, 1.4, (nx, ny, bz - 1.5), (0, 0, 1)))).Volume() > 50, 'seat lip'
assert emp(pan_base, cube((8, 8, 6), (hx - 4, hy, 226))), 'rear cable slot'
assert neck.intersect(probe(9.95, 6.8, (nx, ny, bz + 0.1), (0, 0, 1)).cut(probe(9, 6.8, (nx, ny, bz + 0.1), (0, 0, 1)))).Volume() > 150, 'neck journal'
assert emp(neck, probe(3.9, hz0 + 2 - bz + 1, (nx, ny, bz - 1), (0, 0, 1))), 'horn centre screw bore'
nb_ = neck.BoundingBox()
assert emp(neck, cube((4, 5, 8), (nb_.xmin + 1.5, 1, hz0 + 8))), 'housing cable window'
assert neck.intersect(plate).Volume() < 0.01 and neck.intersect(cube((0.8, 3, 10), (nb_.xmin + 2.6, ts_ear - 2, hz0 + 12))).Volume() < 0.01, 'plate groove'
# pushrod channel: the rod (x = nx + cr cos(tilt)) stays clear of the housing lid and column over the whole tilt range
lo = nx + cr * math.cos(math.radians(max(abs(a) for a in H['tilt_sweep_deg']))) - 1
st = H['rod_shroud_top_z_mm']  # the channel rises between the eyes as a shroud, so the rod is hidden up to here
assert emp(column, cube((nx + cr + 1 - lo, 2, st - hz1 + 1), ((lo + nx + cr + 1) / 2, ry, (hz1 - 1 + st) / 2))), 'rod channel'
assert not emp(column, cube((0.8, 2, st - ct - 1), (nx + cr + 2, ry, (ct + st) / 2))), 'shroud hides the rod from the front'
gy = g['eye_center_y_mm'] - g['eye_pod_mm'][1] / 2                 # eye inner face
pod_l, pod_r = step('UGV-MECH-043-+1'), step('UGV-MECH-043--1')
assert emp(pod_l, probe(3.5, 3, (nx, gy - 0.25, tz), (0, 1, 0))) and emp(pod_r, probe(3.5, 3, (nx, -gy - 2.75, tz), (0, 1, 0))), 'hex axle holes'
assert emp(column, probe(H['axle_d_mm'] / 2 + 0.1, 6, (nx, -3, tz), (0, 1, 0))), 'axle bore in the blade'
assert emp(pod_l, probe(1, 4, (nx + cr, ry - 1, tz), (0, 1, 0))), 'crank pin hole'
assert pod_l.intersect(probe(2.4, 3, (nx + cr, ry - 0.5, tz), (0, 1, 0)).cut(probe(1.2, 3, (nx + cr, ry - 0.5, tz), (0, 1, 0)))).Volume() > 20, 'crank boss'
assert m['head_tilt']['range_deg'] == H['tilt_sweep_deg'] and not m['head_tilt']['hits'], m['head_tilt']
assert m['head_tilt']['min_clearance_mm'] >= 1.5, m['head_tilt']  # the eyes pass over the column top
for pod, sgn in ((pod_l, 1), (pod_r, -1)):  # DD85: eye cables out of the inner wall near the axle, into the column
    assert emp(pod, probe(2.4, 3, (nx - 6, sgn * (gy + 1.5) - 1.5, tz - 10), (0, 1, 0))), 'eye cable hole'
# Fenders: three M3 screws each through flange and side panel (nuts inside).
fen = g['fender']
for w in WHEELS:
    side = 1 if w[1] == 'L' else -1
    fender = step(f'UGV-MECH-015-{w}')
    xs_ = [x for x in fen['screw_x_mm'] if (x > fen['split_x_mm']) == (w[0] == 'F')]
    assert len(xs_) == 3 and fender.BoundingBox().zmax == fen['flange_top_z_mm'], w
    for x in xs_:
        bolt = probe(fast['m3_clear_mm']/2 - 0.2, 12, (x, side * (W/2 - 5), fen['screw_z_mm']), (0, side, 0))
        panel = step(f"UGV-MECH-0{10 if x < -seg/2 else 11 if x < seg/2 else 12}-{side:+d}")
        assert fender.intersect(bolt).Volume() < 0.01 and panel.intersect(bolt).Volume() < 0.01, (w, x)
# Shoulder servo frame: four M3 inserts at the arm ends against the wall, matching panel holes; DS3218 ear holes.
A_ = g['arm']
frame, front_r = step('UGV-MECH-056--1'), step('UGV-MECH-012--1')
fb = frame.BoundingBox()
arm_z = [fb.zmax - 4, fb.zmin + 4]
for dx in (-A_['j1_frame_screw_dx_mm'], A_['j1_frame_screw_dx_mm']):
    for z in arm_z:
        x = A_['shoulder_xz_mm'][0] + dx
        assert frame.intersect(probe(ins_d/2 - 0.05, ins_depth, (x, -(W/2 - wall), z), (0, 1, 0))).Volume() < 0.01, (dx, z)
        assert frame.intersect(probe(ins_d/2 + 1.2, 4, (x, -(W/2 - wall - 1), z), (0, 1, 0))).Volume() > 5, (dx, z)
        assert front_r.intersect(probe(fast['m3_clear_mm']/2 - 0.2, 6, (x, -W/2 - 1, z), (0, 1, 0))).Volume() < 0.01, (dx, z)
xs0, zs0 = A_['shoulder_xz_mm']
for dx in (-5, 5):
    for dz in (-24.75, 24.75):
        assert frame.intersect(probe(1.5, 20, (xs0 + dx, -A_['j1_spline_abs_y_mm'] + 5, zs0 - 10 + dz), (0, -1, 0))).Volume() < 0.01
# Cargo bin flange: two M3 inserts into the front wall.
cgi = it['cargo']
for y in cgi['flange_screw_y_mm']:
    z = cgi['flange_screw_z_mm']
    x_wall = g['body_length_mm']/2 - wall
    assert bin_.intersect(probe(ins_d/2 - 0.05, ins_depth, (x_wall - ins_depth, y, z), (1, 0, 0))).Volume() < 0.01, y
    assert front.intersect(probe(fast['m3_clear_mm']/2 - 0.2, 6, (x_wall - 1, y, z), (1, 0, 0))).Volume() < 0.01, y
# Shoulder journal: 25T disc-horn flange (4 x M3 tapped on the PCD, verify with the purchased horn); the axial cable bore
# is closed toward the horn and the cables leave through a radial hole between the flange and the wall boss.
j50 = step('UGV-MECH-050--1')
tip = A_['j1_spline_abs_y_mm']
r_pcd = A_['horn_pcd_mm'] / 2
for k in range(4):
    a = math.radians(45 + 90 * k)
    hole = probe(1.1, 5, (xs0 + r_pcd * math.cos(a), -(tip + 3), zs0 + r_pcd * math.sin(a)), (0, -1, 0))  # M3 tap, 6 deep
    assert j50.intersect(hole).Volume() < 0.01, k
assert j50.intersect(probe(3, 3, (xs0, -(tip + 2.5), zs0), (0, -1, 0))).Volume() > 50, 'no cable path into the horn'
assert j50.intersect(probe(2.7, 30, (xs0, -(tip + 8.5), zs0 - 15), (0, 0, 1))).Volume() < 0.01, 'radial cable exit'
assert j50.intersect(probe(3.5, W/2 + 6 - (tip + 9), (xs0, -(tip + 9), zs0), (0, -1, 0))).Volume() < 0.01, 'axial cable bore'

# Arm link interfaces (DD81). Probes are built in the zero pose of the right arm (y = -(plane + d), d > 0 outboard)
# and carried into the stow pose the STEPs are exported in, through the manifest's joint chain.
A_, chain = g['arm'], m['arm_chain']['joints']
YA_, T = A_['plane_abs_y_mm'], xs0 + A_['twist_bearing_mm']
xe0, xw0 = xs0 + A_['upper_mm'], xs0 + A_['upper_mm'] + A_['forearm_mm']
MG, M9, horn = A_['mg996r_mm'], A_['mg90s_mm'], A_['horn_25t_mm']
d_b = MG['spline_top'] / 2                              # pitch servos: case bottom outboard, spline inboard on the axis
d_e = d_b - MG['ear_underside']                         # ear seat face
d_h = -d_b - horn['face_above_spline']                  # horn face: the fork's inboard cheek bolts to it
d_i = d_b + 0.5 + A_['pitch_wall_mm'] + 0.5             # outboard cheek (624 idler) starts here


def stowed(shape, link):
    for j in range(link, -1, -1):
        o, d, sign = chain[j]['origin'], chain[j]['axis'], chain[j]['sign']
        q = A_['poses_deg']['stow'][j]
        if q:
            shape = shape.rotate(cq.Vector(*o), cq.Vector(o[0] + d[0], o[1] + d[1], o[2] + d[2]), sign * q)
    return shape


def dy(r, d0, d1, x, z, link):  # probe along y between offsets d0..d1, stowed with `link`
    return stowed(probe(r, d1 - d0, (x, -(YA_ + d1), zs0 + z), (0, 1, 0)), link)


def dx(r, x0, x1, d, z, link):  # probe along x at offset d, height z
    return stowed(probe(r, x1 - x0, (x0, -(YA_ + d), zs0 + z), (1, 0, 0)), link)


def ring(r0, r1, solid_fn):
    return solid_fn(r1).cut(solid_fn(r0))


empty = lambda part, pr: part.intersect(pr).Volume() < 0.01
for xj, seat_name, fork_name, k in ((xe0, 'UGV-MECH-051--1', 'UGV-MECH-052--1', 1),  # k = the seat's link, the fork is k + 1
                                    (xw0, 'UGV-MECH-052--1', 'UGV-MECH-053--1', 2)):
    seat, fork = step(seat_name), step(fork_name)
    xc_ = xj + MG['spline_from_end'] - MG['case'][0] / 2
    for ex in (-1, 1):  # MG996R ears on the seat face: four M3 heat-set inserts, wall around each
        for ez in (-1, 1):
            x_, z_ = xc_ + ex * MG['ear_holes'][0] / 2, ez * MG['ear_holes'][1] / 2
            assert empty(seat, dy(ins_d/2 - 0.05, d_e, d_e + ins_depth, x_, z_, k)), (seat_name, ex, ez)
            assert seat.intersect(ring(ins_d/2 + 0.1, ins_d/2 + 1.2, lambda r: dy(r, d_e + 0.3, d_e + ins_depth, x_, z_, k))).Volume() > 8, (seat_name, ex, ez)
    for n in range(4):  # 25T horn: four M3 clearance holes through the fork's inboard cheek, cheek around them
        a_ = math.radians(45 + 90 * n)
        x_, z_ = xj + A_['horn_pcd_mm'] / 2 * math.cos(a_), A_['horn_pcd_mm'] / 2 * math.sin(a_)
        assert empty(fork, dy(fast['m3_clear_mm']/2 - 0.1, d_h - 6, d_h, x_, z_, k + 1)), (fork_name, n)
    assert fork.intersect(ring(A_['horn_pcd_mm']/2 + 2, 12, lambda r: dy(r, d_h - 2, d_h, xj, 0, k + 1))).Volume() > 200, fork_name
    b0, b1, b2 = A_['idler_624_mm']  # 624ZZ in the outboard cheek; M4 through the seat wall into a captive nut
    assert empty(fork, dy(b1/2 - 0.05, d_i, d_i + b2 - 0.1, xj, 0, k + 1)), fork_name
    assert fork.intersect(ring(b1/2 + 0.2, b1/2 + 2.5, lambda r: dy(r, d_i, d_i + b2, xj, 0, k + 1))).Volume() > 100, fork_name
    assert fork.intersect(ring(b1/2 - 0.8, b1/2 - 0.1, lambda r: dy(r, d_i + b2, d_i + b2 + 0.4, xj, 0, k + 1))).Volume() > 1, 'bearing lip'
    assert empty(seat, dy(fast['m4_clear_mm']/2 - 0.1, d_b, d_i, xj, 0, k)), seat_name
    assert empty(seat, dy(3.45, d_b + 0.5, d_b + 3.6, xj, 0, k)), 'M4 nut pocket'
    assert seat.intersect(dy(3.45, d_b + 3.8, d_i - 0.5, xj, 0, k)).Volume() > 30, 'wall behind the nut'
    # The fork's crossbar clears the ears' sweep: no fork material within fork_clear_mm - 0.1 of the axis between
    # the cheeks, and ahead of the axis the seat stays inside that radius (it is what the fork turns around).
    assert empty(fork, dy(A_['fork_clear_mm'] - 0.1, d_h + 0.1, d_i - 0.1, xj, 0, k + 1)), fork_name
    ahead = stowed(cube((40, 60, 60), (xj + 20, -(YA_ + (d_h + d_i) / 2), zs0)), k).cut(dy(A_['fork_clear_mm'] - 1, d_h, d_i, xj, 0, k))
    assert empty(seat, ahead), seat_name
# Twist (J2): ear-trimmed MG996R in a pocket of link A under a screwed cover (058); the 25T horn bolts to the adapter
# (059) that carries the 6704 inner ring; link B bolts to the adapter with two M3 from its own servo pocket.
a50, b51, cov, adp = (step(n) for n in ('UGV-MECH-050--1', 'UGV-MECH-051--1', 'UGV-MECH-058--1', 'UGV-MECH-059--1'))
for x_, z_ in ((T - 45, -13.85), (T - 25, -13.85), (T - 10, -9), (T - 10, 25)):  # DD85: rear pair in the bottom wall
    assert empty(a50, dy(0.75, 6.6, 12.5, x_, z_, 0)), (x_, z_)
    assert a50.intersect(ring(0.9, 2.2, lambda r: dy(r, 7, 12.4, x_, z_, 0))).Volume() > 5, (x_, z_)
    assert empty(cov, dy(fast['m2_clear_mm']/2 - 0.05, 12, 15, x_, z_, 0)), (x_, z_)
for n in range(4):
    a_ = math.radians(90 * n)
    d_, z_ = A_['horn_pcd_mm'] / 2 * math.cos(a_), A_['horn_pcd_mm'] / 2 * math.sin(a_)
    assert empty(adp, dx(fast['m3_clear_mm']/2 - 0.1, T - 5, T + 5, d_, z_, 1)), ('adapter horn hole', n)
assert empty(adp, dx(2.9, T - 5, T + 5, 0, 0, 1)), 'horn centre screw bore'
assert adp.intersect(ring(9, 9.95, lambda r: dx(r, T + 0.6, T + 4.4, 0, 0, 1))).Volume() > 150, 'adapter journal in the 6704'
for z_ in (-5, 5):
    assert empty(adp, dx(1.2, T - 1.4, T + 4.5, 5, z_, 1)), ('adapter pilot for B', z_)
    assert empty(b51, dx(fast['m3_clear_mm']/2 - 0.1, T + 4.5, xe0 - 31, 5, z_, 1)), ('B screw path', z_)
assert b51.intersect(ring(10.2, 11, lambda r: dx(r, T + 4.5, T + 5.5, 0, 0, 1))).Volume() > 20, 'B hub clamps the inner ring'
# MG90S roll (D) and gripper (E): ears on a seat face, two M2 self-tapping screws each into 1.6 mm pilots.
d53, e54 = step('UGV-MECH-053--1'), step('UGV-MECH-054--1')
roll_ear = xw0 + A_['fork_clear_mm'] + 2.5 + M9['ear_underside']  # roll servo on a 2 mm floor past the crossbar
for s_ in (-1, 1):
    d_ = M9['case'][0] / 2 - M9['spline_from_end'] + s_ * M9['ear_hole_pitch'] / 2
    assert empty(d53, dx(fast['m2_pilot_mm']/2 - 0.05, roll_ear - 6, roll_ear, d_, 0, 3)), ('roll ear pilot', d_)
xg = xw0 + A_['grip_mm'] - 16                           # gripper spline, inboard; ears on E's face at d = -6
gc = xg + M9['spline_from_end'] - M9['case'][0] / 2
for s_ in (-1, 1):
    assert empty(e54, dy(fast['m2_pilot_mm']/2 - 0.05, -6, 0, gc + s_ * M9['ear_hole_pitch'] / 2, 0, 4)), ('grip ear pilot', s_)
# DD93 (M01): twin geared claw. Jaw A on the MG90S spline axis, jaw B on its pin GP higher (a 2.5 mm pilot in the palm's
# post), 16T gears on both; the pads meet at z = GP/2 in the grip region; it opens only where the CAD swept it.
GR_ = A_['gripper']
GP_ = GR_['pivot_spacing_mm']
ja, jb = step('UGV-MECH-055--1'), step('UGV-MECH-062--1')
pa, pb = step('UGV-MECH-063--1'), step('UGV-MECH-064--1')
assert not empty(pa, dx(0.5, xg + 16, xg + 26, -15, GP_ / 2 - 0.75, 4)), 'pad A below the meeting plane'
assert not empty(pb, dx(0.5, xg + 16, xg + 26, -15, GP_ / 2 + 0.75, 4)), 'pad B above it'
assert empty(e54, dy(1.1, -17.5, -8, xg, GP_, 4)) and not empty(e54, dy(2.2, -17, -8, xg, GP_, 4)), 'jaw B pin pilot in its post'
assert not empty(ja, dy(3, -24.5, -18.5, xg, 0, 4)) and not empty(jb, dy(3, -24.5, -18.5, xg, GP_, 4)), 'gears on both pivots'
assert empty(ja, dy(1.0, -26, -17, xg + 7, 0, 4)) and empty(ja, dy(1.0, -26, -17, xg + 11, 0, 4)), 'horn screw holes in jaw A'
gm = m['gripper']
assert gm['open_deg'] == GR_['open_deg'] and not gm['jaw_self_hits'], gm['jaw_self_hits']  # gears mesh, jaws clear the palm
assert set(gm['poses']) == set(GR_['open_poses']) and not any(gm['poses'].values()), gm['poses']
open_edges = {tuple(sorted(e)) for e in A_['pose_edges'] if e[0] in GR_['open_poses'] and e[1] in GR_['open_poses']}
assert {tuple(sorted(e['pose'])) for e in gm['edges']} == open_edges and not any(e['hits'] for e in gm['edges']), gm['edges']
assert 'stow' not in GR_['open_poses'] and set(GR_['release_poses']) <= set(GR_['open_poses'])  # DD94: store
assert gm['gap_open_mm']['tips'] >= 50, gm['gap_open_mm']  # TL5 objects up to 50 mm
# R06 (DD94): the published grasp point is where the closed pads meet (their shared face's middle), not the old
# wrist + 96 mm point on the arm axis.
pads = [step(n).BoundingBox() for n in ('UGV-MECH-063--1', 'UGV-MECH-064--1')]
face = [(min(b.xmin for b in pads) + max(b.xmax for b in pads)) / 2, (min(b.ymin for b in pads) + max(b.ymax for b in pads)) / 2,
        (min(b.zmin for b in pads) + max(b.zmax for b in pads)) / 2]
assert math.dist(face, m['arm_poses']['stow']['grip_mm']) < 0.1, (face, m['arm_poses']['stow']['grip_mm'])
gd = m['grasp_datum_local_mm']
assert abs(gd['from_wrist_x'] - (A_['grip_mm'] + 5)) < 0.01 and gd['z'] == GP_ / 2, gd
# DD94 recheck #1: the pose table in the mechanical doc is the manifest's grasp point, pose by pose (graph order).
import re  # noqa: E402
doc_grip = [[float(v.replace('−', '-').replace(',', '.')) for v in row.split(' / ')]
            for row in re.findall(r'^\| [^|]+ \| [^|]+ \| \(([^)]+)\) \|', (ROOT/'docs/lite_mechanical_A3.md').read_text(), re.M)]
assert len(doc_grip) == len(m['arm_poses']) and all(
    math.dist(d, v['grip_mm']) <= 0.05 for d, v in zip(doc_grip, m['arm_poses'].values())), doc_grip
# R05 (DD94): jaw B turns on a 5 mm nylon spacer (bore 5.2) that the M3 pin screw clamps to the post, 0.5 mm axial play.
for sfx, sgn in (('R', -1), ('L', 1)):
    sp = step(f'REF-SPACER-JAWB-{sfx}').BoundingBox()
    assert abs(max(sp.xlen, sp.ylen, sp.zlen) - 7.5) < 0.01 and abs(sorted((sp.xlen, sp.ylen, sp.zlen))[0] - 5) < 0.01, sp
assert empty(jb, dy(2.55, -25.5, -17.5, xg, GP_, 4)) and not empty(jb, dy(2.7, -24.5, -18.5, xg, GP_, 4)), 'jaw B bore 5.2'
assert empty(step('REF-SPACER-JAWB-R'), dy(1.55, -26, -17, xg, GP_, 4)), 'M3 through the spacer'
# R04 (DD94): the passive left arm is bolted through the right arm's interfaces with printed stand-ins, no free link.
touch = [('UGV-MECH-066-+1', 'UGV-MECH-059-+1'), ('UGV-MECH-059-+1', 'UGV-MECH-051-+1'), ('UGV-MECH-075-+1', 'UGV-MECH-050-+1'),
         ('UGV-MECH-067-+1', 'UGV-MECH-051-+1'), ('UGV-MECH-067-+1', 'UGV-MECH-052-+1'), ('UGV-MECH-076-+1', 'UGV-MECH-052-+1'),
         ('UGV-MECH-068-+1', 'UGV-MECH-052-+1'), ('UGV-MECH-068-+1', 'UGV-MECH-053-+1'), ('UGV-MECH-077-+1', 'UGV-MECH-053-+1'),
         ('UGV-MECH-069-+1', 'UGV-MECH-053-+1'), ('UGV-MECH-069-+1', 'UGV-MECH-054-+1'), ('UGV-MECH-074-+1', 'UGV-MECH-054-+1'),
         ('UGV-MECH-074-+1', 'UGV-MECH-055-+1'), ('UGV-MECH-058-+1', 'UGV-MECH-050-+1')]
for a_, b_ in touch:
    assert step(a_).distance(step(b_)) < 0.01, (a_, b_)
# DD95 (R04 recheck): the passive twist block fills its pocket (<= 0.25 mm to link A and to the cover, not touching) and
# turns < +-1 deg (TL4 joint budget) before it bears: turned 1 deg either way it overlaps A or the cover.
lt = m['left_twist_play']
assert lt['limit_deg'] == 1 and lt['nominal_mm3'] == 0 and min(lt['hit_mm3']) > 0.01, lt
assert all(0 < step('UGV-MECH-066-+1').distance(step(n)) <= 0.25 for n in ('UGV-MECH-050-+1', 'UGV-MECH-058-+1'))
assert not any(p['name'].startswith('REF-SERVO') and p['name'].endswith(('-L', '-+1')) for p in m['parts'])
# Full review: park with all five joints +-1 deg at once (32 corners): >= 3 mm from the side panels (TL4).
pt = m['park_tolerance']
assert pt['corners'] == 32 and pt['error_deg'] == 1 and pt['min_wall_mm'] >= 3.0, pt
# DD85 cable paths: every arm servo cable leaves its pocket through a slot to the link's outboard face; the bundle runs
# outboard (zip ties round the links) and enters the body along the shoulder axis through the journal bore, which opens
# on link A's outboard face beside the twist cover; the twist cable reaches it under the cover through a groove.
assert empty(a50, dy(3.9, -13.5, 12.4, xs0, 0, 0)) and empty(cov, dy(3.9, 12, 15, xs0, 0, 0)), 'shoulder cable entry'
assert empty(a50, dy(1.4, 10.6, 12.5, xs0 + 4.5, 1, 0)), 'twist cable groove'
for xj, seat_name, k in ((xe0, 'UGV-MECH-051--1', 1), (xw0, 'UGV-MECH-052--1', 2)):
    x0_ = xj + MG['spline_from_end'] - MG['case'][0]                # case end away from the spline: cable exit
    assert empty(step(seat_name), stowed(cube((4, d_i - 0.6 - (d_b - 3), 5), (x0_ + 3, -(YA_ + (d_b - 3 + d_i - 0.6) / 2), zs0)), k)), seat_name
xr_ = xw0 + A_['fork_clear_mm'] + 2.5
d_hi9 = M9['case'][0] - M9['spline_from_end']
d_out9 = (d_hi9 - M9['spline_from_end']) / 2 + 19                  # D's outboard face
assert empty(d53, stowed(cube((4, d_out9 - 0.1 - (d_hi9 - 1), 5), (xr_ + 2.5, -(YA_ + (d_hi9 - 1 + d_out9 - 0.1) / 2), zs0)), 3)), 'roll cable slot'
g0_ = xg + M9['spline_from_end'] - M9['case'][0]
assert empty(e54, stowed(cube((4, 4.8, 5), (g0_ + 2, -(YA_ + 14.5), zs0)), 4)), 'gripper cable slot'

# M02 (full review, DD93): each splice rib is bolted across the plate seam, two M3 on either side, from under the plate
# into heat-set inserts in the rib; M03: the passive left shoulder's split collar (slit, clamp screw along x) and its TPU
# friction washer against the wall boss's inner face.
plate_top0 = g['plate_bottom_z_mm'] + g['plate_thickness_mm']
xs_bolts = g['rail_bolt_x_mm']
assert sum(x < g['plate_seam_x_mm'] for x in xs_bolts) == 2 and sum(x > g['plate_seam_x_mm'] for x in xs_bolts) == 2
for sign in (-1, 1):
    rib, y_ = step(f'UGV-MECH-002-{sign:+d}'), sign * g['rail_center_y_mm']
    for x in xs_bolts:
        assert empty(rib, probe(1.9, 6, (x, y_, plate_top0), (0, 0, 1))), ('rib insert', x)
        half = step('UGV-MECH-001-R' if x < g['plate_seam_x_mm'] else 'UGV-MECH-001-F')
        assert empty(half, probe(1.6, g['plate_thickness_mm'] + 2, (x, y_, g['plate_bottom_z_mm'] - 1), (0, 0, 1))), ('plate hole', x)
col, wsh = step('UGV-MECH-057-+1'), step('UGV-MECH-065-+1')
xs1, zs1 = g['arm']['shoulder_xz_mm']
assert empty(col, cube((1.2, 5, 10), (xs1, W/2 - 15.75, zs1 - 17))), 'collar slit'
assert empty(col, probe(1.5, 14, (xs1 - 7, W/2 - 15.75, zs1 - 22), (1, 0, 0))), 'collar clamp screw'
wb = wsh.BoundingBox()
assert abs(wb.ymax - (W/2 - 11)) < 0.01 and abs(wb.ylen - 1.5) < 0.01, 'washer against the boss face'

# E-stop head stands >= 15 mm above the lid and is reachable from above.
estop = step('REF-ESTOP').BoundingBox()
assert estop.zmax >= top + 15 and estop.xmin > -g['body_length_mm']/2, estop
# Front ToF windows are clear through the bumper.
bumper = step('UGV-MECH-017-+1')
for side in (-1, 1):
    window = cube(g['tof_window_mm'], (g['overall_length_mm']/2 - 7.5, side*g['tof_center_y_mm'], 105))
    assert bumper.intersect(window).Volume() < 0.01, 'ToF window blocked'

# Stowed robot stays inside the 330 x 308 footprint; head height follows the taller body.
half_l, half_w = g['overall_length_mm']/2, g['overall_width_mm']/2
assert max(b.xmax for b in bounds) <= half_l + 1e-6 and min(b.xmin for b in bounds) >= -half_l - 1e-6
assert max(b.ymax for b in bounds) <= half_w + 1e-6 and min(b.ymin for b in bounds) >= -half_w - 1e-6
assert max(b.zmax for b in bounds) <= g['tilt_axis_z_mm'] + 35, 'head height'

# M3 Task 2 (DD73): 5-axis right arm out of the side wall, passive left arm.
A = g['arm']
xs, zs = A['shoulder_xz_mm']
L1, L2, L3 = A['upper_mm'], A['forearm_mm'], A['grip_mm']
poses, edges = A['poses_deg'], A['pose_edges']
assert set(A['servos']) == {*A['joints'], 'gripper'} and len(A['joints']) == 5
for name, q in poses.items():
    assert len(q) == 5 and all(lo <= v <= hi for v, (lo, hi) in zip(q, A['limits_deg'])), (name, q)
assert {n for e in edges for n in e} == set(poses), 'every pose is in the graph'
seen, todo = {'stow'}, ['stow']
while todo:
    n = todo.pop()
    for a, b in edges:
        for u, v in ((a, b), (b, a)):
            if u == n and v not in seen:
                seen.add(v)
                todo.append(v)
assert seen == set(poses), 'pose graph connected from stow'
# The shoulder servo sits inside the body; the arm load goes into the wall bearing, not the servo spline.
j1 = step('REF-SERVO-SHOULDER-R').BoundingBox()
assert j1.ymin >= -inner_wall - 1e-6 and j1.zmax < lid_z and j1.xmax < g['body_length_mm']/2 - wall, j1
for side in (-1, 1):
    brg = step(f'REF-BEARING-SHOULDER-{side:+d}').BoundingBox()
    assert math.isclose((brg.xmin + brg.xmax)/2, xs, abs_tol=0.05) and math.isclose((brg.zmin + brg.zmax)/2, zs, abs_tol=0.05)
    assert (brg.ymax if side > 0 else -brg.ymin) <= W/2 + 1e-6, 'shoulder bearing seated in the wall boss'
    assert step(f'UGV-MECH-012-{side:+d}').intersect(probe(9.5, 30, (xs, side*(W/2 - 20), zs), (0, side, 0))).Volume() < 0.01
for k in range(5):  # the passive left arm is the right arm's mirror
    r, l = step(f'UGV-MECH-05{k}--1').BoundingBox(), step(f'UGV-MECH-05{k}-+1').BoundingBox()
    assert all(math.isclose(a, b, abs_tol=0.01) for a, b in ((r.xlen, l.xlen), (r.ylen, l.ylen), (r.zlen, l.zlen))), k
assert set(m['arm_poses']) == set(poses)
for name, pose in m['arm_poses'].items():
    assert not pose['intersections'], (name, pose)
for edge in m['arm_edges']:
    assert edge['max_step_deg'] <= 1 and not edge['hits'], edge  # 1 deg: <= 5 mm at the 287 mm tip
assert {tuple(sorted(e['pose'])) for e in m['arm_edges']} == {tuple(sorted(e)) for e in edges}
# Clearance, not just no-contact: the moving links beyond the upper-arm hub (elbow onward) keep >= 4.5 mm from every
# other part along every edge (1 deg samples, as the collision sweep); only the parked arm itself sits closer (its
# rest on the fender).
for c in m['arm_clearance']:
    assert c['moving_mm'] >= 4.5 and (c['park_mm'] is None or c['park_mm'] >= 1.0), c
assert {tuple(sorted(c['pose'])) for c in m['arm_clearance']} == {tuple(sorted(e)) for e in edges}
grip = {n: v['grip_mm'] for n, v in m['arm_poses'].items()}
assert grip['reach_low'][0] >= half_l + 40 and 5 <= grip['reach_low'][2] <= 40, grip['reach_low']
assert grip['reach_center'][0] >= half_l + 40 and abs(grip['reach_center'][1]) <= 30 and grip['reach_center'][2] <= 80
rest = m['arm_limp_rest']  # rail off at park: the arm settles on its fender within 3 deg, not on a tyre
assert rest and rest['angle_deg'] <= poses['stow'][0] + 3, rest
assert all(h['part'].startswith('UGV-MECH-015') for h in rest['hits']), rest
# Holding torque, arm straight and level, 150 g at the grip centre: stall >= 1.5 x load at every joint (4.8-5 V
# ratings). Masses from the mass screen (printed estimate / catalogue); lever arms from each solid's centroid in the
# straight stow pose. The twist joint sees the elbow's load when the forearm swings sideways.
import importlib.util
spec = importlib.util.spec_from_file_location('body_mass_screen', ROOT/'tools/body_mass_screen.py')
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)
stall, S = A['servo_stall_nm'], A['servos']
by_name = {part['name']: part for part in m['parts']}
loads = [(ms.part_mass(ROOT, by_name[n])[1]/1000, xs - step(n).Center().x, link)
         for n, link in m['arm_chain']['links'].items()] + [(A['payload_kg'], L1 + L2 + L3, 4)]
moment = lambda axis_mm, first: 9.81e-3 * sum(kg * (d - axis_mm) for kg, d, link in loads if link >= first)
for joint, axis_mm, first in (('shoulder', 0, 0), ('twist', L1, 2), ('elbow', L1, 2), ('wrist', L1 + L2, 3)):
    need = moment(axis_mm, first)
    assert stall[S[joint]] >= 1.5 * need, (joint, round(need, 3), stall[S[joint]])

front_wall = step('UGV-MECH-022-+1')
window = cube(g['light_bar_opening_mm'], (g['body_length_mm']/2, 0, g['light_bar_center_z_mm']))
assert front_wall.intersect(window).Volume() < 0.01, 'light bar window blocked'
for side in (-1, 1):
    cam = step(f'REF-EYE-CAMERA-{side:+d}').BoundingBox()
    assert all(a >= b - 1e-6 for a, b in zip((cam.xlen, cam.ylen, cam.zlen), g['eye_camera_envelope_mm'])), cam  # ESP32-CAM
    assert math.isclose((cam.ymin+cam.ymax)/2, side*g['eye_center_y_mm'])

assert g['track_mm']+g['wheel_width_mm'] == g['overall_width_mm']
assert g['wheelbase_mm']+g['wheel_diameter_mm'] == g['overall_length_mm']
assert lid_z-(g['battery_center_mm'][2]+g['battery_envelope_mm'][2]/2) >= 3
urdf = ET.parse(ROOT/'simulation/ugv_geometry.urdf').getroot()
for joint, xyz in (('head_pan_joint', [nx, ny, top + 40]), ('head_tilt_joint', [nx, ny, g['tilt_axis_z_mm']]),
                   ('right_shoulder_joint', [xs, -A['plane_abs_y_mm'], zs])):
    got = [float(v)*1000 for v in urdf.find(f"joint[@name='{joint}']").find('origin').attrib['xyz'].split()]
    assert all(math.isclose(a, b, abs_tol=1e-6) for a, b in zip(got, xyz)), (joint, got)
for j, (lo, hi) in zip(A['joints'], A['limits_deg']):
    lim = urdf.find(f"joint[@name='right_{j}_joint']").find('limit').attrib
    assert math.isclose(float(lim['lower']), math.radians(lo)) and math.isclose(float(lim['upper']), math.radians(hi)), j
for side, y in [('left', g['track_mm']/2000), ('right', -g['track_mm']/2000)]:
    for end, x in [('front', 0.105), ('rear', -0.105)]:
        joint = urdf.find(f"joint[@name='{end}_{side}_wheel_joint']")
        xyz = [float(v) for v in joint.find('origin').attrib['xyz'].split()]
        assert all(math.isclose(a, b) for a, b in zip(xyz, [x, y, 0.06]))
        assert joint.find('axis').attrib['xyz'] == '0 1 0'
print(f"PASS: {len(m['parts'])} valid A3 Lite STEP parts; character body with motors inside, fenders, head at 122 mm, "
      f"5-axis arm in {len(m['arm_poses'])} poses / {len(m['arm_edges'])} swept edges, E-stop, ToF, light bar, eyes, URDF")
