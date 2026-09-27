"""D1 left/front drivetrain candidate. mm; nominal fits, no production release.

World datum: x=0 at wheel axis (add +105 for front), y=0 vehicle centre,
z=0 ground. REF solids are bored supplier envelopes, not vendor CAD.
"""
from pathlib import Path
import itertools
import json
import math
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
P = json.loads((ROOT/'config/drivetrain_module.json').read_text())
OUT = ROOT/'cad/drivetrain/generated'


def calculate(mass_kg=None):
    p = P
    mass_kg = p['gross_mass_kg'] if mass_kg is None else mass_kg
    if mass_kg <= 0:
        raise ValueError('Screening mass must be positive')
    fz = mass_kg*9.80665*p['shock_g']/p['load_sharing_wheels']
    fa = fz*p['lateral_friction']
    moment = fa*p['wheel_radius_mm']/1000
    b1 = p['bearing_inner_start_y_mm']+p['bearing_width_mm']/2
    b2 = p['bearing_outer_start_y_mm']+p['bearing_width_mm']/2
    span = b2-b1
    # Resolve the overturning couple in the radial bearing reactions.
    r1 = fz*(b2-p['wheel_center_y_mm'])/span
    r2 = fz*(p['wheel_center_y_mm']-b1)/span
    radial = max(abs(r1), abs(r2))+moment*1000/span
    p0 = max(radial, 0.6*radial+0.5*fa)
    def shaft_margin(d):
        bending = 32*moment*1000/(math.pi*d**3)
        torsion = 16*p['shaft_screening_torque_nm']*1000/(math.pi*d**3)
        stress = p['shaft_notch_factor_assumption']*math.sqrt(bending**2+3*torsion**2)
        return p['shaft_min_yield_mpa_assumption']/stress
    root_moment = fz*(p['wheel_center_y_mm']-max(p['carrier_bolt_y_mm']))+moment*1000
    stress = p['carrier_stress_factor_assumption']*6*root_moment/(p['carrier_effective_width_mm_assumption']*p['carrier_thickness_mm']**2)
    return dict(gross_mass_kg=mass_kg,wheel_vertical_n=fz, wheel_axial_n=fa, overturning_nm=moment,
                bearing_span_mm=span, bearing_worst_radial_n=radial,
                bearing_static_margin=p['bearing_static_n']/p0,
                shaft_8mm_yield_margin=shaft_margin(8),
                shaft_10mm_yield_margin=shaft_margin(10),
                carrier_stress_mpa=stress,
                carrier_yield_margin=p['carrier_min_yield_mpa_assumption']/stress,
                shaft_insertion_mm=p['coupling_start_y_mm']+p['coupling_length_mm']-p['shaft_start_y_mm'],
                candidate_width_mm=2*p['wheel_center_y_mm']+p['wheel_width_mm'])


def box(size, center):
    return cq.Workplane('XY').box(*size).translate(center).val()


def cyl(r, start, end, x=0, z=None):
    return cq.Solid.makeCylinder(r, end-start, cq.Vector(x,start,P['axle_z_mm'] if z is None else z), cq.Vector(0,1,0))


def ring(ro, ri, start, end):
    return cyl(ro,start,end).cut(cyl(ri,start-0.01,end+0.01))


def parts():
    p=P; z=p['axle_z_mm']; items=[]
    def add(name, shape, color, material, printable=False, role='own_detail_candidate'):
        items.append(dict(name=name,shape=shape.clean(),color=color,material=material,
                          printable=printable,role=role))
    # 5 mm sole with ears outside the motor body; no motor/base overlap.
    carrier=box((66,68,5),(7,109,41.5))
    for x in p['carrier_bolt_x_mm']:
        carrier=carrier.fuse(box((10,10,5),(x,70,41.5)))
    for x,y in itertools.product(p['carrier_bolt_x_mm'],p['carrier_bolt_y_mm']):
        carrier=carrier.cut(cq.Solid.makeCylinder(2.25,8,cq.Vector(x,y,38)))
    face=box((44,3,45),(8,76.5,61.5)).cut(cyl(6.2,74,79))
    # Four of six M3 mounting holes: motor clocked 90 degrees so offset is x.
    for x,dz in itertools.product((7-15.5*math.sqrt(3)/2,7+15.5*math.sqrt(3)/2),(-7.75,7.75)):
        face=face.cut(cyl(1.7,74,79,x,z+dz))
    housing=cyl(18,119.5,143).cut(cyl(13,119,141)).cut(cyl(11.5,141,144))
    carrier=carrier.fuse(face).fuse(housing)
    # Trim the outboard sole corner clear of the rotating rim cavity.
    carrier=carrier.cut(box((20,30,10),(42,134,40)))
    cap=ring(18,7.5,118,119.5).cut(box((50,5,20),(0,119,34)))
    # Axial cap bolt envelope: pilot bores are NOT tapped-thread geometry.
    for angle in (45,135,225,315):
        x=15.5*math.cos(math.radians(angle)); dz=15.5*math.sin(math.radians(angle))
        carrier=carrier.cut(cyl(1.025,119.4,125.5,x,z+dz))
        cap=cap.cut(cyl(1.4,117,120,x,z+dz))
    add('UGV-MECH-040',carrier,(.58,.62,.68),'6061-T6')
    add('UGV-MECH-041',cap,(.65,.67,.70),'6061-T6')
    # Nominal retention groove; supplier groove/shoulder tolerances remain a gate.
    shaft=cyl(5,p['shaft_start_y_mm'],141).fuse(cyl(7.5,141,143.5)).fuse(cyl(28,143.5,147))
    shaft=shaft.cut(ring(5.1,4.7,117.7,118.8))
    for x,dz in ((22,0),(-22,0),(0,22),(0,-22)):
        shaft=shaft.cut(cyl(1.7,143,148,x,z+dz))
    add('UGV-MECH-042',shaft,(.46,.49,.53),'C45 normalized, certified yield required')
    add('UGV-MECH-043',ring(7.5,5.05,127.5,133),(.64,.66,.68),'steel')
    add('UGV-MECH-044',ring(12.95,11.5,127.5,133),(.64,.66,.68),'steel')
    add('UGV-MECH-045',ring(7.5,5.05,118.8,119.5),(.64,.66,.68),'steel')
    # Rim includes bead shoulders and an outboard web, accessible from outside.
    rim=ring(45,42,120,150).fuse(ring(47,42,120,122)).fuse(ring(47,42,148,150))
    rim=rim.fuse(ring(45,7.6,147,150))
    for x,dz in ((22,0),(-22,0),(0,22),(0,-22)):
        rim=rim.cut(cyl(1.7,146,151,x,z+dz))
        rim=rim.cut(cq.Solid.makeCone(1.7,3.5,1.8,cq.Vector(x,148.2,z+dz),cq.Vector(0,1,0)))
    tire=ring(60,45.2,120,150).cut(ring(54,45.1,122,148))
    tire=tire.cut(cyl(47.2,119.9,122)).cut(cyl(47.2,148,150.1))
    # Positive torque drive: eight keys engage tyre ribs; not friction-only.
    for angle in range(0,360,45):
        def rotate(s): return s.rotate((0,0,z),(0,1,z),angle)
        rim=rim.fuse(rotate(box((5,22,5),(0,135,z+47))))
        tire=tire.fuse(rotate(box((6,26,10),(0,135,z+50))))
        tire=tire.cut(rotate(box((5.4,22.4,5.6),(0,135,z+47))))
    add('UGV-MECH-046',rim,(.24,.31,.36),'PAHT-CF coupon required',True)
    add('UGV-MECH-047',tire,(.12,.13,.14),'TPU 95A coupon required',True)
    for n,y in enumerate((119.5,133),1):
        add(f'REF-6000-2RSH-{n}',ring(13,5,y,y+8),(.55,.57,.60),'catalogue mass 0.019 kg',role='supplier_envelope')
    motor=cyl(18.4,75-p['motor_body_length_mm'],75,x=7)
    motor=motor.fuse(cyl(6,75,81))
    dshaft=cyl(3,81,97).cut(box((20,18,3),(0,89,63.9)))
    motor=motor.fuse(dshaft)
    add('REF-POLOLU-4754',motor,(.68,.69,.71),'catalogue mass 0.205 kg',role='supplier_envelope')
    coupling=cyl(12.7,85.5,117.3).cut(cyl(3.05,85.4,97.4)).cut(cyl(5.05,105.4,117.4))
    add('REF-RULAND-OLDHAM',coupling,(.82,.49,.19),'supplier mass TBD',role='supplier_envelope')
    clip=ring(6.5,4.7,117.8,118.7).cut(box((4,2,5),(0,118.2,66)))
    add('REF-RETAINING-RING-10',clip,(.40,.43,.46),'unselected supplier',role='retention_envelope_not_selected')
    return items


def clashes(items):
    result=[]
    for a,b in itertools.combinations(items,2):
        ba=a['shape'].BoundingBox(); bb=b['shape'].BoundingBox()
        if any(getattr(ba,k+'max') <= getattr(bb,k+'min')+1e-6 or getattr(bb,k+'max') <= getattr(ba,k+'min')+1e-6 for k in 'xyz'):
            continue
        v=a['shape'].intersect(b['shape']).Volume()
        if v>.01: result.append(dict(a=a['name'],b=b['name'],volume_mm3=round(v,4)))
    return result


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    items=parts(); assembly=cq.Assembly(name='UGV-01-D1-DRIVETRAIN-CANDIDATE')
    records=[]
    for part in items:
        shape=part['shape']; assert shape.isValid() and shape.Volume()>0,part['name']
        path=OUT/(part['name']+'.step'); cq.exporters.export(shape,str(path))
        if part['printable']:
            # Wheel axis vertical on the build plate, rim web down.
            local=shape.rotate((0,0,0),(1,0,0),90)
            b=local.BoundingBox(); local=local.translate(cq.Vector(-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))
            cq.exporters.export(local,str(OUT/(part['name']+'.stl')),tolerance=.05,angularTolerance=.1)
        assembly.add(shape,name=part['name'],color=cq.Color(*part['color']))
        records.append({**{k:v for k,v in part.items() if k!='shape'},'step':str(path.relative_to(ROOT)),
                        'volume_mm3':round(shape.Volume(),3)})
    assembly.save(str(OUT/'UGV-01-D1-drivetrain.step'))
    report=dict(inputs=P,calculations=calculate(),calculations_9kg_screen=calculate(9),
                parts=records,intersections=clashes(items),
                status='DETAIL_CANDIDATE_NOT_FOR_MANUFACTURE',
                open_gates=['shaft bearing fits and retaining-ring groove supplier drawing',
                            'fatigue, stress concentrations and carrier FEA',
                            'cap screw and rim fastener sizing with supplier heads',
                            'rim tyre torque transfer and print coupons',
                            'mass budget closure and full-vehicle service/tool access review'])
    (ROOT/'cad/drivetrain/manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'calculations':calculate(),'intersections':report['intersections'],'parts':len(records)},indent=2))


if __name__=='__main__': main()
