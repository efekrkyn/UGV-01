# M3 karakter gövdesi ve 5 eksenli kol: uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [M3 spec](../specs/2026-09-25-m3-character-body-arm-design.md)'ini uygulamak:
- gövde 236 mm genişliğe ve z210 yüksekliğe büyür, motorlar gövdenin içine girer;
- baş ile gövde arasındaki 122 mm korunur;
- çamurluklar eklenir;
- kol yandan çıkar, 5 eksen + pençe olur;
- kargo bölmesi eklenir;
- elektronik, firmware ve yazılım bu değişikliklere uyarlanır.

**Architecture:**
- Parametreler `config/vehicle.json` içinde kalır.
- Kol kinematiği `build_concept.py` içindedir: katılar sıfır duruşta çizilir, sonra eklem eksenleri çevresinde uçtan köke doğru döndürülür.
- Duruşlar ve duruş grafiği config'tedir. CAD, `executor.py` ve `vehicle.py` aynı tabloyu okur.
- Her adımda önce test yazılır ve FAIL verdiği görülür; sonra uygulanır ve PASS alınır.

**Commit:** Yok (kullanıcı kuralı). Fiziksel test NOT_RUN. M2 Task 4–5 (baş ve omuz arayüzleri, baskı rehberi) sonra bu gövdeye göre yapılır.

---

### Task 1: Gövde, tahrik, baş, çamurluk
- [x] Test yazılır → FAIL:
  - gövde 236 mm genişlik, üst z210;
  - motor yüzü \|y\| ≤ duvar iç yüzü;
  - göbek boynu Ø18 delikten geçer;
  - mil göbeğe ≥7 mm girer;
  - set vidası 6 mm'lik aralıkta;
  - çamurluk tekerleğin üstünü örter, tekerleğe değmez;
  - eğim ekseni − gövde üstü = 122 mm;
  - omuz kuleleri kaldırılmış.
- [x] Config + CAD → PASS

### Task 2: Kol
- [x] Test yazılır → FAIL:
  - sağ kolda 5 servo zarfı + 2 rulman;
  - J1 servosu gövdenin içinde;
  - bütün duruşlar ve grafik kenarları çakışmasız;
  - gevşek kol ≤3° içinde çamurluğa oturur;
  - her eklemde tork payı ≥1,5;
  - sol kol pasif ve dış ölçüleri sağ kolla aynı.
- [x] CAD kinematiği + duruş grafiği + URDF → PASS

### Task 3: Kargo bölmesi
- [x] Test yazılır → FAIL:
  - ön kapakta atma ağzı var, altında kutu;
  - ağızdan kutu tabanına düşüş yolu açık;
  - "depola" duruşunda kavrama merkezi ağzın üstünde.
- [x] CAD → PASS

### Task 4: Kütle, CG, tahrik
- [x] Güncellenir → PASS:
  - kütle taraması grupları ve kütle bütçesi;
  - `calculations.py` ve `check_design.py` sınırları;
  - makara sayısı.

### Task 5: Elektronik
- [x] Güncellenir → PASS:
  - pin haritası (PCA9685, SERVO_OE);
  - bağlantı şeması (iki servo rayı, 15 A sigorta);
  - BOM ≤13.500 TL.

### Task 6: Firmware ve yazılım
- [x] Güncellenir → C ve Python testleri PASS:
  - 8 servo;
  - 0x122/0x123 çerçeveleri;
  - duruş grafiği yürüyüşü;
  - yürütücü ve AI araç açıklamaları.

### Task 7: Belgeler ve görüntüleyici
- [x] Belgeler: DD72–DD75, lite belgeleri, hesap raporu, README, test planı.
- [x] Görüntüleyiciye duruş seçici eklenir ve yayımlanır.
- [x] Bütün testler PASS.
