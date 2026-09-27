# UGV-MCU-01

> **A2 kaydı.** A3 Lite (≤10.000 TL, DD65–DD67) bu kartları ve pinleri kullanmaz; güncel elektronik: [Lite elektronik](../../docs/lite_electronics_A3.md).

Durum: PHASE5 kısmi [KiCad PWR↔MCU arayüz şematiği](pwr_mcu_interface.kicad_sch), [güçsüz durum alıcı sayfası](status_receiver.kicad_sch) ve PDF'leri var; tam kart şematiği/layout yok. Esas belge: [elektrik mimarisi](../../docs/electrical_architecture.md).

İlk kart: STM32G474VET6 + dörtDRV8874 + BMI088 + CAN transceiver. İki ayrı giriş: always-on5V_CONTROL ve E-stop ile kesilenMOTOR_BUS. USB/SWD/UART servis erişimi üst kapaktan; motor güç bağlantıları kartın dış kenarlarından. INA228 PWR üzerindeki şönt yanında kalır; PA8/PA9 yerel I²C2, kablo tarafında PCA9615 diferansiyel SCL/SDA tamponu adayıdır. Kısmi arayüz sayfası J-PWR, J-SIG, PCA9615 ve sonlandırmayı gösterir. PWR kaynaklı altı durum/izin girişi için [SN74LVC244A alıcı taslağı](../../docs/powered_off_status_receiver.md) ikinci kısmi KiCad sayfasındadır; iki sayfa birleşmedi, 3,3 V regülatör ve `PGOOD` hâlâ açık. Güçsüz giriş ve brownout bench'te doğrulanmadı.

Kaynak haritası elektrik belgesi§9'da; dört encoder TIM2/3/4/5, dört `IN1` PWM TIM8 ve dört `IN2` PWM TIM1, CANPD0/1, USBPA11/12. DRV8874 PMODE=High; iki motor girişi 0 olduğunda coast. MCU reseti sırasında nSLEEP donanımca Low tutulur; hardware inhibit tüm nSLEEP uçlarına MCU'dan bağımsız ulaşır. Servo power PWR üzerinden kesilir; servo sinyalinden geri besleme önlenir.

PHASE5 işi: referans devreler, 5V→3V3 supply/ADC filtering, sabit current limit, boot/SWD, watchdog latch, analog toplama ve CubeMX conflict review. 58 aday atamanın makine tarafından kontrol edilen kaynağı [`config/mcu_pinmap.json`](../../config/mcu_pinmap.json), incelemesi [`docs/mcu_pinmap_review.md`](../../docs/mcu_pinmap_review.md); PWR↔MCU net ve konnektör adayları [`docs/pwr_mcu_interface.md`](../../docs/pwr_mcu_interface.md). Bu kaynaklar şematik değildir. PHASE7 işi: gerçek mounting holes/CAD envelope'e bağlı placement,4katman stackup,termal alanlar ve4yük testi. Mounting hole koordinatları mekanik freeze öncesi icat edilmeyecek.

Kısmi sayfa ERC: 0 hata, henüz diğer sayfalara bağlanmamış J-SIG pin1–8 ve J-PWR `ACT_BUS` için 9 beklenen uyarı. [Pin/net kontrolü](../../tests/check_board_interface_sheets.py) bu sınırı korur. Gelecek üretim dosyaları: tam KiCad projesi, ERC/DRC raporu, stackup, BOM, pick-and-place, Gerber, drill, assembly PDF ve bring-up test kaydı. Üretim onayı ancak pin/power independent review ve güvenlik testleri sonrası.

A2 (24.09.2026): [servo rayı, servo başlıkları ve ışık şeridi kısmi sayfası](servo_light.kicad_sch) ([PDF](servo_light.pdf), [inceleme](../../docs/a2_electronics.md)). 6 V/4 A servo buck bu kartta `ACT_BUS`'tan beslenir; EN = MCU isteği AND PWR izni. Tek başına ERC'de yalnız başka sayfalarda sürülen ağlar kalır (`tests/check_mcu_servo_light.py`).
