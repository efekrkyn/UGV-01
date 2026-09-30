"""M2 Task 5 (M3 geometry): every printed part has one print-plan entry; its STL lies on the bed in the planned
orientation, fits the 240 mm design envelope and stands on a real contact patch; the guide is up to date."""
import importlib.util
import json
import math
from pathlib import Path
import struct

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]


def stl_mesh(path):
    """(triangles, bbox min, bbox max, enclosed volume mm3) of a binary or ASCII STL; (0, [inf]*3, [-inf]*3, 0) if empty."""
    data = path.read_bytes() if path.exists() else b''
    n = struct.unpack_from('<I', data, 80)[0] if len(data) >= 84 else -1
    if len(data) == 84 + 50 * n:
        tris = [(t[3:6], t[6:9], t[9:12]) for t in struct.iter_unpack('<12fH', data[84:])]
    else:
        v = [tuple(map(float, line.split()[1:4])) for line in data.decode(errors='replace').splitlines()
             if line.strip().startswith('vertex')]
        tris = [tuple(v[i:i + 3]) for i in range(0, len(v) - 2, 3)]
    pts = [p for t in tris for p in t]
    lo = [min((p[i] for p in pts), default=math.inf) for i in range(3)]
    hi = [max((p[i] for p in pts), default=-math.inf) for i in range(3)]
    volume = sum(a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                 + a[2] * (b[0] * c[1] - b[1] * c[0]) for a, b, c in tris) / 6
    return len(tris), lo, hi, volume



spec = importlib.util.spec_from_file_location('print_plan', ROOT / 'tools/print_plan.py')
pp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pp)
manifest = json.loads((ROOT / 'cad/assembly/manifest.json').read_text())
config = json.loads((ROOT / 'config/vehicle.json').read_text())
assert manifest['parameters'] == config, 'CAD stale'
limit = config['geometry']['print_design_limit_mm']
printed = [p['name'] for p in manifest['parts'] if p['printable']]
for name in printed:
    matches = [e for e in pp.PLAN if name.startswith(e['prefix'])]
    longest = max(len(e['prefix']) for e in matches) if matches else 0
    assert len([e for e in matches if len(e['prefix']) == longest]) == 1, (name, 'needs exactly one plan entry')
    solid = pp.oriented(name)
    b = solid.BoundingBox()
    assert abs(b.zmin) < 1e-6 and max(b.xlen, b.ylen) <= limit and b.zlen <= limit, (name, b.xlen, b.ylen, b.zlen)
    if not pp.entry(name)['hold']:  # held parts keep their assembly orientation until the interface decision
        # from -0.1: coplanar faces fail; part-sized, since OCC drops the section of a tiny part in a 400 mm slab
        slab = cq.Workplane('XY').box(b.xlen + 20, b.ylen + 20, 0.5).translate((b.center.x, b.center.y, 0.15)).val()
        contact = solid.intersect(slab).Volume() / 0.4
        assert contact >= min(150.0, 0.25 * b.xlen * b.ylen), (name, 'bed contact mm2', round(contact))
    # N8 (M3 review): the delivered STL itself, not only the STEP it came from: a real mesh with the oriented solid's
    # bed position, extent and volume, so an empty, stale, turned or swapped file fails (tessellation 0.05 mm: the
    # generated meshes sit within 0.02 mm and 0.05 % of their solids).
    tris, lo, hi, volume = stl_mesh(ROOT / f'cad/assembly/generated/{name}.stl')
    edges = max(abs(a - c) for a, c in zip(lo + hi, (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)))
    assert tris and edges <= 0.1 and abs(volume - solid.Volume()) <= 0.005 * solid.Volume(), \
        (name, tris, round(edges, 3), round(volume), round(solid.Volume()), 'STL stale: python3 tools/print_plan.py')
assert not [e for e in pp.PLAN if not any(n.startswith(e['prefix']) for n in printed)], 'unused plan entries'
# Every printed part is drawn: arm links (DD81) and head mechanism (DD82); nothing on hold.
held = {n for n in printed if pp.entry(n)['hold']}
assert not held, held
guide = (ROOT / 'docs/print_guide_A3.md').read_text()
assert guide == pp.guide(), 'docs/print_guide_A3.md is stale: python3 tools/print_plan.py'
inserts = pp.fasteners()['M3 ısıl insert (Ø4,0 × 6 delik)']
assert inserts == 50, inserts  # DD93/M02: +8 in the splice ribs; DD94/R04: +8 for the left arm's stand-ins
print(f"PASS: {len(printed)} printed parts planned, none on hold, oriented STLs on the bed within "
      f"{limit} mm, contact patches, {inserts} M3 inserts, guide up to date")
