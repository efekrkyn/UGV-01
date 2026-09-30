# Tam inceleme kapanış kaydı — 29.09.2026

[Bağımsız tam inceleme](review_full_2026-09-29.md) raporundaki bulguların kapanışı. Rapor değiştirilmedi. Kararlar: [DD92](design_decisions.md) (A01–A08) ve [DD93](design_decisions.md) (M01–M03, park toleransı).

Her bulgu önce raporun kendi yeniden üretim betikleriyle ya da CAD taramasıyla doğrulandı, sonra kök nedeni düzeltildi ve karşı örnek kalıcı teste taşındı. Bu kayıt tasarım/yazılım kapanışıdır; **üretim, montaj veya sürüş onayı değildir.** T01–T20 ve TL1–TL6 NOT_RUN.

## Yazılım ve belge (DD92)

| # | Kök neden | Düzeltme | Kanıt (test) | Açık fiziksel kapı |
|---|---|---|---|---|
| A01 | Çekirdek anahtar uzunluğunu denetlemiyordu; NVS'de anahtar yoksa boş HMAC anahtarı geçerliydi | `lite_core_init` yalnız 32 baytlık anahtarı alır; aksi halde her datagram reddedilir, telemetri yok | `tests/lite_core_test.c`: 0/16/31/33 baytlık anahtarla, aynı anahtarla imzalı IDLE→ARM→DRIVE reddedilir, ACT_EN Low. Raporun `ugv_audit_emptykey.c` betiği artık park onayında durur | Kurulumda NVS anahtarının yazılması (`make_nvs.py`) |
| A02 | Sürücü yalnız kesme durumunu ve mesafeyi okuyordu | 0x14 durum baytı: 11 geçerli; sinyal/faz hatası + ≥8190 "hedef yok"; gerisi 0 (ileri engelli); geçersiz örnek eskisini canlı tutmaz | `tests/vl53l0x_test.c`: 13 durum/mesafe çifti, her biri geçerli örnekten hemen sonra. Rapor betiği `1200,1200` yerine `0,0` verir | TL5: açık alanda gerçek sensörün durum kodu; siyah ve cam hedefte 200 mm |
| A03 | Soket Origin/Host denetlemiyordu; global `send` son bağlantıya geçiyordu | Yalnız kendi localhost sayfası (403); tek sahip, ikincisi 1008; yanıt sahibine; sahip kopunca izin düşer | `tests/check_lite_gateway.py`: saf `local_origin` ve `attach/detach`, ayrıca gerçek WebSocket sunucusuyla yabancı Origin, ikinci panel, sahibe yanıt, kopma, yeniden bağlanma | — |
| A04 | Pençe durumu istekten okunuyordu; çekirdek sürüş kilidinde pençe yoktu | Pençe 0x1A2 telemetrisinden; çekirdek kilidinde pençe (DD93: kapalı + boş); başarısız pençe komutunun isteği geri alınır | Çekirdek testi ve uçtan uca test: depola'da bütün "aç" paketleri kaybolunca pençe kapalı kalır, sürüş hem yürütücüde hem çekirdekte reddedilir, bağlantı düzelince geç açılma olmaz | TL5 pençe kabulü |
| A05 | 8 bitlik yankı 256 gönderimden sonra her sırayla eşleşiyordu | Yankı 12 bit; bir kez yanıtlanınca kilitlenir; 255 gönderimde yanıt yoksa `arm_fault` | Uçtan uca: hold'un bütün 0x122'leri kaybolunca sahte başarı yok, tam 255 gönderimde hata; 16 bit sarımı geçen hedef normal tamamlanır | — |
| A06 | Decoder sırayı semantik kabulden önce yazıyordu | Yankı yalnız kolun aldığı komutla ilerler; reddedilen komut sırasını yakar | Çekirdek testi: yeni sıralı grafik dışı komut yankıyı değiştirmez, sırası tekrar kullanılamaz; uçtan uca seq 99 | — |
| A07 | Reset sonrası çekirdek düşük 16 bite bağlanıyor, host 32 bitlik sayaçla doğruluyordu | `request_arm()` yeni oturum açar; el sıkışma yeni oturumda telemetri doğrulanınca sayılır | Uçtan uca: 100 ve 65500'den başlayan oturumda ESP32 resetinden sonra `request_arm` bağı kurar; eski oturum telemetrisi düşer | Donanımda watchdog resetiyle (L4) |
| A08 | Belgeler güncel sayılardan geri kalmıştı | 15 A sigorta, 1,6 mm baş açıklığı, 1° açıklık taraması (4,75 mm), CG z131,1 / 36,1°, panel README'si, üç buck | `tests/check_design.py` (TL4 metni manifestle), `tests/check_markdown_links.py` | — |

## Mekanik (DD93)

| # | Karar | Kanıt (CAD/test) | Açık fiziksel kapı |
|---|---|---|---|
| M01 | İkiz dişli pençe: 16T m0,625 dişliler, çene A MG90S kornasında, çene B M3 pimde, TPU pedler. 60° açık, uçta 53,5 mm; sıkma ≈4,1 N (stall). Yalnız taranmış açık duruşlarda açılır, açıkken yalnız açık kenarlar; kavrama sonrası sürüş için depola'da bırakma | Manifest `gripper`: dişliler kavrar, çeneler avuca değmez (0–60°), 5 açık duruşta her açı ve 3 açık kenar çakışmasız, zarf \|y\| ≤ 154. `tests/check_cad.py`, çekirdek ve uçtan uca testler | Dişli deneme baskısı (boşluk), korna delik aralığı, TL5: 10–50 mm / 150 g kavrama ve 60 s tutma |
| M02 | Ek kirişleri plaka altından 8 × M3 × 10 ile insertlere; yapıştırma yok | Kiriş insertleri ve plaka delikleri CAD testinde; baskı rehberi ve vida listesi | Ek yeri sehimi gerçek baskıda |
| M03 | Sol omuz: yarıklı bilezik + TPU sürtünme pulu, ≈32 N ön yükle 0,24 N·m | Yarık, sıkma vidası, pulun göbek yüzüne oturması CAD testinde | TL5: kol yatayda 60 s tutar, elle çevrilir; pulun zamanla gevşemesi |
| Tolerans | Avucun iç yüzü 3 mm kırpıldı; beş eklem ±1° (32 köşe) → yan duvara ≥4,1 mm (önce 2,80) | Manifest `park_tolerance`, test ≥3 mm | TL4: her eklem ±1° kalibrasyon |

## Çalıştırılanlar

- `tests/README.md`'deki 34 masaüstü kontrolünün tamamı: **34/34 PASS**.
- ESP-IDF 5.3.2 Docker derlemeleri: ESP32-S3 ve ESP32-CAM **PASS**.
- CAD üretimi: 103 STEP, 74 STL, izinsiz çakışma yok; 8 duruş ve 7 kenar 1° adımla çakışmasız; kol açıklığı 1° adımla ≥4,5 mm.

## Açık kalanlar

Rapordaki üretim öncesi ve sehpa adımları (dilimleme kütlesi, E-stop DC kesme değeri, 15 A sigorta koordinasyonu, Mini560 EN eşiği, TL1–TL6, T13/T14) değişmedi ve açıktır. Orijinal CM5/STM32/ROS kapsamı A3'ün dışında kalır.
