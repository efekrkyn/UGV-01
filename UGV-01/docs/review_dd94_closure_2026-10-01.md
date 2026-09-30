# DD94 bağımsız kapanış incelemesinin kapanış kaydı — 01.10.2026

[Codex'in DD94 incelemesindeki](review_dd94_2026-10-01.md) bulguların kapanışı. Rapor ve `review_evidence/dd94_2026-10-01/` kanıtları değiştirilmedi. Karar: [DD95](design_decisions.md). Önceki kapanış: [DD92–DD93 kapanışı](review_dd92_dd93_closure_2026-10-01.md).

**Üretim, montaj veya sürüş onayı değildir.** T01–T20 ve TL1–TL6 NOT_RUN.

## Sürüm sınırı

Codex'in incelediği ara sürüm eksikti. Nedeni, Codex'in eklenti kopyasındaki bir Stop kancası: `auto-checkpoint.sh`, 01.10 00:47:22'de `git stash push -u` ile bütün işi stash'e aldı ve geri uygulamadı (kayıt: `~/.claude/logs/checkpoints.log`). Son DD94 sürümü bu stash'ten `git stash apply` ile eksiksiz geri yüklendi. İzlenen dosyalar stash'le birebir aynı, kapanış belgeleri ve kütle testi düzeltmesi dahil. Stash yedek olarak duruyor. Codex'in betikleri bu son sürümde yeniden çalıştırıldı ve üç bulgu burada da doğrulandı.

## Bulgular

| # | Yeniden üretim (son DD94) | Düzeltme | Kanıt (sonra) | Açık fiziksel kapı |
|---|---|---|---|---|
| #2 | `repro_unknown_claw.py`: gevşek kol, hazır → aç → disarm → rearm → kapat: `ok=True`, `gripper=closed`, pençe darbesi 0 | Gevşekken çekirdek pençe komutunu almaz (model hedefi de değişmez). Gevşeme "boş"u siler, gevşekken "boş" üretilmez. 0x1A2 bit0/2/3 gevşekken 0. MacBook "unknown" okur, yürütücü istek göndermeden "limp" hatası verir | `tests/lite_core_test.c`: gevşek kapatmada darbe 0, hedef değişmez, "boş" yok, telemetri yalnız bit1. `tests/check_lite_gateway.py`: aynı akış gerçek çekirdekle `ok=False` ("limp"), pençe darbesi 0, durum "unknown", `gripper_empty=False`; park onayından sonra kapalı 1500 µs. Codex betiği artık `ok=False` ile düşer | TL5: gevşek kolda pençe komutu verilince pençe oynamaz |
| #3 | `repro_rearm_telemetry_race.py`: eski oturumda doğrulanan DRIVING paketi yeni oturumda `armed=True`, yeni oturumun IDLE ext1 paketi reddedildi | `pump()` soketi kilit dışında okur; doğrulama ve kabul `request_arm()` sıfırlamasıyla aynı kilit altında. Ek: `disarm()`/`request_arm()` teker hedeflerini sıfırlar | Gateway testi iki thread ile: doğrulama sırasında `request_arm()` bekler; sonra durum boş, `last_ext` boş, `armed=False`; yeni oturumun ext0/1 paketleri kabul (IDLE, `last_ext=1`). Eski `vehicle.py` ile aynı test kırmızı. Teker hedefi disarm ve rearm'da 0. Codex betiği artık eski paketi kabul etmez | — |
| #1 | Duruş tablosu eski kavrama koordinatları (park −151/−138/163, öne-orta 265/−10/45); 96 mm "kavrama merkezi" | Tablo manifestin `grip_mm` değerleri (8 duruş, "kaldır" dahil); 96 mm kinematik nominal, gerçek nokta bilek + 101 mm, ofsetli | `tests/check_cad.py`: tablo ile manifest ≤0,05 mm, satır sayısı = duruş sayısı; eski öne-orta değeriyle kırmızı | TL4: kavrama noktasının cetvel/kamerayla ölçümü |
| R04 (açık) | Twist taklidi (066) cepte +0,94°/−2,88° dönüyordu: dış yanda kapağa 2,5 mm | Taklit cebi kapak tarafı dahil her yanda 0,2 mm boşlukla doldurur (A değişmedi). Kabul ±1° (TL4 eklem bütçesi) | CAD: nominal çakışma 0; ±1° döndürünce A ya da kapakla 118 mm³ çakışma (manifest `left_twist_play`); STEP'te 066–A ve 066–kapak 0 < mesafe ≤ 0,25 mm. Nominal boşluk ≈0,4° | TL5: basılı taklidin cepte elle dönmesi ≤ ±1° |
| R01 (açık) | Panel kör sürünmeyi göstermiyordu | Gateway kör moda girişte ve çıkışta panele birer durum mesajı gönderir. 0,3 m çağrı başınadır, toplam sınır değildir; belgeler buna göre | Gateway testi: kör girişte bir mesaj ("kör", "0,3 m"), tekrarda yok, çıkışta "bitti" | TL5: koyu/cam hedefte kör mod ve panel mesajı |
| G01 (ifade) | Kuvvet çifti ve prying toplanıyor gibi okunuyordu; 300 N ölçüm gibi | İki ayrı idealize yük yolu, her biri tam moment, toplanmaz; 300 N ölçülmemiş varsayım | [Lite mekanik](lite_mechanical_A3.md) tablo satırı, DD95 | İnsert çekme ve ek yeri sehimi deneyi |

## Çalıştırılanlar

Sıra: CAD → baskı planı → görüntüleyici → ESP-IDF (tek başına) → masaüstü takımı.

- **CAD:** 115 STEP, izinsiz kesişim yok, 8 duruş ve 7 kenar çakışmasız, park toleransı 4,1 mm, açık çene taramaları temiz, sol twist oyunu yukarıdaki gibi.
- **Baskı ve görüntüleyici:** 84 baskı parçası, 50 insert; görüntüleyici 115 parça, 290.956 üçgen; rota testi 3/3.
- **Kütle:** kollar 710 g (tahsis 720 g, pay 10 g; hesap, tartım değil); PETG 2.337 g; öne devrilme 36,1°.
- **ESP-IDF 5.3.2 Docker, son firmware değişikliğinden sonra:** ESP32-S3 rc=0, imaj 0xcd7a0 bayt (%20 boş); ESP32-CAM rc=0, 0xed7e0 bayt (%37 boş). Derleyici uyarısı yok.
- **Masaüstü takımı:** `tests/README.md` listesi, bu belge yazıldıktan sonra 34/34 PASS.
- **Codex betikleri:** ikisi de artık hatalı davranışı üretemiyor. Pençe betiğinde `ok=False` / "limp"; yarış betiğinde eski paket kabul edilmiyor.

Kaynak SHA-256 (ilk 16 hane):

| Dosya | SHA-256 |
|---|---|
| firmware/lite/lite_core.c | e3198c7fdecebe37 |
| firmware/lite/lite_core.h | 451af129545f6e18 |
| firmware/lite/vl53l0x.c | d1c5494c5e7595ae |
| software/ugv_lite/vehicle.py | afaf8e3f6a683855 |
| software/ugv_lite/gateway.py | e9594ba04a55d797 |
| software/ugv_ai/executor.py | 8e582791e49530bf |
| cad/assembly/build_concept.py | ff1469ad75bd345b |
| cad/assembly/manifest.json | eafe0fc4dca79e65 |
| tests/lite_core_test.c | bdb73240d7b6d24c |
| tests/check_lite_gateway.py | a0eecd7ff61d3208 |
| tests/check_cad.py | 1eab9faf77ba9d52 |

## Kararlar ve sınırlar

- **Link kontrolü:** Codex raporu kaynakları geçici bir dizine mutlak yollarla bağlıyor. Rapor değiştirilmedi; `check_markdown_links.py` artık yalnız depo içi göreli bağlantıları denetliyor, mutlak yollar depo dışı sayılıyor.
- **Kör sürünme:** çağrı başına 0,3 m ve her sonuçta yeni görüntü, bilinçli politikadır. Sürekli körlükte toplam mesafe kilidi eklenmedi; istenirse yeni bir politika olarak eklenir.
- **Pençe "boş" bilgisi:** hâlâ servo modeli ve operatör beyanıdır, sensör değildir. #2 düzeltmesi yalnız darbe gitmeyen pençenin başarı sayılmasını kapatır.
- **Fiziksel kabul yok:** baskı anizotropisi, insert çekme, burç sürtünmesi, omuz ön yükü, servo sapması, termal sınırlar ve gerçek yüzeyde ToF T/TL testleriyle ölçülmeden kabul edilmez. Nominal açıklıklar bu testlerin yerine geçmez.
