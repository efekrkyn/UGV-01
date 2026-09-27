"""Check that a mass candidate only removes material from D1 rotating parts."""
from pathlib import Path
import json
import cadquery as cq

ROOT=Path(__file__).resolve().parents[1]
report=json.loads((ROOT/'cad/drivetrain/lightweight_report.json').read_text())
assert report['revision']=='D2A'
assert report['curb_mass_kg'] < 6
for part in ('UGV-MECH-046','UGV-MECH-047'):
    old=cq.importers.importStep(str(ROOT/f'cad/drivetrain/generated/{part}.step')).val()
    new=cq.importers.importStep(str(ROOT/f'cad/drivetrain/generated/lightweight/{part}-B.step')).val()
    assert new.isValid() and len(new.Solids())==1
    assert new.Volume()<old.Volume()
    assert new.cut(old).Volume()<.01, 'New envelope can intersect other components'
    b=new.BoundingBox()
    assert max(b.xlen,b.ylen,b.zlen)<=240
assert report['unapproved_intersections_impossible_by_subset']
print('PASS: lightweight rotating solids valid, within D1 envelopes and below 6 kg calculated curb')
