"""M2 Task 5 (M3 geometry): print orientation, settings and order for every printed part.

`python3 tools/print_plan.py` (in .venv) writes each printed part's STL in its print orientation, on the bed
(z = 0, centred), and regenerates docs/print_guide_A3.md from the same table. tests/check_print_plan.py checks
coverage, bed contact, the 240 mm envelope and that the guide is current. Settings are starting points for a
0.4 mm nozzle; tune them with the coupons first.
"""
import json
from pathlib import Path
import sys

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from body_mass_screen import TPU_PREFIXES, part_mass  # noqa: E402

AXIS = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}
NONE, FLAT = 'yok', 'Montaj yönünde, alt yüz tablada'


def e(prefix, phase, orient, rot=(), supports=NONE, walls=4, infill=25, note='', hold=False):
    return {'prefix': prefix, 'phase': phase, 'orient': orient, 'rot': list(rot), 'supports': supports,
            'walls': walls, 'infill': infill, 'note': note, 'hold': hold}


# rot: rotations about the world axes through the origin, applied in order, before the part is set on the bed.
PLAN = [
    e('UGV-MECH-001', 1, FLAT, walls=5, infill=40, note='iki yarı; ek yeri x=−35'),
    e('UGV-MECH-002', 1, FLAT, walls=5, infill=40, note='ek kirişi, iki yarıyı üstten bağlar'),
    e('UGV-MECH-003', 1, FLAT, walls=5, infill=40, note='motor kelepçesi alt yuvası'),
    e('UGV-MECH-004', 1, 'Ters çevrili: düz üst yüz tablada, yarım silindir yuvası yukarı', [('x', 180)], walls=5, infill=40),
    e('UGV-MECH-060-FL', 2, 'Dış yüz (jant göbeği) tablada', [('x', -90)], walls=5, infill=40, note='önce D delik deneme parçası'),
    e('UGV-MECH-060-RL', 2, 'Dış yüz (jant göbeği) tablada', [('x', -90)], walls=5, infill=40),
    e('UGV-MECH-060-FR', 2, 'Dış yüz (jant göbeği) tablada', [('x', 90)], walls=5, infill=40),
    e('UGV-MECH-060-RR', 2, 'Dış yüz (jant göbeği) tablada', [('x', 90)], walls=5, infill=40),
    e('UGV-MECH-061', 2, 'Yan yüz tablada (eksen dik)', [('x', 90)], walls=3, infill=20, note='TPU 95A, yavaş (≤25 mm/s)'),
    e('UGV-MECH-010-+1', 3, 'Dış yüz tablada', [('x', -90)]),
    e('UGV-MECH-010--1', 3, 'Dış yüz tablada', [('x', 90)]),
    e('UGV-MECH-011-+1', 3, 'Dış yüz tablada', [('x', -90)]),
    e('UGV-MECH-011--1', 3, 'Dış yüz tablada', [('x', 90)]),
    e('UGV-MECH-012-+1', 3, 'Dış yüz tablada; rulman yuvası tablaya açılır', [('x', -90)], walls=5, infill=40,
      note='omuz boss\'u: önce 6804 yuva deneme parçası'),
    e('UGV-MECH-012--1', 3, 'Dış yüz tablada; rulman yuvası tablaya açılır', [('x', 90)], walls=5, infill=40,
      note='omuz boss\'u ve servo çerçevesi vidaları'),
    e('UGV-MECH-013', 3, 'Üst yüz yukarı; pah son katmanlarda', note='ön kapakta kargo ağzı'),
    e('UGV-MECH-022-+1', 3, 'Dış yüz tablada', [('y', 90)]),
    e('UGV-MECH-022--1', 3, 'Dış yüz tablada', [('y', -90)]),
    e('UGV-MECH-030', 3, FLAT, walls=5, infill=40),
    e('UGV-MECH-031', 3, FLAT + '; havşalar tablaya açılır', walls=5, infill=40),
    e('UGV-MECH-070', 4, FLAT),
    e('UGV-MECH-071', 4, FLAT),
    e('UGV-MECH-072', 4, FLAT, note='direnç rafı: PETG ısıya ≈70 °C\'ye kadar dayanır; TL1\'de ölçülür'),
    e('UGV-MECH-073', 4, 'Arka duvar tablada; taban dikey, köprü yok', [('y', -90)], supports='yalnız yatay ayakların altına'),
    e('UGV-MECH-056', 4, 'Servo plakası tablada, kollar yukarı', [('x', -90)], walls=5, infill=40),
    e('UGV-MECH-057', 4, 'Halka yüzü tablada', [('x', 90)], walls=5, infill=40),
    e('UGV-MECH-015-FL', 5, 'Flanşın gövdeye bakan yüzü tablada', [('x', 90)]),
    e('UGV-MECH-015-RL', 5, 'Flanşın gövdeye bakan yüzü tablada', [('x', 90)]),
    e('UGV-MECH-015-FR', 5, 'Flanşın gövdeye bakan yüzü tablada', [('x', -90)]),
    e('UGV-MECH-015-RR', 5, 'Flanşın gövdeye bakan yüzü tablada', [('x', -90)]),
    e('UGV-MECH-017-+1', 5, 'İç yüz tablada', [('y', -90)], walls=3, infill=15, note='TPU 95A'),
    e('UGV-MECH-017--1', 5, 'İç yüz tablada', [('y', 90)], walls=3, infill=15, note='TPU 95A'),
    e('UGV-MECH-018', 5, FLAT, walls=2, infill=100, note='TPU 95A; yarıklar dilimleyicide açık kalmalı; kapağa yapıştırılır'),
    e('UGV-MECH-043', 6, 'Ön yüz tablada, açık arka yukarı', [('y', 90)],
      supports='dört ön tırnak ve sol gözdeki krank göbeği için ağaç destek', note='altıgen aks deliği iç duvarda'),
    e('UGV-MECH-044', 6, 'Kapak plakası tablada, çerçeve yukarı', [('y', -90)], note='sıkı geçme; önce deneme'),
    # DD82 head mechanism.
    e('UGV-MECH-040', 6, 'Açık alt tablada', walls=5, infill=40,
      note='pan MG90S alttan girer; kulak çıkıntısı köprüyle basılır; 6804 yuvası üstte, önce deneme'),
    e('UGV-MECH-041', 6, 'Bloğun açık üstü tablada, mil yukarı', [('x', 180)], walls=5, infill=40,
      note='Ø20 mil dik; blok tabanı 38 mm köprü (yavaş köprü hızı); servo plakası olukları'),
    e('UGV-MECH-042', 6, 'Kapak plakası tablada, bıçak yukarı', walls=5, infill=40,
      note='itme çubuğu kanalı; aks göbeği deliği Ø9,4 yatay, gerekirse raybalanır'),
    e('UGV-MECH-045', 6, 'Dik (altıgen uç tablada)', [('x', 90)], walls=6, infill=100, note='göz aksı; %100 dolgu'),
    e('UGV-MECH-046', 6, FLAT, walls=4, infill=60, note='tilt servo plakası'),
    # DD81 arm links: B, C and D print on their side (flat 25 mm faces), bores and inserts horizontal.
    e('UGV-MECH-050', 7, 'Omuz kabuğunun düz yüzü tablada (park yönü)', walls=5, infill=40,
      supports='6704 yuvası, korna boşluğu ve twist cebinin altına ağaç destek', note='twist cebi: kapak 4 × M2'),
    e('UGV-MECH-051', 7, 'Yan yüz tablada', [('x', 90)], walls=5, infill=40,
      note='dirsek MG996R: 4 × M3 insert, M4 somun cebi; iki M3 cepten adaptöre'),
    e('UGV-MECH-052', 7, 'Yan yüz tablada', [('x', 90)], walls=5, infill=40,
      note='dirsek çatalı (624 yuvası yatay: önce deneme) + bilek MG996R yuvası'),
    e('UGV-MECH-053', 7, 'Yan yüz tablada', [('x', 90)], walls=5, infill=40, note='bilek çatalı + MG90S dönüş yuvası'),
    e('UGV-MECH-054', 7, 'Dış yüz tablada, kulak yüzü yukarı', [('x', 180)], supports='yalnız çenelerin altına',
      walls=5, infill=40, note='pençe MG90S kulakları ve dönüş kornası M2 ile'),
    e('UGV-MECH-058', 7, 'Düz', [('x', 90)], walls=3, infill=40, note='twist servo kapağı'),
    e('UGV-MECH-059', 7, 'Flanş tablada', [('y', 90)], walls=6, infill=100,
      note='twist adaptörü: 25T korna ↔ 6704 iç bileziği; %100 dolgu, istenirse alüminyumdan tornalanır'),
]


def entry(name):
    return max((x for x in PLAN if name.startswith(x['prefix'])), key=lambda x: len(x['prefix']))


def oriented(name):
    shape = cq.importers.importStep(str(ROOT / f'cad/assembly/generated/{name}.step')).val()
    for axis, deg in entry(name)['rot']:
        shape = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(*AXIS[axis]), deg)
    b = shape.BoundingBox()
    return shape.translate(cq.Vector(-(b.xmin + b.xmax) / 2, -(b.ymin + b.ymax) / 2, -b.zmin))


def fasteners():
    g = json.loads((ROOT / 'config/vehicle.json').read_text())['geometry']
    it = g['internal']
    lids, panels = 3, 6
    return {
        'M3 ısıl insert (Ø4,0 × 6 delik)': panels * 2 + 4 + len(it['tray_standoffs_mm']) + 4 + len(it['cargo']['flange_screw_y_mm'])
        + 8,
        'M3 × 10: kapaklar → panel insertleri': lids * 4,
        'M3 × 25: boyun köprüsü → kapak → flanş → pan tabanı insertleri': 4,
        'M2 × 6 kendinden kılavuzlu: pan ve tilt MG90S kulakları 4, pan kornası → boyun 2, sütun kapağı → blok 4': 10,
        'M4 × 30 + somun: göz aksı (iki gözü aksa sıkar)': 1,
        'M3 × 45 + somun: motor kelepçeleri': 8,
        'M4 × 12 + somun: panel ayakları → plaka': len(g['chassis_mount_x_mm']) * len(g['chassis_mount_y_mm']),
        'M3 × 12 + somun: batarya beşiği, tepsi, balast rafı, kargo ayakları → plaka':
            len(it['battery_mounts_mm']) + len(it['tray_mounts_mm']) + len(it['ballast_mounts_mm']) + len(it['cargo']['leg_mounts_mm']),
        'M3 × 8: pertinaks → tepsi insertleri': len(it['tray_standoffs_mm']),
        'M3 × 10 + somun: çamurluklar → yan paneller': len(g['fender']['screw_x_mm']) * 2,
        'M3 × 10: omuz servo çerçevesi → insertler (duvardan)': 4,
        'M3 × 16 + somun: DS3218 kulakları → çerçeve': 4,
        'M3 × 8: korna → omuz mili (kılavuz)': 4,
        'M3 × 10: kargo kutusu flanşı → insertler (ön duvardan)': len(it['cargo']['flange_screw_y_mm']),
        'M3 × 10: MG996R kulakları → insertler (dirsek, bilek)': 8,
        'M3 × 8: 25T alüminyum korna → çatal iç yanağı (dirsek, bilek)': 8,
        'M3 × 8: 25T alüminyum korna → twist adaptörü (baş yuvada)': 4,
        'M3 × 12: üst kol B → twist adaptörü (B\'nin servo cebinden)': 2,
        'M4 × 12 + somun + 0,5 mm pul: 624 boşta yatakları (dirsek, bilek)': 2,
        'M2 × 8 kendinden kılavuzlu: twist kapağı 4, MG90S kulakları 4, dönüş kornası → pençe 2': 10,
    }


def guide():
    manifest = json.loads((ROOT / 'cad/assembly/manifest.json').read_text())
    parts = [p for p in manifest['parts'] if p['printable']]
    phases = {1: 'Şasi', 2: 'Tekerler', 3: 'Gövde', 4: 'İç düzen', 5: 'Dış parçalar', 6: 'Baş', 7: 'Kollar'}
    rows, grams = [], {'PETG': 0.0, 'TPU': 0.0}
    for p in sorted(parts, key=lambda p: (entry(p['name'])['phase'], p['name'])):
        x = entry(p['name'])
        _, printed_g, _ = part_mass(ROOT, p)
        material = 'TPU' if p['name'].startswith(TPU_PREFIXES) else 'PETG'
        if not x['hold']:
            grams[material] += printed_g
        rows.append(f"| {x['phase']} {phases[x['phase']]} | `{p['name']}` | {material} | {x['orient']} | {x['supports']} | "
                    f"{x['walls']} / %{x['infill']} | {printed_g:.0f} | {x['note']} |")
    held = [p['name'] for p in parts if entry(p['name'])['hold']]
    lines = [
        '# UGV-01 A3 Lite baskı rehberi (M3)', '',
        '`tools/print_plan.py` tarafından üretilir, elle düzenlenmez. STL\'ler `cad/assembly/generated/` içinde, '
        'bu tablodaki yönde ve tablaya oturmuş halde. **Baskı ya da üretim onayı değildir;** hiçbir parça basılmadı.', '',
        '## Genel ayarlar', '',
        '- Makine: 256 × 256 × 256 mm tabla; parçalar ≤240 mm tasarım zarfında. 0,4 mm meme, 0,2 mm katman.',
        '- PETG: 235–245 °C, tabla 75–80 °C. Dolgu gyroid. "Duvar / dolgu" sütunu çevre duvarı sayısı ve dolgu yüzdesidir.',
        '- TPU 95A: 220–230 °C, ≤25 mm/s, geri çekme kısa. Lastik ve tamponlar yumuşak kalmalı.',
        '- Isıl insert (M3, Ø4,0 × 6 delik): 220–230 °C havya ucuyla, yüzeye dik.',
        '- Kütle sütunu, kütle taramasının baskı tahminidir (1,2 mm kabuk + %20 dolgu; tablodaki dolgu farklıysa değişir).', '',
        '## Sıra', '',
        '0. **Deneme parçaları (önce):** M3 insert deliği; motor mili D deliği ve set vidası; 6804 (Ø32), 6704 (Ø27) '
        've 624 (Ø13) rulman yuvaları; göz kapağı geçmesi (CAD yan başına 0,15 mm boşluk, sıkı geçme değil: kupon elle çekmede tutmazsa bir damla yapıştırıcı ya da bant; servis için sökülebilir kalmalı); TPU lastik–jant oturması. Ölçü tutmazsa config '
        'düzeltilir, CAD yeniden üretilir.',
        '1. Şasi → 2. Tekerler (motorla sökülüp takılarak denenir) → 3. Gövde → 4. İç düzen → 5. Dış parçalar → 6. Baş → 7. Kollar.',
        f'- **Bekleyen {len(held)} parça:** ' + ', '.join(held) if held else '- Bütün parçalar basılmaya hazır (DD82).',
        '- Baş (DD82, DD83): pan servosu tabanın altından girer; boyun Ø20 mili 6804\'e oturur; tilt servosu '
        'boyun bloğunda gizli, sol gözü Ø1,5 mm itme çubuğuyla sürer; iki göz altıgen aksla birbirine bağlıdır.',
        '- Kollar (DD81): twist MG996R\'nin kulakları gövde hizasında kesilir; dirsek ve bilek servoları kulaklarıyla '
        'takılır. Korna ve 624 deliği için önce deneme parçası basılır.', '',
        '## Parçalar', '',
        '| Aşama | Parça | Malzeme | Yön | Destek | Duvar / dolgu | Kütle g | Not |', '|---|---|---|---|---|---|---:|---|',
        *rows, '',
        f"Basılmaya hazır parçaların baskı tahmini: PETG ≈{grams['PETG']:.0f} g, TPU ≈{grams['TPU']:.0f} g "
        '(bekleyenler hariç; tamamı için [Lite mekanik](lite_mechanical_A3.md)).', '',
        '## Vida, insert ve rulman', '',
        '| Kalem | Adet |', '|---|---:|',
        *(f'| {k} | {v} |' for k, v in fasteners().items()),
        '| Rulman 6804-2RS (boyun + iki omuz) | 3 |', '| Rulman 6704-2RS (üst kol dönüşü) | 1 |',
        '| Rulman 624ZZ (dirsek, bilek) | 2 |', '| 25T alüminyum disk korna (twist, dirsek, bilek) | 3 |', '',
        'Ek kirişlerin plakaya bağlanması (yapıştırma ya da vida) ve göz kapaklarının yapıştırılması montajda karar verilir.',
    ]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    manifest = json.loads((ROOT / 'cad/assembly/manifest.json').read_text())
    for part in manifest['parts']:
        if part['printable']:
            cq.exporters.export(oriented(part['name']), str(ROOT / f"cad/assembly/generated/{part['name']}.stl"),
                                tolerance=0.05, angularTolerance=0.1)
    (ROOT / 'docs/print_guide_A3.md').write_text(guide())
    print('Wrote oriented STLs and docs/print_guide_A3.md')
