# M3 kol uzvu arayüzleri (DD78 açık işi): uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** DD78'de bekleyen kol uzuvlarını baskıya hazır hale getirmek: servo tutma, korna ve idler bağlantıları.

**Karar (kullanıcı yokken, "karar senin"):** DD78'in (b) seçeneği, yani alüminyum servo braketleri araştırıldı ve bırakıldı.
- Çok amaçlı braket 58 × 37 × 26 mm (Robotistan, 63,70 TL); uzun U braket 56 × 25 × 64,5 mm (≈143 TL).
- Twist servosunun çevresinde 58 mm'lik braketin sığacağı yön yok: y'de parkta 154 mm ayak izi ve yan duvar, z'de parkta çamurluk, uzanmada ön teker.
- Satıcılar delik düzenini vermiyor; baskı parçalar ancak tahminle delinirdi.

Seçilen yol, (c)'nin eksen kaydırmasız türevi:
- **Eğim eklemleri (dirsek B'de, bilek C'de):**
  - MG996R kulaklarıyla kalır. Mil **içe** bakar, kulaklar uzvun iç yüzüne 4 × M3 × 10 ile ısıl insertlere bağlanır.
  - Mile 25T alüminyum disk korna takılır; çatalın iç yanağı kornaya 4 × M3 ile, PCD 14 üzerinden bağlanır.
  - Dış yanakta 624ZZ yatak var. M4 cıvata yatağın iç bileziğinden geçip uzvun dış duvarındaki gömme somuna girer.
  - Çatal köprüsü eksenden ≥22 mm uzakta, böylece kulakların süpürdüğü alanın dışında kalır.
- **Twist (A):**
  - MG996R kulakları **kesilir**; servo, dış yandan kapaklı cebe (UGV-MECH-058) girer.
  - Eksenel konumu cebin arka duvarı ile korna → adaptör → B mili zinciri belirler.
  - Adaptör (UGV-MECH-059) kornaya 4 × M3 ile bağlanır. Altıgen ucu B'nin mil yuvasına girer, eksenel bir M3 çekerek sıkar.
  - 6704'ün iç bileziği adaptör omzu ile B göbeği arasında sıkışır.
- **Bilek dönüşü (D) ve pençe (E):** MG90S kulaklarıyla, 2 × M2 kendinden kılavuzlu vidayla Ø1,6 pilot deliklere bağlanır. E, dönüş servosunun kornasına bağlanır.
- **Boylar:**
  - Ön kol 90 → 80 mm, kavrama 86 → 96 mm. Parkta uç yine x ≥ −165'te kalır (330 mm ayak izi).
  - Artan boy, çatal köprüsünün eksenden uzaklaşmasından ve kulak boşluklarından geliyor.

**Satıcı ölçüleri (gelince doğrulanır):**
- MG996R (Handsontec çizimi): gövde 40,7 × 20 × 36,6; mil üstü 42,9; kulak altı tabandan 26,6; kulak kalınlığı 2,5; kulak açıklığı 54,5; delik aralığı 49,5 × 10.
- MG90S (TowerPro çizimi): 22,8 × 12,2; kulak altı 21; mil üstü 31; kulak açıklığı 32,5; delik aralığı 28.
- 25T disk korna: Ø25; yüzeyi mil üstünden 2 mm ileride; 4 × M3 kılavuz, PCD 14.

**Commit:** Yok. Fiziksel test NOT_RUN.

---

### Task 1: Config ve testler (kırmızı)
- [x] `geometry.arm`'a eklenecekler: `forearm_mm` 80, `grip_mm` 96, `mg996r_mm`, `mg90s_mm`, `horn_25t_mm`, `idler_624_mm`.
- [x] `tests/check_cad.py`'ye her uzuv için probe testleri:
  - kulak insert delikleri (Ø4 × 6) boş ve çevresinde et var;
  - korna delikleri çatal yanağında;
  - 624 yuvası (Ø13 × 5) ve M4 yolu;
  - M4 somun cebi;
  - çatal köprüsü eksenden ≥22 mm;
  - twist cebinde kapak pilotları; adaptörde korna delikleri, merkez deliği ve B'nin iki M3 pilotu; B'nin göbeği iç bileziği sıkıştırır;
  - MG90S pilot delikleri.
- [x] Çalıştır → FAIL.

### Task 2: CAD (yeşil)
- [x] `arm_zero()` yeni yerleşimle yeniden yazılır; 058 ve 059 eklenir. Sağ ve sol uzuvlar ayna kalır; sol kol pasif olduğundan 058 ve 059 yalnız sağda.
- [x] Kurulur. Açıklık ≥4,5 mm (hareketli), park ≥1,0 mm, kesişim yok, gevşek duruş çamurlukta. Duruşların kavrama noktaları testleri tutmazsa duruş açıları yeniden ayarlanır.

### Task 3: Baskı planı, kütle, BOM, belgeler
- [x] 050–054 "bekliyor" durumundan çıkar; baskı yönleri, insert sayısı ve M2/M4 kalemleri eklenir.
- [x] BOM: 25T korna × 3; M4 kalemi, 40 mm'lik cıvata yerine 12 mm cıvata + somun.
- [x] Kütle taraması, DD81, görüntüleyici; bütün testler PASS.
