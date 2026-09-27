# A3 Lite yazılım (L3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lite aracın donanımsız doğrulanabilen yazılımını bitirmek: ESP32'de koşacak taşınabilir C çekirdeği (durum makinesi, Wi-Fi komut protokolü, imza) ve MacBook ağ geçidi; Python↔C uyumu uçtan uca testle kanıtlanır.

**Sıra kararı (kullanıcı, 25.09.2026):** önce tasarım, sonra 3D baskı, satın alma en son. ESP-IDF sürücü katmanı (MCPWM/LEDC/PCNT/RMT/ADC/Wi-Fi çağrıları) ve bring-up parçalar geldiğinde yazılır (L4); bu plan onları kapsamaz.

**Architecture:**
- **Paket biçimi:** 21 baytlık UDP datagramı `'U' + yön('C' komut / 'T' telemetri) + sürüm(1) + id16 + 8 bayt yük + HMAC-SHA256'nın ilk 8 baytı`. Yük ve oturum/lease/sıra anlamı A2 CAN çerçeveleriyle aynıdır (0x080 STOP, 0x100 sürüş, 0x110 lease, 0x120/0x121 servo/AI); `can_protocol.c` olduğu gibi kullanılır. Yön baytı etikete dahil olduğundan telemetri komut diye geri yansıtılamaz. Anahtar yalnız git'e girmeyen bir dosyada ve ESP32 NVS'sinde durur.
- **Lite çekirdeği (`firmware/lite/lite_core.c`):** IDLE → ARMED → DRIVING, ESTOP, FAULT. `ACT_EN` yalnız taze lease + deadman + E-stop kapalı + 500 ms nötr + ARM isteği + arıza yokken High. Sürüş: sol/sağ mm/s → motor başına ±‰ görev oranı (batarya telafili); AI modunda ve bayat 0x121'de 200 mm/s tavanı; ön ToF <250 mm ileri hareketi keser; dört motorun her biri kendi enkoderiyle stall (komut var, 300 ms dönüş yok) ve düşük batarya FAULT; E-stop GPIO2 kenar kilidi, bırakınca yeniden ARM gerekir; hız sınırı 300 mm/s (DD69). Servo ve ışık A2 modülleriyle.
- **MacBook (`software/ugv_lite/`):** `frames.py` (datagram + HMAC, `hmac` stdlib), `vehicle.py` (`LiteVehicle`: yürütücünün beklediği araç arayüzü; telemetri 200 ms'den eskiyse veya geçersizse odometri/ToF `NaN` döner, sıfır ya da eski değerle arıza gizlenmez (inceleme R1); 50 Hz lease/sürüş/servo gönderir, telemetriden odometri ve ToF, ESP32-CAM `/capture` görüntüsü), `gateway.py` (panel WebSocket mesajları → izin/dur/talimat; `websockets` yalnız çalıştırırken içe aktarılır).
- **Uçtan uca test:** C çekirdeği paylaşımlı kütüphane olarak derlenir, Python `ctypes` ile yüklenir; `LiteVehicle` sahte UDP bağlantısıyla gerçek C çekirdeğini sürer.

**Commit:** Yok (kullanıcı kuralı).

---

### Task 1: HMAC-SHA256 ve datagram (C)
- [x] Test önce (`tests/lite_link_test.c`): SHA-256 "abc" ve RFC 4231 1–2 test vektörleri; datagram paketle/aç; yanlış anahtar, değişmiş bayt, yanlış yön, yanlış uzunluk reddedilir. → FAIL.
- [x] `firmware/lite/hmac_sha256.{c,h}`, `firmware/lite/lite_link.{c,h}` → PASS.

### Task 2: Lite çekirdeği (C)
- [x] Test önce (`tests/lite_core_test.c`): açılışta ACT_EN Low; 500 ms nötr + ARM ile kurulur; sürüş görev oranı ve yön; bayat lease → dur + ACT_EN Low; E-stop açık → ESTOP; AI tavanı; ToF ileri keser, geri serbest; düşük batarya ve stall FAULT; STOP çerçevesi; servo darbeleri yalnız kuruluyken; telemetri datagramları. → FAIL.
- [x] `firmware/lite/lite_core.{c,h}` → PASS. (25.09.2026, DD70. Not: plan bu kutuları dosyalar diskte yokken işaretlemişti; çekirdek ve test bu tarihte yazıldı. Yeniden kontrol F1 korumaları dahil: gerilim tavanı, sıfır geçişinde boşa alma, geri-EMK sınırlayıcı, çip ısı bütçesi.)

### Task 3: MacBook ağ geçidi (Python) ve uçtan uca
- [x] Test önce (`tests/check_lite_gateway.py`): Python datagramı C ile birebir aynı; `LiteVehicle` + `SkillExecutor` gerçek C çekirdeğini `ctypes` üzerinden kurar, 0,2 m sürer, ToF engelinde durur, lease düşünce ACT_EN Low olur; panel mesajları izin/dur/talimata çevrilir. → FAIL.
- [x] `software/ugv_lite/{frames,vehicle,gateway}.py` → PASS. (25.09.2026: C çekirdeği ctypes ile; bağlantı/izin kaybı, bayat telemetri NaN, ToF, ağ geçidi. Canlı sunucu yerelde bir kez denendi: panel HTTP + /ai WebSocket. Gerçek UDP/ESP32 ve ücretli API L4'te.)

### Task 4: Belgeler
- [x] `docs/lite_software_A3.md` (akış, protokol, güvenlik, anahtar, ESP32-CAM ayarı, çalıştırma, L4'e kalanlar), `communication_architecture.md` A3 notu, README, DD71, faz kaydı, `tests/README.md`; bütün testler → PASS.
