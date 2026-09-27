"""Candidate mass reconciliation; preserves A0 requirements, exposes shortfall."""
from pathlib import Path
import csv
import json

root=Path(__file__).resolve().parents[1]
module=json.loads((root/'cad/drivetrain/manifest.json').read_text())
pack=json.loads((root/'cad/drivetrain/packaging_report.json').read_text())
vehicle=json.loads((root/'docs/revisions/A2/vehicle.json').read_text())  # D1/D2A were sized against A2
vol={p['name']:p['volume_mm3'] for p in module['parts']}
al=2.7e-6; steel=7.85e-6; polymer=1.2e-6
metal=4*(vol['UGV-MECH-040']+vol['UGV-MECH-041'])*al
metal+=sum(p['volume_mm3']*al for p in pack['parts'] if p['name']=='UGV-MECH-001' or p['name'].startswith('UGV-MECH-002'))
wheel=4*(sum(vol[f'UGV-MECH-{n:03d}']*steel for n in (42,43,44,45))
         +sum(vol[f'UGV-MECH-{n:03d}']*polymer for n in (46,47))
         +2*.019+.040+.002)
budget=vehicle['mass_budget']
old_metal=budget[0]['mass_kg']; old_wheel=budget[3]['mass_kg']
reserve=next(p['mass_kg'] for p in budget if p['name']=='design contingency mass')
base=sum(p['mass_kg'] for p in budget)-reserve
candidate=base-old_metal-old_wheel+metal+wheel
with (root/'manufacturing/bom/drivetrain_D1.csv').open() as f:
    cost=sum(int(r['quantity'])*float(r['unit_cost_usd_estimate']) for r in csv.DictReader(f))
report=dict(metal_group_kg=metal,wheel_group_kg=wheel,curb_without_reserve_kg=candidate,
            remaining_to_6kg_kg=6-candidate,previous_reserve_kg=reserve,
            candidate_subsystem_cost_usd_estimate=cost,
            assumptions=['coupling 40 g and retaining ring 2 g per wheel',
                         'SKF bearing 19 g each; sealed variant mass check pending',
                         'solid polymer equivalent density 1.2 g/cm3',
                         'all other A0 mass allowances unchanged; not weighed'])
(root/'cad/drivetrain/budget_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
