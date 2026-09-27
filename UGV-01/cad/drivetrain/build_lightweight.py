"""D2A conservative envelope subset: open rim web and thinner tread bays.

The original eight TPU torque ribs and all four rim bolt regions are retained.
This is a print/test candidate, not a qualified production wheel.
"""
from pathlib import Path
import json
import math
import cadquery as cq

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/drivetrain/generated/lightweight'
OUT.mkdir(parents=True,exist_ok=True)
d1=json.loads((ROOT/'cad/drivetrain/budget_report.json').read_text())
z=60


def cyl(r,y0,y1,x=0,dz=0):
    return cq.Solid.makeCylinder(r,y1-y0,cq.Vector(x,y0,z+dz),cq.Vector(0,1,0))


def exported(part,shape):
    assert shape.isValid() and len(shape.Solids())==1
    base=cq.importers.importStep(str(ROOT/f'cad/drivetrain/generated/{part}.step')).val()
    outside=shape.cut(base).Volume()
    assert outside<.01, (part,outside)
    cq.exporters.export(shape,str(OUT/f'{part}-B.step'))
    local=shape.rotate((0,0,0),(1,0,0),90)
    b=local.BoundingBox()
    local=local.translate(cq.Vector(-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))
    cq.exporters.export(local,str(OUT/f'{part}-B.stl'),tolerance=.05,angularTolerance=.1)
    return (base.Volume()-shape.Volume())*1.2e-6


rim=cq.importers.importStep(str(ROOT/'cad/drivetrain/generated/UGV-MECH-046.step')).val()
for angle in (45,135,225,315):
    t=math.radians(angle)
    rim=rim.cut(cyl(11,146.9,150.1,28*math.cos(t),28*math.sin(t)))
rim=rim.clean()
rim_saving=exported('UGV-MECH-046',rim)

# Same nominal geometry, new material/procurement revision; STEP carries no
# material certificate, so the BOM and drawing must enforce the condition.
shaft=cq.importers.importStep(str(ROOT/'cad/drivetrain/generated/UGV-MECH-042.step')).val()
cq.exporters.export(shaft,str(OUT/'UGV-MECH-042-B.step'))

tire=cq.importers.importStep(str(ROOT/'cad/drivetrain/generated/UGV-MECH-047.step')).val()
removed=cyl(56,122,148).cut(cyl(54,121.9,148.1))
for angle in range(0,360,45):
    # Keep full-thickness radial bridges around the eight keyed torque ribs.
    keep=cq.Workplane('XY').box(8,26,15).translate((0,135,z+54)).val()
    keep=keep.rotate((0,0,z),(0,1,z),angle)
    removed=removed.cut(keep)
tire=tire.cut(removed).clean()
tire_saving=exported('UGV-MECH-047',tire)

report={'revision':'D2A','status':'PRINT_AND_TEST_CANDIDATE',
        'rim_saving_kg_per_wheel':rim_saving,'tire_saving_kg_per_wheel':tire_saving,
        'curb_mass_kg':d1['curb_without_reserve_kg']-4*(rim_saving+tire_saving),
        'remaining_reserve_to_6kg_kg':6-d1['curb_without_reserve_kg']+4*(rim_saving+tire_saving),
        'unapproved_intersections_impossible_by_subset':True,
        'mechanical_changes':['Four 22 mm diameter windows through the outboard rim web between M3 bolts',
                              'Tread bays thinner by 2 mm while eight key ribs remain full thickness'],
        'conditions':['A 42CrMo4+QT 10 mm shaft with certified >=650 MPa yield is required for the 9 kg, mu=1.2 material screen',
                      'TPU abrasion and key torque tests pending',
                      'PAHT-CF rim bending, layer orientation and fastener fatigue tests pending',
                      'The remaining mass reserve is too small for release']}
(ROOT/'cad/drivetrain/lightweight_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
