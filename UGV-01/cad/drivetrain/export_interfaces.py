"""Write nominal D1 2D DXF interface profiles using only Python stdlib.

Profiles show bolt drilling and face outline. Raised bearing housing, fits,
threads and tolerances require the STEP plus a later manufacturing drawing.
"""
from pathlib import Path
import itertools
import json
import math

ROOT = Path(__file__).resolve().parents[2]
P = json.loads((ROOT/'config/drivetrain_module.json').read_text())
OUT = ROOT/'cad/drivetrain/generated'


def line(a, b):
    return f'0\nLINE\n8\nOUTLINE\n10\n{a[0]:.6f}\n20\n{a[1]:.6f}\n30\n0\n11\n{b[0]:.6f}\n21\n{b[1]:.6f}\n31\n0\n'


def circle(x, y, r):
    return f'0\nCIRCLE\n8\nHOLE\n10\n{x:.6f}\n20\n{y:.6f}\n30\n0\n40\n{r:.6f}\n'


def dxf(name, outline, holes):
    entities = ''.join(line(a, b) for a,b in zip(outline,outline[1:]+outline[:1]))
    entities += ''.join(circle(*hole) for hole in holes)
    content='0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n'
    content+=entities+'0\nENDSEC\n0\nEOF\n'
    path=OUT/name;path.write_text(content)
    assert content.count('0\nCIRCLE\n')==len(holes)
    assert content.count('0\nLINE\n')==len(outline)
    return path


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    base=[(-26,75),(-27,75),(-27,65),(-17,65),(-17,75),
          (30,75),(30,65),(40,65),(40,119),(32,119),(32,143),(-26,143)]
    base_holes=[(x,y,2.25) for x,y in itertools.product(P['carrier_bolt_x_mm'],P['carrier_bolt_y_mm'])]
    x0=P['motor_body_offset_x_mm'];z=P['axle_z_mm'];radius=P['motor_pcd_mm']/2
    motor_holes=[(0,z,6.2)]
    motor_holes += [(x0+sx*radius*math.sqrt(3)/2,z+sz*radius/2,1.7)
                    for sx,sz in itertools.product((-1,1),(-1,1))]
    paths=[dxf('UGV-MECH-040-base-interface-D1.dxf',base,base_holes),
           dxf('UGV-MECH-040-motor-face-interface-D1.dxf',
               [(-14,39),(30,39),(30,84),(-14,84)],motor_holes)]
    assert base_holes==[(x,y,2.25) for x,y in itertools.product((-22,35),(70,90))]
    print('Wrote nominal DXF interface profiles:',', '.join(p.name for p in paths))
