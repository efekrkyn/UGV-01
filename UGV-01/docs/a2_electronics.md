# UGV-01 A2 elektronik — servo rayı, ışık şeridi, göz kameraları, ToF

> **A2 kaydı.** A3 Lite (≤10.000 TL, DD65–DD67) bu kartları ve pinleri kullanmaz; güncel elektronik: [Lite elektronik](lite_electronics_A3.md).

24.09.2026 · Alt proje 3 ([plan](superpowers/plans/2026-09-24-a2-electronics.md)), PH5/6 P0 şema girdisi. **PCB, üretim, fonksiyonel güvenlik veya sürüş onayı değildir.** Fiziksel testler NOT_RUN.

## Yerleşim kararı

6 V / 4 A servo buck'ı **MCU kartındadır**. MCU kartı, J-PWR üzerinden K2 sonrası `ACT_BUS`'ı zaten alır ([arayüz sözleşmesi](pwr_mcu_interface.md)); böylece servo PWM, ray akımı ve ray izni aynı kartta kalır. J-SIG'in 12 hattı **değişmez**. Fiziksel E-stop `ACT_BUS`'ı kestiğinde servo buck'ın girişi de gider. J-PWR `ACT_BUS` kontağı motor + servo akımını taşır; sürekli servo payı ≈8 W / 12,4 V ≈ 0,7 A, F1 15 A zarfı içindedir.

| Blok | Devre ([KiCad](../electronics/ugv_mcu_01/servo_light.kicad_sch), [PDF](../electronics/ugv_mcu_01/servo_light.pdf)) | Neden |
|---|---|---|
| Servo rayı izni | `SERVO_BUCK_EN = SERVO_PWR_REQ (PE8) AND ACT_PERMIT_BUF` (74LVC1G08); iki giriş de pulldown'lı, çıkışta 100 k | MCU reset/çökmesinde ve PWR izni yokken ray kapalı. E-stop hem `ACT_BUS`'ı hem izni düşürür. |
| Ray akımı | 10 mΩ %1 yüksek taraf şönt → INA180A2 (50 V/V, 3,3 V besleme) → 1 k/10 nF → PC4 ADC2_IN5 | 0,5 V/A; 3,3 V'ta 6,6 A tam ölçek, 1,5 × 4 A'yı kapsar. Motor akımları ADC1'de olduğundan eşzamanlı örnekleme çakışmaz. |
| Servo başlıkları | J701–J704: sinyal / +6 V / GND; her sinyalde 1 kΩ seri; 470 µF ray kondansatörü | Ray kapalıyken MCU'nun servoyu sinyal ucundan beslemesini sınırlar. |
| Işık şeridi | `5V_CONTROL` → PTC 0,2 A → `LIGHT_5V`; PB15 SPI2_MOSI → 74AHCT1G125 → 33 Ω → J705 (JST-PH 3 pin); 100 µF + 100 nF | Kısa devre şerit, E-stop tanısını taşıyan kontrol rayını düşürmez. AHCT girişi 2 V eşikli; 3,3 V veri 5 V'a çevrilir. |

`tests/check_mcu_servo_light.py` her bağlantıyı netlist'ten, şönt/kazanç tam ölçeğini ve tek başına ERC'yi denetler. ERC'de yalnız başka MCU sayfalarında sürülen ağlar kalır: `MCU_3V3` ve `PGND` besleme pinleri, `ACT_PERMIT_BUF` girişi, dört MCU servo çıkışı ve `5V_CONTROL` tek pinli etiketleri.

## MCU pinleri

[Pin manifesti](../config/mcu_pinmap.json) KiCad LQFP100 sembolüyle doğrulanır (`tests/check_mcu_pinmap_integration.py`, 58 atama).

| Sinyal | Pin | Kaynak | Not |
|---|---|---|---|
| `SERVO_PAN` / `SERVO_TILT` | PA2 / PA3 | TIM15 CH1/CH2 | Mevcut |
| `SERVO_SHOULDER` | PB9 (96) | TIM17 CH1 | PB8 = BOOT0 kullanılmaz |
| `SERVO_GRIPPER` | PE3 (2) | TIM20 CH2 | |
| `SERVO_PWR_REQ` | PE8 (39) | GPIO | 10 k pulldown |
| `SERVO_I_SENSE` | PC4 (30) | ADC2_IN5 | |
| `LIGHT_DATA` | PB15 (54) | SPI2_MOSI | Yalnız TX; SCK pini bağlanmaz |

Doğrulayıcı iki kuralı zorunlu tutar: PB8 (BOOT0) hiçbir sinyale atanamaz; TIM15/TIM17/TIM20 yalnız 50 Hz servolara aittir, başka sinyal bu zamanlayıcıları kullanamaz. AF numaraları ve SPI TX-only yapılandırması CubeMX `.ioc` ile ayrıca teyit edilecek.

## Firmware kuralları (alt proje 4)

1. Servo rayı **önce PWM Low**, sonra `SERVO_PWR_REQ` Low ile kapatılır. Açılışta ray açılır, 100 ms beklenir, sonra son bilinen hedeften rampa başlar.
2. Ray akımı ortalama >3,5 A 200 ms veya anlık >5,5 A → ray kapatılır, **FAULT** (motorlar da durur), olay kaydı. Aynı anda yalnız bir büyük servo (omuz) hızlanır.
3. **Ray kapalıyken sürüş yok.** Park pozunda ray kesilirse sağ kol ≈5° düşüp orta kapağa oturur ([CAD denetimi](exterior_language_A2.md)); başka pozda keserse kol ve pençedeki yük zemine/nesneye düşer (R48).
4. Dijital servolar PWM darbesi kesilince pozisyon tutabilir; "kolu gevşet" komutu yalnız ray kesmesiyle garanti edilir.
5. Omuz eklemi [−55°, 180°] aralığında ve park↔çalışma arasında yalnız üstten döner (R47).
6. Işık şeridi parlaklığı yazılımda ≤0,5 W (8 LED tam beyazın ≈%21'i) ile sınırlanır; renk kodu: AI modu mavi, ARM sarı, FAULT kırmızı, batarya yüzdesi çubuk.

## Göz kameraları ve ToF (CM5 IO kartı)

- **Kameralar:** İki Camera Module 3 Standard, CM5 IO Board'un iki MIPI bağlantısına Standard–Mini kablolarla (22 pin 0,5 mm ↔ 15 pin 1 mm, [Raspberry Pi kılavuzu](https://www.raspberrypi.com/documentation/accessories/camera.html)); iki bağlantının ikisinin de kamera olarak açılması bring-up'ta teyit edilir. Özel KiCad yok. Kablo pan ekseninde ±90° burulur; boy ve servis kıvrımı boyun kablo yoluyla seçilir (B25). Kamera kablosu motor/servo güç kablolarından ayrı kanaldadır. İki kameranın Ubuntu/CM5'te birlikte açılması ve gecikme T18'de ölçülür.
- **ToF:** İki VL53L1X modülü ön tamponda, CM5 IO kartının 40 pin başlığındaki I²C'ye bağlanır. İkisi de açılışta 0x29 adresindedir; bu yüzden her modülün `XSHUT` ucu ayrı bir CM5 GPIO'suna gider: ikisi Low tutulur, biri bırakılıp 0x30 yapılır, sonra diğeri bırakılır. Kablo ≈0,3 m; 0,5 m'yi aşarsa PWR bağlantısındaki gibi diferansiyel I²C kullanılır. ToF **güvenlik sensörü değildir**: `skill_executor` refleks durdurmasına girdi verir; E-stop, operatör ve MCU tazelik sınırı birincil kalır.

## Güç bütçesi

[Elektrik mimarisi §6](electrical_architecture.md): servo satırı 2/3 W → **3/8 W**, iki CSI kamera 2 W tahsisin içinde (beklenen ≈0,6 W), ışık + ToF 0,6 W. Batarya gücü tipik 63,84 W / ağır 111,54 W; ≈%2 payla görev bütçesi **65,0 / 113,8 W** (`config/vehicle.json`). Yaşlanmalı minimum enerjiyle (84,21 Wh) tipik **1,30 saat**, ağır **0,74 saat**; 60 dakika hedefi yalnız tipik profilde desteklenir (`tests/check_design.py`).

## BOM

[BOM](../manufacturing/bom/initial_bom.csv): B14 iki kamera, B15 üç MG90S, B21 DS3218MG, B22 6804 pan rulmanı, B23 LED şerit, B24 iki ToF modülü, B25 kamera kabloları, B26 servo buck; C14–C17 (INA180A2, 74LVC1G08, 74AHCT1G125, 2512 şönt) MCU kartı içinde. V1 toplamı 1999 → **2082 USD** (%30 payla ≈2707 USD).

## Açık işler

1. 6 V / 4 A buck IC'si, manyetiği ve EN davranışı (alt proje 5); `SERVO_6V_BUCK` burada yalnız etiket.
2. MG90S ve DS3218MG'nin 3,3 V sinyal eşiği ve stall akımı gelen partide ölçülür (R49).
3. ToF tampon penceresi ve CAD tahsisi; tampon TPU katısı şu an dolu.
4. MCU kartı kök hiyerarşisi ve tam kart ERC'si.
5. PTC, şönt, LED şerit, ToF modülü ve kamera SKU'ları.
