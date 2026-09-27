# A3 baskıya hazır mekanik (M2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Konsept CAD'i (61 katı, çakışmasız) montajlanabilir baskı dosyalarına çevirmek: vida/insert/somun yerleri, iç tutucular, kamera/servo arayüzleri, kablo geçişleri ve baskı yönleri. Parçalar alınmadan önce yapılabilen mekanik işin tamamı.

**Architecture:** Her şey `cad/assembly/build_concept.py` + `config/vehicle.json` içinde parametrik kalır; her adım `tests/check_cad.py`'ye geometrik kontrol ekler (delik boşluğu, parça ayrımı, kesişme yok, zarf içinde). Bağlantı standardı config'te: M3 ısıl insert Ø4,0×6 mm delik, M3 geçiş Ø3,4, M3 somun yuvası 5,7 AF × 2,8 mm, M4 geçiş Ø4,5. Satın alınan parçaların ölçüleri satıcı çiziminden; parçalar gelince doğrulanır.

**Commit:** Yok (kullanıcı kuralı). Fiziksel baskı/deneme NOT_RUN.

---

### Task 1: Tahrik baskı arayüzleri
- [x] Test önce: motor kelepçesi yuva + kapak olarak eksende bölünmüş; iki M3 cıvata ekseni kapak, yuva ve taban plakasında boş; göbek deliği D biçimli (düzlük 3,5 mm), M3 sıkma vidası deliği D düzlüğüne dik iner ve somun yuvası motor tarafından açılır; lastiği döndürmeyen 8 kanatçık. → FAIL.
- [x] `build_concept.py`: kelepçe 40×30 mm, `UGV-MECH-003-xx` yuva + `UGV-MECH-004-xx` kapak; göbek D deliği, set vidası, somun yuvası, kanatçıklar; kütle/görüntüleyici grupları. → PASS.

### Task 2: Gövde bağlantıları ve boyun yük yolu
- [x] Kapak bosları M3 insert (Ø4,0×6); flanş/kule/pan tabanı vida yerleri; boynun yükünü yan duvarlara taşıyan kapak altı köprü (elektronik zarfına değmez).

### Task 3: İç düzen
- [x] Batarya beşiği (kayış yuvaları), elektronik tepsisi (delikli pertinaks + ayaklar), dört balast direnci için havalandırmalı tutucu, kablo geçişleri (flanş, omuz kulesi, ToF, ışık şeridi).

> **25.09.2026:** Gövde ve kol M3'te değişti ([M3 planı](2026-09-25-m3-character-body-arm.md)). Task 4–5 M3 geometrisine göre yapılır: omuz kulesi/dişli yok. Omuz servosu gövde içinde çerçevede; kol çatalları 624ZZ + M4 idler kullanır.

### Task 4: Baş ve omuz arayüzleri
- [x] (M3, DD78) Göz kabuğu kapağı, ESP32-CAM tırnakları ve lens yuvası; omuz mili korna flanşı ve kablo çıkışı; çamurluk, omuz çerçevesi ve kargo vidaları. Dişli omuz M3'te kalktı.
- [ ] Bekliyor: pan/tilt MG90S yuvaları ve boyun kaplini; kol uzuvlarının servo tutma, korna ve idler ayrıntıları (DD78 seçenekleri).

### Task 5: Baskı yönü ve rehber
- [x] (DD79) STL'ler baskı yönünde (`tools/print_plan.py`); `docs/print_guide_A3.md`: yön, destek, dolgu, malzeme, sıra, deneme parçaları, vida/insert/rulman listesi; `tests/check_print_plan.py`; bütün testler PASS. Bekleyen 13 parça, Task 4 kalanı çizilince plana eklenir.
