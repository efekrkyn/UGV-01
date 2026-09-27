# M3 baş mekanizması (M2 Task 4'ün son işi): uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bekleyen üç baş parçasını (040 pan tabanı, 041 boyun, 042 tilt köprüsü) baskıya hazır hale getirmek. Kullanıcı DD80/DD81'i onayladı ve "sen devam et" dedi.

**Sorun:** Tilt MG90S'in mil üstüne kadar yüksekliği 31 mm; iki göz kabuğunun arası ise 19 mm. Servo tilt ekseninde iki gözün arasına sığmıyor.

**Karar:** doğrudan tahrik. İtme çubuğu seçeneği ek parça ve boşluk getiriyordu; bu yüzden gözler ayrıldı.
- Göz merkezi ±30,5 → ±39 mm (stereo taban 61 → 78 mm). Gözler boyun eksenine ortalandı (önceki +10 mm öne kaydırma kalktı); kamera yüksekliği z332 (gövdeden 122 mm) aynı.
- **Tilt:**
  - Servo köprüde; mili +y yönünde, tilt ekseninde. Kulakları köprünün yüzüne 2 × M2 ile bağlanır.
  - Sol göz kabuğunun iç duvarı servo kornasına 2 × M2 ile bağlanır; kornanın merkez vidası için Ø5 delik var.
  - Sağ göz, köprünün Ø8 saplamasında burçla döner.
  - İki göz, yeni kaş çubuğu (045) ile üstten rijit bağlanır; bu çubuk göz başına ayrı kaşların yerini alır. Çubuk tilt ekseninden ≥24 mm uzakta olduğundan, −30…+60° aralığında köprüye yaklaşmaz.
- **Pan:**
  - Servo tabanda, mili boyun ekseninde. Kulaklarıyla 32,5 mm olduğu için Ø32 yuvadan geçmez; tabanın açık altından girer, kulakları üstteki çıkıntıya alttan 2 × M2 ile vidalanır.
  - 6804 yatak tabanın tepesindeki yuvada (z252–259, altında dudak).
  - Boyun Ø20 mil olarak yataktan geçer; omzu iç bileziğe oturur. Alt yüzü pan kornasına 2 × M2 ile bağlanır; kornanın merkez vidasına boyun deliğinden ulaşılır.
  - Köprü, boyunun üst flanşına 2 × M3 ile bağlanır (insertler köprüde).
- **Kablolar:** kamera 5 V/GND ve tilt servosu boyun deliğinden iner, boyunun arka penceresinden çıkar. Tabanın arka yarığından içeri girer ve pan servosunun arkasındaki delikten (13, 0) gövdeye iner. Delik flanş, kapak ve kirişten geçer. Eski eksendeki delik kalktı.

**Commit:** Yok. Fiziksel test NOT_RUN.

### Task 1: Config ve testler (kırmızı)
- [x] `eye_center_y_mm` 39, `eye_pod_x_offset_mm` 0, `geometry.head` ölçüleri ve `mg90s_mm.horn_hole_r`.
- [x] `tests/check_cad.py`'ye eklenecek testler:
  - pan tabanında kulak pilotları, rulman yuvası ve dudak, kablo deliği ve arka yarık;
  - boyunda mil, delik, korna pilotları, flanş delikleri ve arka pencere;
  - köprüde kulak pilotları, insertler ve saplama;
  - göz kabuklarında korna delikleri, burç ve kaş pilotları;
  - kaş çubuğunda delikler;
  - tilt taraması −30…+60° kesişimsiz.

### Task 2: CAD (yeşil)
- [x] Baş bölümü yeniden yazılır; kaş çubuğu 045 eklenir. Tilt taraması manifest'e yazılır.

### Task 3: Baskı planı, kütle, görüntüleyici, belgeler
- [x] 040–042 "bekliyor" durumundan çıkar, 045 eklenir; M2/M3 sayıları güncellenir. Kütle grubunda baş 13 parça olur.
- [x] DD82; bütün testler PASS; görüntüleyici yeniden yayımlanır.
