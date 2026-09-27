# M3 baş: tilt servosu boyna gizlenir (DD83): uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** DD82'de gözlerin arasında görünen tilt servosunu kaldırmak. Kullanıcı: "orda niye servo var çok çirkin duruyor"; seçeneklerden "Boyuna gizle" seçildi.

**Tasarım:**
- Göz merkezleri ±39 → ±30,5 mm'ye döner (stereo taban 61 mm). Tilt ekseni göz merkezinde (z332), gözler boyun eksenine ortalı.
- **Boyun alt parçası (041):** 6804'teki Ø20 mil, omuz ve rulmanın hemen üstünde servo bloğu (x 3–47, y −28…10, z 261–287). Blok pan ile döner.
  - Tilt MG90S, mili +y yönünde (z274).
  - Kulakları bir servo plakasına (046) 2 × M2 ile bağlanır; plaka bloğun yan duvarlarındaki oluklara üstten kayar.
  - Bloğun arkasında kablo penceresi var.
- **Sütun ve bıçak (042):**
  - Bloğun üstünü kapatan kapak, üzerinde 19 × 15 mm'lik sütun (tepe z299, gözlerin en alçak noktasının altında).
  - Sütundan gözlerin arasına 6 mm'lik bıçak çıkar; bıçağın tepesinde aks göbeği (r8) var.
  - Sütunun içinde itme çubuğu kanalı ve kablo kanalı var.
  - Kapak, bloğa 4 × M2 ile bağlanır.
- **Aks (045):**
  - Bıçak göbeğinde dönen Ø9 aks; uçları AF7 altıgen olup gözlerin iç duvarlarına geçer.
  - M4 cıvata iki gözü akse sıkar; böylece gözler birbirine rijit bağlıdır.
- **İtme çubuğu:**
  - Ø1,5 mm çelik, iki ucu Z büküm.
  - Servo kornasında ve sol gözün iç duvarındaki krank piminde 8 mm yarıçapta, düzlem y 6,5.
  - Paralelkenar: göz, servo ile birebir aynı açıda döner.
- **Kaşlar:** göz başına eğik kaşlar geri gelir; kaş çubuğu kalkar.

**Commit:** Yok. Fiziksel test NOT_RUN.

### Task 1: Config ve testler (kırmızı)
- [x] `eye_center_y_mm` 30,5. `geometry.head`'den kalkanlar: `neck_flange_z_mm`, `brow_z_mm`. Eklenenler: `housing_z_mm`, `tilt_servo_z_mm`, `tilt_crank_r_mm`, `rod_y_mm`, `column_top_z_mm`, `axle_d_mm`.
- [x] `check_cad.py` baş testleri:
  - servo plakasında kulak pilotları;
  - sütunda çubuk kanalı (bütün tilt yolu boyunca boş);
  - gözlerde altıgen aks delikleri;
  - sol gözde krank pimi deliği ve çevresindeki et;
  - blok kablo penceresi;
  - tilt taraması: kesişim yok, açıklık ≥1,5 mm.

### Task 2: CAD (yeşil)

### Task 3: Baskı planı, kütle, BOM (itme çubuğu), görüntüleyici, DD83; bütün testler PASS
