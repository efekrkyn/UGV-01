# L4a: ESP32-S3 kart katmanı (donanımsız kısım): uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Robot çekirdeğini (`lite_core.c`) ESP32-S3'e bağlayan katmanın donanım gerektirmeyen kısmını bitirmek. Kullanıcı: "daha almadım 3d printerı sen devam et yapmaya".

**Sınır:**
- Makinede ESP-IDF yok. Resmi Docker imajı 3–5 GB tutar; diskte 12 GB boş var (%98 dolu). Kullanıcıya sorulmadan indirilmez.
- Bu yüzden hesaplar ayrı, host'ta test edilen C koduna gider. ESP-IDF uygulaması yazılır, derleyici gelince derlenir.

**Architecture:**
- `firmware/lite/board_math.{c,h}` (saf C, host testli):
  - PCA9685 ön bölücüsü ve µs → sayım dönüşümü. 25 MHz nominal osilatör NVS'ten kalibre edilir; PCA9685 birkaç yüzde hızlı çalışabilir.
  - 0 µs = tam kapalı (darbe yok).
  - LEDn kayıt baytları.
  - TB6612 IN1/IN2 PWM eşlemesi: sür–serbest (coast) ve motor başına kutup.
  - Batarya: ADC mV × (100 k + 22 k)/22 k × kalibrasyon.
- `tools/gen_pins.py` → `firmware/lite/esp32/main/pins.h`, `config/esp32_pinmap.json`'dan üretilir. `check_esp32_pinmap.py` başlığın config'e eşit olduğunu denetler.
- `firmware/lite/esp32/` (ESP-IDF v5 projesi, **derlenmedi**): `app_main.c` içinde
  - NVS (bağlantı anahtarı, Wi-Fi, port, kalibrasyonlar), Wi-Fi STA ve UDP;
  - 20 ms görev ve görev watchdog'u;
  - MCPWM 20 kHz, PCNT, PCA9685 I²C, /OE, ACT_EN;
  - E-stop kesmesi: ACT_EN'i hemen Low yapar;
  - ADC1, RMT ile WS2812.
  - VL53L0X sürücüsü L4b'ye kalır. O zamana kadar menzil 0 okunur; çekirdek bunu "ileri engelli" sayar, yani güvenli yöndedir.

**Sonuç:** Kullanıcı indirmeyi onayladı ("indir devam et"); `espressif/idf:v5.3.2` ile uyarısız derlendi.

**Commit:** Yok. Donanım testi NOT_RUN.

### Task 1: Testler (kırmızı)
- [x] `tests/board_math_test.c`:
  - 50 Hz ön bölücü 121 (25 MHz);
  - 1500 µs → 307 sayım;
  - 0 µs tam kapalı;
  - osilatör +%4'te sayım düzeltilir;
  - motor kutbu ve yönü, coast;
  - batarya 2.270 mV → 12,59 V.
- [x] `check_esp32_pinmap.py`: `pins.h` == `gen_pins.render(config)`.

### Task 2: Kod (yeşil)
- [x] `board_math.c`, `gen_pins.py`, `pins.h`, ESP-IDF projesi.

### Task 3: Belgeler
- [x] DD86, `lite_software_A3.md` (L4a/L4b), `tests/README.md`, `run_all`.
