"""A3 Lite mass screen and filament estimate from the generated STEP solids.

Printed parts: solid-volume upper bound and a print estimate (1.2 mm shell over the
whole surface + 20 % infill inside). Bought parts: catalog masses. Fasteners and
cables are not included. Densities: PETG 1.27, TPU 95A 1.21, steel 7.85 g/cm3.
"""
import json
import math
from pathlib import Path

import cadquery as cq

DENSITY_G_CM3 = {'PETG': 1.27, 'TPU': 1.21, 'steel': 7.85}
SHELL_MM, INFILL = 1.2, 0.20  # ponytail: shell/infill approximation, not a slicer; weigh real prints
TPU_PREFIXES = ('UGV-MECH-017', 'UGV-MECH-018', 'UGV-MECH-061')
MG90S, MG996R, DS3218 = 13.4, 55.0, 60.0  # catalogue grams
CATALOG_G = {'REF-SERVO-PAN': MG90S, 'REF-SERVO-TILT': MG90S, 'REF-SERVO-ROLL-R': MG90S, 'REF-SERVO-GRIPPER-R': MG90S,
             'REF-SERVO-TWIST-R': MG996R, 'REF-SERVO-ELBOW-R': MG996R, 'REF-SERVO-WRIST-R': MG996R,
             'REF-SERVO-SHOULDER-R': DS3218,  # DS3218MG 270 deg
             'REF-EYE-CAMERA--1': 12.0, 'REF-EYE-CAMERA-+1': 12.0,  # ESP32-CAM + OV2640
             'REF-TILT-ROD': 1.0}  # 1.5 mm steel pushrod
GROUPS = {
    'base': (('UGV-MECH-001', 'UGV-MECH-002', 'UGV-MECH-003', 'UGV-MECH-004'),
             'printed PETG base plate splice ribs and motor brackets'),
    'body': (('UGV-MECH-010', 'UGV-MECH-011', 'UGV-MECH-012', 'UGV-MECH-013', 'UGV-MECH-015', 'UGV-MECH-022',
              'UGV-MECH-030', 'UGV-MECH-031', 'UGV-MECH-070', 'UGV-MECH-071', 'UGV-MECH-072', 'UGV-MECH-073'),
             'body panels lids end walls fenders mast flange cargo bin and fixtures PETG'),
    'bumpers': (('UGV-MECH-017', 'UGV-MECH-018'), 'TPU bumpers and slot cover'),
    'wheels': (('UGV-MECH-060', 'UGV-MECH-061'), 'wheels printed hubs and TPU tyres'),
    'head': (('UGV-MECH-040', 'UGV-MECH-041', 'UGV-MECH-042', 'UGV-MECH-043', 'UGV-MECH-044', 'UGV-MECH-045', 'UGV-MECH-046',
              'REF-TILT-ROD', 'REF-SERVO-PAN',
              'REF-SERVO-TILT', 'REF-EYE-CAMERA', 'REF-BEARING-PAN'),
             'head neck pan tilt servos and two ESP32-CAM eyes'),
    'arms': (('UGV-MECH-050', 'UGV-MECH-051', 'UGV-MECH-052', 'UGV-MECH-053', 'UGV-MECH-054', 'UGV-MECH-056',
              'UGV-MECH-057', 'UGV-MECH-058', 'UGV-MECH-059', 'REF-SERVO-SHOULDER', 'REF-SERVO-TWIST', 'REF-SERVO-ELBOW', 'REF-SERVO-WRIST',
              'REF-SERVO-ROLL', 'REF-SERVO-GRIPPER', 'REF-BEARING-SHOULDER', 'REF-BEARING-TWIST'),
             'arms right 5-axis left passive shoulder servo and bearings'),
}


def part_mass(root, part):
    """(solid_g, printed_g, material) for one manifest part."""
    name = part['name']
    if name in CATALOG_G:
        return CATALOG_G[name], CATALOG_G[name], 'bought'
    shape = cq.importers.importStep(str(root/part['step'])).val()
    volume, area = shape.Volume(), shape.Area()  # mm3, mm2
    if name.startswith('REF-BEARING'):  # steel bearings
        grams = volume*DENSITY_G_CM3['steel']/1000
        return grams, grams, 'bought'
    material = 'TPU' if name.startswith(TPU_PREFIXES) else 'PETG'
    shell = min(volume, area*SHELL_MM)
    rho = DENSITY_G_CM3[material]/1000
    return volume*rho, (shell + (volume-shell)*INFILL)*rho, material


def _turn(p, origin, axis, deg):
    """p rotated by deg about the axis through origin (Rodrigues)."""
    a, n = math.radians(deg), math.sqrt(sum(c*c for c in axis))
    k, v = [c/n for c in axis], [p[i]-origin[i] for i in range(3)]
    kxv = [k[1]*v[2]-k[2]*v[1], k[2]*v[0]-k[0]*v[2], k[0]*v[1]-k[1]*v[0]]
    kv = sum(k[i]*v[i] for i in range(3))
    return [origin[i] + v[i]*math.cos(a) + kxv[i]*math.sin(a) + k[i]*kv*(1-math.cos(a)) for i in range(3)]


def _at_pose(p, link, q, chain, stow):
    """A point on right-arm link `link`, exported at stow, moved to pose q (the viewer's chain, zero pose)."""
    for j in range(link+1):  # back to the zero pose, root first
        J = chain['joints'][j]
        p = _turn(p, J['origin'], J['axis'], -J['sign']*stow[j])
    for j in range(link, -1, -1):  # out to q, tip first
        J = chain['joints'][j]
        p = _turn(p, J['origin'], J['axis'], J['sign']*q[j])
    return p


def cg_cases(config, manifest, arm_parts):
    """N4: vehicle CG (mm) and static pitch/roll tip angles for every arm pose and payload placement. Budget items
    keep their x/z (y 0, symmetric); the arms allocation sits at the arms group's CAD centroid (printed-estimate
    weights) moved to the pose; the one payload is redistributed, never added twice: `lid` all of it at
    payload_cg_z_mm, `bin` arm.payload_kg of it in the cargo bin (the `store` release point), `gripper` that part held
    in the gripper. arm_parts: (grams, stow centroid, right-arm link or None)."""
    g, motion, arm = config['geometry'], config['motion'], config['geometry']['arm']
    chain, stow, total = manifest['arm_chain'], arm['poses_deg']['stow'], sum(m for m, _, _ in arm_parts)

    def arm_centroid(q):
        pts = [(m, c if link is None else _at_pose(c, link, q, chain, stow)) for m, c, link in arm_parts]
        return [sum(m*p[i] for m, p in pts)/total for i in range(3)]

    arms = next(b for b in config['mass_budget'] if b['name'] == GROUPS['arms'][1])
    fixed = [(b['mass_kg'], (b['x_mm'], b.get('y_mm', 0), b['z_mm'])) for b in config['mass_budget'] if b is not arms]
    pay, held, lid = motion['payload_kg'], arm['payload_kg'], (0.0, 0.0, motion['payload_cg_z_mm'])
    cg = {}
    for pose, q in arm['poses_deg'].items():
        base = fixed + [(arms['mass_kg'], arm_centroid(q))]
        cg[pose] = {}
        for case, load in (('lid', [(pay, lid)]),
                           ('bin', [(pay-held, lid), (held, manifest['arm_poses']['store']['grip_mm'])]),
                           ('gripper', [(pay-held, lid), (held, manifest['arm_poses'][pose]['grip_mm'])])):
            items = base + load
            mass = sum(m for m, _ in items)
            x, y, z = (sum(m*p[i] for m, p in items)/mass for i in range(3))
            cg[pose][case] = {'x': x, 'y': y, 'z': z,
                              'pitch_tip_deg': math.degrees(math.atan((g['wheelbase_mm']/2-abs(x))/z)),
                              'roll_tip_deg': math.degrees(math.atan((g['track_mm']/2-abs(y))/z))}
    return {'arm_centroid_stow': arm_centroid(stow), 'cg': cg}


def screen(root):
    root = Path(root)
    config = json.loads((root/'config/vehicle.json').read_text())
    manifest = json.loads((root/'cad/assembly/manifest.json').read_text())
    if manifest['parameters'] != config:
        raise ValueError('Regenerate CAD before screening mass')
    budget = {x['name']: x['mass_kg'] for x in config['mass_budget']}
    groups, filament, arm_parts = {}, {'PETG': [0.0, 0.0], 'TPU': [0.0, 0.0]}, []
    for group, (prefixes, budget_name) in GROUPS.items():
        solid = printed = 0.0
        count = 0
        for part in manifest['parts']:
            if not part['name'].startswith(prefixes):
                continue
            s, p, material = part_mass(root, part)
            solid, printed, count = solid+s, printed+p, count+1
            if material in filament:
                filament[material][0] += s
                filament[material][1] += p
            if group == 'arms':
                c = cq.importers.importStep(str(root/part['step'])).val().Center()
                arm_parts.append((p, [c.x, c.y, c.z], manifest['arm_chain']['links'].get(part['name'])))
        allocation = budget[budget_name]
        groups[group] = {'parts': count, 'solid_kg': solid/1000, 'printed_kg': printed/1000,
                         'allocation_kg': allocation, 'printed_margin_kg': allocation-printed/1000}
    return {'revision': config['revision'], 'groups': groups,
            'filament_g': {m: {'solid': v[0], 'printed': v[1]} for m, v in filament.items()},
            **cg_cases(config, manifest, arm_parts)}


if __name__ == '__main__':
    print(json.dumps(screen(Path(__file__).resolve().parents[1]), indent=2))
