"""Independent hand-calculation anchors and actual generated geometry checks."""
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('module', ROOT/'cad/drivetrain/build_module.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
r = m.calculate()
assert math.isclose(r['wheel_vertical_n'], 117.6798, abs_tol=1e-5)
assert math.isclose(r['overturning_nm'], 7.060788, abs_tol=1e-6)
assert r['shaft_8mm_yield_margin'] < 2
assert r['shaft_10mm_yield_margin'] > 2
assert r['bearing_static_margin'] > 2
assert r['carrier_yield_margin'] > 2
assert r['shaft_insertion_mm'] >= 11
assert r['candidate_width_mm'] == 300
assert m.calculate(9)['shaft_10mm_yield_margin'] > 2
if __name__ == '__main__':
    manifest = json.loads((ROOT/'cad/drivetrain/manifest.json').read_text())
    assert manifest['inputs'] == m.P, 'Regenerate stale module CAD'
    assert math.isclose(manifest['calculations_9kg_screen']['shaft_10mm_yield_margin'],
                        m.calculate(9)['shaft_10mm_yield_margin'])
    assert not manifest['intersections'], manifest['intersections']
    import cadquery as cq
    solids = {}
    for part in manifest['parts']:
        shape = cq.importers.importStep(str(ROOT/part['step'])).val()
        solids[part['name']] = shape
        assert shape.isValid() and shape.Volume() > 0, part['name']
        assert len(shape.Solids()) == 1, 'Disconnected material: '+part['name']
        if part['printable']:
            b = shape.BoundingBox()
            assert max(b.xlen, b.ylen, b.zlen) <= 240
    for name,key in [('UGV-MECH-042','shaft_start_y_mm'),
                     ('REF-RULAND-OLDHAM','coupling_start_y_mm'),
                     ('REF-6000-2RSH-1','bearing_inner_start_y_mm'),
                     ('REF-6000-2RSH-2','bearing_outer_start_y_mm')]:
        assert math.isclose(solids[name].BoundingBox().ymin,m.P[key],abs_tol=1e-5)
    tyre=solids['UGV-MECH-047'].BoundingBox()
    assert math.isclose(tyre.ymax*2,r['candidate_width_mm'],abs_tol=1e-5)
    assert math.isclose(tyre.xlen,m.P['wheel_radius_mm']*2,abs_tol=1e-5)
    assert math.isclose(tyre.ylen,m.P['wheel_width_mm'],abs_tol=1e-5)
    packaging=json.loads((ROOT/'cad/drivetrain/packaging_report.json').read_text())
    assert packaging['inputs']==m.P and not packaging['intersections']
    assert len(packaging['added_plate_holes_mm'])==16
    base_dxf=(ROOT/'cad/drivetrain/generated/UGV-MECH-040-base-interface-D1.dxf').read_text()
    face_dxf=(ROOT/'cad/drivetrain/generated/UGV-MECH-040-motor-face-interface-D1.dxf').read_text()
    assert base_dxf.count('0\nCIRCLE\n')==4
    assert face_dxf.count('0\nCIRCLE\n')==5
    # Old and new holes must coincide exactly or have a full material ligament.
    vehicle=json.loads((ROOT/'docs/revisions/A2/vehicle.json').read_text())  # D1 drivetrain archive
    old=[(x,y) for x in vehicle['geometry']['chassis_mount_x_mm']
         for y in vehicle['geometry']['chassis_mount_y_mm']]
    for x,y in packaging['added_plate_holes_mm']:
        for a,b in old:
            distance=math.hypot(x-a,y-b)
            assert distance==0 or distance>=9, 'Merged or weak adjacent chassis holes'
    print('PASS: load anchors, margins, insertion, real STEP solids and print sizes')
