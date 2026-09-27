# UGV-01 A3 "Lite" — 10.000 TL bütçe revizyonu — tasarım spec'i

24.09.2026 · Kullanıcı kararlarıyla yazıldı ve **kullanıcı tarafından onaylandı** ("başla"). **Üretim, baskı veya sürüş onayı değildir.** Fiyatlar tahminidir, sipariş verilmedi.

## Kullanıcı kararları

- Robotun toplam parça bütçesi **≤10.000 TL**. 3D yazıcı ayrıca alınıyor ve hariç.
- Filamentin hariç tutulması 1.000 TL civarında olmasına bağlıydı. Tahmin ≈2.000 TL çıktığı için filament **dahil** (aşağıda).
- **Lite mimari:** araçta ESP32-S3 ana kart + iki ESP32-CAM göz; AI ve panel kullanıcının MacBook'unda.
- **330×270 mm** dış ölçü ve A2'nin animasyon robotlarından ilham alan özgün görünümü (baş, kollar, ışık şeridi) korunur.
- **AI modeli: `deepseek-flash`** (DeepSeek V4.1 Flash: görüntü + araç çağırma). V4.1 Pro henüz yayınlanmadı; `deepseek-v4-pro` görüntü almadığı için kameralarla çalışamaz ([DeepSeek fiyat/model sayfası](https://api-docs.deepseek.com/quick_start/pricing), [görüntü rehberi](https://api-docs.deepseek.com/guides/vision/)).

## Neden yeniden mimari

Kur 23.09.2026'da ≈48,8 TL/USD; 10.000 TL ≈ 205 USD. A2 V1 BOM 2.082 USD ≈ 101.600 TL. Tek başına CM5 (195 USD ≈ 9.500 TL) veya dört Pololu 4754 motor (≈10.700 TL) bütçeyi aşar. Özel PWR/MCU kartları, 6061 CNC plaka ve 4S2P P45B paket de öyle. Hedef ancak araç üstü Linux bilgisayarı kaldırıp hazır modüllerle, baskı şasiyle ve daha hafif (≈3 kg) bir araçla tutar.

## Mimari

| Blok | Seçim | Görev |
|---|---|---|
| Ana kart | ESP32-S3 DevKitC N16R8 | 4 motor PWM, 2 enkoder, 4 servo (LEDC), ışık şeridi (RMT), 2 ToF (I²C + XSHUT), batarya ADC, E-stop durumu, Wi-Fi UDP kontrol. Yerel refleksler: lease 100 ms'yi aşarsa ya da ön ToF <0,25 m ise durur. A2 C modülleri (`safety_core`, `servo_control`, `light_bar`, çerçeve/oturum/sıra mantığı) ESP-IDF'e taşınır. |
| Gözler | 2 × ESP32-CAM (OV2640) | Baştaki göz kabuklarında; MacBook'a JPEG anlık görüntü (HTTP). |
| Motor sürücü | 2 × TB6612FNG modülü | Her motor ayrı kanal; sürücü VM beslemesi E-stop'tan sonra. |
| Motorlar | 4 × JGA25-370 12 V (~130 dev/dk), 2'si enkoderli | Ø120 mm teker ≈0,8 m/s üst hız; AI modunda 0,2 m/s. |
| Güç | 3S1P 18650 3 Ah (≈33 Wh) + 3S BMS, 10 A ana sigorta | **Fiziksel NC mantar E-stop**, motor sürücü VM ve servo buck girişini doğrudan keser; ESP32'ler ve kameralar açık kalıp E-stop'u raporlar. 5 V/5 A servo buck (E-stop sonrası), 5 V/3 A mantık buck (E-stop öncesi). |
| MacBook | Mevcut [panel](../../../software/web_ui/panel.html), [ai_bridge](../../../software/ugv_ai/bridge.py), [skill_executor](../../../software/ugv_ai/executor.py) + yeni UDP ağ geçidi | İnternet, DeepSeek API, operatör. |

Güvenlik ölçeklendi. A2'nin 8 kg / 16,8 V aracı için gereken K1/K2 röle-FET ayırıcı, ön şarj, harici watchdog ve PWR kartı Lite'ta yok. ≈3 kg / 12 V araçta fiziksel NC E-stop'un güç yolunu doğrudan kesmesi, ESP32'nin 100 ms lease sınırı ve MacBook'taki yürütücü sınırları kalır. Öncelik aynı: fiziksel E-stop > STOP/"dur" > operatör > AI.

## Korunan ve arşive giden

- **Korunur:** A2 gövde panelleri, kapaklar, tamponlar, baş/boyun/göz kabukları, kollar, ışık şeridi geometrisi; yürütücü, köprü ve panel (MacBook'ta çalışır); C modülleri (ESP32'ye taşınır); tüm A2 belgeleri A2 referansı olarak.
- **Arşive gider (silinmez):** CM5, STM32G474, PWR kartı ve KiCad sayfaları, özel MCU kartı, 6061 plaka, D1/D2A tahrik, Pololu motorlar, 4S2P paket.
- **Değişir:** alt yük yolu baskı şasiye (PETG plaka + nervür + motor yuvaları), tekerler baskı göbek + TPU lastik (motor miline doğrudan), batarya/elektronik bölmeleri, omuz servosu DS3218MG yerine MG996R.

## Kütle ve yük (hedef, CAD ile doğrulanacak)

**L1 sonucu (DD66):** kütle bütçesi boş **3,47 kg** (sınır 3,5), yük 0,5 kg, brüt 4 kg; yüklü CG z=105 mm. JGA25 için hedef eğim **5°** (kısa süreli); aşağıdaki ilk tahmin kayıt için korunur.

PETG gövde/baş/kollar ≈0,93 kg, şasi ≈0,25 kg, motorlar ≈0,40 kg, tekerler ≈0,36 kg, batarya + BMS ≈0,18 kg, elektronik + kablo ≈0,30 kg, servolar ≈0,10 kg → ≈2,5 kg; payla **≈3 kg**, yük **≈0,5 kg**. MG996R omuzda ≈9–11 kg·cm; 150 g yük için statik ihtiyaç 3,6 kg·cm (≈3× pay, ölçülecek). JGA25 15° eğimde sınırda; ilk hedef düz iç mekân.

## Filament tahmini

**L1 CAD sonucu (DD66):** baskı tahmini (1,2 mm kabuk + %20 dolgu) PETG 1.313 g, TPU 252 g; %25 fireyle ≈1,64 kg PETG + ≈0,32 kg TPU, yani 2 PETG + 1 TPU makarası (≈2.000 TL) doğrulandı ([Lite mekanik](../../lite_mechanical_A3.md)). Aşağıdaki ilk tahmin kayıt için korunur.

Kütleler A2 CAD'den: gövde katı hacmi 492 cm³ × PETG 1,27 g/cm³ ≈ 625 g; baş ≈160 g; kollar ≈140 g; baskı şasi ≈250 g; teker göbekleri ≈160 g → ≈1,33 kg; %25 fire/destek ile **≈1,7 kg PETG**. TPU tampon ≈85 g + lastikler ≈200 g, fireyle **≈0,36 kg**. Fiyatlar: PETG 1 kg ≈500–800 TL, TPU 1 kg ≈650–1.000 TL ([PETG](https://www.akakce.com/filament/petg-filament.html), [TPU](https://www.akakce.com/filament/tpu-filament.html)). 2 makara PETG + 1 makara TPU ≈ **2.000 TL** (1.700–2.600).

## BOM tahmini (yerel perakende, 24.09.2026)

| Kalem | Adet | TL |
|---|---:|---:|
| ESP32-S3 DevKitC N16R8 ([örnek](https://www.akakce.com/elektronik-devre-elemani/en-ucuz-robiz-esp32-s3-devkitc-1-n16r8-wifi-bluetooth-5-modul-gelistirme-karti-esp32-s3-n16r8-32-bit-cift-cekirdek-fiyati,1091323120.html)) | 1 | 600 |
| ESP32-CAM + OV2640 ([örnek](https://www.akakce.com/elektronik-devre-elemani/en-ucuz-esp32-cam-wifi-bluetooth-gelistirme-karti-ov2640-kamera-modulu-fiyati,130512545.html)) | 2 | 1.200 |
| JGA25-370 12 V motor (2 enkoderli + 2 düz) | 4 | 1.800 |
| TB6612FNG sürücü modülü | 2 | 200 |
| MG90S servo ([örnek](https://www.robo90.com/servo-motor)) | 3 | 400 |
| MG996R servo ([örnek](https://www.robotistan.com/mg996-13-kg-servo-motor)) | 1 | 280 |
| 18650 3 Ah hücre + 3S BMS + 12,6 V şarj adaptörü | 3+1+1 | 1.270 |
| 5 V bucklar, NC mantar E-stop, sigorta, ana anahtar, XT30 | set | 470 |
| VL53L0X ToF | 2 | 240 |
| 8 LED WS2812B çubuk | 1 | 60 |
| 6804 boyun rulmanı | 1 | 80 |
| Kablo, konnektör, vida, insert | set | 600 |
| Filament: 2 × PETG 1 kg + 1 × TPU | 3 | 2.000 |
| **Toplam** | | **≈9.200** |

Kargo, KDV farkları ve kur değişimi için pay yalnız ≈800 TL. Yurt dışı siparişle (daha uzun teslim) toplam düşebilir; doğrulanmadı. Bütçe aşılırsa ilk kesinti adayları: tek kamera göz (−600 TL), enkodersiz dört motor (−400 TL).

## AI maliyeti ve gizlilik

`deepseek-flash` fiyatı 1 milyon token başına 0,15–0,30 USD giriş ve 0,6–1,2 USD çıkış (yoğun saat fiyatı yarının iki katı). Görüntü başına ≤1.024 token. 15 adımlık görev kabaca 0,01–0,03 USD ≈ 0,5–1,5 TL; **ölçülmedi**. Köprü DeepSeek'in Anthropic uyumlu uç noktasını kullanır (`https://api.deepseek.com/anthropic`), bu yüzden mevcut kod küçük bir sağlayıcı ayarıyla geçer ([uyumluluk belgesi](https://api-docs.deepseek.com/guides/anthropic_api)). Kameradan alınan görüntüler DeepSeek sunucularına gider; panel bunu yazar. API anahtarı yalnız MacBook'ta izinleri kısıtlı bir dosyada durur (`DEEPSEEK_API_KEY`), sohbete veya repoya girmez.

## Alt projeler (sıra)

| # | İş | Çıktı |
|---|---|---|
| L0 | DeepSeek sağlayıcısı | Köprüde sağlayıcı ayarı (varsayılan `deepseek-flash`), mock testler, belgeler |
| L1 | Lite mekanik | Config/kütle/CG; baskı şasi, JGA25 yuvaları, baskı teker + TPU lastik, batarya/elektronik bölmeleri; A2 üst gövde ve baş/kol korunur; CAD testleri |
| L2 | Lite elektronik | Modül seviyesinde bağlantı şeması (KiCad), ESP32-S3 pin haritası ve testi, güç bütçesi ve çalışma süresi, BOM |
| L3 | Yazılım | ESP32 firmware (C modüllerinin portu, UDP çerçeveleri, lease/ToF refleksi), MacBook UDP ağ geçidi ve panel sunucusu, host testleri |
| L4 | Gerçek testler | Kullanıcı anahtarıyla ≤0,10 USD DeepSeek duman testi; parçalar gelince bring-up |

## Riskler

JGA25 torku ve TB6612 akım sınırı (stall ≈2 A'ya yakın), ucuz E-stop butonunun 12 V DC kesme değeri, ESP32-CAM görüntü kalitesi/gecikmesi, Wi-Fi kopması (lease ile durur), DeepSeek model/fiyat değişimi, kur ve fiyat oynaklığı. Fiziksel testler NOT_RUN.
