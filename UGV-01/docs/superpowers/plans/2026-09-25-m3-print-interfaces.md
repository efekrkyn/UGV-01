# M3 baskı arayüzleri (M2 Task 4, M3 gövdesine göre): uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [M2 planının](2026-09-25-a3-print-ready.md) Task 4 adımını M3 geometrisine uygulamak. Bu planda yalnız kol mimarisinden bağımsız, kesin arayüzler var:
- göz kabuğu: arka kapak, ESP32-CAM rayı, lens yuvası;
- çamurluk, omuz servo çerçevesi ve kargo kutusu vidaları;
- omuz mili–korna bağlantısı ve kablo çıkışı.

Kol uzuvlarının servo tutma ve korna/idler ayrıntıları bu plana girmez. Bunun sebebi DD78'de yazılı: MG996R kulakları dirsek ve bilek çatalına sığmıyor, kulakları çevirmek ise parkta kolu duvara sokuyor. Bu ayrıntılar Codex incelemesinden ve kullanıcı dönüşünden sonra ayrı bir kararla yapılır.

**Architecture:**
- Ölçüler config'te durur; satın alınan parçaların ölçüleri satıcı verisinden alınır, parçalar gelince doğrulanır.
- Bağlantı standardı: M3 insert Ø4,0 × 6, M3 geçiş Ø3,4, M3 somun 5,7 × 2,8. Küçük parçalarda M2 kılavuz Ø1,6 ve geçiş Ø2,2.
- Önce `tests/check_cad.py`'ye test yazılır → FAIL, sonra CAD → PASS.

**Commit:** Yok. Fiziksel test NOT_RUN.

---

### Task 1: Göz kabuğu
- [x] Test → FAIL. İstenenler:
  - kabuğun arkası açık; arka kapak (UGV-MECH-044-±1) açıklığı kapatır ve sıkı geçer. İlk düşünülen M2 vidalı küçük kapak uygulanmadı: 27 × 40,5 mm kart o delikten geçmiyordu;
  - ESP32-CAM kartı dört ön tırnak ile kapağın bastırma çerçevesi arasında durur. Kartın dik yönde takıldığı için ray (oluk) kullanılamadı;
  - lens yuvası pencere ekseninde, Ø8 lens borusu için boş.
- [x] CAD → PASS

### Task 2: Gövde vidaları
- [x] Test → FAIL. İstenenler:
  - çamurluk flanşı üstte z140'a çıkar; her çamurluk parçası 3 × M3 ile yan panele bağlanır, cıvata yolu boş;
  - omuz servo çerçevesinin kolları 4 × M3 insertle yan duvara bağlanır; DS3218 kulakları için 4 delik;
  - kargo kutusu flanşı 2 × M3 insertle ön duvara bağlanır.
- [x] CAD → PASS

### Task 3: Omuz mili
- [x] Test → FAIL. İstenenler:
  - mil ucunda 25T disk korna için 4 × M3 delikli flanş (PCD config'te, satıcıyla doğrulanır);
  - milin eksenel kablo deliği korna tarafında kapalıdır, bu yüzden kablolar duvar ile flanş arasındaki radyal delikten çıkar.
- [x] CAD → PASS

### Task 4: Belgeler
- [x] DD78, lite_mechanical, açık işler, görüntüleyici; bütün testler PASS.
