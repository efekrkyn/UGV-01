# A3 Lite mekanik (L1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Onaylanan [A3 Lite spec'ine](../specs/2026-09-24-a3-lite-budget-design.md) göre config, hesap, CAD, kütle taraması ve testleri A3'e taşımak; A2'yi arşivlemek.

**Architecture:** Tek kaynak yine `config/vehicle.json` (revision A3). `tools/calculations.py` ve `cad/assembly/build_concept.py` parametrik kalır; A2'ye özgü sabitler config'e taşınır veya silinir. Üst gövde, baş ve kollar korunur; alt yük yolu baskı PETG plaka (iki parça, x=−35 ekinde, ek yerini üstten geçen iki baskı kiriş bağlar), JGA25 motor yuvaları, baskı göbek + TPU lastik tekerler, 3S batarya ve elektronik tepsisi zarfları, E-stop ve ön tampon ToF pencereleri eklenir. Göz kabukları ESP32-CAM kartı sığsın diye 48 mm'ye uzar.

**Tech Stack:** CadQuery 2.6.1 (`.venv`), Python 3.

**Motor verisi:** JGA25-370 12 V: Seeed çizimi (dişli kutusu Ø25×21, motor Ø24,4×30,8, Ø4 D-mil 11,5 mm, 17 mm aralıklı 2×M3); 130 dev/dk sürümü için satıcı verisi boşta 0,07 A, anma 0,9 kg·cm / 0,3 A, stall 4,4 kg·cm / 1,8 A; enkoder 11 PPR, redüksiyon ≈1:45 (**gelen partide doğrulanacak**).

**Commit:** Yok (kullanıcı kuralı).

**Durum (24.09.2026):** Tamamlandı ([DD66](../../design_decisions.md)). Sapma: azami hız 3S geriliminde 0,6 m/s alındı, KE 1,28 yerine 0,72 J.

---

### Task 1: A2 arşivi
- [x] `docs/revisions/A2/` altına `vehicle.json`, `manifest.json`, `UGV-01-A2-concept.step`, `concept_preview.png` kopyala; README yaz.
- [x] Arşiv tahrik araçları (`tools/drivetrain_budget.py`, `tests/check_drivetrain.py`) A2 arşiv config'ini okusun. `check_drivetrain.py` → PASS.

### Task 2: Config ve hesap (A3)
- [x] Test önce (`tests/check_design.py`): batarya 32,4 Wh; yaşlanmalı 20,9304 Wh; tipik çalışma ≥1 saat; düz yuvarlanma 1,176798 N; 5° eğimde motor torku 0,1087 N·m ve akım 0,506 A (≤ 0,6 A kısa süreli tavan); enkoder 1.980 sayım/tur; KE 1,28 J; boş kütle ≤3,5 kg; yüklü CG ≤108 mm. → FAIL.
- [x] `config/vehicle.json` A3 (motor, batarya, hareket, kütle bütçesi, yeni geometri anahtarları; A2'ye özgü CM5/batarya zarfları silinir). `tools/calculations.py`: A2 sabitleri (bulk kondansatör, alüminyum plaka yoğunluğu, 15°/1,3 A etiketleri) config'ten. → PASS.

### Task 3: CAD (A3)
- [x] Test önce (`tests/check_cad.py`): A3 parçaları (plaka yarıları, 4 motor yuvası, 4 göbek, 4 lastik, E-stop, 2 ToF, batarya, elektronik) var; CM5/PWR/MCU zarfları yok; izinsiz çakışma yok; bütün baskı parçaları ≤240 mm; göz kamerası zarfı ≥26×27×40,5 mm; motor mili teker göbeğine ≥7 mm girer; E-stop kapak üstünde erişilebilir; ToF pencereleri açık; baş ≤300 mm; kol pozları ve URDF. → FAIL.
- [x] `build_concept.py` A3 değişiklikleri; `build → check_cad` → PASS.

### Task 4: Kütle, filament, önizleme, belgeler
- [x] `tools/body_mass_screen.py` A3 grupları (PETG 1,27, TPU 1,21 g/cm³) ve filament toplamı; `tests/check_body_mass.py` → PASS.
- [x] Önizleme, `docs/lite_mechanical_A3.md`, `mass_budget.md`, spec'te filament tahminini CAD'le güncelle, README, DD66, faz kaydı; bütün testler → PASS.
