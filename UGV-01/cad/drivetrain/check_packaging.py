"""Place D1 modules in A0 body; export candidate only, preserving A0 baseline."""
import itertools
import json
from pathlib import Path
import cadquery as cq
from build_module import ROOT, P, parts, box, clashes

out=ROOT/'cad/drivetrain/generated'
baseline=json.loads((ROOT/'cad/assembly/manifest.json').read_text())
vehicle=json.loads((ROOT/'config/vehicle.json').read_text())
assert baseline['parameters']==vehicle, 'A0 CAD is stale'
assert vehicle['revision']=='A0', 'Re-review adaptation for a new baseline'
items=[]; hole_centers=[]
for end,side in itertools.product((-1,1),(-1,1)):
    for x,y in itertools.product(P['carrier_bolt_x_mm'],P['carrier_bolt_y_mm']):
        hole_centers.append((end*(105+x),side*y))
for entry in baseline['parts']:
    if entry['name'].startswith(('REF-MOTOR','REF-WHEEL')): continue
    shape=cq.importers.importStep(str(ROOT/entry['step'])).val()
    name=entry['name']
    if name=='UGV-MECH-001':
        for x,y in hole_centers:
            shape=shape.cut(cq.Solid.makeCylinder(2.25,6,cq.Vector(x,y,35)))
    if name.startswith(('UGV-MECH-010','UGV-MECH-011','UGV-MECH-012')):
        for end,side in itertools.product((-1,1),(-1,1)):
            # Remove the old end foot; it occupies the new carrier sole.
            shape=shape.cut(box((14.02,17.02,4.02),(end*140,side*91.5,41)))
            shape=shape.cut(box((69,26,37),(end*111.5,side*99,56.5)))
    items.append({**entry,'shape':shape})
for end,side in itertools.product((-1,1),(-1,1)):
    suffix=('F' if end>0 else 'R')+('L' if side>0 else 'R')
    for entry in parts():
        shape=entry['shape']
        if end<0: shape=shape.mirror('YZ')
        if side<0: shape=shape.mirror('XZ')
        shape=shape.translate(cq.Vector(end*105,0,0))
        items.append({**entry,'name':entry['name']+'-'+suffix,'shape':shape})
assembly=cq.Assembly(name='UGV-01-D1-PACKAGING-NOT-FOR-MANUFACTURE')
records=[]
for entry in items:
    shape=entry['shape']; assert shape.isValid() and shape.Volume()>0,entry['name']
    assembly.add(shape,name=entry['name'],color=cq.Color(*entry['color']))
    records.append(dict(name=entry['name'],volume_mm3=shape.Volume(),solids=len(shape.Solids())))
assembly.save(str(out/'UGV-01-D1-packaging.step'))
collisions=clashes(items)
report=dict(status='D1_PACKAGING_CANDIDATE',baseline_revision='A0',candidate_width_mm=300,
            inputs=P,parts=records,intersections=collisions,added_plate_holes_mm=hole_centers,
            modifications=['Four offset gearmotors with separately supported wheels',
                           'Four carrier interfaces: 16 M4 holes, 4 reused from A0, 12 new',
                           'Drivetrain windows and removal of four old end feet'],
            limitations=['Remaining body feet need strength review',
                         'No bolt heads, tooling sweeps, cable harness or tray supports',
                         'A0 URDF and vehicle.json unchanged until full interface release'])
(ROOT/'cad/drivetrain/packaging_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'parts':len(items),'intersections':collisions},indent=2))
if collisions: raise SystemExit('Packaging has unresolved intersections')
