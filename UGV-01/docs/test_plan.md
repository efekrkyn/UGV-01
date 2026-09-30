# UGV-01 — Aşamalı doğrulama ve kabul planı

Revizyon A / 2026-09-22. **Planlanan testler; hiçbir donanım testi yapılmış değildir.** Sayısal kabul sınırları tasarım hedefidir. Parça verisi veya risk incelemesi daha dar sınır gerektirirse dar sınır uygulanır ve revizyon kaydedilir. Bir ölçüm yoksa sonuç PASS yazılmaz.

## Ortak test koşulları ve sıra

Test kimlikleri kullanıcının istediği 20 başlıkla aynıdır. Uygulama sırası güvenlik için farklıdır: T01→T02→T03→T04→T05→T06→T07→T08→T09; **T13 ve T14 sehpa üzerinde başarılı olmadan yerde sürüş yoktur**. T10 önce sehpa, sonra sınırlı saha; T11/T12/T15 yük ve enerji; T16 hareket; T17/T18 entegrasyon; T19/T20 V3/V4 kapılarıdır. E-stop ve iletişim kaybı her önemli güç/firmware değişiminden sonra tekrarlanır.

Başlangıç yapılandırması: 8 kg azami brüt, 0,8 m/s hız sınırı; 4×12 V Pololu70:1 #4754 motor adayı, 120 mm teker; P45B4S2P9 Ah batarya. Mekanik parçalar, korumalı teker sehpası ve kablo sabitlemeleri monte edilir. İlk elektrik testinde hücre paketi yerine akım sınırlı laboratuvar kaynağı kullanılır. Elektronik kısa devre testleri hareketli araçta veya korumasız Li-ion paket üstünde yapılmaz; özel akım sınırlı test düzeneği kullanılır.

Her kayıtta: test/ürün seri no; kişi/tarih; git commit ve firmware hash; PCB/CAD/BOM revizyonu; cihaz seri no ve kalibrasyon tarihi; ortam sıcaklığı; batarya/hücre voltajı/SoC; yük ve ağırlık merkezi; ölçüm yöntemi/belirsizlik; ham CSV/osiloskop dosyası; ön şart; beklenen ve gerçek sonuç; PASS/FAIL/BLOCKED/NOT_RUN; sapma ve düzeltme bulunur. Ölçüm belirsizliği dahil sınırın aşıldığı durum FAIL'dir. Belgelenmemiş sapma kabul sayılmaz.

**Ortak durdurma:** koku/duman, beklenmeyen hareket, hücre şişmesi, sıcaklık veya akım sınırı aşımı, açık koruma, gevşek şasi/teker, sensör güven kaybı, E-stop işlevsizliği. Batarya servis izolasyonu, teker takozu ve bağımsız emniyet halatı testi yapanın ulaşabileceği yerde olmalıdır. Ölçüm cihazı toprak klipsi ile H-köprü çıkışı kısa devre edilmez; uygun diferansiyel/izole prob kullanılır.

## T01 — Power-on test

- **Amaç:** ilk enerji verme, ters polarite koruması, kısa devresiz montaj, ayırıcı ön testi/ön şarj ve resetlerde hareketsizliği doğrulamak; F03/F20.
- **Ekipman:** mikroskop, DMM, direnç ölçer, akım sınırlı kaynak, osiloskop ve diferansiyel/akım probları, termal kamera; motor yerine dirençli yük ve ayırıcı arıza jigi.
- **Prosedür:** enerjisiz polarite, lehim, sigorta ve güç-GND direnci kontrolü; J-PWR/J-SIG demetinde pin↔pin her damarın sürekliliği, komşu pin izolasyonu, iki GND sürekliliği ve yanlış sokete takılamama kontrolü; diferansiyel SCL/SDA çiftlerinin kendi içinde bükümlü ve P/N sırası doğru olduğunu doğrula. E-stop basılıyken düşük akım limitiyle besle; nominal aralığa kademeli çık. E-stop bırakılmış ama ARM edilmemiş durumda `VBAT`, `MID`, `ACT_BUS` ve test/bleed kumandalarını kaydet; K1-kapalı, K2-kısa ve ön şarj FET'i-kısa arızalarını **ayrı** jig deneylerinde K1'e kapatma komutu verilmeden tanılat. Sağlıklı devrede test enjeksiyonundan sonra K1→K2 çevresi 470 Ω ön şarj→K2 sırasını yükselen gerilim ve akımla izle; K1'in boş 4700 µF'e doğrudan kapanmadığını göster. Ön şarj FET'i-açık veya ACT bleed-açık arızasında timeout/fault dene; test anahtarı-kısa arızasını fiziksel NC açıkken dene. 20 aç/kapa ve brownout döngüsü; reset/bootloader/SWD durumlarını dene. PWR ve MCU'yu sırayla tek başına besleyerek J-SIG status/diferansiyel tampon hatlarından güçsüz raylara geri beslemeyi ölç. Ters polariteyi yalnız giriş koruma devresi sınırları içinde akım sınırlı jig ile dene. İlk arıza deneyleri yalnız düşük enerjili dummy yükte yapılır.
- **Ölçülecek:** demet sürekliliği/izolasyonu, ilk akım ve K1/K2 kapanış inrush tepe/süresi, test akımı, `VBAT/MID/ACT_BUS` gerilimleri ve süreleri, ön şarj/bleed direnç sıcaklığı, güçsüz 3,3 V ray gerilimi ve enjeksiyon akımı, kaçak akım, ray gerilimleri, enable seviyeleri, K1/K2 durumu, reset nedeni.
- **Beklenen:** mantık kontrollü açılır, aktüatörler enerjisiz, yalnız SELF_TEST→IDLE; otomatik hareket yok.
- **Kabul:** iki demette tüm pinler doğru eşleşir, komşu pinler izoledir, iki pozitif güç pini fiziksel olarak çapraz ayrılmıştır ve güç/sinyal soketleri eşleşmez; 20/20 döngüde motor/servo sürme darbesi yok; pasif çıkışlar mantık beslemesi yokken de pasif; güçsüz MCU 3,3 V rayı giriş koruması üzerinden çalışır seviyeye çıkmaz, enjeksiyon akımı seçilen IC sınırının altındadır; giriş/ray ölçümleri yayınlanmış tasarım toleransında; K1/K2/ön şarj arızası K1'i kapatmadan ARM'i engeller; sağlıklı ön şarjda K2 kapanmadan `MID−ACT_BUS` ≤1 V ve K1/K2 kapanış akım/gerilimi seçilen parçaların ölçülmüş sınırları içindedir; ters giriş iç rayları ters beslemez. Enjeksiyon sınırı, analog tanı eşikleri, toleranslar ve K1 inrush/kontak limiti şematik/veri sayfasında belirlenmezse BLOCKED.
- **PWR P0 şema karşılığı (24.09.2026):** test penceresi netlist değerleriyle sağlıklı 11,11–15,24 V, K2/ön şarj kısa 1,46–2,35 V; `PWR_K1_FB`/`PWR_K2_FB` eşikleri 0,96·üst ray + 0,15 V. Bu değerler ADC/karşılaştırıcı ölçümüyle doğrulanır; sağlanmazsa BLOCKED.
- **Başarısızlık:** herhangi beklenmedik etkinleştirme, kalıcı kısa devre, aşırı ısınma, boş bulk'a K1 doğrudan kapanması, arıza jiginde K1 kapanması, belirsiz feedback veya yeniden arm. Ray/tanı/kontak sınırları henüz tanımlanmamışsa BLOCKED.

## T02 — Regulator test

- **Amaç:** CM5/sensör raylarının motor yükünden bağımsız kararlılığı ve ölçüm doğruluğu; F12/F17.
- **Ekipman:** programlanabilir kaynak, elektronik yük, güç analizörü, diferansiyel ve kısa topraklı prob, termokupllar.
- **Prosedür:** 12,0–16,8 V giriş boyunca 5 V, 12 V ve servo rayında %0/%25/%50/%100 yük; eşzamanlı yük adımı; 5 V üzerinde CM5 açılış yükü; motor-bus darbeli yükü. J-PWR üzerinden 15 A motor + 2 A kontrol zarfına kadar korumalı dummy yükle iki GND damarının akımını ve MCU referans kaymasını ölç; her GND açık devresini enerjisizken break-out jig üzerinde ayrı kurup kalan tel/kontak sıcaklığını dengeye gelene dek izle. Açık/short sense kablosu jig ile uygulanır. Dump/clamp enerji testi önce sentetik akım kaynağıyla yapılır.
- **Ölçülecek:** regülasyon, ripple, yük adımı undershoot/overshoot, verim, her J-PWR GND damarının akımı/MCU referans kayması, ADC/CAN/IMU hata sayısı, J-PWR krimp ve tel sıcaklık artışı, V-sense hatası, clamp/trip eşiği.
- **Beklenen:** compute reset olmaz; raylar tüketici veri sayfası sınırlarında; aşırı gerilim kesme ve dump bağımsız çalışır.
- **Kabul:** ön hedef CM5 konnektöründe 4,9–5,2 V ve ripple≤100 mVpp, transiyentler CM5 izin sınırlarını aşmaz; 12 V rayı ±%5 yalnız seçilen topolojinin tüm giriş aralığında sağlayabildiği yükte; güç bütçesinde belirtilen sürekli yükte 30 dakika kararlı; voltaj ölçümü≤%1; clamp nominal17,8 V/trip18,5 V tolerans bütçesi doğrulanır.
- **Başarısızlık:** CM5 reset/undervoltage, tüketici abs-max'a yaklaşan transiyent, kararsız/hiccup regülatör, sense arızasıyla izin devamı, tek GND açıkken üretici konnektör/IC sınırının aşılması veya başka kablodan ölçülmemiş paralel dönüş. Dönüş akımı/referans kayması için kabul sınırları PCB tasarımında tanımlanmazsa BLOCKED. 12 V buck-only seçimi 12 V girişte gereksinimi sağlayamıyorsa topoloji veya gereksinim revize edilir.

## T03 — STM32 bring-up

- **Amaç:** boot, çevrim zamanı, pin güvenliği, IWDG ve harici watchdog'un gerçek bağımsızlığı; F07/F20.
- **Ekipman:** SWD probe, osiloskop/logic analyzer, fault-injection debug build, akım sınırlı kaynak.
- **Prosedür:** clock/reset ve BOR ayarlarını doğrula; GPIO pasifliğini açılıştan izle; SWD ile durdur; ana döngü, bir ISR ve sensör görevi ayrı ayrı dondurulsun; kontrol timerı çalışırken görev çökmesini de uygula; config CRC bozulmasını ve reset nedenini dene. J-SIG üzerinde `MCU_RUN_REQ`, `MCU_WDI` ve `PWR_ACT_EN` hatlarını tek tek açık devre yap; PWR→MCU status hatları yüksekken MCU kontrol beslemesini kesip geri beslemeyi ölç. [100 pF CWD watchdog adayı](watchdog_design.md) için 3,3 V açılış/brownout ve `WDO/ENOUT/PGOOD` sinyallerini birlikte kaydet; `EN` veya `SET1` tekil Low enjeksiyonunda aktüatör izninin açılmadığını doğrula. PWR akım sensörü yerel I²C hattında SDA-Low, diferansiyel çiftte P/N swap ve tek damar açık arızalarını uygula; zaman aşımı/bus recovery güvenlik çevrimini kilitlemesin. Motorlar bağlı olmadan başla.
- **Ölçülecek:** 1 kHz kontrol çevrimi süresi/jitter, worst-case execution, son geçerli WDI→`WDO` Low ve kesicilerin açma süresi, CWD gerçek değeri, 3,3 V/PGOOD açılış sırası, stack high-water, reset nedeni.
- **Beklenen:** sağlıklı çevrim dışında watchdog beslenmez; reset sonrası hareket izni kalmaz.
- **Kabul:** başlangıç hedefi 1 ms çevrim, ±50 µs tetik jitter ve ≤500 µs worst-case işlem; iki ardışık deadline kaçırma FAULT; harici watchdog son sağlıklı darbeye≤100 ms trip +≤50 ms kaynak ayırma; MCU/IWDG kilitlense de dış yol çalışır. Brownout/EN/SET1 denemelerinin tamamında SAFE_GATE Low; 20/20 reset yeniden arm gerektirir. CWD veya tüm ortam aralığı ölçümü yoksa watchdog zaman hedefi BLOCKED.
- **Başarısızlık:** timer/DMA pet'inin donmuş uygulamayı sağlıklı göstermesi, debug halt'ta aktüatör enerjisinin sürmesi, stack taşması, eski komutla restart.

## T04 — CAN test

- **Amaç:** mesaj sözleşmesi, yük, hata davranışı ve tazelik; F04/F05.
- **Ekipman:** SocketCAN uyumlu analyzer, osiloskop, fault-injection node, sonlandırma ölçümü.
- **Prosedür:** enerjisiz iki uç sonlandırmanın paralel yaklaşık60 Ω olduğunu ölç; CAN bit timing doğrula. Normal komut/telemetriyi 30 dakika çalıştır; tasarlanan azami yükü ve beklenmeyen ID'leri ekle. Duplicate, out-of-order, eski session, sayaç taşması, yanlış sürüm/uzunluk ve sınır dışı komutları uygula. Heartbeat var/komut yok ve tersi ayrı denensin. Bus-off oluştur; bağlantıyı geri getir.
- **Ölçülecek:** bus utilization, error counter, frame latency, komut kabul sayacı, son geçerli komut yaşı, timeout ve bus-off inhibit zamanı.
- **Beklenen:** protokol dışı paket hareket üretmez; recovery otomatik arm değildir.
- **Kabul:** planlı trafik≤%30 ortalama bus load ve 30 dakika nominal çalışmada bus-off yok; komut kaybı/heartbeat kaybı≤100 ms tespit; duplicate/replay lease yenilemez; MCU inhibit≤2 ms, kaynak ayırma≤50 ms ek süre; hata kaldırılınca yalnız SELF_TEST/IDLE.
- **Başarısızlık:** telemetri komut timeout'unu gizler, sayaç taşmasında yanlış kabul, geçersiz frame ile hareket veya artan kalıcı hata sayacı.

## T05 — Motor driver test

- **Amaç:** sürücü current-limit, nFAULT, kayıp ve rejenerasyon; F08/F12/F17.
- **Ekipman:** akım sınırlı kaynak, endüktif/dummy yük, motor dinamometre jigi, akım+diferansiyel prob, termokupl.
- **Prosedür:** bir kanalı düşük gerilim/dummy yükte başlat; PMODE=High ve `IN1/IN2=00` Hi-Z coast, `10/01` iki yön, `11` brake truth table'ını doğrula. Ardından gerçek firmware ile ileri↔geri komutta iki girişin en az bir PWM periyodu `00` kaldığını, TIM1/TIM8 master/slave fazı, preload/update eşzamanı, break ve nSLEEP'in iki kanalı da bastırdığını logic analyzer ile doğrula. Başlatma, ani duty değişimi, reset ve fault sırasında dört motorun her iki girişini birlikte yakala; istenmeyen `11` darbesi olmasın. 12 V ve16,8 V beslemede yükü artır; VREF ve sense toleransı ölç. Firmware PWM'i uygunsuz yüksek verdiğinde HW akım limitini jig üzerinde doğrula. Her kanalda koruma dene. Kaynak sink yapmıyorken ve batarya yolu açıkken düşük enerjili rejenerasyon uygula; gerçek hareket enerjisine yalnız dump kanıtından sonra yükselt.
- **Ölçülecek:** motor RMS/peak akımı, switching ripple, MOSFET/PCB ısısı, bus overshoot, fault/enable gecikmesi, coast akım sönümü.
- **Beklenen:** cycle-current limit MCU'dan bağımsız, fault bütün sürüşü kilitler; dump enerjiyi alır.
- **Kabul:** `00` gerçek Hi-Z/coast; ileri/geri geçişinde örtüşen giriş yok; iki timer break ve nSLEEP testi başarılı. HW nominal2,7 A; bütün tolerans ve ölçüm belirsizliği dahil≤3,0 A; OCP/nFAULT inhibit; 1,3 A sürekli hedefte junction tahmini derating sınırına uygun; 2,5 A transient yalnız≤250 ms ve termal olarak doğrulanmış; 16,8 V'ta PWM voltaj sınırlaması motorun12 V ortalama sınırını korur. K1/K2 açıkken clamp işlevli; parça abs-max aşılmaz.
- **Başarısızlık:** sıfır komutta brake, ters yönde kısa süreli yanlış tork, yön geçişinde `11`, yalnız yazılım akım sınırına bağımlılık, TVS'nin sürekli ısınması, supply overshoot, driver TSD'nin normal iş rejimi olması veya köprü çakışması.

## T06 — Encoder test

- **Amaç:** dört teker yönü, oran, sayım ve arıza algılama; F16.
- **Ekipman:** işaretli teker/şaft, logic analyzer, sinyal jeneratörü veya encoder simulator, optik takometre.
- **Prosedür:** her tekeri elle10 tur ileri/geri çevir; gerçek gearbox ratio ve motor-shaft CPR×quadrature tanımından beklenen çıktı sayısını hesapla. Timer wrap sınırını geç; hız aralığını tara. A/B kanalı ayrı kopuk/kısa, ters faz, donmuş count ve gürültü dene; hareket komutu verilmeden önce başlangıç yönleri doğrulansın.
- **Ölçülecek:** tur başına count, işaret, edge hata oranı, minimum hız çözünürlüğü, hız hatası ve fault gecikmesi.
- **Beklenen:** dört kanal bağımsız ve doğru yönde; wrap hız sıçraması yaratmaz.
- **Kabul:** 10 tur toplam count üretici gerçek ratio'su ve ölçüm belirsizliği içinde; stabil hız ölçümü takometreye göre≤%2; 0,03 m/s'de işaret/ölçüm kararlı; simüle sayımda kayıp yok; >0,1 m/s istekte100 ms feedback kaybı fault; kablo arızasında runaway yok.
- **Başarısızlık:** tahmini70 oranını kesin count sanmak, quadrature×4'ü iki kez uygulamak, wrap ters hızı veya kayıp kanalla devam.

## T07 — IMU test

- **Amaç:** yönlendirme, bias, titreşim ve kayıp yönetimi; F18/F21.
- **Ekipman:** düz yüzey, açı fikstürü, referans inklinometre, logic analyzer, kayıt bilgisayarı.
- **Prosedür:** altı statik yönelimde ölç; gyro bias'ı 60 s kaydet; bilinen±15° açı uygula; motorlar kapalı/açık karşılaştır; SPI/I2C bağlantısını kes ve eski timestamp enjekte et. Tilt eşiğini araç sürmeden fikstürde geç.
- **Ölçülecek:** ivme normu, statik roll/pitch, gyro bias/noise, örnek hızı/jitter, motor titreşim spektrumu ve fault süresi.
- **Beklenen:** URDF/MCU eksenleri aynı; sensör kaybı özerkliğe izin vermez; kalibrasyon sürümle saklanır.
- **Kabul:** kalibrasyon sonrası norm9,81 m/s²'ye≤%3, statik açı referansa≤2°, durağan gyro bias≤0,5°/s ön hedef; veri yaşı>50 ms FAULT; tilt mutlak>20°100 ms'de inhibit. Degraded mode yalnız IDLE'da açık seçimle≤0,2m/s bench/görüş hattı.
- **Başarısızlık:** eksen tersliği, eski verinin yeni timestamp ile yayımlanması, saturasyon veya kalibrasyonsuz sessiz devam.

## T08 — Single wheel test

- **Amaç:** motor+gearbox+hub+teker+PID fiziksel doğrulama; F08/F09/F16.
- **Ekipman:** koruyuculu tek-teker sehpası/dinamometre, tork kolu/load-cell, takometre, akım ölçer, termokupl.
- **Prosedür:** düşük duty ile yön dene; 0,03/0,1/0,4/0,8m/s eşdeğeri hızlara çık; yükte sürekli akımı1,3 A hedefinde tutarak tork-hız ölç. 2,5 A/250 ms transient'i yalnız kademeli doğrulama sonrası uygula. Kontrollü yük artışıyla stall algıla; motoru gerçek stall akımında uzun süre kilitleme. Encoder kaybı dene; montajı sök/tak kontrol et.
- **Ölçülecek:** tork-hız-akım eğrisi, PID settling/overshoot, hub runout, boşluk, case sıcaklığı, kablo/şaft yükü.
- **Beklenen:** hız pozitif/negatif kararlı; hub kaçırmaz; sürekli ve transient çalışma bölgeleri elde edilir.
- **Kabul:** ön hedef hız hatası≤max(%5,0,01m/s), overshoot≤%10; komut sıfırında integratör boşalır; akım/ısı sınırı aşılmaz; hub radyal runout≤0,5 mm; bağlantı gevşemez; stall/encoder fault matrise uygun keser. Sürekli tork eğrisi gerekli teker torkunu karşılamıyorsa drivetrain seçimi FAIL'dir.
- **Başarısızlık:** kâğıt tork hesabı tek kanıt, gear/hub kayması, oscillation, termal limitin üzerinde sürekli çalışma.

## T09 — Four wheel test

- **Amaç:** dört kanal eşzamanlı yük, polarite ve dağıtım; F08/F09/F16.
- **Ekipman:** tekerler boşta koruyuculu sabitleme sehpası, dört akım kanalı, logic analyzer, elektriksel dummy yük.
- **Prosedür:** dört motor tek tek işaretle; ileri/geri/sol/sağ ve pivot komutunu sehpa üzerinde düşük hızda dene. Dört kanal eşzamanlı hız basamağı ver; maksimum yük güç davranışı dummy/dinamometreyle ayrı doğrula. Tek kanal encoder/nFAULT hatasını enjekte et.
- **Ölçülecek:** dört teker işaret/hız, toplam akım, bus ripple, CM5 reset sayısı, sıcaklık ve fault birlikteliği.
- **Beklenen:** sağ/sol dönüşüm doğru; tek motor arızası aracın kontrolsüz dönmesine izin vermez.
- **Kabul:** 20 yön değişiminde doğru işaret; eşit yüksüz hedefte hız farkı≤%5; tek kritik kanal arızasında dört sürücü inhibit; compute reset yok; motor/servo combined sınırı güç bütçesini aşmaz.
- **Başarısızlık:** kanal mapping hatası, tek fault sonrası kalan motorların sürmesi, besleme çökmesi. Yüksüz sehpa başarısı zemin pivot tork kabulü değildir.

## T10 — Remote control test

- **Amaç:** MacBook tarayıcısı, joystick/gamepad, tek operatör ve telemetri; F06/F22.
- **Ekipman:** MacBook, gamepad, yerel ağ, kayıt bilgisayarı, önce sehpa sonra çevrilmiş düz alan; fiziksel E-stop operatörü.
- **Prosedür:** T13/T14 geçtikten sonra arm-nötr-deadman; ikinci istemci, gamepad çıkarma, sekme gizleme, odak kaybı, sayfa yenileme ve ağ gecikmesi dene. Aynı prosedürü önce0,2m/s sınırında yerde yap. Batarya/akım/hız/IMU/CPU/MCU ısı ve fault telemetrisini referanslarla karşılaştır.
- **Ölçülecek:** kaynak yaşı, uçtan uca komut gecikmesi, kayıp paket, duruş zaman çizelgesi, UI stale işareti, log bütünlüğü.
- **Beklenen:** tek kontrol sahibi; deadman bırakma durdurur; taze veri ile eski veri ayırt edilir.
- **Kabul:** nominal yerel ağda p95 komut gecikmesi≤50 ms hedef; taze kaynak koşulu≤100 ms; ikinci istemci kontrol alamaz; sekme/gamepad kaybında izin düşer; stale telemetri≤500 ms'de açık gösterilir; ağ kesildiğinde UI stop uygulanmış sayılmaz; yeniden bağlantı otomatik arm değil.
- **Başarısızlık:** odak yokken hareket, yeniden açılan tarayıcıda eski komut, sahte yeşil bağlantı, zaman etiketsiz telemetri.

## T11 — Load test

- **Amaç:** azami brüt8 kg'da taşıma, şasi/bağlantı ve tahrik yeterliliği; F09/F13/F21.
- **Ekipman:** tartı, dört köşe terazi, sabitlenmiş ağırlıklar, eğim rampası, emniyet halatı, sıcaklık/akım kaydı, kumpas.
- **Prosedür:** boş aracı bütün kablo/krimp/vida/insert ile tart; payload=min(2 kg, 8 kg−gerçek boş kütle). %25/%50/%100 yükle CG ve teker normal yüklerini ölç. Teker sehpasında TPU yanağını 40 N her iki aksiyel yönde ayrı ön tara; hub milinde kontrollü aksiyel itme/çekme ve sıcak/soğuk endplay ölç. Önce düz kalkış/duruş, sonra5°/10°/15° kontrollü kısa tırmanış; eğimde bağımsız halat sürekli hazır. Her adımda yapısal hasar ve kalıcı deformasyonu kontrol et. Yük ve ölçülmüş hız/akım çifti kaydedilsin.
- **Ölçülecek:** dört teker yükü, CG, akım/RMS/transient, hız, tork talebi, TPU yanağı aksiyel kayması, hub endplay, deflection ve sıcaklık.
- **Beklenen:** yük altında servis edilebilirlik ve bağlantı bütünlüğü korunur; termal bölge aşılmaz.
- **Kabul:** boş kütle≤6 kg ve PH4 marj kararı; toplam≤8 kg; öngörülen CG kararlılık alanında; askıda teker veya kontrolsüz kayma yok; 40 N/teker ön taramada lastik yanağı dışarı çıkmaz veya kalıcı kaymaz; hub endplay seçilmiş tolerans çizimi içinde ve rulman sıkışmadan döner; akım1,3 A sürekli hedef ve doğrulanmış transient alanında; deformasyon/sıyrılmış insert/gevşeme yok. 15° ancak ölçülmüş lastik tutunması ve akım/ısı bütçesiyle geçer.
- **Başarısızlık:** sadece anlık tırmanışla sürekli eğim yeterliliği ilanı, halatsız rollback, motor/gearbox aşırı yük, şasi kalıcı şekil değişimi. Hedef karşılanmazsa payload/eğim düşür veya tahriki revize et.

## T12 — Thermal test

- **Amaç:** kapalı gövdede motor, sürücü, DC/DC, CM5 ve batarya termal sınırlarını belirlemek; F09/F13/F14/F15/F17.
- **Ekipman:** termokupl kayıt sistemi, termal kamera, kontrollü yük/dinamometre, güç analizörü; güvenli çevre sıcaklığı düzeneği.
- **Prosedür:** gerçek kapak/filtre/kabloyla25°C ortamda önce hafif sonra tasarım duty-cycle; en az60 dakika veya sıcaklık eğimi10 dakika boyunca<1°C/10min olana kadar izle. Isıl denge60 dakikada yoksa test sürer veya FAIL.40°C hedef ortam ayrı kontrollü test; fan kopması ve termistör açık/kısa jig ile denensin. Li-ion hücreyi arıza üretmek için ısıtma; eşikler simülatörle doğrulansın.
- **Ölçülecek:** motorcase/driverPCB/junction tahmini, converter hot-spot, hücre yüzeyi, CM5/STM32, hava sıcaklığı, fan RPM ve RMS akım.
- **Beklenen:** belirtilen çalışma zarfında limit aşmadan denge; arızada derate/stop.
- **Kabul:** normal nominal yükte motorcase<60°C,driverPCB<70°C,hücre<45°C ön hedef; junction veri sayfası derating hesabında yeterli marj; hiçbir normal kullanım TSD'ye dayanmaz; sensör arızası fault;55°C hücre veya70°C motorcase eşik simülasyonu keser.40°C testi geçmezse ortam zarfı düşürülür.
- **Başarısızlık:** kısa süreli ölçümü denge sanmak, case=junction varsayımı, kapaksız testten kapalı gövde kabulü, ısı nedeniyle ASA/PA parça sürünmesi.

## T13 — Emergency stop test

- **Amaç:** fiziksel kesmenin bilgisayar/yazılımdan bağımsızlığını, açık kablo ve tek ayırıcı arızasında işlevini doğrulamak; F01/F02/F03/F07/F12.
- **Ekipman:** korumalı sehpa, akım sınırlı kaynak, diferansiyel ve akım probları, logic analyzer, kontak arıza simülatörü, emniyet halatı/takoz.
- **Prosedür:** A1'de motor çalışırken E-stop'a bas; pan/tilt kurulu sonraki revizyonda hareketli servo altında da tekrar et. Her NC kabloyu sırayla aç; güvenlik mantığı beslemesini kes; MCU'yu dondur. J-SIG açık devresini enerjisiz fiş sökme yerine akım sınırlı break-out jig ile uygula; J-PWR kopuğunu yalnız enerjisiz kurup sonra dummy yükle başlat. `PWR_ACT_EN` hattını ayrı açık devre yap; High'a kısa devre arızasını yalnız akım sınırlı jig ile deneyip fiziksel K1/K2 kesmenin bunu bastırdığını doğrula. `ACT_BUS`–`5V_CONTROL` kısa devresini E-stop basılıyken ve akım sınırlı jig üzerinde tekil arıza olarak kur; 5 V dalının güvenli sınırda kalmasını ve aktüatörün sürülmemesini ölç. Kontak arıza jigiyle K1'in kapalı kalmasını, ayrı deneyde K2'nin iletimde kalmasını simüle et; diğer yolun kesmesini ölç. K2 kontrolcüsünde `EN=Low` kapatmasının iki yönde iletimsizliğini ve `SLEEP=Low, EN=High` durumunun güvenli OFF olmadığını ayrıca akım sınırlı dummy yükle ölç; `FLT` latçi olmadan otomatik yeniden iletime izin verilmediğini doğrula. Ayrı deneylerde ön şarj FET'ini ve test enjeksiyon FET'ini kısa tut; NC açıldığında test kaynağından `MID/ACT_BUS` üzerinden aktüatöre enerji geçip geçmediğini ölç. Tekli arızalarda fiziksel kesme ve sonraki ARM ön testinin arızayı tanılamasını ayrı ayrı kaydet; iki arızayı aynı anda oluşturma. Her deneyde E-stop bırak, güç ve CAN'ı geri getir; otomatik arm olmadığını dene. Kanallar arası kısa devre tanılamasını doğrula. İlk deneyler dummy yükte, sonra teker sehpasında; düz zemin düşük hız ancak bütün bench kapıları geçtikten sonra.
- **Ölçülecek:** NC→enable pasif, NC→kaynak izolasyonu, `VBAT/MID/ACT_BUS` ve test kaynağı akımı, motor/servo akımı, K1/K2 tanı sonucu, VM overshoot, coast akım sönümü, encoder/video durma zamanı/mesafesi.
- **Beklenen:** tek sağlam ayırıcı iki aktüatör dalını keser; bilgisayar kayıt için açık; fiziksel bırakma hareket başlatmaz. Son motor bus'unda regen gerilimi bulunması otomatik olarak “kesici kapalı” diye yorumlanmaz.
- **Kabul:** enable≤2 ms, kaynak ayırma≤50 ms hedef; son sağlıklı WD darbesinden kesmeye≤150 ms; motor ve servo alanında bataryadan sürme enerjisi kesildiği doğrulanır; mekanik durma ayrıca kaydedilir. Her açık-kablo/tek-ayırıcı/ön şarj/test kaynağı tekil arızası 10/10 denemede kesme ya da güvenli ARM reddi verir; K1/K2/ön şarj tanısı arızalı kesiciyi bir sonraki ARM'den önce yakalar; test kaynağı NC açıkken tork üretecek enerji vermez;20 bırak/reset/power-return döngüsünde otomatik hareket yok; parça voltaj limiti aşılmaz. ARMING için taslak≤15 s bütçe ≤150 ms E-stop kesme hedefini gevşetmez.
- **PWR P0 şema ölçüm noktaları (24.09.2026):** [güç/güvenlik sayfaları](pwr_safety_path.md) TP201 `F1_OUT`, TP202 `MID`, TP203 `ACT_BUS`, TP204 K1 bobin alt ucu. NC-A ve NC-B'yi ayrı ayrı, `SAFE_GATE` jiglerle High'a zorlanmışken aç; `SAFE_EN`, `PCH_DRV`, `TEST_PERMIT_DRV`, TP203 ve TP204'ü kaydet. Q202/Q206/Q208 kısa jigleri, K2-kısa dummy yükünde K1 `I_break`, `V(TP201)−V(TP202)` ve bırakma süresi; TPS3431 `SET1` Low ve `EN` Low enjeksiyonu; WDI durdurma → `WD_OK` → `SAFE_EN`/TP204 zaman damgası. Sonuçlar NOT_RUN.
- **Başarısızlık:** herhangi motor veya servo enerjisinin kalması, kaynaklı ayırıcının/ön şarj kısa devresinin tanılanamaması, test FET'i kısa kaldığında NC'nin enjeksiyon kaynağını kesmemesi, MCU'nun E-stop'a veto koyabilmesi, yalnız PWM gözleyerek geçer kararı, ölçülmeden durma mesafesi garantisi. Bu test FAIL ise zeminde sürüş yapılmaz.

## T14 — Communication loss test

- **Amaç:** tüm komut yolunda kopuş, gecikme ve yeniden oynatma güvenliği; F04/F05/F06/F07/F20.
- **Ekipman:** CAN analyzer, programlanabilir ağ gecikmesi, logic analyzer, sehpa, PC kayıt aracı.
- **Prosedür:** ayrı deneylerde UI ağını kes, gateway/ROS sürecini durdur, CM5 resetle, CAN kablosunu ayır, bus-off, MCU ana-loop hang uygula. Heartbeat gelirken komutu dondur ve tersi. Eski session, duplicate, sıra dışı,100–1000 ms buffered komut, sayaç taşması ve gateway restart dene. Kaynak saatine sıçrama ve RTT artışı uygula. Geri gelen iletişim sırasında joystick'i ileri tut.
- **Ölçülecek:** son taze kaynak/komut/heartbeat zamanları, inhibit, kesici açılması, tekrar arm, kabul/red sayaçları.
- **Beklenen:** her kopuş uygun timeout ile keser; eski joystick yenilenmiş lease sayılmaz.
- **Kabul:** MCU son geçerli komut veya heartbeat'ten≤100 ms tespit; ek≤50 ms kaynak kesme; uçtan uca kaynak kaybı≤250 ms kaynak kesme ön hedef; duplicate/queued paket süre yenilemez;20 yeniden bağlantıda otomatik hareket yok; saat belirsizliği tazelik sınırını aşarsa arm reddedilir.
- **Başarısızlık:** heartbeat ile eski komutun canlı tutulması, gateway'in eski komuta yeni sayaç basması, yeniden bağlanınca hareket, saat alanlarını doğrudan çıkararak yanlış tazelik kabulü.

## T15 — Battery test

- **Amaç:** hücre denetimi, enerji kapasitesi, BMS, düşük gerilim ve konnektör/fuse tasarımı; F10/F11/F12/F14/F17.
- **Ekipman:** dört-kanal hücre simülatörü, batarya analizörü, kontrollü yük, üreticiye uygun şarj cihazı, sıcaklık kaydı, DMM.
- **Prosedür:** paket yapım/kaynak ve hücre eşleme kaydını kontrol; ilk eşik testlerini gerçek hücreyi aşırı deşarj etmeden simülatörle yap. Bir düşük hücreyi toplam paket normal görünürken uygula. BMS ölçümü kopuk/stale dene. Sonra uygun kesme sınırlarıyla kapasite ve görev duty-cycle testi; konnektör ısınması, BMS açılması ve dolu bataryada regen yolu doğrulansın. Şarj/deşarj sıcaklık inhibitlerini simüle et.
- **Ölçülecek:** her hücre V/T, denge, Ah/Wh, ESR yaklaşımı, toplam akım, konektör sıcaklık artışı, BMS trip/geri dönüş, CM5 kapanması.
- **Beklenen:**4S2P9 Ah/129,6 Wh nominal etiket gerçek ölçümle karıştırılmaz; bir zayıf hücre gizlenmez.
- **Kabul:** hücre V ölçüm hatası≤20 mV ön hedef; warn3,4 V5 s/stop3,2 V1 s/hard3 V10 ms simülasyonu matrise uygun; bir hücre veya sense arızası arm'ı engeller; tasarım akımında konnektör rise≤20°C ve kendi üretici sınırı içinde; kapasite yeni-hücre üretici minimumu ve yük/sıcaklık koşulu ile karşılaştırılır; nominal9 Ah'ın tamamı kullanılabilir enerji diye alınmaz.
- **Başarısızlık:** yalnız paket voltajından SoC/güvenlik, BMS trip sonrası otomatik yeniden hareket, hücre verisi yokken sürüş, uygunsuz şarj, dump yetersizliği. Canlı paket kısa devresi bu prosedür değildir.

## T16 — Mobility test

- **Amaç:** düz/sürtünmeli zemin, dönüş, eşik ve eğim çalışma zarfı; F09/F21.
- **Ekipman:** ölçülü düz parkur, kontrollü pürüzlü yüzey,5°/10°/15° rampa, bariyer, emniyet halatı, video, akım/ısı kaydı.
- **Prosedür:** T11/T12 sınırlarıyla0,2→0,4→0,8m/s;10 m düz, geniş dönüş ve kontrollü pivot. Pivot önce düşük tutunmalı sonra yüksek tutunmalı yüzeyde kısa süre; TPU'nun iki yanağında eksenel kayma/çıkma işareti ara. Eşik yüksekliği10 mm'den kademeli artır; alt gövde/teker teması gözle. Eğimde ankraja bağlı bağımsız halat, fiziksel durdurucu ve takoz kurulduktan sonra çıkış/iniş ile düşük enerjili E-stop/coast geri kaymasını ölç; pasif fren olmadığını test kurulumunda hesaba kat.
- **Ölçülecek:** gerçek hız, sapma, minimum kontrollü hız, akım/termal yük, slip, dönüş yarıçapı, clearance, durma mesafesi ve geri kayma.
- **Beklenen:**0,8m/s üstüne yazılımla çıkılmaz; mümkün zemin/payload zarfı ölçülür.
- **Kabul:**0,03m/s kontrollü ilerleme ön hedef;0,8m/s yalnız akım/ısı bütçesinde; teker/şasi teması ve gevşeme yok; ölçülmüş güvenli alan içinde duruş;15° yalnız motor/tutunma/CG sınırları aynı anda geçerse kabul. Kuru yüksek sürtünmede sürekli pivot zorunlu V1 kabul değildir; izinli pivot süresi testle tanımlanır.
- **Başarısızlık:** devrilme eğilimi, halatsız rollback, termal/akım alanı dışı sürüş, odometriyi gerçek mesafe sanmak, kendiliğinden gevşeyen hub/mount.

## T17 — ROS integration

- **Amaç:** ölçü kaynağı, URDF/TF, driver, odometri, güvenlik ve kayıt akışının uyumu; F18/F20/F22.
- **Ekipman:** CM5 Ubuntu/ROS2 test kurulumu, CAN veya HIL cihazı, RViz/rosbag, ölçüm aracı.
- **Prosedür:** ortak ölçü dosyasından model üret; gerçek track/wheelbase/radius ölçümüyle karşılaştır. TF tree ve teker yönlerini dene;10 m ölçülü düz sürüş; driver node öldür; odometry timestamp/clock reset, rosbag disk dolu, QoS kopuşu ve config değişimini test et. MCU safety'nin ROS çalışmasa da işlediğini doğrula.
- **Ölçülecek:** model boyutları, TF bağlantı/epoch, odometri hatası, message yaş/drop, CPU/RAM/disk, fault ile komut inhibit gecikmesi.
- **Beklenen:**tek TF sahibi, ortak birim/metre/radyan, eski sensörün taze gösterilmemesi, MCU bağımsızlığı.
- **Kabul:** fiziksel/URDF kritik ölçü farkı≤1 mm veya CAD üretim toleransı; nominal10 m düz odometri hatası kalibrasyon sonrası≤%5; TF kopuk/döngü yok; driver ölümü T14 sınırında keser; disk dolu durumu kayıt edilir/gösterilir; simülasyon sonuçları hardware PASS sayılmaz.
- **Başarısızlık:** mm/m veya eksen hatası, birden fazla odom→base yayını, ROS kapandığında hareketin sürmesi, sim zamanının sahada timeout'u dondurması.

## T18 — Camera test

- **Amaç:** A1 sabit ön kamerada görüntü, titreşim, kablo ve gecikme; çift göz/pan-tilt eklenirse ayrı hareket sınırı ve ömür kabulü; F19.
- **Ekipman:** çözünürlük hedefi, görünür saat/LED latency jigi, goniometre, CM5/UI kayıt, akım ölçer.
- **Prosedür:** A1'de durağan ve sürüşte hedef görüntüle; kamera podunun bağlantı/FFC gerginliği ve darbe korumasını incele; kamerayı ayır/dondur, aynı kare tekrarına güncel frame etiketi basılmamasını dene. Pan/tilt takılan sonraki revizyonda ayrıca 180°pan/90°tilt açıklığı düşük hızda tara, servo uçlarını fiziksel stoptan önce sınırla; 100 tam tarama, kablo sürtünmesi ve servo yükte E-stop deneyi yap.
- **Ölçülecek:** video FPS/drop/end-to-end latency, titreşim blur, motor kablosu EMI etkisi, frame yaşı; hareketli revizyonda gerçek açı ve servo akımı.
- **Beklenen:** kablo ezilmez; mekanik stopa sürekli servo torku yok; E-stop servo enerjisini keser; video kaybı görünür.
- **Kabul:** A1'de en az720p/20fps, p95 video latency≤250 ms; frame>500 ms eskiyse açık stale ve kamera ile sürüş stop; pod/FFC sürüş titreşiminde gevşemez, optik alanı kesilmez. Hareketli revizyonda ayrıca hedef açılar kablo/çarpışma olmadan, 100 taramada temas/gevşeme yok; E-stop sonrası servo kaynak enerjisi≤50 ms kesilir ve servo güçsüz düşmesi zarar üretmez.
- **Başarısızlık:** CSI/USB kablosunu hareket sınırı olarak kullanma, servo sinyalinden geri besleme, donuk görüntüyle sürüş, fiziksel stoptan önce limit yokluğu.

## T19 — SLAM test (V3)

- **Amaç:** LiDAR, zaman hizası, harita ve localization güveni; F19.
- **Ekipman:** doğrulanmış LiDAR montajı, ölçülü kapalı parkur, referans işaretler/zemin planı, rosbag, RViz.
- **Prosedür:** önce kayıt/simülasyon, sonra≤0,2m/s teleop; kapalı döngü parkuru üç kez gez; scan extrinsic ve timestamp hizasını dene. LiDAR verisini kes, geciktir; dinamik engel ve düşük geometrili alan ekle; reboot sonrası harita/localization prosedürünü uygula.
- **Ölçülecek:** scan age, extrinsic residual, harita ölçeği/duvar sapması, loop-closure sapması, localization covariance, CPU/ısı ve kayıp frame.
- **Beklenen:** geometrik olarak tutarlı harita, güven kaybının açık bildirilmesi; V1 güvenliği değişmez.
- **Kabul:** seçilen küçük iç mekân parkurunda ölçülü duvar mesafeleri≤0,10 m veya%2 (büyük olan); 3 tekrar son konum sapması≤0,20 m ön araştırma hedefi; eski scan>200 ms özerklik iznini keser; TF/zaman hatası gizlenmez. Bu eşikler seçilen sensörle tekrar gözden geçirilir.
- **Başarısızlık:** harita görselini metrik doğrulama saymak, confidence kaybıyla özerk hareket, CPU yükünün heartbeat/safety'yi etkilemesi.

## T20 — Navigation test (V4)

- **Amaç:** Nav2 waypoint ve engel kaçınmanın doğrulanmış güvenlik zarfında çalışması; F19.
- **Ekipman:** T19 geçmiş robot, kapalı bariyerli parkur, yumuşak test engelleri, fiziksel E-stop operatörü, kayıt/video ve referans ölçüm.
- **Prosedür:** simülasyonda görev+fault senaryoları, ardından yerde≤0,2m/s.10 waypoint koşusu; statik engel, yola sonradan çıkan yumuşak engel, sensör kaybı, localization kaybı, planner/controller çökmesi ve unreachable goal. Collision monitor/yerel stop aralığını T13/T16 gerçek durma alanına göre ayarla; yalnız geçtikçe hız artır.
- **Ölçülecek:** waypoint hata/başarı, obstacle clearance, stop mesafesi, kaynak/sensör yaşı, recovery davranışı, compute yükü.
- **Beklenen:** doğrulanmış footprint ve durma mesafesi kullanılır; veri/güven kaybında duruş; güvenlik komutu planner üzerinde önceliklidir.
- **Kabul:** kontrollü parkurda10/10 görev çarpışmasız, hedef konum≤0,15 m/başlık≤5° ön hedef; clearance≥ölçülmüş en kötü durma mesafesi + localization/sensör belirsizliği +0,10 m deney marjı; bütün fault senaryolarında yeniden arm olmadan devam yok; unreachable goal güvenli sonuç verir.
- **Başarısızlık:** çarpışma/izinsiz yeniden hareket, bilinmeyen alanı boş sayarak ilerleme, safety'nin ROS planner tarafından geçersiz kılınması, simülasyon PASS'ını saha PASS'ı sayma.

## Aşama kapıları ve rapor

Her faz kapanışında teknik tutarlılık, üretilebilirlik, montaj, test erişimi ve servis erişimi kontrol edilir; açık riskler kimlik ve sorumlu ile kaydedilir. Test başarısızsa önce neden/konfigürasyon belirlenir, sadece etkilenen test ve regresyon kapıları tekrarlanır. Kanıt klasörü [tests/README.md](../tests/README.md) sözleşmesine uyar. Emniyet süreleri ve hata davranışları için tek referans [safety_architecture.md](safety_architecture.md) belgesidir; çelişki bulunursa sürüş serbest bırakılmaz.

## A3 Lite ek kabul testleri (DD69, bağımsız inceleme R4/R6/R7)

T01–T20 A2 donanımına yazıldı; A3 Lite'ta aşağıdakiler T08/T09/T13'e eklenir. Hepsi **NOT_RUN**.

- **TL1 — Tek teker sıkışması (T08 eki, R4):** Sehpada, tam dolu pakette (12,6 V), her tekeri **ayrı ayrı** (FL, FR, RL, RR) kilitle; diğer üçü dönebilir durumda. Ölç: kanal akımı (akım probu, balastın iki ucu), TB6612 ve balast sıcaklığı, enkoder sayımı, firmware'in durma anı. Ayrıca aynı modülün iki kanalını (FL+RL) birlikte yükle: ağır yükte yavaş dönen teker (stall değil) ile çekirdeğin ısı bütçesi kesmesini ve TB6612 gövde sıcaklığını (termokupl) kaydet; ters yön komutunda boşa alma turunu ve frenleme akımını ölç. **Kabul:** kanal akımı ≤1,0 A (hesap 0,89 A), frenlemede ≤0,9 A; kilitlenen teker kendi enkoderiyle ≤300 ms + bir kontrol döngüsünde durdurulur ve FAULT kilitlenir; arka teker sıkışması ön teker dönerken de yakalanır; ağır yükte THERMAL FAULT ≤30 s (model ≈20 s) gelir ve çip sıcaklığı veri sayfası Tj sınırının altında kalır; ölçülen çip ısınmasıyla `LITE_CHIP_CONT_W`/`LITE_CHIP_HEAT_J` kalibre edilir. Sargı direnci ve 1:78/PPR bu testte ölçülür. Dıştan geri sürülme (itilme) akımı ayrıca ölçülür.
- **TL2 — Yerinde dönüş ve rampada ivme (T09/T16 eki, R7):** Üç zeminde (kaygan, ahşap/laminat, halı veya kauçuk) boş ve dolu pakette 90° yerinde dönüş; 5° rampada 0,5 m/s² kalkış. Ölç: motor başına akım, dönüş süresi, stall olayları, motor gövde sıcaklığı. **Kabul:** akım balast sınırını aşmaz; dönmeyen zeminde stall/ısı denetimi dönüşü keser ve hata raporlar; rampada sürekli akım ≤0,6 A. Ölçülen µ ile hesaptaki model karşılaştırılır (M3, 5,1 kg brüt: 0,45 rad/s dönüşte boş pakette µ≤0,30, nominal µ≤0,36, dolu µ≤0,45; kopma µ≤0,38). 5° rampada boş pakette hız ≥0,15 m/s. Hız döngüsü (N2, inceleme 26.09.2026): 63 mm/s sabit hedefte sehpadaki tekerin freni birden bırakılınca tepe hız AI tavanını (200 mm/s) aşmaz ve 1 s içinde hedefin ±%10'una oturur. Model 174 mm/s tepe (2,77×) veriyor; aşarsa KP/KI (`lite_core.h`) sehpada ayarlanır. Fiziksel ayar NOT_RUN.
- **TL3 — E-stop kısa basış ve ikinci kontak (T13 eki, R6):** IDLE, ARMED ve DRIVING'de 50 ms, 200 ms ve 1 s basış; ikinci NC kablosunu sök (kopuk tel). Ölç: GPIO2 kenarı, `ACT_EN`, VM_ACT, motor akımı, kilit durumu. **Kabul:** basıştan `ACT_EN` Low'a ≤2 ms (hesap: süzgeç en kötü 1,69 ms + kesme ≤0,3 ms), her basış kilitlenir (20/20); bırakmak hareketi başlatmaz, IDLE lease + yeniden ARM gerekir; kopuk tel E-stop olarak okunur; güç kontağı açıkken motor enerjisi kesilir. Güç kontağının kaynaklaşması bu şemayla görülmez; periyodik kontrol prosedürü yazılır.
- **TL4 — Kol (M3, DD73):**
  - Önce kalibrasyon: her servonun uç darbeleri açıölçerle ölçülür, `servo_control.c` tablosu düzeltilir. Park darbesiyle kol çamurluğa yaslanmalıdır.
  - DD81 montaj kontrolleri: 25T kornanın delik çemberi (PCD 14) ve 624 yuvası deneme parçasıyla; MG996R kulak delikleri 49,5 × 10 ve MG90S 28 mm; twist servosunun kulakları gövde hizasında kesilir ve cepte boşluksuz oturur; dirsek elle 120°'ye kadar çatal köprüsüne değmeden döner.
  - Sonra, araç sehpada, duruş grafiğinin her kenarı üçer kez yürütülür. Kenarlar: park–kaldır, kaldır–yukarı, kaldır–depola, yukarı–hazır, hazır–öne, hazır–yere, hazır–öne-orta.
  - Ölçümler:
    - her ray akımı (A ve B);
    - her rayın servo konektöründeki en düşük gerilimi, hareket ve tutma boyunca (en düşüğü tutan multimetre ya da osiloskop; ölçüm buck çıkışında değil, kablonun servo ucunda);
    - büyük eklemler aynı anda hızlanırken `5V_LOGIC` ve `3V3` (ESP32 resetlenmemeli);
    - omuz ve dirsek servosunun gövde sıcaklığı;
    - kavrama merkezinin gerçek konumu (cetvel/kamera);
    - 150 g yükle (kavrama merkezinde) "öne" duruşunda 60 s tutma.
  - Ayrıca rayı hareket sırasında kes (E-stop). Kolun nereye düştüğünü ve yeniden ARM'da ne yaptığını kaydet.
  - **Kabul:**
    - hiçbir kenarda gövdeye, çamurluğa, tekere ya da başa temas yok;
    - kavrama merkezi CAD değerinden ≤10 mm uzakta;
    - parktan kalkışta ön kol ve pençe yan duvara ≥3 mm uzakta (CAD 4,75 mm, 1° tarama; beş eklem birlikte ±1° saparken 4,1 mm, DD93): her eklemin kalibrasyonu ±1° içinde olmalı, yalnız dirseğinki yetmez;
    - 150 g ile 60 s tutmada servo kasası ≤55 °C: termokupl ya da IR ile kasada, motorun yanında; ortam sıcaklığı ayrıca kaydedilir. 55 °C, MG996R çalışma aralığının üst ucudur ve temkinli okunarak kasa sınırı sayılır (config `servo_case_max_c`);
    - her rayda servo konektöründe ≥4,8 V: üç servonun veri sayfası alt sınırı; tork hesabı bu gerilimi varsayar (config `servo_supply_min_v`, N5). Düşük çıkarsa kabul gevşetilmez: buck çıkışı 5,1–5,2 V'a ayarlanır ya da servo kablosu kısaltılır veya kalınlaştırılır;
    - servo yük adımında ESP32 resetlenmez (`5V_LOGIC` ve `3V3` sınırında kalır);
    - gerçek kablo demetiyle grafiğin bütün kenarları 10 kez: omuzdaki 225° servis halkası sürtünmez ve gerilmez, bükülme yarıçapı kablo çapının ≥10 katı; halkanın boyu ve yolu kaydedilip DD85'e işlenir;
    - parktayken ray kesilirse kol çamurluğa oturur;
    - yeniden ARM öncesi prosedür (kolu elle parka alma) işe yarar;
    - DD80 gevşek kilidi: ray hareket ortasında kesilip yeniden ARM edilince kol servoları beslenir ama darbe almaz ve kol yerinden oynamaz (servonun "beslenmiş, darbesiz" hali gevşek olmalı; değilse bu kilit yetmez), panelden park onayından sonra park darbesiyle çamurluğa yaslanır; açılışta da aynı.
- **TL6 — Baş (DD82):** pan ±90° ve tilt −30…+60° boyunca her uçta 10 kez. Ölç: boyun rulmanında boşluk, itme çubuğu bağlantısındaki boşluk (göz ucunda), kablo döngüsünün gerilmesi, iki göz arasındaki dönme farkı (aks rijitliği), servo açısı ile göz açısı (1:1). **Kabul:** kablo gerilmez ve sürtünmez; göz arka kapakları tilt taraması boyunca yerinde kalır ve elle 5 kez sökülüp takılabilir; tilt boşluğu ≤1°, iki göz arası fark ≤0,5°, göz açısı servo açısından ≤2° sapar; pan/tilt servosu kalıcı sıcaklıkta ≤50 °C.
- **TL5 — Pençe ve kargo bölmesi (M3, DD74; DD93 ikiz dişli pençe):** 10–50 mm ve 10–150 g beş nesneyle: "hazır"da pençeyi aç, "yere" in, kapat; "depola"ya git, pençeyi aç, her nesneyi 10'ar kez düşür. Önce dişli çiftinin deneme baskısı: boşluk ve sıkışma; B çenesi kuponu (avuç direği + çene + naylon burç + M3 × 16, yaylı rondela, 0,4 N·m) son montaj koşulunda 0–60° serbest dönmeli, eksenel boşluk 0,3–0,7 mm (R05). Operatör sözleşmesi (R02): açık pençeyle gücü kes, yeniden kurunca pençe darbesiz kalmalı; panelde "parkta, kapalı ve boş" onayından sonra pençe kapalı darbe almalı. Ölç: çene uçları arası açıklık (CAD 53,5 mm), dişli boşluğu, 150 g nesnede kayma. **Kabul:** TPU yarıklı kapak nesneyi ≥%90 geçirir ve kutu tabanına düşürür (geçirmezse kapak çıkarılır ya da yarık derinliği artırılır); pençe 150 g nesneyi "öne" duruşunda 60 s kaydırmadan tutar; açıklık ≥50 mm; parkta ve "kaldır"da "aç" komutu çeneyi oynatmaz; kavramadan sonra parkta sürüş reddedilir, "depola"da açıp kapattıktan sonra serbesttir; sol omuz bileziği pasif kolu yatay konumda 60 s tutar ve elle çevrilebilir; sol kolun taklitlerle kurulan dirsek, bilek, dönüş ve twist eklemleri elle zorlandığında oynamaz (R04); twist taklidi (066) cebinde elle ±1°'den fazla dönmez (DD95, CAD nominal ≈0,4°); kol gevşekken verilen pençe komutu pençeye darbe göndermez, AI "limp" hatası alır (DD95). Ön ToF (R01): açık alanda ve 200 mm'deki siyah ve cam hedefte ham durum kodu kaydedilir; "hedef yok" okunduğunda araç ≤0,1 m/s sürünür ve her hareket çağrısında 0,3 m'de durur; panel kör modun başını ve sonunu gösterir (DD95).
