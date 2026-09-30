# UGV-01 — Baştan sona bağımsız inceleme

29.09.2026 · İncelenen commit: `42524c9d271edaa842ca49b30e2747520887d61b`.

**Sonuç: proje tamamlanmış veya üretime/sürüşe hazır değil.** A3 Lite'ın önemli bir CAD, elektronik bağlantı ve yazılım altyapısı var. Mevcut 34 masaüstü kontrolü ve iki gerçek ESP-IDF derlemesi geçti. Buna rağmen dört yüksek, üç orta ve bir düşük öncelikli bulgu doğrulandı; ayrıca üç mekanik tasarım kapısı açık. Fiziksel T01–T20 ve TL1–TL6 sonuçları NOT_RUN. Bu rapor kod düzeltmesi veya üretim onayı değildir.

## Kapsam ve yöntem

- Git'te izlenen 453 dosyalı projenin gereksinimleri, karar kayıtları, güncel mekanik üreticisi/STEP/STL/URDF, hesapları/BOM'u, modül bağlantıları, firmware, MacBook ağ geçidi, AI yürütücüsü, paneli ve kabul prosedürleri incelendi. Oluşturulmuş görsellerin her pikseli veya her arşiv dosyasının her satırı için inceleme iddiası yoktur.
- Aktif ürün **A3 Lite / M3**: ESP32-S3, iki ESP32-CAM, MacBook üzerinde panel ve AI; dört JGA25 motor, 3S1P batarya, baskı gövde ve beş eksenli sağ kol. A0/A2 CM5–STM32–özel PCB–ROS kapsamı ayrı değerlendirildi. A3'ün kayıtlı kapsam daraltması bir regresyon olarak sayılmadı.
- Firmware, mekanik/elektrik ve uygulama için üç bağımsız inceleme yapıldı. Yazılım bulgularının tekrar üretimleri ana incelemede de çalıştırıldı. C çekirdeği gerçek kaynaklardan derlendi; motorlar ve sensör kayıtları test modelidir.
- Üretici kaynakları yalnız gerekli teknik doğrulamalar için okundu. Gerçek araç, servo, batarya veya API denenmedi; ücretli API çağrısı yapılmadı, kullanıcı anahtar/env dosyaları okunmadı.
- Testler ve üreticiler kaynak kopyasında çalıştırıldı. 230 kaynak/belge/config dosyasının başlangıç SHA-256 değerleri ile asıl çalışma ağacı karşılaştırıldı: değişiklik yok. Firmware/CAD kaynakları, DD kayıtları ve önceki inceleme raporları değiştirilmedi. Yeni teslim bu rapordur; commit/push yapılmadı.

## Code Review Results

**Scope:** mevcut projenin tamamı; aktif A3 ve arşiv kapsamının ayrımı.
**Intent:** “proje bitti” iddiasını tasarım, çalıştırılabilir kontroller ve kabul kanıtlarıyla sınamak.
**Mode:** salt okunur inceleme; bulgular raporlandı, otomatik düzeltme uygulanmadı.
**Reviewers:** firmware/protokol, mekanik/elektrik/üretim, uygulama/ağ/güvenlik; ana incelemede tekrar doğrulama ve gereksinim eşlemesi.

### Applied (safe, verified)

Yok. Kullanıcının inceleme kapsamı korundu; aşağıdaki düzeltmeler uygulanmış gibi gösterilmiyor.

### P0 — Critical

Doğrulanmış P0 bulgu yok. Bu, fiziksel güvenliğin doğrulandığı anlamına gelmez.

### P1 — High

| # | File | Issue | Reviewer | Confidence |
|---|---|---|---|---|
| A01 | `firmware/lite/esp32/main/app_main.c:58–69`, `firmware/lite/lite_core.c:29–30,57` | Eksik bağlantı anahtarı, boş HMAC anahtarıyla hareket kabulüne dönüşüyor | firmware, ana inceleme | 100 |
| A02 | `firmware/lite/vl53l0x.c:154–161` | ToF ölçüm durumunu denetlemeden hatalı mesafeyi geçerli kabul ediyor | firmware, ana inceleme | 100 |
| A03 | `software/ugv_lite/gateway.py:104–124` | WebSocket kontrol sahipliği ve Origin denetimi yok; ikinci bağlantı yanıtları devralıyor | uygulama/güvenlik, ana inceleme | 100 |
| A04 | `software/ugv_lite/vehicle.py:229–245`, `software/ugv_ai/executor.py:157–163` | Pençenin açık olması kabul edilmiş konumdan değil istenen komuttan okunuyor | uygulama, ana inceleme | 100 |

**A01 — Anahtar ayarı yokken güvenli biçimde kapalı kalınmıyor.** NVS'de Wi-Fi bilgisi bulunup `link_key` bulunmazsa `cfg.key_len=0` kalır. `settings_load()` yalnız hata günlüğü yazar; `lite_core_init()` ve `lite_core_receive()` anahtarın 32 bayt olmasını zorunlu tutmaz. Boş anahtarla imzalanmış IDLE → park onayı → ARM → DRIVE komutları kabul edildi. Model çıktısı: `key_len=0 state=2 ACT_EN=1 wheel_duty=287,287,287,287`. Fiziksel E-stop'un bırakılmış olduğu varsayılır; bu bulgu E-stop'u bypass etme iddiası değildir. `make_nvs.py`'nin doğru CSV üretmesi firmware'in eksik/bozulmuş NVS'yi reddettiğini kanıtlamaz.

Düzeltme: çalıştırılan firmware/core sınırında geçerli anahtarı zorunlu tut; yoksa bütün hareket komutlarını reddet ve aktüatörleri kapalı tut. Sıfır, kısa, uzun ve doğru uzunlukta anahtarlarla regresyon yaz; özellikle Wi-Fi var/anahtar yok kurulumunu kapsa.

**A02 — Ölçüm tamamlanması, ölçüm geçerliliği sanılıyor.** Sürücü interrupt durumunu ve mesafe baytlarını okur; `0x14` range-status alanını okumaz. Modelde iki sensöre 1200 mm ve raw status 4 (`0x14=0x20`) verildiğinde çıktı yine `1200,1200` olur. Çekirdeğin `lite_core.c:153–161` denetimi bunları açık yol sayar. ST'nin API eşlemesinde raw 4 Signal Fail'dir; PAL RangeStatus ile ham register değeri aynı numaralandırma değildir. [ST API kaynak kodu](https://github.com/STMicroelectronics/Azure-cloud-samples/blob/main/b-l4s5i-iot01a/iar/stm32l4xx_lib/Components/vl53l0x/vl53l0x_api_core.c), [ST UM2039](https://www.st.com/resource/en/user_manual/um2039-world-smallest-timeofflight-ranging-and-gesture-detection-sensor-application-programming-interface-stmicroelectronics.pdf).

Düzeltme: üreticinin geçerlilik/kalite kurallarını uygula; signal/hardware/phase ve diğer geçersiz ölçümleri ileri sürüş için güvenli engel/unknown durumuna çevir. Geçersiz örnek, eski geçerli ölçümü tazeleyerek kullanmayı sürdürmemeli. İlk ölçüm yokluğu ve 100 ms bayatlık mevcut testlerde doğru; eksik olan, I²C başarılıyken ölçümün geçersiz olmasıdır. `8190 = boş yol` varsayımı da status ile birlikte yeniden sınanmalı.

**A03 — Yerel sunucu, kontrol yetkisini bağlantıya bağlamıyor.** Gerçek localhost WebSocket sunucusuna `Origin: https://untrusted.example` ile bağlantı kabul edildi. Bu istemci `lease/ai=true`, görev ve `arm_parked` gönderebildi. İkinci bağlantı global `gateway.send` callback'ini değiştirdi; ilk operatörün mesajına verilen yanıt ikinci bağlantıya gitti, ilk istemci timeout aldı. Testte görev/araç mock'tur; fiziksel hareket veya bütün tarayıcıların internet sayfasından localhost'a erişebildiği iddia edilmiyor. Sunucunun yabancı Origin'i ve ikinci kontrol istemcisini reddetmediği doğrudan doğrulandı.

Düzeltme: izinli Origin/Host ve kontrol bağlantısının sahipliğini denetle. Kontrol lease'i, park onayı ve görev gönderimi aynı yetkili operatöre bağlı olmalı; yanıt yönlendirmesi global callback ile son bağlantıya taşınmamalı. Sahip bağlantı kopunca izin düşmeli. İki istemci, yabancı Origin, yeniden bağlanma ve bağlantı kapanması regresyonları gerekir.

**A04 — Kaybolan açma komutu sürüş kilidini aşabiliyor.** Gerçek C çekirdeğinde pençe kapandıktan sonra yalnız `0x121` paketleri düşürüldü. Host `open` istendiği anda açık gösterdi; çekirdeğin pençe darbesi 2500 µs'de kaldı. AI yürütücüsü 0,1 m sürüşü başarılı tamamladı: model mesafesi `0,1096367 m`, pençe hâlâ `2500 µs`, faults `0`. Çekirdeğin `lite_core_arm_allows_drive():263–265` kilidi kolu denetler, pençeyi denetlemez. DD90 N4'ün “nesneyi kargoda taşı/pençeyi aç” koşulu bu durumda uygulanmıyor. Mekanik çene henüz tamamlanmamış olsa da gelecekte kullanılacak güvenlik sözleşmesindeki hata şimdiden gösterilebilir.

Düzeltme: istenen pençe durumunu kabul edilmiş/komut yürütmesi yerleşmiş durumdan ayır; paket kaybında `pending/unknown` sürüşü engellesin. Açma onayı gelmeden sürüş başlatma; uygun çekirdek kilidini de değerlendir. Servo yazılım hedefi veya darbesi, fiziksel nesnenin bırakıldığının ölçümü değildir. Kaybolan açma paketi, bayat telemetri ve açılma sürerken sürüş regresyonları gerekir.

### P2 — Moderate

| # | File | Issue | Reviewer | Confidence |
|---|---|---|---|---|
| A05 | `software/ugv_lite/vehicle.py:174–192` | 256 yeniden gönderim sonunda eski düşük-bayt ACK her durumda geçerli oluyor | uygulama, ana inceleme | 100 |
| A06 | `firmware/stm32/can_protocol.c:100–106`, `firmware/lite/lite_core.c:60–68,291` | Semantik olarak reddedilen yol komutu ACK sırasını yine değiştiriyor | firmware, uygulama, ana inceleme | 100 |
| A07 | `firmware/lite/lite_core.c:74–78`, `software/ugv_lite/vehicle.py:66–83,118–120` | Lease sayacı taşmasından sonraki MCU resetinde telemetri bağı geri kurulamıyor | firmware, ana inceleme | 100 |

**A05 — Hold'a sahte başarı.** Stow → lift hareketi başladıktan sonra bütün `0x122` hold paketleri düşürüldü; diğer komutlar, lease ve taze telemetri sürdü. Host hold durumunu **10,3 s / 256 gönderim** sonra temizledi; çekirdek hold almamış, eski hedef lift'e gitmişti, ACK hâlâ `4` idi. `_answers()` içindeki `min(sent,256)` nedeniyle 256'dan itibaren her 8 bit fark geçer. Bu süre 20 s kol timeout'undan kısadır. Bulgudan grafik dışı çarpışma sonucu çıkarılmıyor; yanlış tamamlanma/hold sözleşmesi bozuluyor.

Düzeltme: tam sıra/işlem kimliği veya düşük-bayt alias oluşmadan açık başarısızlık veren sınır kullan; sürekli yeniden gönderim eski ACK'yi yeni onaya çevirmesin. 256+ gönderim ve 16 bit sarım birlikte test edilmeli. N3'ün kısa gecikme düzeltmesi korunmalı.

**A06 — ACK, uygulanmış komutun ACK'si değil.** `seq=99` ile geçersiz stow → reach_low kenarı gönderildi. `lite_core_receive=0` döndü, fakat sonraki taze `0x1A2` echo `99` oldu. Decoder sıra alanını önce değiştirir, `arm_path_command()` sonra geometrik komutu reddeder. DD90'ın mevcut “reddedilen komut yankıyı değiştirmez” testi eski sıra reddini kapsar; yeni sıra/geçersiz kenar reddini kapsamaz.

Düzeltme: tekrar/replay sırası ile gerçekten kabul edilmiş hareket ACK'sini ayır ya da semantik kabulden sonra ACK'yi commit et. Replay korumasını kaldırmadan geçersiz kenar, mevcut konumla süreksiz komut ve limp durumunda red testleri ekle.

**A07 — Resetten sonra güvenli duruyor, fakat mevcut bağlantı kurtulamıyor.** Host 32 bit lease sayacı `65543` iken taze MCU aynı oturumun kablodaki düşük 16 bitini `7` olarak başlatır. MCU telemetrisi `7` bağlamıyla imzalanır; host `65543` bekler. Doğrulama sonucu `verify_host=0`, `verify_low16=1`. İdeal 50 Hz lease hızında eşik yaklaşık **21,8 dakika**; gerçek zamanlayıcı hızı değişebilir. `request_arm()` yalnız IDLE handshake başlatır, oturumu/sayaç bağını yenilemez. Sorun otomatik tehlikeli yeniden sürüş değil, firmware watchdog/reset sonrası tekrar kullanıma dönüşün başarısızlığıdır.

Düzeltme: MCU yeniden başlama/bağ kaybı sonrasında güvenli yeni oturum ve sayaç bağını yeniden kur; taze kontrol niyeti ve park onayını koru. Eski telemetriyi kabul ederek düzeltme yapma. 65536 öncesi/sonrası MCU reseti, host reseti, eski oturum replay'i ve açık yeniden ARM birlikte sınanmalı.

### P3 — Low

| # | File | Issue | Reviewer | Confidence |
|---|---|---|---|---|
| A08 | `docs/lite_electronics_A3.md:11`, `docs/lite_mechanical_A3.md:20,60–63,97–99`, bazı alt README'ler | Güncel imalat/mimari değerleriyle eski açıklamalar birlikte kalmış | mekanik/elektrik, ana inceleme | 100 |

**A08 — Belge kapanışı eksik.** Güç tablosu 10 A sigorta derken güncel şema/BOM L14 15 A ister. Mekanik metin baş açıklığını ≥2,5 mm söyler; DD85 ve yeniden üretilen manifest 1,6 mm gösterir. Park → lift için yayımlanan 5,65 mm, üreticideki 5° açıklık örneklemesinden gelir; bu incelemenin 1° nominal taraması 4,75 mm buldu. Kol çarpışma taraması gerçekten 1° iken açıklık taraması ayrı döngüde 5°'dir. Metinler ikisini ayırmalı. Ayrıca 130,8 mm CG, güncel 131,1 mm sonucundan eski; `software/web_ui/README.md` “çalışan panel yok” derken A3 yerel sunucusu var, elektronik alt README'sindeki iki buck açıklaması güncel üç buck düzenini anlatmıyor.

Düzeltme: tarihsel A0/A2 anlatımlarını silmeden aktif A3 talimatlarını tek parametre kaynağına bağla; sigorta, CG, açıklık örnekleme aralığı ve sunucu mimarisini düzelt. Sigortayı yeni veri olmadan 10 A'e geri çevirmek veya açıklık kabulünü gevşetmek çözüm değildir. Eski incelemenin önüne eklenmiş Claude konuşması bağımsız rapor ve kapanış kaydını karıştırıyor; bu rapor o geçmişi değiştirmedi.

### Actionable Findings

| # | Issue | Route | Kabul kanıtı |
|---|---|---|---|
| A01 | Anahtar yokken hareket | manual → firmware | Eksik/bozuk anahtarla ARM/DRIVE reddi; geçerli kurulum regresyonu |
| A02 | Geçersiz ToF açık yol | manual → firmware | ST status eşlemesi; geçersiz ve bayat örneklerde ileri inhibit |
| A03 | Kontrol bağlantısı sahipliği | manual → uygulama | Yabancı Origin/ikinci istemci reddi; sahip kopunca permit düşüşü |
| A04 | Pençe açma onayı | manual → protokol/uygulama | Yalnız açma paketleri kaybolurken sürüş reddi |
| A05 | Düşük bayt alias | manual → protokol/uygulama | 256+ kayıp hold komutunda sahte başarı oluşmaması |
| A06 | Reddedilen komut ACK'si | manual → protokol/firmware | Yeni sıralı geçersiz komutta uygulanmış ACK'nin değişmemesi |
| A07 | Reset/lease epoch | manual → protokol/uygulama | Sayaç taşması sonrası güvenli yeni oturumla kurtarma; replay reddi |
| A08 | Aktif talimatların tutarlılığı | manual → dokümantasyon | Kaynaktan üretilen sayılar ve aktif/arşiv ayrımı |

## Önceden bildirilmiş fakat hâlâ açık mekanik kapılar

Bunlar yeni gizli hatalar olarak sayılmadı. Kaynak ve belgeler açık iş olduklarını zaten bildiriyor; buna rağmen tasarımın “%98/bitti” sayılmasını engelliyorlar.

| Kapı | Kanıt | Eksik olan |
|---|---|---|
| M01 — İşlevsel kıskaç | `cad/assembly/build_concept.py:548–566,750`; UGV-MECH-054 | Çeneler avuçla tek katı olarak fuse edilmiş. Pivot, hareketli çene, servo korna/link aktarımı ve ped yok. Böyle basılan parça açılıp kapanamaz; TL5 kavrama/bırakma uygulanamaz. |
| M02 — Şasi ekinin yük yolu | `build_concept.py:60–72`, `tools/print_plan.py:178` | Kiriş–plaka bağlantısı “yapıştırma ya da vida” olarak montaja bırakılmış. Seçilmiş bağlantı, delik/donanım veya yapıştırıcı/surface hazırlığı/alanı, yük ve sehim kabulü tanımlanmamış. |
| M03 — Pasif sol kolun poz tutması | `build_concept.py:629–630,751` | “Split friction collar” düz tam halkadır; yarık/sıkma vidası/ayarlanabilir sürtünme geometrisi yok. Elle konumlandırılıp pozunu tutan kolun imalat tarifi kapanmamış. |

M01 için tek hareketli çene gibi sade bir çözüm yeterli olabilir; tasarım seçimi, kuvvet hesabı, açık/kapalı CAD ve bağlantı toleransları gerekir. M02/M03 için yalnız güzel görünüş veya katıların birbirine değmemesi mekanik yük yolunun yerini tutmaz.

## Çalıştırılan kontroller ve CAD doğrulaması

| Kontrol | Sonuç | Sınır |
|---|---|---|
| `tests/README.md` içindeki 34 host komutu | **34/34 PASS** | A3 kontrolleri yanında A2/D1 arşiv regresyonları da var; 34 aktif araç özelliği veya 34 fiziksel test değildir. |
| ESP32-S3, ESP-IDF v5.3.2 gerçek Docker build | **PASS**, uygulama `0xCD510`, %20 partition boş | Donanımda flash/run yok; derleme logunda compiler warning/error yok. |
| ESP32-CAM, aynı IDF, pinli camera bileşeni | **PASS**, `0xED7E0`, %37 boş | Kamera çalışması, bağlantı hızı ve görüntü kalitesi ölçülmedi. |
| Graph/pins/hesap/CAD/baskı planı yeniden üretimi | **8/8 komut PASS** | Salt kaynak kopyasında; tekrar CAD/print/mass testleri dahil. CAD manifestinin semantik değişen anahtarı yok. |
| Oluşturulmuş dosya eşleşmesi | **67/67 STL byte eşit**; graph/pins, hesap JSON/MD, print guide ve URDF eşit | STEP metadata byte eşitliği değil; katı geçerliliği ve manifest karşılaştırıldı. |
| Nominal kol çarpışması | **7 kenar, toplam 523 örnek, ≤1°; 0 çarpışma** | Ayrık örnek, sürekli yol/tolerans/kablo garantisi değil. |
| Nominal montaj | **96 geçerli STEP parça, 0 izinsiz hacimsel çakışma** | Servo zarfı gibi referans katılar da 96 sayısına dahil; 96 imalata hazır özgün parça değildir. |
| Baskı hazırlığı | **67 STL, ≤240 mm; 34 M3 insert; mevcut kontrol PASS** | Bambu 256 mm hacmine pay bırakılmış. Dilimleme, nozzle/material kuponu ve baskı yapılmadı. |
| Park → lift açı duyarlılığı | **273 durum, 0 çarpışma** | J1 90…180°, 1°; dirsek −1/0/+1°. Diğer hatalar yok. |
| Stow/lift birleşik açı uç köşeleri | **64 durum, 0 çarpışma** | Beş eklemde ±1°'nin 32 köşesi × 2 duruş; yol boyunca bütün birleşik hatalar taranmış değil. |

**Açıklık ayrıntısı:** 1° nominal park → lift taramasında en küçük hareketli-uzuv/fixed-parça uzaklığı **4,75 mm**; 5° üretici raporunun 5,65 mm'sinden küçüktür, fakat 4,5 mm nominal kriteri hâlâ geçer. Dirsek +1° durumunda minimum **2,8845 mm**: `[179,90,1,0,0]`, bilek UGV-MECH-053 / arka çamurluk UGV-MECH-015-RR. Birleşik ±1° uç köşede minimum **1,9249 mm**: `[179,89,1,1,-1]`, aynı parça çifti. Bunlar çamurluk uzaklıklarıdır; TL4'ün özellikle yan duvara ≥3 mm kabulünün FAIL'i diye sunulamaz. Kablo, baskı sapması, servo boşluğu ve esneme eklenmediği için mekanik tolerans kapanışı verilemez.

**Yan duvar ayrıca denetlendi:** aynı 337 durumun yalnız sağ yan panel 010/011/012'ye uzaklığı hesaplandı. Tek dirsek −1°/0°/+1° boyunca minimumlar sırasıyla **7,440 / 7,500 / 4,991 mm**; 3 mm şartı bu dar hata varsayımında korunuyor. Buna karşılık parkta beş eklemin birleşik ±1° köşesinde `[179,91,1,1,1]`, UGV-MECH-054 / UGV-MECH-010--1 uzaklığı **2,7978 mm**. Bu kombinasyonda çarpışma yok, fakat **3 mm yan duvar payı korunmuyor**. Bu ölçülmüş servo hatası veya fiziksel test FAIL'i değildir; ilan edilecek açı hata bütçesi için doğrulanmış bir tasarım nitelendirme açığıdır. Gerçek hata bütçesi daha dar olacaksa bütün eklemler ve yük altında kanıtlanmalı; aksi halde açıklık artırılmalı. Yalnız dirsek kalibrasyonunu ±1° yapmak birleşik tolerans payının kanıtı değildir.

Baş tilt −30…+60° nominal 5° taramada çakışmasız; manifest minimumu **1,6 mm**. İtme çubuğunun tam hareket zarfı ve gerçek kablolar bu taramada yoktur. Parkta güç kesildiğinde kolun 1,5°'de çamurluğa temas etmesi nominal CAD sonucudur; gerçek servonun beslenmiş/darbesiz gevşek davranışı ve yeniden park prosedürü TL4 bekler.

## Hesaplar, kütle ve satın alma hazırlığı

- Araç park zarfı **330 × 308 mm**, gövde **300 × 236 mm / üst kot z210**, baş üstü yaklaşık **z361**. İlk 270 mm genişlik hedefine sapma DD72'de kayıtlı; A3/M3 revizyonudur.
- Bütçe boş kütlesi **4,58 kg**, sınır **4,6 kg**; dış rezerv **20 g**. Bu tahsis toplamıdır, tartım değildir. 0,5 kg yükle yaklaşık 5,08 kg; tahrik hesabı 5,1 kg kullanır.
- CAD baskı tahmini PETG **2249,192 g**, TPU **280,816 g**. Kütle modeli 1,2 mm kabuk/%20 dolgu; gerçek baskı planı 4–6 duvar/%25–100. Gerçek dilimleme kütlesi ve destek/fire gelmeden 3 PETG makara ve kütle sınırı kapanmaz.
- Sağ/sol kolların park CAD kütle merkezi `[37,676; −55,420; 163,050] mm`. Park + kapak yükü araç CG `[9,864; −7,855; 131,121] mm`, öne statik devrilme yaklaşık **35,963°**. Kargo dağılımında `[13,554; −8,617; 130,619] mm`, yaklaşık **34,996°**. N4'ün yalnız stow'da sürüş seçimi bu sadeleştirilmiş modelde tutarlıdır; A04 uygulama koşulunu bozar.
- Güncel 30 satırlı Lite BOM toplamı **13.478 TL**, repository'de kayıtlı 13.500 TL tavana **22 TL** pay. DD90 kullanıcı onayını kayıtlı kabul ediyor; bu inceleme o onay konuşmasını veya bugünkü piyasa fiyatlarını bağımsız doğrulamadı. Onay yeniden istenmedi. Kargo, varyant, crimp/terminal, yedek ve tahmin kalemleri yüzünden bu toplam satın alma garantisi değildir.
- Mini560, E-stop kontak bloğu, BMS ve servo/motor varyantlarının bir kısmı sınıf/genel modül olarak tanımlı. Üretici MPN, gerçek mekanik ölçü, DC kesme değeri ve güvenilir tedarik tamamlanmadan satın alma/imalat BOM'u kapanmaz.
- Tahrik hedefi A3'te **0,3 m/s**, AI **0,2 m/s**, 5° rampada **0,15 m/s**; başlangıç 1–1,5 m/s hedefi yerine kayıtlı düşük bütçeli mimari seçilmiş. 9,7 V / µ=0,3 dönüş modeli elektriksel sınıra yakındır; µ ve scrub gerçek lastik/zeminden ölçülmedi. Model PASS, gerçek halı/zeminde dönüş garantisi değildir.
- PI, anti-windup, ters yön coast, akım ve süreli TB6612 ısı modeli host testlerinde geçer. Çekirdeğin akım/ısı değerleri doğrudan akım veya sıcaklık ölçümü değildir. Yük birden kalktığında daha önce belgelenen 174 mm/s aşım ve TL2 ayarı fiziksel olarak açık; tek kanallı encoder dıştan geri sürülmeyi ayıramaz.

## Önceki N1–N8 / DD77–DD91 düzeltmeleri

| Alan | Bu incelemenin kararı |
|---|---|
| N1 — Çekirdekte ortak grafik hareketi | Host kontrolleri geçer; grafik dışı/süreksiz hareket reddi ve beş eklem ortak yol korunmuş. “Yerleşti” ölçülmüş servo konumu değildir. |
| N2 — PI / dönüş / 9,2 V tavanının kaldırılması | Mevcut host modeli geçer. Kullanıcı kararı olan tavan kaldırılması geri alınmadı. Gerçek motor/zemin/ısı ayarı açık. |
| N3 — Taze/sıralı telemetri ve hold | Kısa gecikme/reorder düzeltmesi geçer; **A05/A06 nedeniyle genel kapanış eksik**. |
| N4 — Duruşa bağlı CG ve sürüş | Stow-only grafik/CG testi tutarlı; **A04 nedeniyle pençe koşulu eksik**. |
| N5 — Servo alt gerilim/sıcaklık kabulü | 4,8 V / 55 °C ve servo ucunda ölçüm şartı belgelerde/testte var; fiziksel NOT_RUN. |
| N6 — Görüntüleyici rotası | Saf rota testi geçer; kenar ortasında kestirme yerine finish/reverse kullanılıyor. |
| N7 — Güncel sayılar | BOM/TL4 değerlerinin önemli bölümü hizalanmış; **A08 belge kalıntıları sürüyor**. |
| N8 — STL teslimi | İçerik/bbox/hacim kontrolü mevcut, 67 STL yeniden üretimle byte eşit. Kontrol tam mesh kimliği/watertightness/üretim doğrulaması değildir. |
| DD77 — Kol açıklığı | Nominal 1° çarpışma ve sınırlı ±1° duyarlılık tamamlandı; gerçek tolerans/kablo/servo esneme açık. |
| DD78 — Göz kapağı / omuz çıkışı | Geometri ve vida arayüzleri mevcut; 0,15 mm geçme ve 225° kablo halkası kupon/servis testi bekler. |
| DD79 — Baskı planı | Plan ve yönlendirilmiş STL'ler tekrar üretildi; M01–M03 yüzünden “none on hold” bütün işlevlerin imalata hazır olduğu anlamına gelmez. |
| DD91 — E-stop yarışı / PCA retry | Saf kart hesabındaki E-stop araya girme kontrolü geçer; kaynakta PCA yazma cache'i yalnız başarılı I²C yazısında değişir. Fiziksel kesme/rail/I²C süreleri kanıtlanmış değil. ToF geçerliliği için A02 açık. |

## Başlangıç gereksinimleri ve aktif A3 tamamlanma durumu

| İş paketi | Var olan | Tam kapanış için kalan |
|---|---|---|
| İlk 16 sistem çıktısı | SRS, blok diyagramı, alt sistem/boyut/kütle/tahrik/güç/iletişim/güvenlik/BOM/risk/faz/üretim yöntemi belgeleri | Güncel A3 hedefleriyle tek izlenebilir kabul baz çizgisi; eski ve aktif değerlerin ayrılması |
| Özgün mekanik CAD | Modüler gövde, teker/göbek/lastik, iç tutucular, baş/kol, STEP/STL, PN ve baskı planı | M01–M03, yük yolu/sehim, gerçek geçmeler, kablo servis hacmi, üretim resimleri/toleranslar |
| A3 elektrik | Pin map, KiCad modül bağlantı şeması, modül/rail/pin testleri, güç modeli | Tam parça seçimi, modül yerleşim/bağlantı montaj detayı, fuse/kablo/DC kesme ve ısı ölçümleri |
| Özel MCU/PWR/CM5 kartları | A0/A2 kısmi şemalar/referanslar, bazı ERC/netlist kontrolleri | Tam şema, layout, stackup/DRC, Gerber/drill/PnP/assembly; **A3 tesliminin dışında/gelecek kapsam** |
| Firmware | A3 C çekirdeği, ESP32-S3 board katmanı, ToF ve camera kaynakları; gerçek derlemeler | A01/A02/A05/A06/A07, flash/bring-up ve motor/servo/ADC/ToF nitelendirmesi |
| MacBook uygulaması / AI | UDP/HMAC gateway, yerel yürütücü, model köprüsü, görev kayıtları, sohbet/izin/STOP paneli | A03/A04/A05/A07; gerçek araç/ağ ve kontrollü API entegrasyonu |
| Başlangıçtaki tam web paneli | A3 sohbet ve güvenlik izin paneli | Canlı görüntü, ayrıntılı motor/akım/IMU/sıcaklık telemetrisi, joystick/gamepad ve analiz paneli uygulanmış değil |
| ROS 2 / SLAM / Nav2 | Paket mimarisi belgeleri ve ortak ölçüden geometrik URDF | Dokuz ROS paketi, gerçek eklem zinciri/collision/inertial/Xacro/simülasyon/SLAM/Nav2 yok; **gelecek kapsam** |
| Üretim dosyaları | Kavram STEP/STL/DXF, baskı/BOM taslağı | `CONCEPT_NOT_FOR_MANUFACTURE` durumu sürer; PN/revizyon teknik resim/tolerans/datum ve doğrulanmış montaj BOM'u yok |
| Fiziksel prototip / test | T01–T20 ve TL1–TL6 prosedürleri | Baskı, satın alma, montaj, ölçüm, ham kayıt ve imzalı kabul yok |

Orijinal CM5/STM32/özel PCB/ROS projesinin bütünü tamamlandı denemez. Onaylı A3 sadeleştirmesi kendi kapsamıyla değerlendirilse bile işlevsel mekanik ve güvenlik yazılımı kapanmamış. Kayıtlı “%98 tasarım” ya da “%46 proje” için güncel, kabul kapılarına bağlı bir payda bulunmadı; bu inceleme yeni bir kesin yüzde üretmez. `docs/design_progress.md`'deki %45 ise 24.09 tarihli eski kapsamın kaba tahminidir.

## Kapanış sırası ve fiziksel kabul

1. **A01–A04** düzeltmeleri: geçersiz anahtar, ToF kalitesi, operatör sahipliği ve kabul edilmiş pençe durumu. Ardından **A05–A07** protokol ACK/reset düzeltmeleri; A08 belge tutarlılığı.
2. **M01–M03** mekanik işlev/yük yolu kapanışı ve birleşik servo hata bütçesi. Önce gerçek satın alınacak parçanın ölçüsü ve bağlantısı, sonra STEP/STL/BOM/rehber güncellemesi. Print plan'da tamamlanmamış mekanizmayı baskıdan önce açık kapı olarak göster. 2,7978 mm birleşik hata yan duvar açıklığını 3 mm kriteriyle uzlaştır.
3. **Üretim öncesi:** dilimlenmiş kütle/fire ve CG, kupon/geçme, seçilmiş servo kornası PCD'si, E-stop DC kontak kapasitesi, 15 A sigorta zaman-akım/I²t–18 AWG koordinasyonu, Mini560 EN/akım/rail toleransı. Bütçe ve fiziksel çalışma zarfını bu sonuçlarla yeniden hesapla.
4. **Sehpa:** ilk güç/regülatör/MCU/encoder/tek teker; TL1–TL3 ve T13/T14 güvenlik; servo rail/load/park/baş/kablo ve kıskaç/kargo TL4–TL6. Güç kesmede motorlar coast eder; E-stop eğimde tutma freni değildir.
5. **Sınırlı saha:** düşük hız/boş yük → kontrollü yük, akım ve termal çalışma → kamera/ağ/telemetri. T13/T14 geçmeden yerde sürüş yok. SLAM/Nav2 ve tam CM5/STM32 mimarisi sonraki ayrı kapılardır.

### Coverage / residual risks

Model testlerinin fiziksel sensör doğruluğu, gerçek servo takibi, gerçek kablo, nominalden farklı motor, sıcak modül kaybı veya kaynaklaşmış E-stop kontak davranışını doğrulamadığı özellikle korunur. Ana hata matrisi ve T01–T20'nin eski A2 ayrıntıları A3 için birebir uygulanamaz; TL ekleriyle hangi kabulün aktif olduğu açık bir A3 test baz çizgisinde belirtilmeli. Üretim klasörlerinin boşluğu ve URDF'nin geometrik ön model olması belgelerde zaten açıklanmıştır.

## Claude'a düzeltme ve kapanış promptu

```text
UGV-01 üzerinde çalış: UGV-01.
Önce docs/review_full_2026-09-29.md, aktif A3 config/spec, DD90–DD91 ve mevcut testleri oku.
Bu bir tasarım/yazılım düzeltme görevidir; donanım yok. Gerçek API çağırma, kullanıcı env/anahtarlarını okuma,
fiziksel PASS veya üretim/sürüş onayı yazma. CM5/STM32/ROS arşivini aktif A3'e istemeden geri taşıma.
Kullanıcı kararı olan 9,2 V tavanının kaldırılmasını geri alma; CG/servo/ısı güvenlik sınırlarını gevşetme.

Öncelik A01,A02,A03,A04; ardından A05,A06,A07 ve A08.
Her bulgu için önce mevcut kaynakta hatayı gösteren küçük regresyonu çalıştır, sonra kök nedeni düzelt.
A01: firmware/core, Wi-Fi var fakat link_key yok veya uzunluğu yanlışken hareketi reddetmeli.
A02: ST ham range-status/PAL kalite kurallarına göre geçersiz ToF örneği ileri sürüşü kapatmalı;
       önceki geçerli mesafeyi hatalı yeni örnekle tazeleme.
A03: Origin/Host ve tek kontrol sahibi; ikinci istemci lease/park/task ya da yanıt yönünü devralamamalı.
       Sahip kopunca permit düşmeli. İzinli panel yeniden bağlanmasını da test et.
A04: requested gripper ile kabul edilmiş/yerleşmiş durumu ayır. Yalnız 0x121 açma paketleri düşürülünce
       pençe hâlâ kapalı/pending iken drive/turn reddedilmeli. Fiziksel bırakmayı varsayma.
A05: 256+ kayıp0x122 hold gönderiminde eski ACK ile başarı oluşmamalı. 20 s timeout ve sıra sarımını kapsa.
A06: yeni seq99 ile stow→reach_low reddedildiğinde applied ACK değişmemeli; replay sırasını da koru.
A07: 65536 lease eşiği sonrası MCU resetinde güvenli yeni oturum kurulmalı; yalnız request_arm ile
       kurtarma mümkün olmalı veya açık kurtarma akışı sağlanmalı. Eski telemetri/replay kabul edilmemeli.
A08: 10A/15A talimatı, 1,6mm baş açıklığı, kol çarpışması1°/açıklığı5° ayrımı, güncelCG ve aktifREADME'leri hizala.

M01: pençenin hareketli çenesini, pivot/korna aktarımını, kuvvet ve açık/kapalı geometrisini tasarla.
M02: şasi ekinin bağlantısını kesinleştir; seçilen yöntemin delik/donanım veya yapıştırma alanı/proses/yükünü modelle.
M03: pasif sol kolun poz tutma elemanını mekanik olarak tamamla.
Mevcut yaklaşık bütçeyi ve baskı hacmini korumaya çalış; hesap göstermeden yeni kritik ölçü/parça seçme.
Gerçek dilimleme/tartım gelmeden4,58kg veya filament tahminini ölçülmüş sayma.

CAD'i güncelleyen her değişiklikte graph→CAD→printplan→viewer/URDF ve BOM/rehber tutarlılığını yeniden üret.
Mevcut34host kontrolünü ve ikiESP-IDFbuild'i çalıştır; yalnız PASS toplamı ile kapanış ilan etme:
bu rapordaki karşı örneklerin artık güvenli davranışı verdiğini ayrıca göster.
1°nominal kol taraması, uygun ±1°duyarlılık ve artık işlevsel çene hareket zarfını yeniden kontrol et.
Parkta[179,91,1,1,1] köşesinde çene054/yanpanel010--1 açıklığı2,7978mm:3mm şartını gerçekçi,
belgeli bütün-eklem hata bütçesi veya geometri değişikliğiyle sağla; fiziksel kabulü gevşetme.
Kararları design_decisions.md'ye yeni kayıtla ekle; eski bağımsız rapora konuşma ekleyerek değiştirme.
Son teslim: değişen dosyalar, her A/M kimliği için test/hesap kanıtı ve açık fiziksel kabul kapıları.
```

## Tekrar üretim kayıtları

34 host ve iki Docker komutunun kalıcı tarifi `tests/README.md`'nin ilk komut bloğudur. Ek inceleme dosyaları aşağıda yerel `/tmp` yardımcıları olarak verilmiştir; kalıcı ürün testi veya donanım kanıtı değillerdir. Düzeltmede senaryolar ilgili mevcut testlere taşınmalıdır.

```sh
# Çalışma dizini UGV-01; gerçek C çekirdeği + ağ/motor test modeli.
python3 /tmp/ugv_full_protocol_repro.py   # A04,A05,A06
python3 /tmp/ugv_full_gateway_repro.py    # A03; localhost test sunucusu, mock araç/API yok

cc -std=c11 -Wall -Wextra -Werror /tmp/ugv_audit_emptykey.c firmware/lite/lite_core.c firmware/lite/arm_path.c firmware/lite/lite_link.c firmware/lite/hmac_sha256.c firmware/stm32/can_protocol.c firmware/stm32/servo_control.c firmware/stm32/light_bar.c -lm -o /tmp/ugv-audit-emptykey
/tmp/ugv-audit-emptykey                  # A01
cc -std=c11 -Wall -Wextra -Werror /tmp/ugv_audit_tofstatus.c firmware/lite/vl53l0x.c -o /tmp/ugv-audit-tofstatus
/tmp/ugv-audit-tofstatus                 # A02
cc -std=c11 -Wall -Wextra -Werror /tmp/ugv_audit_leasewrap_reset.c firmware/lite/lite_core.c firmware/lite/arm_path.c firmware/lite/lite_link.c firmware/lite/hmac_sha256.c firmware/stm32/can_protocol.c firmware/stm32/servo_control.c firmware/stm32/light_bar.c -lm -o /tmp/ugv-audit-leasewrap-reset
/tmp/ugv-audit-leasewrap-reset           # A07
```

Ana kontrol logları ve kaynak kopyası: yerel geçici klasör (yol yayında gizlendi); `checks.json`, `builds.json`, `regen.json`, `source_sha256.json` ve ilgili log klasörleri. Açı taraması: `/tmp/ugv-full-tolerance-20260929.{py,json,log}`; yan duvar ayrımı `/tmp/ugv-full-tolerance-wall-20260929.{py,json,log}`. Temel gözlenen çıktı:

```text
host checks:34/34 PASS; ESP32-S3:PASS; ESP32-CAM:PASS
emptykey:key_len=0 state=2 ACT_EN=1 wheel_duty=287,287,287,287
tof:range_status=4(signal fail),fresh output=1200,1200mm
gripper:host=open,corepulse=2500; driveok=True; distance=0.1096367386m; faults=0
hold:cleared=True elapsed=10.3s commands_sent=256 host_pose=lift oldecho=4
invalidedge:accepted=0 telemetryecho=99
reset:hostlease_ext=65543 corelease_ext=7 verify_host=0 verify_low16=1
websocket:untrustedOrigin accepted; ownerreply sentto secondclient; ownerTIMEOUT
```

> **Verdict:** Tasarım/entegrasyon kapanışı açık.
>
> **Reasoning:** Test ve derlemeler önemli bir temel sağlıyor; A01–A07 gerçek yazılım sözleşmesi açıkları, M01–M03 işlevsel mekanik eksikler ve tamamı NOT_RUN fiziksel kabul varken “bitti” sonucu desteklenmiyor.
