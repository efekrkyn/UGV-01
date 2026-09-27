"""D1/D2 shaft and bearing screening; no CAD or manufacturing output."""
from pathlib import Path
import json
import math

ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'config/drivetrain_module.json').read_text())
BASE=json.loads((ROOT/'cad/drivetrain/budget_report.json').read_text())


def screen(diameter_mm,yield_mpa,bearing_static_n,inner_y_mm,outer_y_mm,mu,mass_kg=9):
    load=mass_kg*9.80665*3/2
    axial=mu*load
    moment=axial*P['wheel_radius_mm']
    span=outer_y_mm-inner_y_mm
    if span <= 0 or diameter_mm <= 0 or mu <= 0:
        raise ValueError('Invalid screening geometry')
    cy=P['wheel_center_y_mm']
    radial=max(abs(load*(outer_y_mm-cy)/span),abs(load*(cy-inner_y_mm)/span))+moment/span
    p0=max(radial,.6*radial+.5*axial)
    bend=32*moment/(math.pi*diameter_mm**3)
    shear=16*P['shaft_screening_torque_nm']*1000/(math.pi*diameter_mm**3)
    eq=P['shaft_notch_factor_assumption']*math.sqrt(bend*bend+3*shear*shear)
    return {'shaft_yield_margin':yield_mpa/eq,'bearing_static_margin':bearing_static_n/p0,
            'bearing_radial_n':radial,'shaft_equivalent_mpa':eq}


def main():
    d1={str(mu):screen(10,305,1960,123.5,137,mu) for mu in (1,1.2)}
    d1_alloy={str(mu):screen(10,650,1960,123.5,137,mu) for mu in (1,1.2)}
    # 608 widths are 7 mm; separate centres as far as the unchanged package allows.
    d2={str(mu):screen(8,650,1370,123,137.5,mu) for mu in (1,1.2)}
    density_steel=7.85e-6; density_al=2.7e-6
    shaft=math.pi*(5**2-4**2)*(141-P['shaft_start_y_mm'])*density_steel
    shoulder=math.pi*(7.5**2-6**2)*2.5*density_steel
    bearings=2*(.019-.012)
    housing=(math.pi*((18**2-13**2)-(16**2-11**2))*21.5
             +math.pi*((18**2-11.5**2)-(16**2-9.5**2))*2)*density_al
    # Inner/outer spacer and retention washer still require actual D2 CAD.
    saving_per_wheel=shaft+shoulder+bearings+housing
    curb=BASE['curb_without_reserve_kg']-4*saving_per_wheel
    report={'basis':'9 kg mechanical screen, 3 g over two wheels, 1.5 Nm drive torque',
            'D1_10mm_6000_C45':d1,'D1_10mm_6000_42CrMo4_QT':d1_alloy,
            'D2_8mm_608_42CrMo4_QT':d2,
            'D2_precise_parts_saving_kg_per_wheel':saving_per_wheel,
            'D2_optimistic_curb_kg_excluding_spacer_savings':curb,
            'D2_remaining_mass_reduction_to_0p3kg_reserve_kg':curb-5.7,
            'decision':'Reject D2 8mm/608: at mu=1.2 both margins <2. Current D1 C45 shaft also <2; use certified 42CrMo4+QT 10 mm shaft or restrict the load envelope.',
            'caveats':['Material minimum 650 MPa applies only to certified +QT stock and representative section size.',
                       'The D2 reduced housing shape and spacers were not modelled; mass saving is analytical.',
                       'Static screening is not fatigue, bearing life, fit or physical test.']}
    (ROOT/'docs/drivetrain_trade_D2.json').write_text(json.dumps(report,indent=2)+'\n')
    assert d1['1.2']['shaft_yield_margin']<2 and d1['1.2']['bearing_static_margin']>2
    assert d1_alloy['1.2']['shaft_yield_margin']>2 and d1_alloy['1.2']['bearing_static_margin']>2
    assert d2['1.2']['shaft_yield_margin']<2 and d2['1.2']['bearing_static_margin']<2
    assert 0<saving_per_wheel<.04
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
