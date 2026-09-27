# UGV-01 A3 Lite elektronik

25.09.2026 · L2 ([spec](superpowers/specs/2026-09-24-a3-lite-budget-design.md), [plan](superpowers/plans/2026-09-25-a3-lite-electronics.md)); **M3** (DD75): 8 servo PCA9685'te, iki servo rayı, 15 A sigorta. Hazır modüllerle delikli pertinaks üzerinde kurulacak bir bağlantı tasarımıdır; **PCB, üretim, fonksiyonel güvenlik veya sürüş onayı değildir.** Parça alınmadı, fiziksel test yapılmadı. A2'nin özel PWR/MCU kartları [A2 kaydında](revisions/A2/README.md) kalır.

## Blok yapı

[KiCad bağlantı şeması](../electronics/ugv_lite_01/lite_wiring.kicad_sch) ([PDF](../electronics/ugv_lite_01/lite_wiring.pdf)), [pin haritasından](../config/esp32_pinmap.json) üretilir.

| Blok | Parça | Bağlantı |
|---|---|---|
| Güç girişi | 3S1P 18650 + 3S BMS → 10 A bıçak sigorta → ana anahtar → `VBAT_SW` | Şarj 12,6 V CC/CV adaptörle BMS üzerinden |
| Fiziksel E-stop | Mantar buton, **2 NC kontak bloğu**: 1. NC `VBAT_SW` → `VM_ACT` | İki TB6612'nin VM'ini ve iki servo buck girişini **doğrudan keser** (en kötü ≈9,4 A); 2. NC durumu doğrudan GPIO2'ye verir. ESP32, gözler ve ToF açık kalıp durumu raporlar |
| Mantık rayı | Mini560 5 V (girişi E-stop'tan önce) → `5V_LOGIC` | DevKitC 5V pini, iki ESP32-CAM, ışık şeridi, 74AHCT1G125; DevKitC LDO'su `3V3` verir |
| Servo rayları (M3) | 2 × Mini560 5 V 5 A (girişleri E-stop'tan sonra, EN = `ACT_EN`) → `5V_SERVO_A`, `5V_SERVO_B` | A: omuz (DS3218MG), dirsek (MG996R), pan, tilt. B: üst kol dönüşü ve bilek eğimi (MG996R), bilek dönüşü ve pençe (MG90S). PCA9685'in V+ ucu kullanılmaz |
| Servo PWM (M3) | PCA9685 16 kanal modülü, I²C0 (0x40; ToF'lar 0x29/0x30), VCC 3V3 | Kanal k = firmware eklemi k (`servo_control.h`). /OE = `SERVO_OE` (GPIO39), 10 k pull-up: reset ve açılışta 8 çıkış da kapalı. Modülde her çıkışta 220 Ω seri |
| Motorlar | 2 × TB6612FNG: sol modül FL + RL, sağ modül FR + RR; her motor çıkışında **7,5 Ω 10 W seri balast** | PWMA/PWMB = 3V3; hız IN1/IN2'de MCPWM (sür/boşta); STBY = `ACT_EN` |
| Algılayıcılar | 2 × VL53L0X (I²C, yalnız soldakinde XSHUT), **dört motorda** Hall enkoder, yalnız A kanalı (PCNT) | ToF'lar 3V3; enkoderler 3V3; yön komuttan bilinir |
| Ölçüm | `VBAT_SW` 100 k/22 k bölücüyle ADC1'e (GPIO1) | 12,6 V → 2,27 V (en kötü %1 tolerans ve +%1 şarj: 2,33 V); 9,6 V → 1,73 V. ESP32-S3 veri sayfası v2.2 Tablo 5-6: ATTEN3 etkin aralık 0–2.900 mV |

**`ACT_EN`** (GPIO21, 10 k pulldown), iki sürücünün STBY girişini ve iki servo buck'ın EN girişini birlikte sürer. ESP32 reset ya da açılış sırasında pin girişe döndüğünde pulldown motorları ve servo rayını kapalı tutar. **E-stop durumu** (DD69, R6) butonun ikinci NC kontağından doğrudan okunur: kontak 3V3'e 10 k pull-up'lı düğümü GND'ye çeker, 1 k seri + 100 nF süzgeçle GPIO2'ye gelir. Bırakılmış = Low; basılı ya da kopuk kablo = High (arızada güvenli). İki kenar farklı yoldan dolar (yeniden kontrol F3): **basışta** kondansatör 10 k + 1 k üzerinden VIH'e (0,75·VDD, ESP32-S3 veri sayfası v2.2 Tablo 5-4) yükselir, τ = 1,1 ms, eşiğe nominal 1,53 ms, en kötü (%1 direnç, +%10 X7R) **1,69 ms**; **bırakmada** yalnız 1 k üzerinden VIL'e (0,25·VDD) iner, en kötü 0,15 ms. Kesme servisi kenarda `ACT_EN`'i hemen Low yapar ve kilitler (gecikme bütçesi 0,3 ms): basıştan `ACT_EN` Low'a ≤2 ms; çekirdek bir sonraki 20 ms döngüde ESTOP'a geçer. ≈1,7 ms'den kısa kontak açılmaları (sıçrama) eşiğe ulaşmayabilir; insan basışı bundan çok uzundur. Güç kontağı bu süreden bağımsız olarak enerjiyi doğrudan keser. Kilit, E-stop bırakılıp IDLE lease ve yeniden ARM gelene kadar sürer; bırakmak hareketi kendiliğinden başlatmaz. Önceki `VM_ACT` ADC karşılaştırması kaldırıldı: 470 µF ve yalnız 133 kΩ boşalma yoluyla yarıya inmesi model üzerinde ≈43 s sürebiliyordu ve kısa basışı kaçırabiliyordu. Güç kontağının kaynaklaşması bu şemayla görülmez; periyodik E-stop kontrolü açık iştir.

## ESP32-S3-DevKitC-1 pinleri (20 kullanılan + 3 boş)

Kaynak: Espressif ESP32-S3-DevKitC-1 v1.1 kullanıcı kılavuzu, J1/J3 tabloları. N16R8'de GPIO35–37 octal flash/PSRAM'a, GPIO38 kart üstü RGB LED'e ayrılmıştır. Strapping (0, 3, 45, 46), USB (19, 20) ve konsol (43, 44) pinleri kullanılmaz. ADC2, Wi-Fi açıkken kullanılamadığından analog girişler ADC1'dedir. `tests/check_esp32_pinmap.py` bu kuralları ve çevre birimi kapasitesini (MCPWM 12, LEDC 8, PCNT 4, RMT 4) denetler.

| Sinyal | GPIO | Başlık | Çevre birimi |
|---|---|---|---|
| M_FL_IN1/IN2, M_FR_IN1/IN2 | 4, 5, 6, 7 | J1-4…7 | MCPWM0 |
| M_RL_IN1/IN2, M_RR_IN1/IN2 | 15, 16, 17, 18 | J1-8…11 | MCPWM1 |
| ENC_FL_A, ENC_RL_A, ENC_FR_A, ENC_RR_A | 11, 12, 13, 14 | J1-17…20 | PCNT (4 birim, tek kanal) |
| SERVO_OE (M3) | 39 | J3-9 | GPIO; PCA9685 /OE, 10 k pull-up |
| boş (M3) | 40, 41, 42 | J3-8…6 | servolar PCA9685'e geçti |
| LIGHT_DATA | 47 | J3-17 | RMT |
| I2C_SDA / I2C_SCL / TOF_XSHUT | 8, 9, 10 | J1-12, 15, 16 | I²C0 / GPIO |
| VBAT_SENSE / ESTOP_SENSE | 1, 2 | J3-4, 5 | ADC1_CH0 / dijital giriş (kesme) |
| ACT_EN | 21 | J3-18 | GPIO |

M3'te 8 servo PCA9685'e (I²C) taşındığı için GPIO40–42 boş kaldı. `tests/check_esp32_pinmap.py` bunları `spare` listesinde ister; PCA9685 kanal sırasını, adresini ve ray atamalarını da denetler.

## Güç bütçesi (tahmin, ölçülmedi)

| Tüketici | Tipik W | Ağır W | Not |
|---|---:|---:|---|
| 4 motor (11,1 V) | 6,7 (0,15 A/motor, düz, 5,1 kg) | 17,4 (0,39 A/motor, 5° rampa) | Doğrudan batarya, TB6612 + balast üzerinden |
| Balast kaybı (4 × 7,5 Ω) | 0,7 | 4,6 | Isı gövde içinde |
| ESP32-S3 + 2 ESP32-CAM + 2 ToF + ışık | 3,1 | 3,7 | 5 V mantık rayı |
| 8 servo + PCA9685 | 4,0 | 16,0 | İki 5 V servo rayı (M3: 5 eksenli kol) |
| Buck kaybı (%90) | 0,8 | 2,2 | |
| **Toplam batarya** | **≈15,3** | **≈43,9** | Config görev gücü 16,0 / 46 W (≈%5 pay; M3'te 14,0 / 38 W'tan çıkarıldı) |

32,4 Wh paket, minimum kapasite, %80 kullanım ve %85 yaşlanmayla 20,9 Wh verir: tipik **1,31 saat**, ağır **0,46 saat** ([hesap](calculation_results.md)). En kötü anlık akım (M3): 4 motor stall (4 × 0,89 A, balastla sınırlı) + iki servo buck girişi (2 × 5 A × 5 V / 0,9 / 9,6 V ≈ 5,8 A) + mantık ≈0,4 A ≈ **9,8 A**; bunun ≈9,4 A'i E-stop güç kontağından geçer. 15 A yavaş sigorta kablo korumasıdır (güç 18 AWG), motor kanalı koruması değildir; kanal akımını balast sınırlar. 18650 hücre (≥15 A) ve 20 A BMS yeter. Servo raylarının akım sınırı buck'ın kendi sınırıdır (Lite'ta servo akım ölçümü yok); büyük eklemler aynı anda hızlanırken bir ray kısa süre çökebilir. Mantık rayı ayrı olduğu için ESP32'nin resetlenmemesi **hedeflenir**; batarya, BMS ve kablo empedansı ortak olduğundan bu bir garanti değildir, TL4'te servo yük adımı sırasında `5V_LOGIC` ve `3V3` ölçülür (N5).

## Güvenlik (Lite ölçeği)

Öncelik: fiziksel E-stop > STOP/"dur" > operatör > AI. A2'nin K1/K2 ayırıcı, ön şarj ve harici watchdog zinciri ≈3,5 kg / 12 V Lite araçta yok. Kalan katmanlar:

1. NC E-stop motor ve servo enerjisini doğrudan keser; motorlar boşa düşer (fren yok). Kol parkta ise çamurluğa oturur (CAD denetimi, M3). PCA9685 /OE pull-up'ı reset ve açılışta servo darbelerini de keser.
2. `ACT_EN` pulldown: ESP32 reseti, çökmesi veya açılışı aktüatörleri kapatır. ESP-IDF görev watchdog'u takılan firmware'i resetler.
3. ESP32 lease sınırı 100 ms: MacBook'tan komut gelmezse IN pinleri Low, `ACT_EN` Low (L3).
4. Motor sıkışması ve sürücü ısısı (DD69 R4, DD70 yeniden kontrol F1): TB6612'nin önerilen çalışma akımı kanal başına 1,0 A'dır (1,2 A mutlak; 2 A yalnız ≤20 ms, ≤%20 görev darbesi). 7,5 Ω balast, tam pakette sıkışmayı **0,89 A** ile sınırlar (en kötü 0,97 A), ancak **bu süresiz çalışma kanıtı değildir**: iki kanal aynı çipte ısınır. Firmware arızasında (tam görev, iki kanal sıkışık) çip kaybı ≈1,22 W olur; bu, veri sayfasının 0,78 W (çip) ve 0,89 W (50×50 mm kart) değerlerini aşar ([hesap](calculation_results.md)). Koruma [Lite çekirdeğinde](../firmware/lite/lite_core.c) zamanla sınırlıdır:
   - **Hız döngüsü (N2, DD76):** motor başına PI; çıkış paket gerilimine kadar çıkabilir. DD70'teki ≈9,2 V gerilim tavanı kaldırıldı, çünkü yerinde dönüşü engelliyordu. Akımı geri-EMK sınırlayıcı tutar: çekirdeğin tahmini ≤0,9 A, nominal yolda ≤0,825 A. Duran teker 300 ms stall kesmesiyle, akım sınırında dönen çift ≈3 s içinde ısı bütçesiyle kesilir.
   - **Stall kesmesi:** her motor kendi enkoderiyle izlenir; ≥3 V komutta 300 ms kenar yoksa FAULT, ardından 10 s soğuma ve IDLE el sıkışması gerekir.
   - **Isı bütçesi:** çip başına kayıp muhafazakâr akımla (2·I²·0,7 Ω) tahmin edilir. 0,5 W'ın (55 °C gövdede 0,59 W'lık izin, PWM payıyla) üstündeki enerji 2 J'ü aşınca THERMAL FAULT. Model: ağır yükle yavaş dönen teker ≈20 s'de kesilir.
   - **Yön değişimi:** ters komutta çıkış önce bir tur (20 ms) boşa alınır. Frenleme akımı geri-EMK sınırlayıcıyla (|V−EMK|/R_min ≤ 0,9 A) tutulur; yön, teker 2 dev/dk altına inince değişir. Rampa (0,5 m/s²) ek olarak akımı düşük tutar.
   - **Son katman:** TB6612 ısıl kapanması ve ESP-IDF watchdog + `ACT_EN` pulldown.
   - **Bilinen sınır:** tek kanallı enkoder dıştan geri sürülmeyi (itilme, rampada geri kayma) ileri dönüşten ayıramaz. O durumda akım (V + EMK)/R'ye çıkabilir; 0,3 m/s itilmede ≈1,08 A, önerilenin üstünde ama mutlak 1,2 A'in altında.
   - **Doğrulama:** kabul testleri [TL1/TL2](test_plan.md), NOT_RUN.

## Parça listesi

[lite_bom_A3.csv](../manufacturing/bom/lite_bom_A3.csv): **13.478 TL** (M3 tavanı 13.500 TL, 22 TL pay; `tests/check_lite_bom.py`). A3'teki 9.987 TL'ye M3 ile eklenenler (+3.491 TL):
- Servolar +1.795 TL: DS3218MG 270° omuz 1.100 TL tahmin, iki MG996R daha, bir MG90S daha.
- Üçüncü PETG makarası +650 TL.
- PCA9685 (236 TL), üçüncü Mini560, iki 6804-2RS ve bir 6704-2RS rulman, ek vida ve kablo.
- DD81–DD83: üç 25T alüminyum disk korna (270 TL) ve tilt itme çubuğu (30 TL); M4 vida satırı kısaldı (−10 TL).

DD68–DD69 kalemleri (dört enkoderli motor, dört balast direnci) korunur. Adetler config ve pin haritasıyla test edilir: servo adedi PCA9685 kanal sayısına ve config'teki eklem servolarına eşit. Fiyatlar yerel perakende tahminidir; kaynağı olmayan satırlar "tahmin" diye işaretlidir. DS3218MG 270°'nin yerel stoğu belirsizdir; yedek RDS3115MG 270° (941 TL, 5 V'ta 1,47 N·m, omuz payı 1,74). Güvenlik sınırını gevşeten kesintiler (enkodersiz motor, balastsız sürüş) bütçe için kullanılmaz.

Kısma seçenekleri (kullanıcı isterse):
- Bilek dönüşünü (J5) çıkarmak ≈−135 TL.
- Üst kol dönüşünü (J2) çıkarmak ≈−340 TL; kol yeniden tek düzleme iner.
- 2,4 mm duvarla ≈160 g PETG azalır, ama üçüncü makara yine gerekir.

## Açık işler

1. Satın alınan TB6612, Mini560 ve VL53L0X kartlarının pin sırası şemayla karşılaştırılır (şema yaygın kart sırasını kullanır).
2. Mini560 EN girişinin 3,3 V ile açıldığı ve açık EN'de çalıştığı doğrulanır.
3. E-stop butonunun 12 V DC kesme değeri; sigorta tipi; kablo kesitleri (güç 18 AWG, motor 22 AWG).
4. MG90S/MG996R'nin 3,3 V servo sinyalini algılaması (R49).
5. TB6612 ve balast ısınması; her tekerin ayrı sıkıştırma testi, pivot akımı (µ'ya göre); ADC bölücü kalibrasyonu.
7. E-stop 2 NC kontak bloğunun bulunması ve güç kontağının kaynaklaşma kontrolü (periyodik).
6. Pertinaks yerleşimi ve elektronik tepsisinin CAD bağlantısı.
8. PCA9685 modülünün başlık sırası ve kanal çıkışlarındaki seri direnç doğrulanır; /OE'nin ESP32 GPIO39 ile sürüldüğü ve pull-up'la açılışta kapalı kaldığı ölçülür (M3).
9. E-stop güç kontağı M3'te en kötü ≈9,4 A DC keser; 12 V DC ≥10 A kontak ya da kontaktör seçilir.
10. Servo rayı yeniden açılınca, konum geri bildirimi olmadığından düşmüş kol son komut açısına tam hızla gider: bring-up'ta ölçülür; yeniden ARM öncesi kol parka alınır.
