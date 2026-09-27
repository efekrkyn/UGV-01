# UGV-01 A2 karakter revizyonu — baş, kollar, ışık şeridi

24.09.2026 · PH4 kavram revizyonu. **A3 Lite (DD66):** göz kabukları ESP32-CAM için 48 mm yüksekliğe çıktı, omuz servosu MG996R oldu; alt yük yolu ve elektronik için [Lite mekanik](lite_mechanical_A3.md). Bu belge; [A1](exterior_language_A1.md) biçim sınırlarının yerini alır. [CAD önizlemesi](../cad/assembly/concept_preview.png) gerçek STEP katılarından çizilir; **üretim dosyası değildir**, baskı ve fiziksel test yapılmadı.

Kullanıcı yönü (DD61): tekerler kalır; gövde ve baş sevimli animasyon robotlarından **ilham alan özgün** bir robot. Başka bir karakterin adı, logosu, renk düzeni veya birebir oranı kullanılmaz; karakteri boyunlu iki "kamera göz", kaşlı göz kabukları, gövdeye katlanan kollar ve ön ışık şeridi taşır. Sarı bölmeli ASA gövde ve koyu TPU tamponlar A1'den korunur.

| Bölge | A2 biçim kararı | Parça / tahsis | Mühendislik sınırı |
|---|---|---|---|
| Boyun | 50×50 mm flanşa oturan pan tabanı, rulman, Ø18 boyun | UGV-MECH-040/041, REF-SERVO-PAN (MG90S), REF-BEARING-PAN (Ø32/Ø20×7) | Pan ±90°; eksen (30,0), pan eklemi z186. Rulman tutucu, servo kornası ve boyundan geçen kablo burulması modellenmedi. |
| Baş | Tilt köprüsü + iki yuvarlatılmış göz kabuğu, üstte içe 8° eğik kaş | UGV-MECH-042, UGV-MECH-043-±1, REF-SERVO-TILT (MG90S) | Tilt ekseni z268; eğim −60° (aşağı) … +30° (yukarı). Göz kabuğu 40×42×40 mm, 2,5 mm duvar, Ø14 lens deliği. |
| Göz kameraları | Her göz kabuğunda bir Camera Module 3 Standard | REF-EYE-CAMERA-±1, merkez y±30,5 (61 mm taban) | 11,5×25×24 mm tahsis; M2 montaj, lens penceresi, FFC yolu ve stereo kalibrasyon açık. Bağlantı: [A2 elektronik](a2_electronics.md). |
| Sağ kol (işlevsel) | Omuz kulesinden çıkan tek bağlantı + iki parmaklı pençe | UGV-MECH-050--1, UGV-MECH-051--1, REF-SERVO-SHOULDER-R (DS3218MG), REF-SERVO-GRIPPER-R (MG90S) | Pivot (138,−106,176); kol 200 mm. Park 180° (gövde üst kenarı boyunca geriye), çalışma −55°. ≤150 g yük. |
| Sol kol (pasif) | Aynı kabuk, sürtünmeli eklem, servo yuvası boş | UGV-MECH-050-+1, UGV-MECH-051-+1 | Simetri ve karakter için; tahrik yok, URDF'de sabit. |
| Işık şeridi | Ön duvarda yatay durum şeridi, A1 kamera açıklığının yerine | REF-LIGHT-BAR, pencere 8×120×6 mm, z128 | Üst duvar ligamenti ≥5 mm. 8 adreslenebilir LED, 74AHCT1G125 veri tamponu, PTC'li besleme: [A2 elektronik](a2_electronics.md). |
| Kapak | Ön kapakta iki köşe çentiği (47×25 mm) | UGV-MECH-013-3 | Omuz kuleleri kapağa değmeden gövdeye iner; kule-şasi yük yolu açık. |

## Kontrol edilen geometri

`.venv/bin/python cad/assembly/build_concept.py && .venv/bin/python tests/check_cad.py` → **PASS**, 46 geçerli STEP katısı, izinsiz çakışma yok.

- **Dış zarf:** Park pozunda bütün katılar 330×270 mm içinde. Baş tepesi (kaş) **z292,8 mm**; üst sınır 300 mm.
- **Park kolu:** x−62…148, z159…193; kapak üstüyle (z146) 13 mm boşluk, kuleyle 1 mm yanal boşluk (|y| 101…111).
- **Çalışma pozu (−55°):** Pençe ucu **x263,4 mm** (ön zarftan 98 mm ileride), en alt **z4,7 mm**; ön teker ve tamponla çakışma yok.
- **Kol süpürmesi:** 180° → −55° hareket **üstten** (90°'den) geçer. 5° adımla 48 açıda çakışma yok. Arka/alttan dönüş zemine ve tekerlere çarpar; MCU yazılımı eklem aralığını [−55°, 180°] ile sınırlamalı ve her komutta bu yolu izlemelidir. 5° örnekleme sürekli süpürme kanıtı değildir.
- **Güç kesilirse (park):** Servo rayı kapanınca sağ kol 1° adımlı CAD taramasında **≈5° düşüp orta kapağa (UGV-MECH-013-2) oturur**; lastiğe ulaşmaz. Pençe gövdesi bu yüzden gövdeye doğru 4 mm genişletildi (kapak üstünde 6 mm taşıma). Kapak sökülmeden önce kol kaldırılır.
- **URDF:** `head_pan` (z ekseni) → `head_tilt` (y ekseni) zinciri, sabit iki göz kamerası, `right_shoulder` (y ekseni, sınırlar config'ten), sabit `left_arm`. Düz kavram ağacıdır; kinematik sürüm değildir.

## Kütle ve CG

`.venv/bin/python tools/body_mass_screen.py` (test: `tests/check_body_mass.py`). Baskı parçaları %100 dolu ASA (1,05 g/cm³), rulman dolu çelik halka (7,85 g/cm³, üst sınır). Servo ve kamera değerleri katalog kütlesidir: MG90S 13,4 g ×3, DS3218MG 60 g, Camera Module 3 4 g ×2. **Vida, korna ve kablolar dahil değildir**; kalan marja sığmalıdır.

| Grup | CAD taraması | Tahsis | Marj |
|---|---:|---:|---:|
| Baş, boyun, pan/tilt servo, iki kamera (10 kalem) | 195,4 g | 300 g | 104,6 g |
| Kollar, kuleler, omuz + pençe servosu (6 kalem) | 186,9 g | 235 g | 48,1 g |
| Gövde paneli/kapak/tampon (13 parça, A2 çentikli) | 730,5 g | 700 g | **−30,5 g** |

Hesap ([sonuçlar](calculation_results.md)): boş **6,235 kg** (sınır 6,25), CG x−2,35 / z86,67 mm. Faydalı yük, kullanıcının "≈1,5 kg" kararına göre **1,5 kg** (CG z190 mm). Yüklü CG **z106,7 mm** olur; 110 mm sınırına 3,3 mm pay kalır. Bu pay 1,75 kg'da 0,7 mm'ye iner. Yük CG'si z200 mm'de olursa 108,6 mm çıkar. Brüt 8 kg'a 0,25 kg hesap payı kalır; bu pay **ölçülmüş değildir**.

**Omuz statik torku:** Kol yatayken 150 g yük 200 mm uçta, kol kabuğu ≈37 g ve pençe servosu 13,4 g ile toplam ≈0,35 N·m (3,6 kg·cm). DS3218MG satıcı verisi ≈19 kg·cm (5 V, doğrulanmadı), yaklaşık 5× pay. Dinamik yük, dişli boşluğu ve servo ısınması ölçülmedi.

## Açık işler (A2 üretim onayı yok)

1. Servo kornası, mil ve rulman tutucusu; boyundan geçen iki FFC ile servo kablolarının ±90° pan burulması.
2. Omuz kulesinden metal şasiye yük yolu; kule, kapak çentiğinden gövde içine inmelidir.
3. Pençe parmak kinematiği ve ped malzemesi; ≤150 g tutma testi.
4. Göz lens penceresi, kamera M2 montajı, stereo kalibrasyon ve toz yolu.
5. Gövde paneli 30,5 g aşımı (R41) ve bütün araç tartımı.
6. Kıstırma riski: kol ve boyun hareketinde parmak sıkışması. Servo rayının E-stop ile kesilmesi ve AI modunda hız sınırı alt proje 3/4'te tasarlanır (R47).
7. Baskı yönü, slicer doluluğu, gerçek parça kütlesi. Baskı yazıcı gelince yapılacak; T01–T20 **NOT_RUN**.
