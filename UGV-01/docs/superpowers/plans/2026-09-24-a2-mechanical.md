# UGV-01 A2 Mekanik Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A1 kavram CAD'ini A2'ye taşımak: ön kamera podu yerine durum ışık şeridi, boyunlu iki göz kameralı pan/tilt baş, sağ işlevsel/sol pasif kol; kütle/CG bütçesi ve testleriyle.

**Architecture:** Tek kaynak `config/vehicle.json` (geometri + kütle bütçesi) → `tools/calculations.py` (kütle/CG, yüklü CG yeni metrik) ve `cad/assembly/build_concept.py` (CadQuery katıları, manifest, URDF). A1 çıktıları `docs/revisions/A1/` arşivine alınır. Testler önce güncellenir ([spec](../specs/2026-09-24-a2-character-ai-design.md) §2).

**Tech Stack:** Python 3, CadQuery 2.6.1 (`.venv`), matplotlib (önizleme), stdlib.

**Commit:** Kullanıcı git/paylaşımı proje sonuna bıraktı; commit yok, test kanıtı kaydedilir.

**Koordinatlar:** mm; x ileri, y sol, z yukarı. Sağ kol = −y. Mevcut flanş `UGV-MECH-030` (x 5…55, y ±25, z 146…152). Ön kapak `UGV-MECH-013-3` x 50,25…149,75, z 143…146. CM5 zarfı z ≤121.

**Durum (24.09.2026):** Tamamlandı. Uygulamadaki sapmalar (park 180°, çalışma −55°, yük 1,5 kg, kol süpürme denetimi) [DD62](../../design_decisions.md) içinde.

---

## Dosya yapısı

- Modify `config/vehicle.json` — ön kamera anahtarları çıkar; ışık şeridi, baş, kol parametreleri; kütle bütçesi A2; `payload_cg_z_mm`.
- Modify `tools/calculations.py` — `loaded_cg_z_mm` metriği.
- Modify `tests/check_design.py` — A2 kütle/CG beklentileri.
- Modify `cad/assembly/build_concept.py` — A2 katıları, çalışma pozu kontrolü, manifest, URDF.
- Modify `tests/check_cad.py` — A2 parçaları, zarf, yükseklik, çalışma pozu, URDF.
- Modify `tools/render_concept.py` — A2 başlıkları.
- Create `docs/revisions/A1/` arşivi, `docs/exterior_language_A2.md`.
- Modify `docs/mass_budget.md`, `docs/front_camera_A1.md` (başa "A2'de kaldırıldı"), `docs/exterior_language_A1.md` (başa "A2 ile değiştirildi"), `docs/risk_register.md` (R40 kapandı), `README.md`, `cad/assembly/README.md`, `docs/design_decisions.md`, `docs/phase_reviews.md`.

### Task 1: A1 arşivi

- [x] **Step 1:** `mkdir -p docs/revisions/A1 && cp cad/assembly/generated/UGV-01-A1-concept.step cad/assembly/manifest.json cad/assembly/concept_preview.png docs/revisions/A1/` ve `docs/revisions/A1/README.md` içine: "A1 kavram montajı 24.09.2026 arşivi; A2 tarafından değiştirildi; üretim dosyası değildir."
- [x] **Step 2:** `python3 tests/check_markdown_links.py` → PASS.

### Task 2: A2 konfigürasyonu, kütle ve yüklü CG

**Files:** `tests/check_design.py`, `tools/calculations.py`, `config/vehicle.json`

- [x] **Step 1: Testi A2'ye göre değiştir (önce başarısız olmalı)** — `tests/check_design.py` içindeki iki kütle satırını şununla değiştir:

```python
assert math.isclose(r['curb_mass_kg'], 6.235), r
assert 86 < r['curb_cg_z_mm'] < 88, r
assert r['loaded_cg_z_mm'] <= p['motion']['loaded_cg_max_z_mm'], r
assert p['motion']['curb_mass_limit_kg'] + p['motion']['payload_kg'] <= p['motion']['gross_mass_kg'], p['motion']
```

Run: `python3 tests/check_design.py` → Expected: FAIL (`curb_mass_kg` 6.0).

- [x] **Step 2: `tools/calculations.py`** — dönüş sözlüğüne ekle:

```python
        'loaded_cg_z_mm': (sum(x['mass_kg']*x['z_mm'] for x in budget)
                           + motion['payload_kg']*motion['payload_cg_z_mm'])
                          / (curb + motion['payload_kg']),
```

- [x] **Step 3: `config/vehicle.json`** —
  - `mass_budget`: `"RGB camera and future mast mass allocation"` → `"A2 head neck pan tilt servos and two eye cameras"`, 0,30 kg, `x_mm` 35, `z_mm` 235; yeni satır `"A2 arms right functional left passive shoulder towers"` 0,235 kg, `x_mm` 140, `z_mm` 175.
  - `motion`: `curb_mass_limit_kg` 6,25; `payload_kg` 1,75; yeni `payload_cg_z_mm` 190.
  - `geometry`: `front_camera_opening_mm`, `front_camera_envelope_mm`, `front_camera_center_mm`, `front_camera_opening_center_z_mm` sil; ekle `light_bar_opening_mm` [8, 120, 6], `light_bar_center_z_mm` 128, `neck_axis_xy_mm` [30, 0], `tilt_axis_z_mm` 268, `eye_center_y_mm` 30,5, `eye_pod_mm` [40, 42, 40], `shoulder_pivot_mm` [138, 106, 176], `arm_length_mm` 200, `arm_stow_deg` 150, `arm_work_deg` -60.
- [x] **Step 4:** `python3 tools/calculations.py && python3 tests/check_design.py` → PASS; `loaded_cg_z_mm` ≈109,3 raporda.

### Task 3: A2 CAD

**Files:** `tests/check_cad.py`, `cad/assembly/build_concept.py`

- [x] **Step 1: `tests/check_cad.py`** — ön kamera kontrollerini (satır 22–32, 37–38) kaldır; şunları ekle:

```python
required = {'UGV-MECH-040', 'UGV-MECH-041', 'UGV-MECH-042', 'UGV-MECH-043--1', 'UGV-MECH-043-+1',
            'UGV-MECH-050--1', 'UGV-MECH-050-+1', 'UGV-MECH-051--1', 'UGV-MECH-051-+1',
            'REF-SERVO-PAN', 'REF-SERVO-TILT', 'REF-SERVO-SHOULDER-R', 'REF-SERVO-GRIPPER-R',
            'REF-EYE-CAMERA--1', 'REF-EYE-CAMERA-+1', 'REF-LIGHT-BAR', 'REF-BEARING-PAN'}
assert required <= names, required - names
assert 'REF-FRONT-CAMERA' not in names
bounds = [cq.importers.importStep(str(ROOT/part['step'])).val().BoundingBox() for part in m['parts']]
assert max(b.xmax for b in bounds) <= g['overall_length_mm']/2 and min(b.xmin for b in bounds) >= -g['overall_length_mm']/2
assert max(b.ymax for b in bounds) <= g['overall_width_mm']/2 and min(b.ymin for b in bounds) >= -g['overall_width_mm']/2
assert max(b.zmax for b in bounds) <= 300, 'A2 head height'
work = m['arm_working_pose']
assert not work['intersections'], work
assert work['xmax_mm'] >= g['overall_length_mm']/2 + 50 and 0 <= work['zmin_mm'] <= 20, work
front_wall = cq.importers.importStep(str(ROOT/'cad/assembly/generated/UGV-MECH-022-+1.step')).val()
window = cq.Workplane('XY').box(*g['light_bar_opening_mm']).translate((g['body_length_mm']/2, 0, g['light_bar_center_z_mm'])).val()
assert front_wall.intersect(window).Volume() < 0.01, 'light bar window blocked'
for joint, xyz in (('head_pan_joint', [30, 0, 186]), ('head_tilt_joint', [30, 0, 268]),
                   ('right_shoulder_joint', [138, -106, 176])):
    got = [float(v)*1000 for v in urdf.find(f"joint[@name='{joint}']").find('origin').attrib['xyz'].split()]
    assert all(math.isclose(a, b, abs_tol=1e-6) for a, b in zip(got, xyz)), (joint, got)
```

Run: `.venv/bin/python tests/check_cad.py` → Expected: FAIL (parametre/parça yok).

- [x] **Step 2: `build_concept.py` — ışık şeridi**: ön uç duvarda kamera açıklığı yerine `box(light_bar_opening_mm, (body_length/2, 0, light_bar_center_z))` kesimi; `add('REF-LIGHT-BAR', box((4,124,10),(143.5,0,128)), ..., role='reserved_envelope')`; `REF-FRONT-CAMERA` satırını sil.
- [x] **Step 3: ön kapak köşe çentikleri**: `UGV-MECH-013-3` için `x 103,5…150`, `|y| 75,5…100` kutuları kes (omuz kuleleri buraya oturur).
- [x] **Step 4: boyun ve baş** (hepsi `neck_axis_xy` = (30,0)):
  - `UGV-MECH-040` pan tabanı: r24, z152…186 silindir − cep kutusu (24,14,31) merkez (30,0,170,5); `REF-SERVO-PAN` kutu (22,8,12,2,28,5) merkez (30,0,169,25).
  - `REF-BEARING-PAN`: r16−r10 halka, z186…193.
  - `UGV-MECH-041` boyun: r9 silindir z186…248.
  - `UGV-MECH-042` köprü: kutu (34,18,40) merkez (30,0,268) − cep (24,14,30); `REF-SERVO-TILT` (22,8,12,2,28,5) merkez (30,0,268).
  - `UGV-MECH-043-±1` göz podu: dış kutu (40,42,40) merkez (40,±30,5,268), x-kenarları r8 yuvarlatılmış, 2,5 mm kabuk (iç kutu çıkarılır), önde r7 lens deliği, üstte (36,40,3) kaş plakası ±8° roll ile dışa-aşağı eğik ve poda 1 mm gömülü (tek katı). `REF-EYE-CAMERA-±1` (11,5,25,24) merkez (51,25,±30,5,268).
- [x] **Step 5: kollar** (omuz `shoulder_pivot` = (138, ±106, 176)):
  - `UGV-MECH-050-±1` kule: dış kutu x104…150, |y| 76…100, z143…192 − cep x106…148, |y| 77,5…98,5, z145…190. Sağda `REF-SERVO-SHOULDER-R` (40,20,40,5) merkez (127,−88,167,25).
  - Kol yerel çerçevesi (x' kol ekseni, y' kalınlık, z' genişlik): bağlantı x'10…140 (10×16), pençe gövdesi x'140…172 (14×26) − servo cebi (sağda), iki parmak x'172…200 (5 kalın, 16 aralık). Katı, y ekseni etrafında `arm_stow_deg` döndürülüp pivota taşınır → `UGV-MECH-051-±1` (|y| 101…111). Sağda `REF-SERVO-GRIPPER-R` aynı dönüşümle.
  - Çalışma pozu: sağ kol katısı `arm_work_deg` açısıyla ayrı üretilir, `UGV-MECH-051--1-working.step` olarak dışa aktarılır, kendisi hariç tüm parçalarla kesişim hacmi ve bbox `manifest['arm_working_pose']`'a yazılır (montaja eklenmez).
- [x] **Step 6: manifest ve URDF**: montaj adı `UGV-01_A2_CONCEPT_NOT_FOR_MANUFACTURE`, STEP `UGV-01-A2-concept.step`; `not_modelled` listesine servo kablo/rulman tutucu, omuz yük yolu, pençe kinematiği. URDF: `camera` bağlantısı yerine `head_pan` (revolute, z ekseni, (30,0,186)), `head_tilt` (revolute, y, (30,0,268)), `left_eye_camera`/`right_eye_camera` sabit, `right_shoulder` (revolute, y, (138,−106,176)), `left_arm` sabit.
- [x] **Step 7:** `.venv/bin/python cad/assembly/build_concept.py && .venv/bin/python tests/check_cad.py` → Expected: PASS, "Unapproved intersections: []".

### Task 4: Kütle taraması, önizleme, belgeler

- [x] **Step 1:** `.venv/bin/python tests/check_body_mass.py` → gövde taraması değişmediyse PASS; yeni baskı parçalarının (040–043, 050, 051) katı hacmi × ASA 1,05 g/cm³ + katalog servo/kamera kütleleri (MG90S 13,4 g ×3, DS3218MG 60 g, Camera Module 3 4 g ×2) baş ≤0,30 kg ve kollar ≤0,235 kg tahsisleriyle karşılaştırılıp `docs/exterior_language_A2.md`'ye yazılır (komut ve sonuç).
- [x] **Step 2:** `.venv/bin/python tools/render_concept.py` (başlıklar A2) → `cad/assembly/concept_preview.png`; görsel olarak kontrol.
- [x] **Step 3:** Belgeler: `docs/exterior_language_A2.md` (biçim kararları, ölçüler, kütle/CG, eğim −60…+30°, açık işler), A1 belgelerine yönlendirme notu, `mass_budget.md` satırları, R40 kapandı, README/cad README, DD62, faz kaydı.
- [x] **Step 4: Doğrulama:** tüm test listesi (`tests/README.md`) + iki C testi → PASS.
