# DD92–DD93 doğrulamasının kapanış kaydı — 01.10.2026

[Bağımsız doğrulama raporundaki](review_dd92_dd93_2026-09-30.md) açık bulguların kapanışı. Rapor ve `review_evidence/dd92_dd93_2026-09-30/` betikleri değiştirilmedi. Karar: [DD94](design_decisions.md). Önceki kapanış: [29.09 kaydı](review_full_closure_2026-09-29.md).

Her karşı örnek önce raporun betiğiyle mevcut kodda yeniden üretildi (hepsi doğrulandı), sonra düzeltildi ve güvenli davranış kalıcı teste taşındı. **Üretim, montaj veya sürüş onayı değildir.** T01–T20 ve TL1–TL6 NOT_RUN.

## Bulgular

| # | Yeniden üretim (önce) | Düzeltme | Kanıt (sonra) | Açık fiziksel kapı |
|---|---|---|---|---|
| R01 | `tof_invalid.c`: ham 4/6/9 + 8190 → `8190,8190` (açık yol) | Ham 11 = mesafe (≤8189); sinyal/faz hatası + menzil dışı = `UGV_TOF_NO_TARGET` (0xFFFF, "kör"); gerisi 0. Çekirdek kör iken ileriyi 100 mm/s ile sınırlar (0x1A0 bit5); yürütücü kör 0,3 m'den sonra durur | `tests/vl53l0x_test.c`: 19 durum/mesafe çifti, 8190/8191 dahil, her biri eski geçerli ölçümü düşürür. `tests/lite_core_test.c`: 0xFFFF'de 100 mm/s, geri serbest, 0'da dur. `tests/check_lite_gateway.py`: gerçek çekirdekle 0,3 m'de durur, host 0,3 m/s istese de ≤0,12 m/s. Rapor betiği artık `65535,65535` verir | TL5: açık alanda, siyah ve cam hedefte ham durum kodu; sürünme davranışı |
| R02 | `gripper_park_open.c`: park + ARM sonrası pençe 6000 / 2167 µs; `gripper_empty_reset.c`: reset sonrası `empty=1`, sürüş izinli | Açılış/reset'te "boş" değil. Güç, kol parkta ve pençe kapalıyken düşmediyse kol ve pençe "bilinmiyor", ikisine de darbe yok. 0x123 = kol parkta **ve** pençe kapalı ve boş (bayt 1); onay pençeyi kapalı yapar, host isteği "kapat"a döner. Yalnız depola'da kapanış "boş" | Çekirdek testi: hazır'da açık + IDLE → darbe yok, yalnız kol beyanlı onay reddedilir, tam onayla pençe 1500 µs; kavrama + watchdog → sürüş yok, tam onayla serbest; hazır'da aç-kapat "dolu". Uçtan uca: izin kaybı ve yeniden kurmada pençe darbesiz, onaydan sonra kapalı. Ağ geçidi: alan yoksa onay reddedilir. Rapor betikleri artık kapalı pençe ve sürüş yasağı verir | TL5: açık pençeyle güç kesme, operatör onayı |
| R03 | `software_recheck.py`: 17. denemede `seq=4097, echo=0, ok=True` | MacBook çekirdeğin aldığı son komutu (`ack`) izler, oturumda ondan en fazla 255 ileri gider (hedefler arasında da); hata oturum boyunca kilitli, yeni görev yeni oturum | Uçtan uca: 17 art arda hedef hepsi hata, `ack` 0, kol parkta; 40'ar gönderimde kesilen hedefler toplamda 255'te hata; `request_arm` sonrası kol yine çalışır. Birim: `ack` penceresi 16 bit sarımında. Raporun betiği kaldırılan iç alan `answered`'e baktığı için artık çalışmaz; senaryo kalıcı testte | — |
| R04 | Sol 050/051 arası 1,0 mm boşluk, sol B'nin bağlandığı parça yok | Sol kol sağın arayüzleriyle taklitlerle kurulur: twist (066 + kapak 058 + adaptör 059 + halka 075), dirsek/bilek (067/068, kulak insertleri, korna diski, burç 076/077 + M4), dönüş (069, merkez M3 + iki pim), pençe (074, çene A 2 × M2) | `tests/check_cad.py`: 14 bağlantı çiftinin her biri temas ediyor (mesafe < 0,01 mm), sol kolda servo zarfı yok, izinsiz kesişim yok. Vida listesi ve baskı planı sol kol satırlarını içerir | TL5: eklemler elle zorlanınca oynamaz |
| R05 | Çene B vidanın altında, eksenel tutma ile dönme ayrılmamış | Ø5/Ø3,2 × 7,5 naylon burç; M3 × 16 + yaylı rondela burcu direğe sıkar (0,4 N·m); çene Ø5,2 delikle burçta döner, 0,5 mm eksenel boşluk | CAD testi: burç ölçüleri, çene deliği, M3 geçişi; çene 0–60° burca değmeden döner (manifest `jaw_self_hits` boş) | TL5 kuponu: son montajda 0–60° serbest dönüş ve boşluk |
| R06 | Yayınlanan kavrama noktası pedlerden ≈18 mm farklı | Kavrama noktası pedlerin buluştuğu yüzün ortası (bilek + 101 mm, kol düzleminden 16,5 mm içte, 5 mm yukarıda); kargodaki nesne kutunun tabanında | CAD testi: parktaki ped temas yüzünün ortası manifestteki noktayla < 0,1 mm; öne-orta (281,1 / −11,8 / 53,5) ve depola (108,5 / −19,0 / 231,4), raporun ölçtüğüyle aynı. Kütle modeli bu noktaları kullanır | TL4: kavrama noktasının cetvel/kamerayla ölçümü |
| G01 | Hesap yalnız cıvata kesmesiydi | Serbest cisim hesabı: kiriş 3,9 MPa; iki ayrı idealize yol (her biri tam moment, toplanmaz): kuvvet çifti → 88 N kesme, 5,8 MPa ezilme; prying → 47/23 N cıvata çekmesi, plaka yerel 5,6 MPa; insert ≈6 kat (300 N ölçülmemiş varsayım) | [Lite mekanik](lite_mechanical_A3.md) tablo satırı ve DD94 | İnsert çekme deneyi (katmana dik), ek yeri sehimi |

## Çalıştırılanlar

- `tests/README.md` masaüstü takımı: **34/34 PASS**.
- ESP-IDF 5.3.2 Docker: ESP32-S3 ve ESP32-CAM **PASS** (uyarısız).
- CAD: 115 STEP, 84 baskı parçası, 50 insert, izinsiz kesişim yok; 8 duruş ve 7 kenar 1° çakışmasız; açık çene taramaları temiz; park toleransı 4,1 mm.
- Raporun betikleri: R01 ve R02 güvenli sonuç verir; R03 senaryosu kalıcı testte; A03 WebSocket betiği hâlâ doğru sonuç verir.

## Bilinçli kararlar ve sınırlar

- **R01:** "Hedef yok" okumasında hiç ileri gitmemek açık odada robotu kullanılamaz yapardı. Bunun yerine sınırlı sürünme seçildi: 100 mm/s, hareket çağrısı başına 0,3 m, sonra yeni görüntüyle bakış (toplam sınır değil; DD95'ten beri panel kör modu bildirir). Koyu ya da cam bir hedef de "hedef yok" okunabilir; bu risk operatör denetimi ve fiziksel E-stop ile kabul edildi, TL5'te ölçülür.
- **R02:** Nesnenin gerçekten bırakıldığını ölçen sensör yok; "boş" işareti bir servo modeli ve operatör beyanıdır.
- **Kütle:** kollar grubunun baskı payı 12 g'a indi; PETG %25 payla 2,92 kg, üç makaraya sınırda.
