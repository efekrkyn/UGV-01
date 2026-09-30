"""Functional interface concept + reserved volumes; NOT production CAD.

CadQuery 2.6.1, millimetres. M3 (DD72-DD74): character body 300 x 236 x z210 with the motors inside,
fenders over the wheels, head 122 mm above the body, 5-axis right arm out of the side wall and a
passive left arm. Arm poses and the pose-graph edges are swept for collisions.
"""
from pathlib import Path
import itertools
import json
import math
import xml.etree.ElementTree as ET
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
P = json.loads((ROOT/'config/vehicle.json').read_text())
G = P['geometry']
M = P['motor']
OUT = ROOT/'cad/assembly/generated'
OUT.mkdir(parents=True, exist_ok=True)
PARTS = []
ASSEMBLY = cq.Assembly(name='UGV-01_A3_LITE_CONCEPT_NOT_FOR_MANUFACTURE')
PETG, TPU = (0.27,0.28,0.30), (0.10,0.11,0.12)
ORANGE, DARK, SERVO, STEEL = (0.80,0.53,0.12), (0.30,0.31,0.33), (0.10,0.10,0.12), (0.70,0.70,0.72)


def box(size, center):
    return cq.Workplane('XY').box(*size).translate(center).val()


def cylinder(radius, length, start, axis=(0, 0, 1)):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*axis))


def spur_gear(teeth, module, width):
    """20 deg involute spur gear, axis +y from y = 0 to width, centred on the y axis (straight root segments)."""
    rp=teeth*module/2; rb=rp*math.cos(math.radians(20)); ra,rf=rp+module,rp-1.25*module
    inv=lambda a: math.tan(a)-a
    half=math.pi/(2*teeth)+inv(math.radians(20))  # half tooth angle at the base circle
    flank=[(r,half-inv(math.acos(rb/r))) for r in (rb+(ra-rb)*i/5 for i in range(6))]
    pts=[]
    for k in range(teeth):
        c=2*math.pi*k/teeth
        pts.append((rf*math.cos(c-half),rf*math.sin(c-half)))
        pts+=[(r*math.cos(c-t),r*math.sin(c-t)) for r,t in flank]
        pts+=[(r*math.cos(c+t),r*math.sin(c+t)) for r,t in reversed(flank)]
        pts.append((rf*math.cos(c+half),rf*math.sin(c+half)))
    solid=cq.Workplane('XY').polyline(pts).close().extrude(width).val()
    return solid.rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),-90)  # profile (u, v) -> (x, -z), extrusion -> +y


def add(name, shape, color, printable=False, role='interface_concept'):
    if not shape.isValid() or shape.Volume() <= 0:
        raise ValueError(f'Invalid solid: {name}')
    step = OUT/f'{name}.step'
    cq.exporters.export(shape, str(step))
    # Printed parts' STLs are written in print orientation by tools/print_plan.py (M2 Task 5).
    ASSEMBLY.add(shape, name=name, color=cq.Color(*color))
    PARTS.append({'name':name,'shape':shape,'step':str(step.relative_to(ROOT)),
                  'printable':printable,'role':role,'color':color})


W=G['body_width_mm']; HW=W/2
top=G['body_top_z_mm']
plate_top=G['plate_bottom_z_mm']+G['plate_thickness_mm']
holes=list(itertools.product(G['chassis_mount_x_mm'],G['chassis_mount_y_mm']))
# A3: printed PETG base plate in two halves (<=240 mm); the seam avoids every mount hole and
# is bridged by the two printed splice ribs (UGV-MECH-002).
half_l,seam=G['plate_length_mm']/2,G['plate_seam_x_mm']
FAST=G['fasteners']
IT=G['internal']
HD=G['head']
# M2: four M3 bolts clamp beam (under the lid), lid, mast flange and pan base; clear of the lid seam.
NECK_BOLTS=[(G['neck_axis_xy_mm'][0]+dx,G['neck_axis_xy_mm'][1]+dy) for dx in (-14,14) for dy in (-14,14)]
# M2: each motor clamp is held by two M3 bolts through cap, cradle and base plate (nuts under the plate).
CLAMP_BOLTS=[(x+dx,side*(G['motor_face_abs_y_mm']-38)) for x in (-G['wheelbase_mm']/2,G['wheelbase_mm']/2)
             for side in (-1,1) for dx in (-G['motor_bracket_bolt_dx_mm'],G['motor_bracket_bolt_dx_mm'])]
# M02 (full review, DD93): each splice rib bridges the seam with two M3 x 10 on either side, from under the plate into
# heat-set inserts in the rib (no glue): the bolts carry the seam's bending as shear.
RAIL_BOLTS=[(x,s_*G['rail_center_y_mm']) for x in G['rail_bolt_x_mm'] for s_ in (-1,1)]
for suffix,(x0,x1) in (('R',(-half_l,seam)),('F',(seam,half_l))):
    half=box((x1-x0,G['plate_width_mm'],G['plate_thickness_mm']),
             ((x0+x1)/2,0,G['plate_bottom_z_mm']+G['plate_thickness_mm']/2))
    for x,y in holes:
        half=half.cut(cylinder(G['chassis_mount_diameter_mm']/2,20,(x,y,G['plate_bottom_z_mm']-5)))
    for x,y in CLAMP_BOLTS+RAIL_BOLTS+[tuple(m) for k in ('battery_mounts_mm','tray_mounts_mm','ballast_mounts_mm')
                            for m in IT[k]]+[tuple(m) for m in IT['cargo']['leg_mounts_mm']]:
        half=half.cut(cylinder(FAST['m3_clear_mm']/2,20,(x,y,G['plate_bottom_z_mm']-5)))
    add(f'UGV-MECH-001-{suffix}',half,PETG,True)

for sign in (-1,1):
    rib=box((G['rail_length_mm'],G['rail_width_mm'],G['rail_height_mm']),(0,sign*G['rail_center_y_mm'],plate_top+G['rail_height_mm']/2))
    for x in G['rail_bolt_x_mm']:
        rib=rib.cut(cylinder(FAST['m3_insert_hole_mm'][0]/2,FAST['m3_insert_hole_mm'][1]+0.5,(x,sign*G['rail_center_y_mm'],plate_top-0.01)))
    add(f'UGV-MECH-002-{sign:+d}',rib,PETG,True)

wall=G['wall_thickness_mm']
lid_z=top-G['lid_thickness_mm']
height=lid_z-plate_top
segment_length=G['body_length_mm']/3
BOSS_Y=HW-6  # lid screw bosses
# M3 arm (DD73): shoulder axis through the front side panels, 6804-2RS in a wall boss carries the arm load.
A=G['arm']
xs,zs=A['shoulder_xz_mm']
YA=A['plane_abs_y_mm']
L1,L2,L3=A['upper_mm'],A['forearm_mm'],A['grip_mm']
TB=A['twist_bearing_mm']
MG,M9,HORN=A['mg996r_mm'],A['mg90s_mm'],A['horn_25t_mm']
xe,xw=xs+L1,xs+L1+L2
BRG=(10,16,7)  # 6804-2RS: bore radius, outer radius, width (shoulder, in the wall boss)
TIP=A['j1_spline_abs_y_mm']  # DS3218 spline tip |y|; the journal's horn flange starts 2.5 mm outboard
J1_FRAME_Z=(zs+23.5,zs-41)   # centres of the frame's two 8 mm arms (screwed to the wall)
BTW=(10,13.5,4)  # 6704-2RS thin section on the upper-arm twist (the ring stays inside the wheel line)
boss_r=BRG[1]+3
for module,cx in enumerate((-segment_length,0,segment_length),start=10):
    for side in (-1,1):
        panel=box((segment_length-0.5,wall,height),
                  (cx,side*(HW-wall/2),plate_top+height/2))
        for x in G['chassis_mount_x_mm']:
            if abs(x-cx) < segment_length/2:
                foot=box((14,17,4),(x,side*(HW-8.5),plate_top+2))
                panel=panel.fuse(foot).cut(cylinder(2.25,8,(x,side*(HW-10),plate_top-1)))
        for x in (-G['wheelbase_mm']/2,G['wheelbase_mm']/2):
            # M3: the motor sits inside; only the hub boss crosses the wall.
            panel=panel.cut(cylinder(G['hub_wall_hole_diameter_mm']/2,W+40,(x,-HW-20,G['wheel_axle_z_mm']),(0,1,0)))
        # Lid bosses are through-hole interfaces; inserts require coupons.
        for x in (cx-38,cx+38):
            boss=box((12,12,8),(x,side*BOSS_Y,lid_z-4))
            ins_d,ins_depth=FAST['m3_insert_hole_mm']  # M2: lid screws into M3 heat-set inserts
            panel=panel.fuse(boss).cut(cylinder(ins_d/2,ins_depth+0.5,(x,side*BOSS_Y,lid_z-ins_depth)))
        FENS=G['fender']
        for x in FENS['screw_x_mm']:  # M3 through fender flange + panel, nut inside
            if abs(x-cx) < segment_length/2-3:
                panel=panel.cut(cylinder(FAST['m3_clear_mm']/2,wall+2,(x,side*(HW-wall-1) if side>0 else -HW-1,FENS['screw_z_mm']),(0,1,0)))
        if module == 12 and side < 0:  # M3 screws into the shoulder-servo frame inserts
            for dx in (-A['j1_frame_screw_dx_mm'],A['j1_frame_screw_dx_mm']):
                for zf in J1_FRAME_Z:
                    panel=panel.cut(cylinder(FAST['m3_clear_mm']/2,wall+2,(xs+dx,-HW-1,zf),(0,1,0)))
        if module == 12:  # shoulder bearing boss: seat from outside, journal hole inward
            y_in=HW-11
            panel=panel.fuse(cylinder(boss_r,11,(xs,side*y_in if side>0 else -HW,zs),(0,1,0)))
            panel=panel.cut(cylinder(BRG[1],8,(xs,side*(HW-BRG[2]-0.5) if side>0 else -HW-0.5,zs),(0,1,0)))
            panel=panel.cut(cylinder(BRG[0]+0.5,6,(xs,side*(y_in-1) if side>0 else -(y_in+5),zs),(0,1,0)))
        add(f'UGV-MECH-{module:03d}-{side:+d}',panel.clean(),ORANGE,True)
    lid=box((segment_length-0.5,W,G['lid_thickness_mm']),
            (cx,0,lid_z+G['lid_thickness_mm']/2))
    lid=cq.Workplane(obj=lid).faces('>Z').edges().chamfer(1).val()
    for x,y in itertools.product((cx-38,cx+38),(-BOSS_Y,BOSS_Y)):
        lid=lid.cut(cylinder(1.7,8,(x,y,lid_z-1)))
    if cx == 0:
        for x,y in NECK_BOLTS:
            lid=lid.cut(cylinder(FAST['m3_clear_mm']/2,8,(x,y,lid_z-1)))
        lid=lid.cut(cylinder(IT['neck_cable_hole_mm']/2,8,(*HD['cable_hole_xy_mm'],lid_z-1)))
    if cx > 0:  # M3: cargo drop slot under the arm's "store" pose
        (sw,sl),(scx,scy)=IT['cargo']['slot_mm'],IT['cargo']['slot_center_xy_mm']
        lid=lid.cut(box((sw,sl,10),(scx,scy,lid_z)))
    if cx < 0:
        # A3: E-stop through the rear lid, reachable from above and behind.
        ex,ey=G['estop_xy_mm']
        lid=lid.cut(cylinder(G['estop_body_mm'][0]/2+0.5,10,(ex,ey,lid_z-1)))
    add(f'UGV-MECH-013-{module-9}',lid,(0.92,0.65,0.19),True)

for sign in (-1,1):
    # End walls sit between side panels, keeping a 0.25 mm assembly gap.
    end_wall=box((wall,W-2*wall-0.5,height),
                 (sign*(G['body_length_mm']/2-wall/2),0,plate_top+height/2))
    if sign>0:
        # A2: status light bar window replaces the A1 front camera opening.
        opening=box(G['light_bar_opening_mm'],
                    (G['body_length_mm']/2,0,G['light_bar_center_z_mm']))
        end_wall=end_wall.cut(opening)
        for vz in IT['front_vents_z_mm']:  # M2: vents in front of the ballast resistors
            end_wall=end_wall.cut(box((wall+2,40,3),(G['body_length_mm']/2-wall/2,0,vz)))
        for yb_ in IT['cargo']['flange_screw_y_mm']:  # M3 into the cargo bin flange inserts
            end_wall=end_wall.cut(cylinder(FAST['m3_clear_mm']/2,wall+2,(G['body_length_mm']/2-wall-1,yb_,IT['cargo']['flange_screw_z_mm']),(1,0,0)))
        for side in (-1,1):  # M2: ToF cables from the bumper into the body
            end_wall=end_wall.cut(cylinder(IT['tof_cable_hole_mm']/2,wall+2,
                (G['body_length_mm']/2-wall-1,side*G['tof_center_y_mm'],105),(1,0,0)))
    add(f'UGV-MECH-022-{sign:+d}',end_wall,ORANGE,True)
    bumper=box((15,W-10,30),(sign*157.5,0,105))
    if sign>0:  # A3: two front ToF windows through the TPU bumper
        for side in (-1,1):
            bumper=bumper.cut(box(G['tof_window_mm'],(157.5,side*G['tof_center_y_mm'],105)))
    add(f'UGV-MECH-017-{sign:+d}',bumper,TPU,True)

FEN=G['fender']
for x in (-G['wheelbase_mm']/2,G['wheelbase_mm']/2):
    for side in (-1,1):
        suffix=f'{"F" if x>0 else "R"}{"L" if side>0 else "R"}'
        z=G['wheel_axle_z_mm']
        face=G['motor_face_abs_y_mm']
        # JGA25-370: body inward from the gearbox face, bushing + D-shaft outward into the hub.
        body=cylinder(M['body_diameter_mm']/2,M['body_length_mm'],
                      (x,face-M['body_length_mm'] if side>0 else -face,z),(0,1,0))
        bushing=cylinder(3.5,2.5,(x,face if side>0 else -face-2.5,z),(0,1,0))
        shaft=cylinder(M['shaft_diameter_mm']/2,M['shaft_length_mm'],
                       (x,face if side>0 else -face-M['shaft_length_mm'],z),(0,1,0))
        flat=M['shaft_flat_to_mm']-M['shaft_diameter_mm']/2  # D flat on top, distance from the axis
        shaft=shaft.cut(box((10,M['shaft_length_mm']+2,5),(x,side*(face+M['shaft_length_mm']/2),z+flat+2.5)))
        motor=body.fuse(bushing).fuse(shaft).clean()
        add(f'REF-MOTOR-{suffix}',motor,(0.66,0.67,0.69),role='reserved_envelope')
        bw,bl=G['motor_bracket_mm']
        clamp_top=z+M['body_diameter_mm']/2+4
        bracket=box((bw,bl,clamp_top-plate_top),(x,side*(face-38),(clamp_top+plate_top)/2)).cut(body)
        for bx,by in CLAMP_BOLTS:
            bracket=bracket.cut(cylinder(FAST['m3_clear_mm']/2,clamp_top-plate_top+2,(bx,by,plate_top-1)))
        # M2: split on the motor axis -> printable cradle (on the plate) and cap.
        add(f'UGV-MECH-003-{suffix}',bracket.intersect(box((bw+2,bl+2,z-plate_top),(x,side*(face-38),(z+plate_top)/2))),PETG,True)
        add(f'UGV-MECH-004-{suffix}',bracket.intersect(box((bw+2,bl+2,clamp_top-z),(x,side*(face-38),(clamp_top+z)/2))),PETG,True)
        width,r_out,r_tyre=G['wheel_width_mm'],G['wheel_diameter_mm']/2,G['tyre_inner_diameter_mm']/2
        inner=side*G['track_mm']/2-width/2  # wheel start y (cylinders run +y)
        web=G['hub_web_mm']
        web_start=inner+width-web if side>0 else inner
        # M3: the hub boss reaches through the 18 mm wall hole to the motor face inside the body.
        boss_abs=face+3  # clear of the 2.5 mm bushing
        outer_abs=G['track_mm']/2+width/2
        boss=cylinder(G['hub_boss_radius_mm'],outer_abs-boss_abs,(x,boss_abs if side>0 else -outer_abs,z),(0,1,0))
        hub=(cylinder(r_tyre,width,(x,inner,z),(0,1,0)).cut(cylinder(r_tyre-4,width,(x,inner,z),(0,1,0)))
             .fuse(cylinder(r_tyre-4,web,(x,web_start,z),(0,1,0)))
             .fuse(boss))
        for k in range(6):  # lightening holes in the web
            a=math.radians(60*k)
            hub=hub.cut(cylinder(10,web+2,(x+32*math.cos(a),web_start-1,z+32*math.sin(a)),(0,1,0)))
        # M2: D bore (0.05 clearance) with an M3 set screw onto the flat, reached in the 6 mm body-wheel gap;
        # its nut slides in from the motor-side end of the boss.
        bore=cylinder(M['shaft_diameter_mm']/2+0.05,outer_abs-boss_abs+2,(x,(boss_abs-1) if side>0 else -outer_abs-1,z),(0,1,0)).cut(
            box((10,outer_abs-boss_abs+4,5),(x,side*(boss_abs+outer_abs)/2,z+flat+0.05+2.5)))
        ys=side*(face+G['hub_set_screw_mm'])
        nut_len=abs(ys)-boss_abs+FAST['m3_nut_af_mm']/2+1
        nut=box((FAST['m3_nut_af_mm'],nut_len,FAST['m3_nut_t_mm']),
                (x,side*(boss_abs-1+nut_len/2),z+4.2))
        hub=hub.cut(bore).cut(cylinder(FAST['m3_clear_mm']/2,8,(x,ys,z+1),(0,0,1))).cut(nut)
        # Anti-rotation ribs on the rim, mirrored as grooves in the TPU tyre.
        ribs=None
        for k in range(G['hub_ribs']):
            rib=box((3,width,1.5),(x,inner+width/2,z+r_tyre+0.75)).rotate(
                cq.Vector(x,0,z),cq.Vector(x,1,z),360*k/G['hub_ribs'])
            ribs=rib if ribs is None else ribs.fuse(rib)
        hub=hub.fuse(ribs).clean()
        add(f'UGV-MECH-060-{suffix}',hub,ORANGE,True)
        tyre=cylinder(r_out,width,(x,inner,z),(0,1,0)).cut(cylinder(r_tyre,width,(x,inner,z),(0,1,0))).cut(ribs)
        add(f'UGV-MECH-061-{suffix}',tyre,TPU,True)
        # M3 fender (track-style top): shelf over the wheel on a flange along the side wall; the parked arm rests on it.
        xa,xb=(FEN['split_x_mm']+0.25,FEN['x_mm'][1]) if x>0 else (FEN['x_mm'][0],FEN['split_x_mm']-0.25)
        fz0,fz1=FEN['z_mm']
        y0,y1=HW+0.25,outer_abs  # flush with the tyre outer face
        fender=box((xb-xa,y1-y0,fz1-fz0),((xa+xb)/2,side*(y0+y1)/2,(fz0+fz1)/2)).fuse(
            box((xb-xa,2.5,FEN['flange_top_z_mm']-fz1),((xa+xb)/2,side*(y0+1.25),(fz1+FEN['flange_top_z_mm'])/2)))
        gx=FEN['gusset_x_mm'][1 if x>0 else 0]
        fender=fender.fuse(box((4,30,20),(gx,side*(y0+15),fz0-10)))
        for sx_f in FEN['screw_x_mm']:
            if xa < sx_f < xb:
                fender=fender.cut(cylinder(FAST['m3_clear_mm']/2,6,(sx_f,side*(y0-1) if side>0 else -(y0+5),FEN['screw_z_mm']),(0,1,0)))
        add(f'UGV-MECH-015-{suffix}',fender.clean(),(0.62,0.40,0.10),True)

add('REF-BATTERY',box(G['battery_envelope_mm'],G['battery_center_mm']),(0.78,0.46,0.12),role='reserved_envelope')
add('REF-ELECTRONICS',box(G['electronics_envelope_mm'],G['electronics_center_mm']),(0.16,0.38,0.68),
    role='reserved_envelope')
# M2 Task 3: internal fixtures, all bolted to the base plate with M3 (nuts under the plate).
def ears(mounts, size, z0, t):
    solid=None
    for x,y in mounts:
        ear=box((size,size,t),(x,y,z0+t/2)).cut(cylinder(FAST['m3_clear_mm']/2,t+2,(x,y,z0-1)))
        solid=ear if solid is None else solid.fuse(ear)
    return solid
bx,by,bz=G['battery_center_mm']; bl,bw,bh=G['battery_envelope_mm']
cradle=box((bl+6,bw+6,12),(bx,by,plate_top+6)).cut(box((bl+0.5,bw+0.5,14),(bx,by,plate_top+6)))
for sx_ in IT['strap_slots_x_mm']:  # hook-and-loop strap over the pack
    cradle=cradle.cut(box((20,bw+10,3),(sx_,by,plate_top+4.5)))
cradle=cradle.fuse(ears(IT['battery_mounts_mm'],12,plate_top,3))
for x,y in IT['battery_mounts_mm']:
    cradle=cradle.cut(cylinder(FAST['m3_clear_mm']/2,20,(x,y,plate_top-1)))
add('UGV-MECH-070',cradle.clean(),PETG,True)
ex_,ey_,ez_=G['electronics_center_mm']; el,ew,eh=G['electronics_envelope_mm']
ez0=ez_-eh/2  # module/perfboard underside = standoff tops
tray=box((el,ew,2),(ex_,ey_,plate_top+1)).fuse(ears(IT['tray_mounts_mm'],12,plate_top,2))
ins_d,ins_depth=FAST['m3_insert_hole_mm']
for x,y in IT['tray_standoffs_mm']:
    tray=tray.fuse(cylinder(ins_d/2+1.6,ez0-plate_top-2,(x,y,plate_top+2))).cut(
        cylinder(ins_d/2,ins_depth+0.5,(x,y,ez0-ins_depth)))
for x,y in IT['tray_mounts_mm']:
    tray=tray.cut(cylinder(FAST['m3_clear_mm']/2,10,(x,y,plate_top-1)))
add('UGV-MECH-071',tray.clean(),PETG,True)
rw,rl,rh=IT['ballast_resistor_mm']
cols,rows=(121,137),IT['front_vents_z_mm']  # two columns x two layers, resistors along y
rack=box((30,rl+4,max(rows)+rh/2+3-plate_top),(129,0,(plate_top+max(rows)+rh/2+3)/2))
for k,(x,z) in enumerate(itertools.product(cols,rows),start=1):
    rack=rack.cut(box((rw+0.6,rl+10,rh+0.6),(x,0,z)))
    add(f'REF-BALLAST-{k}',box((rw,rl,rh),(x,0,z)),(0.85,0.85,0.80),role='reserved_envelope')
rack=rack.cut(box((4,rl+10,max(rows)-min(rows)-rh-1),(129,0,(min(rows)+max(rows))/2)))  # airflow gap
rack=rack.fuse(ears(IT['ballast_mounts_mm'],16,plate_top,3))  # 16 mm ears touch the rack body
for x,y in IT['ballast_mounts_mm']:
    rack=rack.cut(cylinder(FAST['m3_clear_mm']/2,10,(x,y,plate_top-1)))
add('UGV-MECH-072',rack.clean(),PETG,True)
# M3 cargo bay (DD74): open-top bin under the front-lid slot, two legs bolted to the plate, flange to the front wall.
CG=IT['cargo']
(bx0,bx1),by_,(bz0,bz1),t_=CG['bin_x_mm'],CG['bin_abs_y_mm'],CG['bin_z_mm'],CG['wall_mm']
bin_=box((bx1-bx0,2*by_,bz1-bz0),((bx0+bx1)/2,0,(bz0+bz1)/2)).cut(
    box((bx1-bx0-2*t_,2*by_-2*t_,bz1-bz0),((bx0+bx1)/2,0,(bz0+bz1)/2+t_)))
for x,y in CG['leg_mounts_mm']:
    bin_=bin_.fuse(box((8,8,bz0-plate_top),(x,y,(bz0+plate_top)/2)))
bin_=bin_.fuse(ears(CG['leg_mounts_mm'],12,plate_top,3))
bin_=bin_.fuse(box((G['body_length_mm']/2-wall-0.25-bx1,80,20),((bx1+G['body_length_mm']/2-wall-0.25)/2,0,bz1-10)))
for x,y in CG['leg_mounts_mm']:
    bin_=bin_.cut(cylinder(FAST['m3_clear_mm']/2,bz0-plate_top+2,(x,y,plate_top-1)))
for yb_ in CG['flange_screw_y_mm']:  # M3 heat-set inserts, screws through the front wall
    x_wall=G['body_length_mm']/2-wall
    bin_=bin_.cut(cylinder(ins_d/2,ins_depth+0.5,(x_wall-ins_depth,yb_,CG['flange_screw_z_mm']),(1,0,0)))
add('UGV-MECH-073',bin_.clean(),PETG,True)
# TPU cross-slit cover on the lid: an item dropped from the gripper pushes through, dust stays out.
(sw,sl),(scx,scy)=CG['slot_mm'],CG['slot_center_xy_mm']
cover=box((sw+8,sl+8,CG['cover_mm']),(scx,scy,top+CG['cover_mm']/2))
for size in ((sw-2,1,4),(1,sl-2,4)):
    cover=cover.cut(box(size,(scx,scy,top+1)))
add('UGV-MECH-018',cover,TPU,True)
ex,ey=G['estop_xy_mm']
estop=cylinder(G['estop_head_mm'][0]/2,G['estop_head_mm'][1],(ex,ey,top)).fuse(
    cylinder(G['estop_body_mm'][0]/2,G['estop_body_mm'][1]+G['lid_thickness_mm'],(ex,ey,lid_z-G['estop_body_mm'][1])))
add('REF-ESTOP',estop.clean(),(0.85,0.10,0.10),role='reserved_envelope')
for side in (-1,1):
    add(f'REF-TOF-{side:+d}',box(G['tof_envelope_mm'],(G['overall_length_mm']/2-2,side*G['tof_center_y_mm'],105)),
        (0.2,0.2,0.2),role='reserved_envelope')

mast=box((50,50,6),(30,0,top+3))
beam=box((50,120,8),(G['neck_axis_xy_mm'][0],0,lid_z-4))
for x,y in NECK_BOLTS:
    mast=mast.cut(cylinder(FAST['m3_clear_mm']/2,10,(x,y,top-1)))
    beam=beam.cut(cylinder(FAST['m3_clear_mm']/2,10,(x,y,lid_z-9))).cut(cylinder(3.2,3,(x,y,lid_z-8.5)))
hole=cylinder(IT['neck_cable_hole_mm']/2,20,(*HD['cable_hole_xy_mm'],lid_z-10))
mast,beam=mast.cut(hole),beam.cut(hole)  # DD82: head and pan-servo cables behind the pan servo
add('UGV-MECH-030',mast,PETG,True)
# M2: neck beam spreads the head load over the lid and bridges the lid seam at x = 50.
add('UGV-MECH-031',beam,PETG,True)
add('REF-LIGHT-BAR',box((4,124,10),(143.5,0,G['light_bar_center_z_mm'])),(0.52,0.72,0.92),role='reserved_envelope')

# Head (DD82, DD83) on the mast flange; the camera keeps its 122 mm above the body. Pan: MG90S on the neck axis, put
# in from the open bottom of the base and screwed up into the ledge above its ears; the neck turns in the 6804 at the
# top of the base and bolts to the pan horn. Tilt (DD83): the MG90S hides in a housing on the neck (it pans with it)
# and drives the left eye through a pushrod up the neck column; the eyes turn together on a hex axle through the
# blade between them. Cables leave the housing at the back and enter the body behind the pan servo.
nx,ny=G['neck_axis_xy_mm']
tilt_z=G['tilt_axis_z_mm']
m9l,m9w,m9h=M9['case']; m9s,m9se,hr=M9['spline_top'],M9['spline_from_end'],M9['horn_hole_r']
BZ,PR=HD['bearing_z_mm'],HD['pan_base_r_mm']
nb=BZ-1                                   # neck bottom = pan horn face
zb=nb-HORN['face_above_spline']-m9s       # pan servo bottom
ze=zb+M9['ear_underside']                 # ear underside; the ears' top faces bear on the ledge
et=ze+M9['ear_t']
xc9=nx+m9se-m9l/2                         # case centre, spline on the axis
pan_servo=(box((m9l,m9w,m9h),(xc9,ny,zb+m9h/2)).fuse(box((M9['ear_span'],m9w,M9['ear_t']),(xc9,ny,ze+M9['ear_t']/2)))
           .fuse(cylinder(3,m9s-m9h,(nx,ny,zb+m9h))))
pan_base=cylinder(PR,BZ+7-(top+6),(nx,ny,top+6))
pan_base=(pan_base.cut(box((M9['ear_span']+1,m9w+1,et-(top+5)),(xc9,ny,(top+5+et)/2)))  # open bottom, servo + ears
          .cut(box((m9l+1,m9w+1,zb+m9h+0.5-et+0.01),(xc9,ny,(et+zb+m9h+0.5)/2)))       # case top above the ledge
          .cut(cylinder(11.5,BZ-(zb+m9h+0.5)+0.01,(nx,ny,zb+m9h+0.5)))                 # spline boss and horn
          .cut(cylinder(16,8,(nx,ny,BZ))))                                              # 6804 seat on a lip
for s_ in (-1,1):
    pan_base=pan_base.cut(cylinder(FAST['m2_pilot_mm']/2,4.5,(xc9+s_*M9['ear_hole_pitch']/2,ny,et-0.5)))
for x,y in NECK_BOLTS:
    pan_base=pan_base.cut(cylinder(FAST['m3_insert_hole_mm'][0]/2,FAST['m3_insert_hole_mm'][1]+0.5,(x,y,top+5.5)))
hx,hy=HD['cable_hole_xy_mm']
pan_base=pan_base.cut(box((hx-(nx-PR)+2,8,8),((nx-PR-2+hx)/2,hy,226)))  # rear slot for the head cable loop
add('UGV-MECH-040',pan_base.clean(),DARK,True)
add('REF-SERVO-PAN',pan_servo.clean(),SERVO,role='reserved_envelope')
add('REF-BEARING-PAN',cylinder(16,7,(nx,ny,BZ)).cut(cylinder(10,9,(nx,ny,BZ-1))),STEEL,role='reserved_envelope')
def hex_y(af,y0,y1,x,z):  # hexagonal prism along y
    lo,hi=sorted((y0,y1))
    prism=cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(hi-lo).val()
    return prism.rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),-90).translate(cq.Vector(x,lo,z))
HZ0,HZ1=HD['housing_z_mm']; TS=HD['tilt_servo_z_mm']
CR,RY,CT=HD['tilt_crank_r_mm'],HD['rod_y_mm'],HD['column_top_z_mm']
gy=G['eye_center_y_mm']-G['eye_pod_mm'][1]/2   # eye inner face
ts_bot=RY-1-m9s                                 # tilt servo: spline +y, 1 mm short of the rod plane
ts_ear=ts_bot+M9['ear_underside']               # ear underside (faces -y) on the servo plate
tilt_servo=(box((m9l,m9h,m9w),(xc9,ts_bot+m9h/2,TS)).fuse(box((M9['ear_span'],M9['ear_t'],m9w),(xc9,ts_ear+M9['ear_t']/2,TS)))
            .fuse(cylinder(3,m9s-m9h,(nx,ts_bot+m9h,TS),(0,1,0))))
HX0,HX1,HY0,HY1=nx-27,nx+17,ts_bot-2.5,RY+3.5   # housing outside
LID_SCREWS=[(x_,y_) for x_ in (HX0+1.5,HX1-1.5) for y_ in (HY0+5,HY1-5)]
neck=(cylinder(10,BZ+7-nb,(nx,ny,nb)).fuse(cylinder(12,HZ0-(BZ+7),(nx,ny,BZ+7)))   # journal in the 6804, shoulder
      .fuse(box((HX1-HX0,HY1-HY0,HZ1-HZ0),((HX0+HX1)/2,(HY0+HY1)/2,(HZ0+HZ1)/2))))
neck=neck.cut(box((HX1-HX0-6,HY1-HY0-4,HZ1-HZ0-2+0.1),((HX0+HX1)/2,(HY0+HY1)/2,(HZ0+2+HZ1+0.1)/2)))  # open top
for gx in (HX0+2.5,HX1-2.5):  # 1 mm grooves for the servo plate's edges
    neck=neck.cut(box((1.2,4.2,HZ1-HZ0-2+0.1),(gx,ts_ear-2,(HZ0+2+HZ1+0.1)/2)))
neck=neck.cut(cylinder(4,HZ0+3-nb+1,(nx,ny,nb-1)))  # pan horn centre screw, reached from the open housing
neck=neck.cut(box((5,6,10),(HX0+1.5,1,HZ0+8)))       # cable window at the back
for s_ in (-1,1):
    neck=neck.cut(cylinder(FAST['m2_pilot_mm']/2,6.5,(nx+s_*hr,ny,nb-0.5)))  # pan horn, 2 x M2
for x_,y_ in LID_SCREWS:
    neck=neck.cut(cylinder(FAST['m2_pilot_mm']/2,6.5,(x_,y_,HZ1-6)))
add('UGV-MECH-041',neck.clean(),(0.40,0.41,0.43),True)
plate=box((HX1-HX0-4,4,HZ1-HZ0-2),((HX0+HX1)/2,ts_ear-2,(HZ0+2+HZ1)/2))  # slides into the grooves from the top
plate=plate.cut(box((m9l+1,6,m9w+1),(xc9,ts_ear-2,TS)))
for s_ in (-1,1):
    plate=plate.cut(cylinder(FAST['m2_pilot_mm']/2,5,(xc9+s_*M9['ear_hole_pitch']/2,ts_ear-4.5,TS),(0,1,0)))
add('UGV-MECH-046',plate.clean(),DARK,True)
add('REF-SERVO-TILT',tilt_servo.clean(),SERVO,role='reserved_envelope')
col=box((HX1-HX0,HY1-HY0,3),((HX0+HX1)/2,(HY0+HY1)/2,HZ1+1.5))   # lid of the housing
col=col.fuse(box((19,15,CT-(HZ1+3)),(nx+1.5,2.5,(HZ1+3+CT)/2)))   # column, below the eyes' lowest sweep
col=col.fuse(box((12,6,tilt_z-CT),(nx+2,0,(CT+tilt_z)/2))).fuse(cylinder(8,6,(nx,-3,tilt_z),(0,1,0)))  # blade, boss
col=col.cut(cylinder(HD['axle_d_mm']/2+0.2,8,(nx,-4,tilt_z),(0,1,0)))
lo=nx+CR*math.cos(math.radians(max(abs(a_) for a_ in HD['tilt_sweep_deg'])))-1.5
ST=HD['rod_shroud_top_z_mm']  # U-shroud between the eyes (open toward the left eye): hides the rod from front and back
for x0_,x1_ in ((lo-1,lo),(nx+CR+1.5,nx+CR+2.5)):
    col=col.fuse(box((x1_-x0_,3.9,ST-CT),((x0_+x1_)/2,RY-0.55,(CT+ST)/2)))
col=col.fuse(box((nx+CR+2.5-(lo-1),1,ST-CT),((lo-1+nx+CR+2.5)/2,RY-2,(CT+ST)/2)))
col=col.cut(box((nx+CR+1.5-lo,3,ST-HZ1+2),((lo+nx+CR+1.5)/2,RY,(HZ1+ST)/2)))  # pushrod channel, whole tilt travel
col=col.cut(box((4,5,CT-HZ1+2),(nx-5,0,(HZ1+CT)/2)))                          # eye cables
for x_,y_ in LID_SCREWS:
    col=col.cut(cylinder(FAST['m2_clear_mm']/2,5,(x_,y_,HZ1-1)))
add('UGV-MECH-042',col.clean(),DARK,True)
add('REF-TILT-ROD',cylinder(0.75,tilt_z-3-(TS+1),(nx+CR,RY,TS+1)),STEEL,role='reserved_envelope')  # Z-bends not drawn
ax=cylinder(HD['axle_d_mm']/2,2*gy,(nx,-gy,tilt_z),(0,1,0))
for s_ in (-1,1):
    ax=ax.fuse(hex_y(7.0,s_*gy,s_*(gy+2.5),nx,tilt_z))
ax=ax.cut(cylinder(2.25,2*gy+6,(nx,-gy-3,tilt_z),(0,1,0)))  # M4 clamps both eyes to it
add('UGV-MECH-045',ax.clean(),(0.72,0.71,0.66),True)
pod_x=nx+G['eye_pod_x_offset_mm']
PL,PW,PH=G['eye_pod_mm']
eb_t,eb_w,eb_l=G['eye_board_mm']
lens_d,lens_l=G['eye_lens_mm']
rear=pod_x+G['eye_board_rear_from_pod_x_mm']  # ESP32-CAM board rear face
front_in=pod_x+PL/2-2.5
def rounded(size,r,center):
    return cq.Workplane('XY').box(*size).edges('|X').fillet(r).translate(center).val()
for side in (-1,1):
    y=side*G['eye_center_y_mm']
    # M3 print interfaces (DD78): the rear wall is a press-fit cap, since the 27 x 40.5 board cannot pass a hole
    # in it; the board sits between four front stops and the cap's pressing frame; the lens sits in a collar.
    pod=rounded((PL,PW,PH),8,(pod_x,y,tilt_z)).cut(rounded((front_in-(pod_x-PL/2-1),PW-5,PH-5),5.5,
                                                          ((front_in+pod_x-PL/2-1)/2,y,tilt_z)))
    pod=pod.cut(cylinder(6,6,(front_in-1,y,tilt_z),(1,0,0)))
    pod=pod.fuse(cylinder(7.5,4,(front_in-4,y,tilt_z),(1,0,0)).cut(cylinder(lens_d/2+0.3,6,(front_in-5,y,tilt_z),(1,0,0))))
    for sy_ in (-1,1):
        for sz_ in (-1,1):
            pod=pod.fuse(box((3,PW/2-2.5-(eb_w/2-3),PH/2-2.5-(eb_l/2-4.5)),
                             (rear+eb_t+1.5,y+sy_*(eb_w/2-3+PW/2-2.5)/2,tilt_z+sz_*(eb_l/2-4.5+PH/2-2.5)/2)))
    pod=pod.cut(hex_y(7.2,side*(gy-0.5),side*(gy+3),nx,tilt_z))  # DD83: hex end of the axle through the inner wall
    pod=pod.cut(cylinder(2.5,4.5,(nx-6,side*(gy+1.5)-2.25,tilt_z-10),(0,1,0)))  # DD85: camera cable, near the axle
    if side>0:  # left eye: crank pin boss for the pushrod's Z-bend, radius CR ahead of the axle
        pod=pod.fuse(cylinder(2.5,gy-(RY-1),(nx+CR,RY-1,tilt_z),(0,1,0))).cut(cylinder(1.05,6,(nx+CR,RY-1.5,tilt_z),(0,1,0)))
    brow=cq.Workplane('XY').box(36,40,3).val().rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),-side*8)
    pod=pod.fuse(brow.translate(cq.Vector(pod_x,y,tilt_z+PH/2+0.5))).cut(  # the tilted brow must not dip into the cavity
        rounded((rear+eb_t-(pod_x-PL/2-1),PW-5,PH-5),5.5,((rear+eb_t+pod_x-PL/2-1)/2,y,tilt_z))).clean()
    add(f'UGV-MECH-043-{side:+d}',pod,(0.72,0.71,0.66),True)
    cap=rounded((2,PW,PH),8,(pod_x-PL/2-1,y,tilt_z)).fuse(
        rounded((rear-(pod_x-PL/2),PW-5.3,PH-5.3),5.35,((rear+pod_x-PL/2)/2,y,tilt_z))).cut(
        box((rear-(pod_x-PL/2)-2.5+0.01,eb_w-2,eb_l-6),((rear+pod_x-PL/2+2.5)/2+0.005,y,tilt_z)))
    add(f'UGV-MECH-044-{side:+d}',cap.clean(),(0.72,0.71,0.66),True)
    # ESP32-CAM on its PCB at the rear, OV2640 on the FPC forward, lens barrel in the collar (vendor sizes; verify).
    cam=(box((eb_t,eb_w,eb_l),(rear+eb_t/2,y,tilt_z))
         .fuse(box((3.4,18,25.5),(rear+eb_t+1.7,y,tilt_z)))            # ESP32-S module on the front
         .fuse(box((2.5,24,34),(rear-1.25,y,tilt_z)))                  # microSD, flash LED, regulator behind
         .fuse(box((front_in-lens_l-8.5-(rear+eb_t+3.4),8,1),((front_in-lens_l-8.5+rear+eb_t+3.4)/2,y,tilt_z)))  # FPC
         .fuse(box((8.5,8.5,8.5),(front_in-lens_l-4.25,y,tilt_z)))     # camera module
         .fuse(cylinder(lens_d/2,lens_l,(front_in-lens_l,y,tilt_z),(1,0,0))))
    add(f'REF-EYE-CAMERA-{side:+d}',cam.clean(),(0.08,0.20,0.45),role='reserved_envelope')

# M3 arms (DD73). Zero pose: arm straight forward (+x) in the plane |y| = YA. Joints: 0 shoulder (y, through the
# wall), 1 upper-arm twist (x), 2 elbow (y), 3 wrist pitch (y), 4 wrist roll (x). Right arm powered, left passive.
DS3218=(20,45,40)  # x, y (height incl. spline, shaft axis), z (length, spline 10 mm from the top end)
GR=A['gripper']; GP=GR['pivot_spacing_mm']  # M01: jaw pivots GP apart (= gear pitch diameter)
XG=xw+L3-16                                 # gripper MG90S spline axis (along y), x
DG0,DG1=-25,-18                             # gear plane (d, 7 mm face), inboard of the MG90S horn face
ARM_NAMES=('UGV-MECH-050','UGV-MECH-051','UGV-MECH-052','UGV-MECH-053','UGV-MECH-054')
COVER_SCREWS=[(xs+TB+dx,dz) for dx,dz in ((-45,-13.85),(-25,-13.85),(-10,-9),(-10,25))]  # twist cover, M2 into link A


def arm_zero(side):
    """[(name, shape, link, color)] in the zero pose; link = last joint that moves the solid.
    DD81: offsets d from the arm plane (|y| = YA, d > 0 outboard) and heights z from the shoulder axis."""
    s=side
    def yb(x0,x1,a0,a1,z0,z1):  # box between |y| a0..a1 on this side
        lo,hi=sorted((s*a0,s*a1))
        return box((x1-x0,hi-lo,z1-z0),((x0+x1)/2,(lo+hi)/2,(z0+z1)/2))
    def yc(r,a0,a1,x,z):  # cylinder along y between |y| a0..a1
        return cylinder(r,a1-a0,(x,min(s*a0,s*a1),z),(0,1,0))
    def db(x0,x1,d0,d1,z0,z1):
        return yb(x0,x1,YA+d0,YA+d1,zs+z0,zs+z1)
    def dc(r,d0,d1,x,z=0):
        return yc(r,YA+d0,YA+d1,x,zs+z)
    def xc(r,x0,x1,d=0,z=0):  # cylinder along x, on the arm axis by default
        return cylinder(r,x1-x0,(x0,s*(YA+d),zs+z),(1,0,0))
    def hex_d(af,d0,d1,x,z=0):  # hexagonal prism (nut pocket) along y between offsets d0..d1
        lo,hi=sorted((s*(YA+d0),s*(YA+d1)))
        prism=cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(hi-lo).val()
        return prism.rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),-90).translate(cq.Vector(x,lo,zs+z))
    # Pitch joints (elbow, wrist): MG996R with its ears, spline INBOARD on the joint axis. The ears sit on the seat
    # face (d = DE) on four M3 heat-set inserts; a 25T aluminium disc horn on the spline carries the fork's inboard
    # cheek (4 x M3 on the PCD); the outboard cheek turns on a 624ZZ held by an M4 into a nut captive in the seat
    # wall. The fork's crossbar stays FC from the axis, outside the ears' sweep (DD78's open issue).
    L_,W_,Hc=MG['case']; Hs=MG['spline_top']; SE=MG['spline_from_end']
    DB=Hs/2; DE=DB-MG['ear_underside']; DH=-DB-HORN['face_above_spline']
    DW=DB+0.5+A['pitch_wall_mm']; DI=DW+0.5; FC=A['fork_clear_mm']; _,bo,bw=A['idler_624_mm']
    CI,CO=(DH-5,DH),(DI,DI+3.5)  # fork cheeks: inboard (horn, M3 heads counterbored), outboard (624)
    def pitch_servo(xj):
        xc_=xj+SE-L_/2
        return (db(xj+SE-L_,xj+SE,DB-Hc,DB,-W_/2,W_/2)
                .fuse(db(xc_-MG['ear_span']/2,xc_+MG['ear_span']/2,DE-MG['ear_t'],DE,-W_/2,W_/2))
                .fuse(dc(6,-DB,DB-Hc,xj)))
    def seat(xj,x_rear):
        xc_=xj+SE-L_/2
        body=db(x_rear,xj+FC-1,DE,DW,-12.5,12.5)
        body=body.cut(db(xj,xj+FC,DE-1,DW+1,-20,20).cut(dc(FC-1.5,DE-2,DW+2,xj)))  # ahead of the axis: r <= FC-1.5
        body=body.fuse(dc(3.3,DW,DI,xj))  # spacer onto the 624 inner ring
        body=body.cut(db(xj+SE-L_-0.5,xj+SE+0.5,DE-1,DB+0.5,-W_/2-0.5,W_/2+0.5))  # case pocket, open to the ears
        for ex in (-1,1):
            for ez in (-1,1):
                body=body.cut(dc(ins_d/2,DE-0.5,DE+ins_depth+0.5,xc_+ex*MG['ear_holes'][0]/2,ez*MG['ear_holes'][1]/2))
        body=body.cut(db(xj+SE-L_+0.5,xj+SE-L_+5.5,DB-3,DW+0.1,-2.5,2.5))  # DD85: cable exit at the case's far end
        return body.cut(dc(FAST['m4_clear_mm']/2,DB,DI+1,xj)).cut(hex_d(7.0,DB+0.4,DB+3.8,xj))  # M4 + captive nut
    def fork(xj):
        f=None
        for d0,d1 in (CI,CO):
            cheek=dc(13,d0,d1,xj).intersect(db(xj-14,xj+1,d0,d1,-12.5,12.5)).fuse(db(xj,xj+FC,d0,d1,-12.5,12.5))
            # r13 flattened to the 25 mm link height: prints on its side, >= 4.5 mm off the wall when twisted
            f=cheek if f is None else f.fuse(cheek)
        f=f.fuse(dc(bo/2+3,DI,DI+bw+0.5,xj))  # 624 boss
        f=f.cut(dc(bo/2,DI-0.1,DI+bw,xj)).cut(dc(bo/2-1,DI+bw-0.1,DI+bw+1,xj))  # seat, lip on the outer ring
        f=f.cut(dc(3,CI[0]-1,CI[1]+1,xj))  # horn centre screw
        for k in range(4):
            ang=math.radians(45+90*k)
            x_,z_=xj+A['horn_pcd_mm']/2*math.cos(ang),A['horn_pcd_mm']/2*math.sin(ang)
            f=f.cut(dc(FAST['m3_clear_mm']/2,CI[0]-1,CI[1]+1,x_,z_)).cut(dc(3,CI[0]-1,CI[0]+3,x_,z_))
        return f
    out=[]
    # A: journal through the wall bearing, hub flange, shell around the twist MG996R (output +x on the arm axis).
    # There is no room for its ears (park: fender; reach: front tyre; |y| <= 154), so they are trimmed; the case
    # sits in a pocket under a screwed cover (058), axially held by the pocket floor and horn -> adapter -> 6704.
    T=xs+TB
    twist=db(T-6.5-Hs,T-6.5-(Hs-Hc),-W_/2,W_/2,-SE,L_-SE).fuse(xc(6,T-6.5-(Hs-Hc),T-6.5))
    a=(yc(BRG[0],TIP+2.5,HW+0.75,xs,zs).fuse(yc(22,HW+0.75,YA+12.5,xs,zs))  # rear end rounded on the shoulder axis
       .fuse(yb(xs,T,HW+5.5,YA+12.5,zs-17,zs+34))
       .fuse(xc(BTW[1]+2.5,T-7,T+BTW[2]+1)))
    a=(a.cut(xc(BTW[1],T,T+BTW[2]+2)).cut(xc(13,T-7.5,T+0.01))  # 6704 seat; horn + adapter cavity (lip at T)
        .cut(yc(4,TIP+6.5,HW+7,xs,zs))  # cable bore
        .cut(cylinder(3,30,(xs,s*(TIP+8.5),zs-15)))  # radial cable exit between the horn flange and the wall boss
        .cut(db(T-6.5-Hs-0.5,T-6.5-(Hs-Hc)+0.5,-W_/2-0.5,13,-SE-0.5,L_-SE+0.5))  # pocket, open outboard
        .cut(xc(7,T-7-(Hs-Hc),T-7.4))  # spline boss and horn hub
        .cut(dc(4,HW+6-YA,13,xs))       # DD85: the shoulder cable bore opens on A's outboard face
        .cut(db(xs+2.5,xs+6.8,10.5,13,-2,4)))  # groove for the twist cable, under the cover, into that bore
    for x_,z_ in COVER_SCREWS:
        a=a.cut(dc(FAST['m2_pilot_mm']/2,6.5,12.6,x_,z_))
    if side<0:  # 25T disc-horn flange on the powered shoulder: 4 x M3 tapped on the PCD (verify with the horn)
        a=a.fuse(yc(13,TIP+2.5,TIP+5,xs,zs))
        for k in range(4):
            ang=math.radians(45+90*k)
            a=a.cut(yc(1.25,TIP+2.5,TIP+8.5,xs+A['horn_pcd_mm']/2*math.cos(ang),zs+A['horn_pcd_mm']/2*math.sin(ang)))
    out.append((ARM_NAMES[0],a.clean(),0,DARK))
    # B: hub on the 6704 inner ring, seat of the elbow servo; two M3 from its pocket into the twist adapter.
    elbow=pitch_servo(xe)
    b=xc(11,T+BTW[2]+0.5,T+6).fuse(seat(xe,T+6))
    for z_ in (-5,5):
        b=b.cut(xc(FAST['m3_clear_mm']/2,T+4,xe+SE-L_,5,z_)).cut(xc(3,xe+SE-L_-4,xe+SE-L_,5,z_))
    out.append((ARM_NAMES[1],b.clean(),1,(0.55,0.56,0.58)))
    # C: forearm: elbow fork, full-width beam up to the wrist servo's rear ear (clear of the wrist fork's sweep),
    # then the seat of the wrist servo.
    wrist=pitch_servo(xw)
    c=fork(xe).fuse(db(xe+FC,xw-39,CI[0],CO[1],-12.5,12.5)).fuse(seat(xw,xw-39))
    out.append((ARM_NAMES[2],c.clean(),2,(0.55,0.56,0.58)))
    # D: wrist fork and the wrist-roll MG90S (output +x on the arm axis, ears on D's face, 2 x M2 pilots).
    m9l,m9w,m9h=M9['case']; m9s=M9['spline_top']
    xr=xw+FC+2.5; m9e=xr+M9['ear_underside']
    dlo,dhi=-M9['spline_from_end'],m9l-M9['spline_from_end']
    dmid=(dlo+dhi)/2
    roll=(db(xr,xr+m9h,dlo,dhi,-m9w/2,m9w/2)
          .fuse(db(m9e,m9e+M9['ear_t'],dmid-M9['ear_span']/2,dmid+M9['ear_span']/2,-m9w/2,m9w/2))
          .fuse(xc(3,xr+m9h,xr+m9s)))
    dd=fork(xw).fuse(db(xw+FC,xw+FC+5,CI[0],CO[1],-12.5,12.5)).fuse(db(xw+FC+5,m9e,dmid-19,dmid+19,-12.5,12.5))
    dd=dd.cut(db(xr-0.5,m9e+1,dlo-0.5,dhi+0.5,-m9w/2-0.5,m9w/2+0.5))
    dd=dd.cut(db(xr,xr+5,dhi-1.5,dmid+19.1,-2.5,2.5))  # DD85: roll servo cable to D's outboard face
    for s_ in (-1,1):
        dd=dd.cut(xc(FAST['m2_pilot_mm']/2,m9e-6.5,m9e+1,dmid+s_*M9['ear_hole_pitch']/2))
    out.append((ARM_NAMES[3],dd.clean(),3,DARK))
    # E: palm on the roll horn (2 x M2), gripper MG90S (spline inboard, ears on E's face). M01 (full review, DD93):
    # twin geared claw. Jaw A (055) is on the MG90S arm horn, jaw B (062) turns on an M3 pin screw in a post of the palm,
    # GP higher; two 16T gears (module 0.625, GP = pitch diameter) make the jaws turn together; they meet at z = GP/2,
    # TPU pads (063/064) on both. Parked, +z points outboard: the whole claw stays inside |y| <= 154 (gear B top).
    xg=XG; GB=15; GE=GB-M9['ear_underside']
    gc=xg+M9['spline_from_end']-m9l/2
    g0,g1=xg+M9['spline_from_end']-m9l,xg+M9['spline_from_end']
    grip_servo=(db(g0,g1,GB-m9h,GB,-m9w/2,m9w/2)
                .fuse(db(gc-M9['ear_span']/2,gc+M9['ear_span']/2,GE-M9['ear_t'],GE,-m9w/2,m9w/2))
                .fuse(dc(3,GB-m9s,GB-m9h,xg)))
    e0=xr+m9s+HORN['face_above_spline']
    e=db(e0,xw+L3-3.5,GE,GB+2,-9,12)  # -z face at -9 (was -12): the parked palm keeps >= 3 mm off the wall at +-1 deg
    e=e.fuse(db(xg-3.5,xg+3.5,GE,GB+2,9,GP+3.5)).fuse(dc(3.5,DG1+0.25,GE,xg,GP))  # jaw B post on a web
    e=e.cut(dc(1.25,DG1+0.15,GE-1,xg,GP))  # 2.5 mm pilot: jaw B's M3 pin screw taps into the post
    e=e.cut(db(g0-0.5,g1+0.5,GE-1,GB+0.5,-m9w/2-0.5,m9w/2+0.5))
    e=e.cut(db(g0,g0+5,GB-3,GB+2.1,-2.5,2.5))  # DD85: gripper servo cable to E's outboard face
    for s_ in (-1,1):
        e=e.cut(dc(FAST['m2_pilot_mm']/2,GE-0.5,GE+6.5,gc+s_*M9['ear_hole_pitch']/2))
    for z_ in (-7,7):
        e=e.cut(xc(FAST['m2_pilot_mm']/2,e0-0.5,e0+6,0,z_))  # roll horn screws
    e=e.cut(xc(2.5,e0-0.5,g0))  # roll horn centre screw
    out.append((ARM_NAMES[4],e.clean(),4,(0.72,0.71,0.66)))
    def gear_at(z,phase=0.0):  # 16T gear in the gear plane DG0..DG1, axis along y through (xg, z)
        lo,hi=sorted((s*(YA+DG0),s*(YA+DG1)))
        g_=spur_gear(GR['gear_teeth'],GR['gear_module'],hi-lo).rotate(cq.Vector(0,0,0),cq.Vector(0,1,0),phase)
        return g_.translate(cq.Vector(xg,lo,zs+z))
    ja=(gear_at(0).fuse(db(xg,xg+14,DG0,DG1,-3,GP/2-1.5)).fuse(db(xg+13,xg+28,DG0,-8,GP/2-7,GP/2-1.5))
        .cut(dc(1.25,DG0-1,DG1+1,xg)))  # the horn's centre screw, reached through the gear
    for dx in (7,11):  # two M2 into the MG90S single-arm horn laid along the jaw, arm cut to 12 mm (clear of the finger)
        ja=ja.cut(dc(FAST['m2_clear_mm']/2,DG0-1,DG1+1,xg+dx))
    jb=(gear_at(GP,180/GR["gear_teeth"]).fuse(db(xg,xg+14,DG0,DG1,GP/2+1.5,GP+2.5)).fuse(db(xg+13,xg+28,DG0,-8,GP/2+1.5,GP/2+7))
        .cut(dc(2.6,DG0-1,DG1+1,xg,GP)))  # R05: turns on a 5 mm spacer, not on the screw
    # R05 (DD94): the M3 pin screw clamps a nylon spacer (5/3.2 mm, 7.5 long) to the post face; jaw B (7 mm) turns on the
    # spacer with 0.5 mm axial play (0.25 each side); the screw's head, spring washer and washer bear on the spacer only.
    spacer=dc(2.5,DG0-0.25,DG1+0.25,xg,GP).cut(dc(1.6,DG0-1,DG1+1,xg,GP))
    out+=[('UGV-MECH-055',ja.clean(),4,DARK),('UGV-MECH-062',jb.clean(),4,DARK),
          (f"REF-SPACER-JAWB-{'R' if s<0 else 'L'}",spacer,4,STEEL)]
    if side<0:  # powered right arm: servo envelopes, the twist bearing, cover and adapter
        cover=db(xs+5,T-7.5,12.5,14.5,-16,33)  # starts beside the shoulder cable entry
        for x_,z_ in COVER_SCREWS:
            cover=cover.cut(dc(FAST['m2_clear_mm']/2,12,15,x_,z_))
        adp=xc(12,T-4.5,T-1.5).fuse(xc(11.2,T-1.5,T+0.5)).fuse(xc(BTW[0],T+0.5,T+BTW[2]+0.5))
        adp=adp.cut(xc(3,T-5,T+5))  # horn centre screw
        for k in range(4):  # 25T horn screws from the front, heads counterbored under the 6704 inner ring
            ang=math.radians(90*k)
            d_,z_=A['horn_pcd_mm']/2*math.cos(ang),A['horn_pcd_mm']/2*math.sin(ang)
            adp=adp.cut(xc(FAST['m3_clear_mm']/2,T-5,T+5,d_,z_)).cut(xc(3,T-2.5,T+0.6,d_,z_))
        for z_ in (-5,5):  # link B's two M3 (self-tapping into the adapter)
            adp=adp.cut(xc(1.25,T-1.5,T+5,5,z_))
        out+=[('UGV-MECH-058',cover.clean(),0,DARK),('UGV-MECH-059',adp.clean(),1,DARK),
              ('REF-SERVO-TWIST-R',twist,0,SERVO),('REF-SERVO-ELBOW-R',elbow,1,SERVO),
              ('REF-SERVO-WRIST-R',wrist,2,SERVO),('REF-SERVO-ROLL-R',roll,3,SERVO),
              ('REF-SERVO-GRIPPER-R',grip_servo,4,SERVO),
              ('UGV-MECH-063',db(xg+14,xg+28,DG0+1,-9,GP/2-1.5,GP/2),4,TPU),   # jaw pads, TPU 95A, glued
              ('UGV-MECH-064',db(xg+14,xg+28,DG0+1,-9,GP/2,GP/2+1.5),4,TPU),
              ('REF-BEARING-TWIST-R',xc(BTW[1],T+0.5,T+BTW[2]+0.5).cut(xc(BTW[0],T,T+9)),0,STEEL)]
    else:  # R04 (DD94): the passive left arm is assembled through the right arm's own interfaces, with printed stand-ins
        # for its servos, horns and bearings: every joint is bolted and fixed at the stow angles; only the shoulder turns.
        cover=db(xs+5,T-7.5,12.5,14.5,-16,33)
        for x_,z_ in COVER_SCREWS:
            cover=cover.cut(dc(FAST['m2_clear_mm']/2,12,15,x_,z_))
        adp=xc(12,T-4.5,T-1.5).fuse(xc(11.2,T-1.5,T+0.5)).fuse(xc(BTW[0],T+0.5,T+BTW[2]+0.5))
        adp=adp.cut(xc(3,T-5,T+5))
        pcd=A['horn_pcd_mm']/2
        # twist MG996R + its 25T horn, one printed block. DD95 (R04 recheck): it fills the pocket to 0.2 mm on every side,
        # the cover's too (the servo's envelope left 0.5 mm and 2.5 mm), so it turns < 1 deg before it bears (LEFT_TWIST).
        dtw=(db(T-6.5-Hs,T-6.5-(Hs-Hc),-W_/2-0.3,12.3,-SE-0.3,L_-SE+0.3).fuse(xc(6,T-6.5-(Hs-Hc),T-6.5))
             .fuse(xc(12.5,T-6.5,T-4.5)))
        for k in range(4):  # the adapter's four M3 from the front (as on the right), self-tapping here
            ang=math.radians(90*k)
            d_,z_=pcd*math.cos(ang),pcd*math.sin(ang)
            adp=adp.cut(xc(FAST['m3_clear_mm']/2,T-5,T+5,d_,z_)).cut(xc(3,T-2.5,T+0.6,d_,z_))
            dtw=dtw.cut(xc(1.25,T-6.6,T-4.4,d_,z_))
        for z_ in (-5,5):  # link B's two M3 (self-tapping into the adapter)
            adp=adp.cut(xc(1.25,T-1.5,T+5,5,z_))
        def dpitch(xj):  # elbow/wrist MG996R block: ears on the seat's four inserts, horn disc under the fork's cheek
            d=elbow.translate(cq.Vector(xj-xe,0,0)).fuse(dc(12.5,DH,-DB,xj))
            for k in range(4):
                ang=math.radians(45+90*k)
                d=d.cut(dc(1.25,DH-0.1,-DB+0.1,xj+pcd*math.cos(ang),pcd*math.sin(ang)))
            return d
        def bush(xj):  # 624 stand-in: the M4 clamps the outboard cheek through it
            return dc(bo/2,DI,DI+bw,xj).cut(dc(FAST['m4_clear_mm']/2,DI-1,DI+bw+1,xj))
        drl=roll.fuse(xc(10,xr+m9s,e0)).cut(xc(1.25,e0-6,e0+0.1))  # roll MG90S + horn disc; E's centre M3 taps in
        for z_ in (-7,7):  # two pins into E's M2 pilots stop the disc turning
            drl=drl.fuse(xc(0.7,e0-0.1,e0+3,0,z_))
        dgr=grip_servo.fuse(db(xg-4,xg+12.5,DG1,GB-m9s,-3,3))  # gripper MG90S + arm horn (cut at 12 mm, as on the right)
        for dx in (7,11):
            dgr=dgr.cut(dc(0.8,DG1-0.1,GB-m9s+0.1,xg+dx))    # jaw A's two M2, self-tapping
        out+=[('UGV-MECH-058',cover.clean(),0,DARK),('UGV-MECH-059',adp.clean(),1,DARK),
              ('UGV-MECH-066',dtw.clean(),0,DARK),('UGV-MECH-067',dpitch(xe).clean(),1,DARK),
              ('UGV-MECH-068',dpitch(xw).clean(),2,DARK),('UGV-MECH-069',drl.clean(),3,DARK),
              ('UGV-MECH-074',dgr.clean(),4,DARK),
              ('UGV-MECH-075',xc(BTW[1],T+0.5,T+BTW[2]+0.5).cut(xc(BTW[0],T,T+9)),0,DARK),
              ('UGV-MECH-076',bush(xe),2,DARK),('UGV-MECH-077',bush(xw),3,DARK)]
    return out


def joint_axes(side):
    """(origin, direction, sign) per joint in the zero pose; positive angles: shoulder up, twist bends the elbow
    toward the body, elbow and wrist down, roll mirror-symmetric."""
    return [((xs,0,zs),(0,1,0),-1),((xs+TB,side*YA,zs),(1,0,0),-side),((xe,side*YA,zs),(0,1,0),1),
            ((xw,side*YA,zs),(0,1,0),1),((xw+30,side*YA,zs),(1,0,0),-side)]


def posed(shape, link, q, side):
    for j in range(link,-1,-1):
        o,d,sign=joint_axes(side)[j]
        if q[j]:
            shape=shape.rotate(cq.Vector(*o),cq.Vector(o[0]+d[0],o[1]+d[1],o[2]+d[2]),sign*q[j])
    return shape


POSES=A['poses_deg']
RIGHT,LEFT=arm_zero(-1),arm_zero(1)
for side in (-1,1):
    for name,shape,link,color in (RIGHT if side<0 else LEFT):
        full=name if name.startswith('REF') else f'{name}-{side:+d}'
        role='reserved_envelope' if name.startswith('REF') else 'interface_concept'
        add(full,posed(shape,link,POSES['stow'],side),color,not name.startswith('REF'),role)
    # 6804-2RS in the wall boss.
    add(f'REF-BEARING-SHOULDER-{side:+d}',cylinder(BRG[1],BRG[2],(xs,side*(HW-7.5) if side>0 else -(HW-0.5),zs),(0,1,0)).cut(
        cylinder(BRG[0],BRG[2]+2,(xs,side*(HW-8.5) if side>0 else -(HW+0.5),zs),(0,1,0))),STEEL,role='reserved_envelope')
# Right shoulder DS3218MG (270 deg) inside the body; spline + horn on the shoulder axis, ears on a frame bolted to the wall.
sy0=TIP-DS3218[1]
j1=(box((DS3218[0],DS3218[1]-4.5,DS3218[2]),(xs,-(sy0+(DS3218[1]-4.5)/2),zs-10))
    .fuse(box((DS3218[0],2.5,54.5),(xs,-(sy0+27.25),zs-10)))
    .fuse(cylinder(12,6.5,(xs,-(TIP+2),zs),(0,1,0))))  # spline + disc horn up to the journal flange
add('REF-SERVO-SHOULDER-R',j1.clean(),SERVO,role='reserved_envelope')
fy0=sy0+28.5  # frame plate against the ears
fz0,fz1=J1_FRAME_Z[1]-4,J1_FRAME_Z[0]+4
frame=(box((28,4,fz1-fz0),(xs,-(fy0+2),(fz0+fz1)/2)).cut(box((21,6,41),(xs,-(fy0+2),zs-10))))
for zf in J1_FRAME_Z:
    frame=frame.fuse(box((28,HW-wall-fy0-4,8),(xs,-(fy0+4+HW-wall)/2,zf)))
    for dx in (-A['j1_frame_screw_dx_mm'],A['j1_frame_screw_dx_mm']):  # M3 heat-set inserts, screws through the wall
        frame=frame.cut(cylinder(ins_d/2,ins_depth+0.5,(xs+dx,-(HW-wall)-0.5,zf),(0,1,0)))
for dx in (-5,5):  # DS3218 ears: 49.5 x 10 mm hole pattern (verify), M3 through ears and plate, nuts behind
    for dz in (-24.75,24.75):
        frame=frame.cut(cylinder(FAST['m3_clear_mm']/2,10,(xs+dx,-(fy0+6),zs-10+dz),(0,1,0)))
add('UGV-MECH-056--1',frame.clean(),PETG,True)
# M03 (full review, DD93): the passive left shoulder holds its pose by friction. A split collar clamps the journal (M3
# screw + nut across the slit) and turns with it; a TPU washer between it and the wall boss's inner face (fixed) is the
# friction pair. At assembly the collar is pushed outboard to preload the washer, then clamped.
cy0,cy1=HW-19,HW-12.5
collar=cylinder(18,cy1-cy0,(xs,cy0,zs),(0,1,0)).cut(cylinder(BRG[0],cy1-cy0+2,(xs,cy0-1,zs),(0,1,0)))
collar=collar.fuse(box((11,cy1-cy0,9),(xs,(cy0+cy1)/2,zs-21.5)))      # clamp lugs below the slit
collar=collar.cut(box((1.5,cy1-cy0+2,19),(xs,(cy0+cy1)/2,zs-17.5)))   # slit through the ring wall and the lugs
collar=collar.cut(cylinder(FAST['m3_clear_mm']/2,14,(xs-7,(cy0+cy1)/2,zs-22),(1,0,0)))
nut=cq.Workplane('YZ').polygon(6,FAST['m3_nut_af_mm']/math.cos(math.pi/6)).extrude(FAST['m3_nut_t_mm']+0.3).val()
collar=collar.cut(nut.translate(cq.Vector(xs+5.5-FAST['m3_nut_t_mm']-0.3,(cy0+cy1)/2,zs-22)))
add('UGV-MECH-057-+1',collar.clean(),PETG,True)
add('UGV-MECH-065-+1',cylinder(19,1.5,(xs,cy1,zs),(0,1,0)).cut(cylinder(BRG[0]+0.5,3,(xs,cy1-0.5,zs),(0,1,0))),TPU,True)

# Arm sweeps: every pose and the joint-space straight line of every pose-graph edge (<= 1 deg per step).
RIGHT_NAMES={n if n.startswith('REF') else f'{n}--1' for n,_,_,_ in RIGHT}
OTHERS=[p_ for p_ in PARTS if p_['name'] not in RIGHT_NAMES]
for p_ in PARTS:
    p_['bb']=p_['shape'].BoundingBox()


def overlap(a,b,m=0.0):
    return (a.xmin-m<=b.xmax and b.xmin-m<=a.xmax and a.ymin-m<=b.ymax and b.ymin-m<=a.ymax
            and a.zmin-m<=b.zmax and b.zmin-m<=a.zmax)


# M01: jaw A (and its pad) turns about the MG90S spline axis, jaw B (and its pad) about its pin GP higher, oppositely.
JAW_PIVOT={'UGV-MECH-055':(0,1),'UGV-MECH-063':(0,1),'UGV-MECH-062':(GP,-1),'UGV-MECH-064':(GP,-1)}


def jaw(name, shape, alpha):
    """Zero-pose solid with the jaws opened by alpha deg (0 = closed)."""
    if not alpha or name not in JAW_PIVOT:
        return shape
    z_,sign=JAW_PIVOT[name]
    return shape.rotate(cq.Vector(XG,0,zs+z_),cq.Vector(XG,1,zs+z_),sign*alpha)  # +: ahead of the pivot goes down


def arm_hits(q, self_check=True, alpha=0):
    solids=[(n if n.startswith('REF') else f'{n}--1',posed(jaw(n,s,alpha),l,q,-1),l) for n,s,l,_ in RIGHT]
    boxes=[s.BoundingBox() for _,s,_ in solids]
    hits=[]
    for (n,s,_),sb in zip(solids,boxes):
        for p_ in OTHERS:
            if overlap(sb,p_['bb']) and (v:=s.intersect(p_['shape']).Volume())>0.01:
                hits.append({'arm':n,'part':p_['name'],'volume_mm3':round(v,3)})
    if self_check:
        for (a_,b_) in itertools.combinations(range(len(solids)),2):
            (n1,s1,l1),(n2,s2,l2)=solids[a_],solids[b_]
            if l1!=l2 and overlap(boxes[a_],boxes[b_]) and (v:=s1.intersect(s2).Volume())>0.01:
                hits.append({'arm':n1,'part':n2,'volume_mm3':round(v,3)})
    return hits


# R06 (DD94): the grasp datum is where the closed pads meet: the middle of their shared face, from the pad geometry.
GRASP_LOCAL=(XG+21,(DG0+1-9)/2,GP/2)  # x, d (offset from the arm plane, + outboard), z, zero pose


def grip_point(q, side=-1):
    x_,d_,z_=GRASP_LOCAL
    v=posed(cq.Vertex.makeVertex(x_,side*(YA+d_),zs+z_),4,q,side)
    return [round(c,1) for c in v.toTuple()]


ARM_POSES={name:{'q':q,'grip_mm':grip_point(q),'intersections':arm_hits(q)} for name,q in POSES.items()}
ARM_EDGES=[]
for a_,b_ in A['pose_edges']:
    qa,qb=POSES[a_],POSES[b_]
    n=max(1,math.ceil(max(abs(u-v) for u,v in zip(qa,qb))/1))
    hits=[]
    for k in range(n+1):
        q=[u+(v-u)*k/n for u,v in zip(qa,qb)]
        if h:=arm_hits(q):
            hits.append({'q':[round(t,2) for t in q],'hits':h[:4]})
    ARM_EDGES.append({'pose':[a_,b_],'samples':n+1,'max_step_deg':round(max(abs(u-v) for u,v in zip(qa,qb))/n,3),'hits':hits})
# M01: the claw opens only where the CAD swept it (config gripper.open_poses): every jaw angle at each of those poses,
# every edge between two of them with the jaws open, and the jaws against their own palm, servos and each other.
OPEN_DEG=GR['open_deg']
OPEN_POSES=GR['open_poses']
JAW_NAMES=[n for n,_,_,_ in RIGHT if n in JAW_PIVOT]
LINK4=[(n,s) for n,s,l,_ in RIGHT if l==4 and n not in JAW_PIVOT]
jaw_self=[]
for ang in range(0,OPEN_DEG+1,5):
    js=[(n,jaw(n,s,ang)) for n,s,l,_ in RIGHT if n in JAW_PIVOT]
    pairs=[(a_,b_) for a_ in js for b_ in LINK4]+[(a_,b_) for a_,b_ in itertools.combinations(js,2)
                                                 if JAW_PIVOT[a_[0]][0]!=JAW_PIVOT[b_[0]][0]]  # A side vs B side
    for (n1,s1),(n2,s2) in pairs:
        if (v:=s1.intersect(s2).Volume())>0.01:
            jaw_self.append({'deg':ang,'jaw':n1,'part':n2,'volume_mm3':round(v,3)})
GRIPPER={'open_deg':OPEN_DEG,'jaw_self_hits':jaw_self,'poses':{},'edges':[]}
for name in OPEN_POSES:
    GRIPPER['poses'][name]=[{'deg':ang,'hits':h[:4]} for ang in range(5,OPEN_DEG+1,5) if (h:=arm_hits(POSES[name],alpha=ang))]
for a_,b_ in A['pose_edges']:
    if a_ in OPEN_POSES and b_ in OPEN_POSES:
        qa,qb=POSES[a_],POSES[b_]
        n=max(1,math.ceil(max(abs(u-v) for u,v in zip(qa,qb))/1))
        hits=[{'q':[round(u+(v-u)*k/n,2) for u,v in zip(qa,qb)],'hits':h[:4]} for k in range(n+1)
              if (h:=arm_hits([u+(v-u)*k/n for u,v in zip(qa,qb)],alpha=OPEN_DEG))]
        GRIPPER['edges'].append({'pose':[a_,b_],'samples':n+1,'hits':hits})
# Opening at the contact point: pad faces at the jaw tips and at the pad centres, jaws fully open.
def pad_gap(x_,alpha):
    a,b=math.radians(alpha),x_-XG
    za=-b*math.sin(a)+GP/2*math.cos(a)                    # pad A face point, turned down about (XG, 0)
    zb=GP+b*math.sin(a)-GP/2*math.cos(a)                  # pad B face point, turned up about (XG, GP)
    return round(zb-za,1)
GRIPPER['gap_open_mm']={'tips':pad_gap(XG+28,OPEN_DEG),'pad_centres':pad_gap(XG+21,OPEN_DEG)}

# Park tolerance (full review): with every joint off by +-1 deg at once (32 corners), the moving links (twist onward)
# keep >= 3 mm from the side panels (TL4 wall criterion); the joint error budget TL4 has to hold is +-1 deg per joint.
WALLS=[p_ for p_ in OTHERS if p_['name'] in ('UGV-MECH-010--1','UGV-MECH-011--1','UGV-MECH-012--1')]
def wall_gap(q):
    best=(99.0,None)
    for n,s,l,_ in RIGHT:
        if l>=1:
            ps=posed(s,l,q,-1)
            for p_ in WALLS:
                if overlap(ps.BoundingBox(),p_['bb'],12) and (d_:=ps.distance(p_['shape']))<best[0]:
                    best=(d_,f"{n} / {p_['name']}")
    return best
PARK_TOL=min((wall_gap([u+e for u,e in zip(POSES['stow'],es)])+(list(es),) for es in itertools.product((-1,1),repeat=5)),
             key=lambda t: t[0])
PARK_TOLERANCE={'error_deg':1,'corners':32,'min_wall_mm':round(PARK_TOL[0],2),'pair':PARK_TOL[1],'worst_error_deg':PARK_TOL[2],
                'nominal_wall_mm':round(wall_gap(POSES['stow'])[0],2)}
# DD95 (R04 recheck): the passive left twist has no servo holding it: its printed block (066) turns in link A's pocket
# about the twist axis until it bears on A or the cover (058). Accepted: < +-1 deg (the TL4 joint budget above), i.e.
# turned 1 deg either way it already overlaps one of them; nominal it is clear. Axially the block stays where the
# right arm's servo does: bolted to the adapter (059), which the ring (075) holds in A's seat; the cover closes the pocket.
LZ={n:sh for n,sh,_,_ in LEFT}
def twist_overlap(deg):
    blk=LZ['UGV-MECH-066'].rotate(cq.Vector(0,YA,zs),cq.Vector(1,YA,zs),deg)
    return round(max(blk.intersect(LZ[k]).Volume() for k in (ARM_NAMES[0],'UGV-MECH-058')),3)
LEFT_TWIST={'limit_deg':1,'fill_clearance_mm':0.2,'nominal_mm3':twist_overlap(0),'hit_mm3':[twist_overlap(-1),twist_overlap(1)]}

# Clearance along every edge (1 deg samples, as the collision sweep): moving links (elbow onward) to every other part,
# and the whole arm in the park pose (where it rests on the fender by design). The shoulder hub/journal turns in place
# in its bearing.
def arm_clearance(q, first_link, margin=12.0):
    best=margin
    for n,s,l,_ in RIGHT:
        if l<first_link:
            continue
        ps=posed(s,l,q,-1)
        pb=ps.BoundingBox()
        for p_ in OTHERS:
            if overlap(pb,p_['bb'],margin) and not (n.startswith('UGV-MECH-050') and
                    (p_['name'] in ('UGV-MECH-012--1','REF-SERVO-SHOULDER-R','UGV-MECH-056--1','UGV-MECH-057-+1') or p_['name'].startswith('REF-BEARING-SHOULDER'))):
                best=min(best,ps.distance(p_['shape']))
    return round(best,2)
ARM_CLEARANCE=[]
for a_,b_ in A['pose_edges']:
    qa,qb=POSES[a_],POSES[b_]
    n=max(1,math.ceil(max(abs(u-v) for u,v in zip(qa,qb))/1))
    samples=[[u+(v-u)*k/n for u,v in zip(qa,qb)] for k in range(n+1)]
    ARM_CLEARANCE.append({'pose':[a_,b_],'moving_mm':min(arm_clearance(q,1) for q in samples if q!=POSES['stow']),
                          'park_mm':arm_clearance(POSES['stow'],0) if POSES['stow'] in samples else None})
# Servo rail off at park: the limp right arm droops about the shoulder until its first contact (0.5 deg steps).
ARM_LIMP_REST=None
for k in range(1,181):
    q=[POSES['stow'][0]+0.5*k,*POSES['stow'][1:]]
    if h:=arm_hits(q,self_check=False):
        ARM_LIMP_REST={'angle_deg':q[0],'hits':h}
        break

# DD82/DD83: tilt sweep of the eyes (pods, caps, cameras and the axle turn about the tilt axis; the column, housing,
# servo plate, tilt servo and the pan base do not), 5 deg steps over the look range. The pushrod is not swept.
TILTING=('UGV-MECH-043','UGV-MECH-044','UGV-MECH-045','REF-EYE-CAMERA')
HEAD_FIXED=('UGV-MECH-030','UGV-MECH-040','UGV-MECH-041','UGV-MECH-042','UGV-MECH-046','REF-SERVO-PAN','REF-SERVO-TILT',
            'REF-BEARING-PAN')
head_hits,head_clear=[],12.0
t0,t1=HD['tilt_sweep_deg']
for ang in range(t0,t1+1,5):
    for p_ in PARTS:
        if not p_['name'].startswith(TILTING):
            continue
        ps=p_['shape'].rotate(cq.Vector(nx,0,tilt_z),cq.Vector(nx,1,tilt_z),ang)
        pb=ps.BoundingBox()
        for f_ in PARTS:
            if f_['name'].startswith(HEAD_FIXED) and overlap(pb,f_['bb'],3):
                if (v:=ps.intersect(f_['shape']).Volume())>0.01:
                    head_hits.append({'tilt_deg':ang,'part':p_['name'],'hits':f_['name'],'volume_mm3':round(v,3)})
                if not (p_['name']=='UGV-MECH-045' and f_['name']=='UGV-MECH-042'):  # the axle turns in the blade bore
                    head_clear=min(head_clear,ps.distance(f_['shape']))
HEAD_TILT={'range_deg':[t0,t1],'step_deg':5,'hits':head_hits,'min_clearance_mm':round(head_clear,2)}

# Scan actual solid volumes, not merely bounding boxes. Contacts have zero volume.
intersections=[]
for a,b in itertools.combinations(PARTS,2):
    if not overlap(a['bb'],b['bb']):
        continue
    volume=a['shape'].intersect(b['shape']).Volume()
    if volume > 0.01:
        intersections.append({'a':a['name'],'b':b['name'],'volume_mm3':round(volume,3)})
ASSEMBLY.save(str(OUT/'UGV-01-A3-concept.step'))
manifest={'parameters':P,'status':'CONCEPT_NOT_FOR_MANUFACTURE','revision':P['revision'],
          'parts':[{k:v for k,v in part.items() if k not in ('shape','bb')} for part in PARTS],
          'unapproved_intersections':intersections,
          'arm_poses':ARM_POSES,'arm_edges':ARM_EDGES,'arm_limp_rest':ARM_LIMP_REST,'arm_clearance':ARM_CLEARANCE,
          'gripper':GRIPPER,'park_tolerance':PARK_TOLERANCE,'left_twist_play':LEFT_TWIST,
          'grasp_datum_local_mm':{'from_wrist_x':round(GRASP_LOCAL[0]-xw,2),'d':GRASP_LOCAL[1],'z':GRASP_LOCAL[2]},
          'head_tilt':HEAD_TILT,
          'arm_chain':{'joints':[{'origin':list(o),'axis':list(d),'sign':sign} for o,d,sign in joint_axes(-1)],
                       'links':{(n if n.startswith('REF') else f'{n}--1'):l for n,_,l,_ in RIGHT}},
          'not_modelled':['wiring and connector service sweeps, E-stop and battery wiring',
                         'ESP32-CAM FPC routing and antenna placement inside the eye pods',
                         'ToF window covers and cable routes',
                         'servo horns, screws, 624 idlers and M4 hardware (their holes, seats and nut pockets are modelled)',
                         'cables themselves, service loops and zip ties (DD85: exits, slots, the shoulder bore and the head channels are modelled)',
                         'fender flange screws into the side panels, shoulder-servo frame screws',
                         'eye camera mounts, lens windows, FFC routes and stereo calibration',
                         'arm sweeps are joint-space straight lines sampled at <= 1 deg; the planner must use the same path',
                         'gear tooth contact, backlash and the pads\' grip on a real object (the claw is swept as rigid jaws)',
                         'left arm distal joints: fixed by their bolts (no servos, no bearings); only the shoulder is posed',
                         'full load path from mast to chassis']}
(ROOT/'cad/assembly/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

# Datum drawing profile only: NOT a production DXF release.
profile=cq.Workplane('XY').rect(G['plate_length_mm'],G['plate_width_mm'])
for x,y in holes:
    profile=profile.moveTo(x,y).circle(G['chassis_mount_diameter_mm']/2)
cq.exporters.export(profile,str(OUT/'UGV-MECH-001-concept.dxf'))

robot=ET.Element('robot',name='ugv_01_geometry_concept')
ET.SubElement(robot,'link',name='base_link')
def urdf_part(name, size, center, cylinder_shape=False, joint_type='fixed', parent='base_link',
              axis='0 1 0', limits=None):
    link=ET.SubElement(robot,'link',name=name)
    visual=ET.SubElement(link,'visual')
    if cylinder_shape:
        ET.SubElement(visual,'origin',rpy='1.5707963267948966 0 0')
    geo=ET.SubElement(visual,'geometry')
    if cylinder_shape:
        ET.SubElement(geo,'cylinder',radius=str(size[0]/1000),length=str(size[1]/1000))
    else:
        ET.SubElement(geo,'box',size=' '.join(str(v/1000) for v in size))
    joint=ET.SubElement(robot,'joint',name=name+'_joint',type=joint_type)
    ET.SubElement(joint,'parent',link=parent); ET.SubElement(joint,'child',link=name)
    ET.SubElement(joint,'origin',xyz=' '.join(str(v/1000) for v in center))
    if joint_type in ('continuous','revolute'): ET.SubElement(joint,'axis',xyz=axis)
    if limits:
        ET.SubElement(joint,'limit',lower=str(limits[0]),upper=str(limits[1]),effort='1',velocity='2')
urdf_part('chassis',(G['body_length_mm'],W,top-plate_top),(0,0,(top+plate_top)/2))
for end,x in [('front',G['wheelbase_mm']/2),('rear',-G['wheelbase_mm']/2)]:
    for side,y in [('left',G['track_mm']/2),('right',-G['track_mm']/2)]:
        urdf_part(f'{end}_{side}_wheel',(G['wheel_diameter_mm']/2,G['wheel_width_mm']),
                  (x,y,G['wheel_axle_z_mm']),True,'continuous')
        my=G['motor_face_abs_y_mm']-M['body_length_mm']/2
        urdf_part(f'{end}_{side}_motor',(M['body_diameter_mm']/2,M['body_length_mm']),(x,my if y>0 else -my,60),True)
urdf_part('battery',G['battery_envelope_mm'],G['battery_center_mm'])
urdf_part('electronics',G['electronics_envelope_mm'],G['electronics_center_mm'])
urdf_part('sensor_mast_mount',(50,50,6),(30,0,top+3))
# Head chain and arm joints. Origins are zero-pose world positions (flat concept tree, not a kinematic release).
urdf_part('head_pan',(48,48,34),(nx,ny,top+40),joint_type='revolute',axis='0 0 1',limits=(-1.5708,1.5708))
urdf_part('head_tilt',(34,103,40),(nx,ny,tilt_z),joint_type='revolute',limits=(-0.5236,1.0472))
for name,side in (('left_eye_camera',1),('right_eye_camera',-1)):
    urdf_part(name,G['eye_camera_envelope_mm'],(pod_x+4,side*G['eye_center_y_mm'],tilt_z))
for (o,d,_),j,(lo,hi) in zip(joint_axes(-1),A['joints'],A['limits_deg']):
    urdf_part(f'right_{j}',(20,20,20),(o[0],-YA,zs),joint_type='revolute',axis=' '.join(str(v) for v in d),
              limits=(math.radians(lo),math.radians(hi)))
urdf_part('left_arm',(L1+L2,24,48),(xs+(L1+L2)/2,YA,zs))
ET.indent(robot)
ET.ElementTree(robot).write(ROOT/'simulation/ugv_geometry.urdf',encoding='utf-8',xml_declaration=True)
print(f'Generated {len(PARTS)} STEP parts, printable STL, assembly, concept DXF and geometry URDF')
print('Unapproved intersections:',intersections)
print('Arm poses:',{k:(v['grip_mm'],len(v['intersections'])) for k,v in ARM_POSES.items()})
print('Arm edges:',[(e['pose'],len(e['hits'])) for e in ARM_EDGES])
print('Limp rest:',ARM_LIMP_REST)
print('Head tilt:',HEAD_TILT)
print('Clearance:',[(c['pose'],c['moving_mm'],c['park_mm']) for c in ARM_CLEARANCE])
print('Gripper:',{'self':GRIPPER['jaw_self_hits'][:3],'poses':{k:len(v) for k,v in GRIPPER['poses'].items()},
                  'edges':[(e['pose'],len(e['hits'])) for e in GRIPPER['edges']],'gap':GRIPPER['gap_open_mm']})
print('Park tolerance:',PARK_TOLERANCE)
print('Left twist play:',LEFT_TWIST)
