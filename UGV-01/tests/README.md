# Doğrulama

Çalıştırılabilir masaüstü kontrolleri:

```
python3 tests/check_design.py
.venv/bin/python tests/check_cad.py
.venv/bin/python tests/check_print_plan.py   # önce: .venv/bin/python tools/print_plan.py
.venv/bin/python tests/check_body_mass.py
.venv/bin/python tests/check_drivetrain.py   # A2 arşivi: D1 tahrik
.venv/bin/python tests/check_lightweight.py  # A2 arşivi: D2A hafif teker
python3 tests/check_esp32_pinmap.py      # A3 Lite
python3 tests/check_lite_wiring.py       # A3 Lite
python3 tests/check_lite_bom.py          # A3 Lite
python3 tests/check_mcu_pinmap_integration.py
python3 tests/check_mcu_servo_light.py
python3 tests/check_ai_executor.py
python3 tests/check_ai_bridge.py
python3 tests/check_lite_gateway.py        # A3 Lite MacBook ↔ C çekirdeği (ctypes)
node --test software/web_ui/panel_logic.test.mjs
node --test tests/viewer_route.test.mjs   # görüntüleyici kol rotası grafikte kalır (N6)
python3 tests/check_pwr_mcu_harness.py
python3 tests/check_pwr_mcu_connector.py
python3 tests/check_differential_i2c_reference.py
python3 tests/check_board_interface_sheets.py
python3 tests/check_status_receiver.py
python3 tests/check_k2_reference.py
python3 tests/check_pwr_actuator_path.py
python3 tests/check_pwr_safety_gate.py
python3 tests/check_pwr_board.py
python3 tests/check_markdown_links.py
python3 tests/check_make_nvs.py   # kurulum NVS yardımcısı ↔ firmware anahtarları (DD89)
cc -std=c11 -Wall -Wextra -Werror tests/safety_core_test.c firmware/stm32/safety_core.c -o /tmp/ugv-safety-core-test && /tmp/ugv-safety-core-test
cc -std=c11 -Wall -Wextra -Werror tests/can_protocol_test.c firmware/stm32/can_protocol.c -o /tmp/ugv-can-test && /tmp/ugv-can-test
cc -std=c11 -Wall -Wextra -Werror tests/servo_light_test.c firmware/stm32/servo_control.c firmware/stm32/light_bar.c -o /tmp/ugv-servo-light-test && /tmp/ugv-servo-light-test
cc -std=c11 -Wall -Wextra -Werror tests/lite_link_test.c firmware/lite/hmac_sha256.c firmware/lite/lite_link.c firmware/stm32/can_protocol.c -o /tmp/ugv-lite-link && /tmp/ugv-lite-link   # A3 Lite UDP+HMAC
cc -std=c11 -Wall -Wextra -Werror tests/lite_core_test.c firmware/lite/lite_core.c firmware/lite/arm_path.c firmware/lite/lite_link.c firmware/lite/hmac_sha256.c firmware/stm32/can_protocol.c firmware/stm32/servo_control.c firmware/stm32/light_bar.c -lm -o /tmp/ugv-lite-core && /tmp/ugv-lite-core   # A3 Lite çekirdeği
cc -std=c11 -Wall -Wextra -Werror tests/board_math_test.c firmware/lite/board_math.c -o /tmp/ugv-board-math && /tmp/ugv-board-math   # A3 Lite ESP32 kart hesabı (L4a)
cc -std=c11 -Wall -Wextra -Werror tests/vl53l0x_test.c firmware/lite/vl53l0x.c -o /tmp/ugv-vl53 && /tmp/ugv-vl53   # A3 Lite ön ToF çifti (L4b)
docker run --rm -v "$PWD/firmware":/fw:ro -e IDF_COMPONENT_MANAGER=0 espressif/idf:v5.3.2 bash -c 'cd /fw/lite/esp32 && idf.py -B /tmp/build -DSDKCONFIG=/tmp/build/sdkconfig -DIDF_TARGET=esp32s3 build'   # ESP32-S3 derlemesi (Docker, 8 GB imaj; isteğe bağlı)
docker run --rm -v "$PWD/firmware":/fw:ro espressif/idf:v5.3.2 bash -c 'cp -r /fw/lite/eye /tmp/eye && cd /tmp/eye && idf.py -DIDF_TARGET=esp32 build'   # ESP32-CAM göz derlemesi (Docker; esp32-camera bileşenini indirir)
```

Mühendislik hesabı, gerçek STEP geometrisi, aktarma yükleri, hafifletme sınırları ve host referans güvenlik durum makinesi sınanır. CAD testleri `.venv` içindeki CadQuery ile çalıştırılır. KiCad 10 kurulu macOS ortamında MCU pin atamaları gerçek LQFP100 sembolüyle, kablo sürekliliği ve J-PWR footprint pad haritası karşılaştırılır; PCA9615 referans devresi ile iki kısmi kart sayfasının pin bağlantıları denetlenir. K2 kısmi referans sayfasında gerçek LM74900 pinleri, FET/şönt netleri ve pad25 ayrımı denetlenir. PWR aktüatör yolu, güvenlik kapısı ve ARM I/O sayfalarında pin netleri, K1'in boş footprint'i ve netlist değerlerinden test/karşılaştırıcı pencereleri; birleşik PWR hiyerarşisinde J-SIG kaynakları, 4 096 senaryoluk izin mantığı (lojik High'a takılıyken dahil) ve 0 hatalı ERC denetlenir. PWR sayfalarının tek başına ERC'sinde yalnız başka sayfada sürülen raylar/etiketler kalır. A2 MCU servo/ışık sayfasında servo rayı izni, INA180 akım ölçümü, dört servo başlığı ve ışık şeridi netleri ile yalnız sayfa dışı sürücülere ait ERC kayıtları denetlenir. Kısmi kart sayfalarında dokuz haricî ağ için beklenen ERC uyarıları; güçsüz alıcı kısmi sayfasında altı dış sürücü yokluğundan hata ve yedi uyarı vardır. Tam kart ERC PASS sayılmaz. A2 AI katmanı mock Claude istemcisiyle ücretsiz sınanır (gerçek API çağrısı yok): yerel sınırlar, izin/lease kaybı, dur sözü, ToF refleksi, `stop_reason` ve adım/dolar tavanları; MCU servo/ışık/CAN ve panel mantığı ayrı testlerde. A3 Lite UDP bağlantısı RFC 4231 HMAC vektörleri, bit değişimi, yanlış anahtar, yansıtma ve mod değişiminden sonra eski imzalı komutun tekrarı (inceleme R3) ile sınanır. Lite çekirdeği motor modeliyle sınanır: ARM, rampa, AI tavanı, ToF, lease kaybı, E-stop kilidi, STOP, düşük batarya, teker başına stall, ters yönde sıfırdan geçiş ve ≤0,9 A, TB6612 ısı bütçesi ve imzalı telemetri. ESP32 kart katmanının hesabı (L4a) ayrı sınanır: PCA9685 ön bölücü/sayım ve osilatör kalibrasyonu, TB6612 IN1/IN2 kutbu, batarya bölücüsü, ACT_EN ve /OE açma sırası (E-stop kenarı kontrolle yazma arasına düşse de hemen kazanır). Ön VL53L0X çifti iki sensörlü bir kayıt modeline karşı sınanır: XSHUT sırası (çakışma testi durdurur), kurulum/ayar/SPAD haritası, ölçüm, bayat veya kayıp sensörde 0, sıcak yeniden başlatma, sınırlı bekleme; `firmware/lite/esp32/` (ESP32-S3) ve `firmware/lite/eye/` (ESP32-CAM) ESP-IDF 5.3.2 ile uyarısız derlenir (donanımda çalışmadı). Kurulum NVS yardımcısının CSV'si iki firmware'in okuduğu anahtar ve türlerle birebir sınanır; hatalı anahtar, Wi-Fi ve kalibrasyon reddedilir, dosyalar repo dışına yalnız sahibinin okuyacağı izinle yazılır. Sonuçlar model sonucudur, ölçüm değildir. İnceleme R1–R10 ve yeniden kontrol F1–F3 regresyonları ilgili testlerde işaretlidir ([kapanış kaydı](../docs/review_closure_2026-09-25.md)). Bunlar üretim veya fiziksel test değildir.

20 donanım/saha prosedürü [test_plan.md](../docs/test_plan.md) içinde. Kanıtlar tests/evidence/Txx/tarih-konfigürasyon altında saklanacak; rapor alanları: test ID, tarih, kişi, ölçüm cihazı/kalibrasyonu, CAD/PCB/firmware revizyonu, batarya, yük/CG, ortam, ham kayıt, ölçüm belirsizliği, beklenen/gerçek, PASS/FAIL/BLOCKED/NOT_RUN, sapma ve düzeltme. Bu teslimde bütün fiziksel testler NOT_RUN.
