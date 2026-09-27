"""Browser 3D viewer of the A3 concept assembly (three.js), generated from the STEP parts.

Tessellates every manifest part, quantises to 0.1 mm Int16 + per-part Uint16 indices and
embeds them with Turkish part notes into tools/viewer_template.html.
Writes docs/renders/UGV-01-A3-viewer.html (standalone) and, with an argument, the
wrapper-less page body used for the Artifact publish.
"""
import base64
import json
import sys
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from body_mass_screen import CATALOG_G, part_mass  # noqa: E402

TOL, ANG_TOL = 0.1, 0.1  # mm, rad
GROUPS = [  # key, label, name prefixes; every part lands in exactly one group
    ('chassis', 'Şasi ve motor kelepçeleri', ('UGV-MECH-001', 'UGV-MECH-002', 'UGV-MECH-003', 'UGV-MECH-004')),
    ('body', 'Gövde panelleri', ('UGV-MECH-010', 'UGV-MECH-011', 'UGV-MECH-012', 'UGV-MECH-022', 'UGV-MECH-030', 'UGV-MECH-031')),
    ('lids', 'Üst kapaklar', ('UGV-MECH-013',)),
    ('fenders', 'Çamurluklar', ('UGV-MECH-015',)),
    ('fixtures', 'İç tutucular', ('UGV-MECH-070', 'UGV-MECH-071', 'UGV-MECH-072', 'UGV-MECH-073')),
    ('bumpers', 'Tamponlar ve TPU kapaklar', ('UGV-MECH-017', 'UGV-MECH-018')),
    ('wheels', 'Tekerler', ('UGV-MECH-060', 'UGV-MECH-061')),
    ('drive', 'Motorlar', ('REF-MOTOR',)),
    ('head', 'Baş ve boyun', ('UGV-MECH-040', 'UGV-MECH-041', 'UGV-MECH-042', 'UGV-MECH-043', 'UGV-MECH-044', 'UGV-MECH-045',
                              'UGV-MECH-046', 'REF-TILT-ROD', 'REF-SERVO-PAN',
                              'REF-SERVO-TILT', 'REF-BEARING-PAN', 'REF-EYE-CAMERA')),
    ('arms', 'Kollar', ('UGV-MECH-050', 'UGV-MECH-051', 'UGV-MECH-052', 'UGV-MECH-053', 'UGV-MECH-054', 'UGV-MECH-056',
                        'UGV-MECH-057', 'UGV-MECH-058', 'UGV-MECH-059', 'REF-SERVO-SHOULDER', 'REF-SERVO-TWIST', 'REF-SERVO-ELBOW', 'REF-SERVO-WRIST',
                        'REF-SERVO-ROLL', 'REF-SERVO-GRIPPER', 'REF-BEARING-SHOULDER', 'REF-BEARING-TWIST')),
    ('electronics', 'Elektronik ve sensörler', ('REF-BATTERY', 'REF-ELECTRONICS', 'REF-ESTOP', 'REF-TOF',
                                                'REF-LIGHT-BAR', 'REF-BALLAST')),
]
LR = {'+1': 'sol', '-1': 'sağ'}
WHEEL = {'FL': 'ön sol', 'FR': 'ön sağ', 'RL': 'arka sol', 'RR': 'arka sağ'}
DESC = [  # prefix, note ({s} = position from the name suffix), suffix map
    ('UGV-MECH-001', 'Taban plakası, {s} yarı: 5 mm PETG, ek yeri x=−35 mm', {'R': 'arka', 'F': 'ön'}),
    ('UGV-MECH-002', 'Ek kirişi ({s}): 150×12×15 mm, iki plaka yarısını üstten bağlar', LR),
    ('UGV-MECH-003', 'Motor kelepçesi alt yuvası ({s}): JGA25 yükünü taban plakasına aktarır', WHEEL),
    ('UGV-MECH-004', 'Motor kelepçesi kapağı ({s}): iki M3 cıvata kapak, yuva ve plakayı sıkar', WHEEL),
    ('UGV-MECH-010', 'Arka yan panel ({s}): motor içeride, duvardan yalnız göbek boynu Ø18 delikten geçer', LR),
    ('UGV-MECH-011', 'Orta yan panel ({s})', LR),
    ('UGV-MECH-012', 'Ön yan panel ({s}): omuz rulman yuvası (6804-2RS) ve göbek boynu deliği', LR),
    ('UGV-MECH-013-1', 'Arka üst kapak: acil stop butonu bu kapaktan geçer', {}),
    ('UGV-MECH-013-2', 'Orta üst kapak: altında boyun köprüsü', {}),
    ('UGV-MECH-013-3', 'Ön üst kapak: kargo bölmesinin atma ağzı', {}),
    ('UGV-MECH-015', 'Çamurluk ({s}): tekerleğin üstünü örter; park eden kol buna yaslanır', WHEEL),
    ('UGV-MECH-017-+1', 'Ön TPU tampon: iki ToF sensör penceresi', {}),
    ('UGV-MECH-017--1', 'Arka TPU tampon', {}),
    ('UGV-MECH-018', 'Atma ağzının TPU yarıklı kapağı: nesneyi geçirir, tozu tutar', {}),
    ('UGV-MECH-022-+1', 'Ön uç duvar: durum ışık şeridi penceresi, balast havalandırması', {}),
    ('UGV-MECH-022--1', 'Arka uç duvar', {}),
    ('UGV-MECH-030', 'Boyun flanşı 50×50 mm: baş bu plakaya oturur', {}),
    ('UGV-MECH-031', 'Boyun köprüsü: kapak altında, başın yükünü kapağa yayar; 4 × M3 pan tabanına kadar sıkar', {}),
    ('UGV-MECH-040', 'Pan tabanı: MG90S pan servosu alttan girer, kulakları 2 × M2; tepesinde 6804 boyun rulmanı', {}),
    ('UGV-MECH-041', 'Boyun: Ø20 mili 6804’ten geçer, alt yüzü pan kornasına 2 × M2; üstündeki blokta gizli tilt servosu', {}),
    ('UGV-MECH-042', 'Boyun sütunu: bloğun kapağı, içinden itme çubuğu ve kablolar geçer; tepesindeki ince bıçak gözlerin menteşesi', {}),
    ('UGV-MECH-043', 'Göz kabuğu ({s}) 40×42×48 mm: arkası açık; ESP32-CAM ön tırnaklara, lens pencere yuvasına oturur; iki göz ortak altıgen aksta, sol gözde itme çubuğu krankı', LR),
    ('UGV-MECH-044', 'Göz arka kapağı ({s}): sıkı geçme; çerçevesi kartı ön tırnaklara bastırır', LR),
    ('UGV-MECH-045', 'Göz aksı: bıçakta döner, altıgen uçları iki göze geçer; M4 iki gözü birbirine sıkar (stereo taban 61 mm)', {}),
    ('UGV-MECH-046', 'Tilt servo plakası: servo kulaklarıyla vidalanır, bloğun oluklarına üstten kayar', {}),
    ('REF-TILT-ROD', 'Ø1,5 mm itme çubuğu: gizli tilt servosundan sol gözün krankına, 1:1 paralelkenar', {}),
    ('UGV-MECH-050--1', 'Sağ omuz ve üst kol: rulmandan geçen mil (kablo deliği); kulakları kesilmiş MG996R twist servosu kapaklı cepte', {}),
    ('UGV-MECH-050-+1', 'Sol omuz ve üst kol: pasif, sürtünmeyle elle poz verilir', {}),
    ('UGV-MECH-051', 'Üst kolun dış parçası ({s}): 6704 ile kendi ekseninde döner; MG996R dirsek servosu kulaklarıyla 4 × M3 insertte, mili içe bakar', LR),
    ('UGV-MECH-052', 'Ön kol ({s}): dirsek çatalı (iç yanak 25T kornaya 4 × M3, dış yanak 624ZZ üstünde); MG996R bilek eğim servosu', LR),
    ('UGV-MECH-053', 'Bilek ({s}): bilek çatalı; MG90S dönüş servosu kulaklarıyla 2 × M2', LR),
    ('UGV-MECH-054', 'Pençe ({s}): dönüş kornasına 2 × M2; MG90S pençe servosu ve iki çene; kavrama merkezi bilek ekseninden 96 mm', LR),
    ('UGV-MECH-056', 'Omuz servosu çerçevesi: DS3218’i yan duvara bağlar, servo yalnız tork verir', {}),
    ('UGV-MECH-057', 'Sol omuz sürtünme bileziği: pasif kolu tutar', {}),
    ('UGV-MECH-058', 'Twist servo kapağı: kulakları kesilmiş MG996R’yi omuz kabuğundaki cebinde tutar (4 × M2)', {}),
    ('UGV-MECH-059', 'Twist adaptörü: 25T alüminyum kornaya 4 × M3; 6704 iç bileziğini taşır, üst kolun dış parçası 2 × M3 ile bağlanır', {}),
    ('UGV-MECH-060', 'Teker göbeği ({s}): boynu duvardan motora uzanır; D delik, M3 sıkma vidası 6 mm aralıkta, 8 kanatçık', WHEEL),
    ('UGV-MECH-061', 'Lastik ({s}): Ø120/Ø110 mm TPU', WHEEL),
    ('UGV-MECH-070', 'Batarya beşiği: kayış yuvalı, plaka ek yerini köprüler', {}),
    ('UGV-MECH-071', 'Elektronik tepsisi: 4 insertli ayak, delikli pertinaks bunlara vidalanır', {}),
    ('UGV-MECH-072', 'Direnç rafı: 4 × 10 W balast, ön duvar yarıklarından hava alır', {}),
    ('UGV-MECH-073', 'Kargo kutusu: kolun ağızdan bıraktığı nesneleri toplar', {}),
    ('REF-MOTOR', 'JGA25-370 motor ({s}): 12 V, 77 dev/dk 1:78, Hall enkoderli, 7,5 Ω balastla; gövdenin içinde', WHEEL),
    ('REF-BATTERY', 'Batarya: 3S1P 18650 paket, 70×60×24 mm', {}),
    ('REF-BALLAST', '7,5 Ω 10 W motor seri direnci ({s})', {'1': 'FL', '2': 'FR', '3': 'RL', '4': 'RR'}),
    ('REF-ELECTRONICS', 'Elektronik: ESP32-S3 + 2×TB6612FNG + PCA9685 + 3 buck, 100×76×25 mm', {}),
    ('REF-ESTOP', 'Acil stop butonu Ø40 (NC): motor ve servo gücünü keser', {}),
    ('REF-TOF', 'VL53L0X ön mesafe sensörü ({s})', LR),
    ('REF-LIGHT-BAR', 'Durum ışık şeridi: adreslenebilir LED', {}),
    ('REF-SERVO-PAN', 'MG90S pan servosu: başı sağa/sola çevirir', {}),
    ('REF-SERVO-TILT', 'MG90S tilt servosu: boyun bloğunda gizli; gözleri itme çubuğuyla aşağı/yukarı eğer', {}),
    ('REF-BEARING-PAN', '6804-2RS boyun rulmanı: başın yükünü pan tabanına verir, servo yalnız tork verir', {}),
    ('REF-EYE-CAMERA', 'Göz kamerası ({s}): ESP32-CAM kartı arkada, OV2640 FPC ile önde, lens yuvada', LR),
    ('REF-SERVO-SHOULDER-R', 'DS3218MG 270° omuz servosu (gövde içinde): kolu parktan öne 225° çevirir', {}),
    ('REF-SERVO-TWIST-R', 'MG996R üst kol dönüş servosu: dirseği içe/dışa çevirir', {}),
    ('REF-SERVO-ELBOW-R', 'MG996R dirsek servosu', {}),
    ('REF-SERVO-WRIST-R', 'MG996R bilek eğim servosu', {}),
    ('REF-SERVO-ROLL-R', 'MG90S bilek dönüş servosu', {}),
    ('REF-SERVO-GRIPPER-R', 'MG90S pençe servosu', {}),
    ('REF-BEARING-SHOULDER', '6804-2RS omuz rulmanı ({s}): kolun yükünü yan duvara verir', LR),
    ('REF-BEARING-TWIST', '6704-2RS üst kol dönüş rulmanı', {}),
]
PAN = ('UGV-MECH-041', 'UGV-MECH-042', 'UGV-MECH-046', 'REF-SERVO-TILT', 'REF-TILT-ROD')
TILT = ('UGV-MECH-043', 'UGV-MECH-044', 'UGV-MECH-045', 'REF-EYE-CAMERA')
POSE_TR = {'stow': 'Park', 'lift': 'Kaldır', 'up': 'Yukarı', 'ready': 'Hazır', 'reach_mid': 'Öne',
           'reach_low': 'Yere', 'reach_center': 'Öne-orta', 'store': 'Depola'}


def note(name):
    prefix, text, sides = max(((p, t, s) for p, t, s in DESC if name.startswith(p)), key=lambda d: len(d[0]))
    return text.format(s=sides.get(name[len(prefix)+1:], ''))


def hex_color(rgb):
    return '#' + ''.join(f'{round(c*255):02x}' for c in rgb)


def build(template=ROOT/'tools/viewer_template.html'):  # the film (media/film) reuses the mesh export
    config = json.loads((ROOT/'config/vehicle.json').read_text())
    manifest = json.loads((ROOT/'cad/assembly/manifest.json').read_text())
    if manifest['parameters'] != config:
        raise ValueError('Regenerate CAD (cad/assembly/build_concept.py) before building the viewer')
    G = config['geometry']
    positions, indices, parts, zmax = bytearray(), bytearray(), [], 0.0
    filament = {'PETG': 0.0, 'TPU': 0.0}
    shapes = {}
    chain, stow = manifest['arm_chain'], G['arm']['poses_deg']['stow']
    for part in manifest['parts']:
        name = part['name']
        group = [key for key, _, prefixes in GROUPS if name.startswith(prefixes)]
        assert len(group) == 1, (name, group)
        shape = shapes[name] = cq.importers.importStep(str(ROOT/part['step'])).val()
        link = chain['links'].get(name)
        if link is not None:  # right arm: back from the stow pose to the zero pose (inverse FK, root first)
            for j in range(link + 1):
                o, d = chain['joints'][j]['origin'], chain['joints'][j]['axis']
                angle = chain['joints'][j]['sign'] * stow[j]
                if angle:
                    shape = shape.rotate(cq.Vector(*o), cq.Vector(*o) + cq.Vector(*d), -angle)
        verts, tris = shape.tessellate(TOL, ANG_TOL)
        assert len(verts) < 65536, name
        q = [round(c*10) for v in verts for c in v.toTuple()]
        assert max(map(abs, q)) < 32767, name
        bb = shape.BoundingBox()
        zmax = max(zmax, bb.zmax)
        entry = {'name': name, 'group': group[0], 'note': note(name), 'color': hex_color(part['color']),
                 'role': part['role'], 'link': link, 'size': [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
                 'v': [len(positions)//6, len(verts)], 'i': [len(indices)//2, 3*len(tris)]}
        if part['printable'] or name in CATALOG_G:
            _, printed, material = part_mass(ROOT, part)
            entry['material'], entry['grams'] = material, round(printed)
            if material in filament:
                filament[material] += printed
        if part['printable']:
            entry['stl'] = f'cad/assembly/generated/{name}.stl'
        positions += b''.join(int(c).to_bytes(2, 'little', signed=True) for c in q)
        indices += b''.join(i.to_bytes(2, 'little') for t in tris for i in t)
        parts.append(entry)

    nx, ny = G['neck_axis_xy_mm']
    meta = {
        'revision': config['revision'], 'parts': parts,
        'groups': [{'key': k, 'label': label} for k, label, _ in GROUPS],
        'stats': {'length': G['overall_length_mm'], 'width': G['overall_width_mm'], 'height': round(zmax, 1),
                  'count': len(parts), 'printed': sum('stl' in p for p in parts),
                  'mass_kg': round(sum(x['mass_kg'] for x in config['mass_budget']), 2),
                  'filament_g': {m: round(g) for m, g in filament.items()}},
        'motion': {'arm': {'joints': chain['joints'], 'limits': G['arm']['limits_deg'], 'poses': G['arm']['poses_deg'],
                           'edges': G['arm']['pose_edges'], 'names': POSE_TR},
                   'pan': {'parts': PAN + TILT, 'pivot': [nx, ny, 0], 'min': -90, 'max': 90},
                   'tilt': {'parts': TILT, 'pivot': [nx, ny, G['tilt_axis_z_mm']], 'min': -30, 'max': 60}},
    }
    mesh = base64.b64encode(bytes(positions) + bytes(indices)).decode()
    page = (Path(template).read_text()
            .replace('__META__', json.dumps(meta, ensure_ascii=False, separators=(',', ':')))
            .replace('__MESH__', mesh))
    return page, meta


if __name__ == '__main__':
    page, meta = build()
    head = ('<!doctype html>\n<html lang="tr">\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')
    out = ROOT/'docs/renders/UGV-01-A3-viewer.html'
    out.write_text(head + page)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(page)
    tris = sum(p['i'][1] for p in meta['parts'])//3
    print(f"{out.relative_to(ROOT)}: {meta['stats']['count']} parts, {tris} triangles, {len(page)//1024} KiB")
