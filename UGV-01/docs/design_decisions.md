# Tasarım kararları

22.09.2026 · A0. Her değişiklikte etkilenen gereksinim, hesap, CAD ve test aynı revizyonda güncellenir.

| Karar | Seçim ve gerekçe | Yeniden açma koşulu |
|---|---|---|
| DD01 | 6 kg boş + 2 kg yük; 0,90 kg tasarım rezervi | Tartım veya CG sınırı aşılırsa |
| DD02 | Ø120 teker; 240 iz; 210 dingil arası; 330×270 mm dış zarf | Lastik/yatak seçimi veya servis boşluğu değişirse |
| DD03 | Pololu 4754 70:1 koşullu aday; 0,8 m/s düz, 0,6 m/s eğim | Tork/ısıl test geçmezse; 1–1,5 m/s hedefi ertelendi |
| DD04 | 0,03 m/s için encoder periyot/pencere hibrit ölçümü | Düşük hız kararlılık testi |
| DD05 | 4S2P P45B, 14,4 V / 9 Ah / 129,6 Wh | Paket hacmi, görev süresi ve BMS testi |
| DD06 | Ham 4S motor barası; 12 V efektif sınır + donanım akım limiti | PWM, komütasyon ve ısıl test yetersizse |
| DD07 | STM32G474VET6 LQFP100; dört encoder timer ve PWM | Pin/ADC/DMA incelemesi |
| DD08 | V1 resmi CM5 IO; özel carrier ayrı faz | V1 sürüş/kamera doğrulandıktan sonra |
| DD09 | CAN 500 kbit/s; prototip USB–CAN; carrier'da SPI CAN denetleyicisi | Gecikme/EMI ve USB reset testleri |
| DD10 | NC STOP + harici watchdog + iki seri hareket kesicisi | Tek arıza testi ve güvenlik gözden geçirmesi |
| DD11 | STOP motor/servoyu keser, mantık açık kalır | Enerji dönüş yolu ve kesici geri bildirimi |
| DD12 | Rejenerasyon için klemp ve enerji direnci | Dolu batarya + açık kesici en kötü durum testi |
| DD13 | Metal yük yolu, ASA dış kabuk, seçici PAHT-CF, PETG prototip, TPU tampon | Kupon/ısı/nem sonuçları |
| DD14 | Üç 100 mm gövde; 300×196×3 mm metal alt plaka | Sehim, imalat ve montaj incelemesi |
| DD15 | Bağımsız teker yatağı ve özgün göbek | Dar aksiyel hacim PH4 kritik açık madde |
| DD16 | Yüklü CG ≤110 mm; 2 kg yük CG'si ≤190 mm örneği | Her yeni yük konfigürasyonu |
| DD17 | Ubuntu 24.04 arm64 + ROS 2 Jazzy; önce UVC kamera | Gerçek CM5 boot/kamera/CAN uyumu |
| DD18 | Web panel CM5 üzerinde yerel çalışır | Ağ erişim ve komut tazeliği testi |
| DD19 | AI yüksek seviye öneri/görev üretir; hareket arbiter ve MCU sınırlarını değiştirmez | V2–V5 her geçişte güvenlik regresyonu |
| DD20 | PH2 CAD arayüz/zarf modelidir; PH4 imalat modelinden ayrıdır | Rulman, tolerans, konektör ve malzeme testleri kapanınca |

Süreç kararı: kullanıcının ayrıntılı gereksinimleri ve «şimdi başla» talimatı doğrultusunda ilk 16 çıktı hazırlanır, ardından CAD mimarisine geçilir. Donanım doğrulaması ve üretim siparişi yapılmış gibi sunulmaz.

**DD21:** Gövde üstü146 mm; kasa dahil55 mm batarya z83–138, kapak altı143. Başlangıç140 mm hedefinden6 mm sapma, ölçü/tolerans incelemesinde gerçek batarya boşluğu için. İki150 mm rijitleştirici motorlar arasında; sehim onayı PH4'te açık.

## D1 tahrik detayı — aday kararlar

**DD22:** D1 dış genişlik300 mm /iz270 mm. İki bağımsız yatak +31,8 mm kaplin için ayrılan hacim; kullanıcının300 mm üst sınırı içinde. A0 ölçüleri henüz değiştirilmedi; D1 ayrı aday montajdır.

**DD23:** Pololu çizimindeki7 mm gövde/mil kaçıklığı x yönüne çevrilir. 22 mm toplam çıkıntı ve16 mm kullanılabilir mil ayrı ölçülerdir. Motor yerleşimi ve dört M3 delik buna göre modellenir.

**DD24:** 8 mm mil/608 fikri ön yük hesabında elendi. 10 mm C45 mil +iki6000 rulman adayı;3g/iki teker ve μ=1 varsayımında ön akma payı2,32. Varsayılan çentik katsayısı ve sertifikalı malzeme kontrolü açık; üretim onayı değil.

**DD25:** Lastik torku sekiz mekanik tırnak üzerinden taşınır; TPU-rim sürtünmesi tek tutma yöntemi değildir. CNC metal taşıyıcı yük yolunda kalır. Kaplin MOCT25-6-A/AT disk/MOCT25-10-A koşullu adaydır.

**DD26:** D1'in kütle revizyonu0,90 kg rezervi tüketiyor. Ana tasarımın6 kg hedefi kapanmadı. Hafifletme, tolerans/vida/segman ve servis erişimi tamamlanmadan PH4 release yapılmaz. Ayrıntılar [D1 raporunda](drivetrain_detail_D1.md).

## D2A duyarlılık ve kütle kararı

**DD27:** Ø8/608 seçeneği 9 kg/3g/μ=1,2 taramasında mil1,89 ve rulman1,79 payda kalır; yaklaşık109 g/araç kütle kazancı için seçilmedi. D1'in Ø10 C45 mili aynı koşulda1,73 paydadır. Yeni mil malzemesi, Ø56 kaynak billet kesitinde sertifikalı minimum650 MPa akma koşuluyla 42CrMo4+QT adayıdır; Ø10/6000 geometri korunur. Yorulma ve geçme açık. [D2 karşılaştırması](drivetrain_trade_D2.md).

**DD28:** Jant webindeki dört pencere ve lastik kaburgalar arası2 mm inceltme D2A baskı adayıdır. Gerçek CAD hacmiyle boş kütle5,933 kg tahmini; yalnız67 g rezerv kaldığı için SYS-004/PH4 gerçek tartım olmadan geçmez. Metal taşıyıcı ve şasi keyfi hafifletilmez.

## P0 elektronik pin seçimi

**DD29:** STM32G474VET6 I²C2 ölçüm hattı PA8 SDA / PA9 SCL, AF4 olarak atanır. Eski PB10/PB11 adayı ST DS12288 Tablo 13'te I²C2 işlevi taşımadığı için çıkarıldı. PB8-BOOT0 pull-up riski nedeniyle I²C1 seçilmedi. Aday pinler KiCad LQFP100 sembolüyle otomatik karşılaştırıldı; CubeMX, elektriksel bağlantı, şematik/ERC ve donanım doğrulaması açık. [Pin incelemesi](mcu_pinmap_review.md).

**DD30:** TI DRV8874, sabit PMODE=High PWM modunda kullanılır. PH/EN modunda `EN=0` frenleme yaptığı için nötr/coast gereksinimiyle uyuşmaz. Her motor için TIM8 IN1 ve TIM1 IN2 kanalları ayrılır; `00` coast, tek giriş PWM ileri/geri, iki giriş 1 brake durumudur. TIM1 ve TIM8 break girişleri eklenir; haricî nSLEEP ve K1/K2 bağımsız güvenlik katmanı olarak kalır. Timer senkronizasyonu, boş geçiş, ADC akımı ve fiziksel davranış henüz onaylanmadı. [TI sürüş tablosu](https://www.ti.com/lit/ds/symlink/drv8874.pdf), [pin incelemesi](mcu_pinmap_review.md).

**DD31:** İlk PWR↔MCU taslağındaki ayrı Mega-Fit motor/AWG14 ve Micro-Fit kontrol/AWG20 dönüşleri, 15 A motor akımında ideal tel direnciyle bile yaklaşık3,7 A'yı AWG20 kontrol GND'sine taşıyordu; 2 A zarfı aşıldığı için reddedildi. Revizyon: motor `ACT_BUS` ve sürekli `5V_CONTROL` tek 4 pin Mega-Fit J-PWR üzerinde, ACT+ ve iki ortak GND AWG12, 5 V+ AWG16; 10 düşük akım güvenlik/telemetri sinyali ayrı JST GH J-SIG. Molex'in 4 devre/AWG12 çıplak bakır referansı18 A; 15 A motor+2 A kontrol tek GND arızasında dar pay bırakır, 50 °C/krimp/PCB termali açık. Çift NC E-stop PWR'ye doğrudan gider. 53 MCU pin ataması sembol kontrolünü geçti. Başka dönüşlerden dolaşım akımı, güçsüz giriş geri beslemesi ve demet kütlesi de açık. [Arayüz sözleşmesi](pwr_mcu_interface.md).

**DD32:** J-PWR kart ayak izi için KiCad 10 `Molex_Mega-Fit_76829-0004_2x02_P5.70mm_Vertical` **adayı** denetlendi. Pad1 `ACT_BUS`, pad4 `5V_CONTROL` fiziksel olarak çapraz; pad2/3 iki ortak AWG12 dönüşüdür. [JSON pin haritası](../config/pwr_mcu_connector.json) ve [regresyon kontrolü](../tests/check_pwr_mcu_connector.py) yanlış pozitif pad değişimini reddeder. KiCad courtyard20,10×15,04 mm ve Molex takılı yükseklik16,78 mm yalnız PCB yerleşim girdisidir; AWG12 kablo çıkışı/mandal servisi mevcut kart/CM5 zarfında çözülmedi. Dişi housing cavity yönü de açık olduğundan harness üretim onayı değildir.

**DD33 (DD32 revizyonu):** 5 mm kart/CM5 aralığı nedeniyle dikey J-PWR header adayı bırakıldı. [Molex 768250004](https://www.molex.com/en-us/products/part-detail/768250004) dik açılı 4 pin ve KiCad `Molex_Mega-Fit_76825-0004_2x02_P5.70mm_Horizontal` yeni adaydır; pad 3/4 y=5,5 mm, pozitifler hâlâ çapraz. Kart kenarı/kablo/mandal hacmi mevcut gövde zarfında **doğrulanmadı**; PH4/7 çıkışı engellidir. [Teknik karşılık](design_review_response.md).

**DD34:** Harici 0,4 m tek uçlu I²C kablo kabul edilmedi. INA228, 2 mΩ şöntün yanında PWR kartında kalır; MCU PA8/PA9 ve INA228'in yerel I²C'si arasında iki PCA9615 ile dört damar diferansiyel SCL/SDA taşınır. J-SIG 12 pin JST GH oldu. PCA9615 güç/sonlandırma, I²C kurtarma ve güçsüz giriş koruması gerçek kart şematiği ve testle kapanır. Uzak Kelvin hatları da ölçüm/arıza riskinden dolayı seçilmedi. [Arayüz](pwr_mcu_interface.md).

**DD35:** Review'un taşıyıcıdan doğrudan ≥25 g/parça cep açma ve rulmanda “sıfır endplay” önerileri üretim kararı değildir. 0,25 kg kütle marjına varmak için bugünkü hesapta en az 0,183 kg net kazanım gerekir; 4×25 g tek başına yetmez. Rulman kontrollü boşluğu ve Oldham disk aralığı gerçek tolerans/ısıl zincirle belirlenir. E-stop coast eğimde park freni sayılmaz; 11 brake yalnız ayrı enerji testi sonrası değerlendirilir. TIM1/TIM8 faz/preload kanıtı ve iz testi PH8 kapısıdır.

**DD36:** PCA9615 referans devresinde her kartın tek uçlu tarafı `VDD(A)=3,3 V`, diferansiyel tarafı `VDD(B)=5 V` seçildi. NXP'nin 5 V/100 Ω sınıfı kablo örneği temel alınarak her iki uçta, her çift için 600 Ω üst + 120 Ω çapraz + 600 Ω alt bias/sonlandırma kullanıldı. Yerel I²C pull-up 4,7 kΩ. `EN` başlangıçta 10 kΩ pulldown ile kapalıdır: veri sayfasındaki 54 µA azami Low giriş akımı için üst sınır `0,54 V`, 3,3 V `VIL(max)=0,99 V` altında kalır. `PGOOD` kaynağı gerçek kart şematiğinde iki ray kararlı olduğunda High yapacak; `EN` değişimi idle bus koşulunda sınanacak. Bu [KiCad referans çizimi](../electronics/interconnect/differential_i2c_reference.kicad_sch) kart üretim dosyası değildir. Kablo empedansı, 100 kHz dalga şekli, iki yönde güç sırası ve termal/EMI doğrulaması hâlâ açık.

**DD37:** J-PWR/J-SIG ve PCA9615, [MCU](../electronics/ugv_mcu_01/pwr_mcu_interface.kicad_sch) ile [PWR](../electronics/ugv_pwr_01/pwr_mcu_interface.kicad_sch) için ayrı kısmi KiCad arayüz sayfalarına taşındı. Her kartta J-PWR pin2/3 aynı `PGND` ağına bağlanır; kabloda ayrı iki damar ve kontak olarak kalır. Tam kart ERC'si değil: sayfa başına 0 hata ve başka sayfalarda devam edecek sekiz güvenlik + `ACT_BUS` için 9 izole-net uyarısı var. Güçsüz PWR→MCU sinyalleri için [SN74LVC244APWR](powered_off_status_receiver.md) `Ioff` özellikli alıcı adayı ve 10 kΩ çıkış pulldown seçildi. OE/güç sırası, MCU 0–1,65 V brownout ve nSLEEP fan-out doğrulanmadan P0 geri besleme bulgusu kapanmaz.

**DD38 (DD32–33 paketleme yorum düzeltmesi):** A0 `REF-PWR-PCB`/`REF-MCU-PCB` z=57–81 mm kutusu **PCB+bileşen tahsisidir**; z81 çıplak PCB üstü olarak kullanılamaz. 1,6 mm PCB altı z57 varsayımında yüzey z58,6, Molex 76825 takılı üstü z75,38 olur: nominal dikey hacim uygundur. Önceki “81→86 yalnız5mm, dikey konnektör kesin sığmaz” gerekçesi aynı kutunun üstüne konnektörü ikinci kez eklediği için geçerli paketleme kanıtı değildir. Dikey header'a geri dönülmedi; yatay demet/mandal/çıkarma yolu 3B CAD ve gerçek örnek olmadan açık P0. [Kesit ve servis kapısı](electronics_packaging_gate.md).

**DD39:** K1'e 12 V bobini doğrudan 4S bağlama reddedildi. Ön 5 V/1 W TE T9AS1D17-5, PCB zarfında yalnız 2 mm nominal üst pay ve 20 A/28 V **rezistif** DC seri testi taşır; motor-indüktif kesme kanıtı değildir. Panasonic ACTE3CH2A05V 12 V bobin için 10–16 V çalışma ve 25 A/14 V motor kilit testi verse de tam dolu 4S 16,8 V bobini aşar, 16,8 V kontak testi yoktur. K1 MPN'si seçim-açık kalır; 5 V kontrol rayına olası 1 W bobin yükü eklendi ve koşullu PH6 kapısı [ayrı kayda](k1_relay_selection.md) bağlandı.

**DD40:** Altı PWR→MCU status/izin hattı, [ayrı kısmi KiCad alıcı sayfasında](../electronics/ugv_mcu_01/status_receiver.kicad_sch) SN74LVC244APWR pin eşlemesiyle çizildi. Her kullanılan çıkışta 10 kΩ GND pulldown; iki OE ortak `MCU_RAILS_OK_N` ve 10 kΩ 3,3 V pull-up; kullanılmayan girişler GND, çıkışlar NC'dir. [Netlist testi](../tests/check_status_receiver.py) fiziksel pinleri kontrol eder. Altı PWR sürücü kaynağı, açık-drenaj ray gözetimi ve nSLEEP fan-out başka sayfalarda olmadığından bu bağımsız çizim **6 beklenen ERC giriş-sürücü hatası** taşır; tam kart/P0 backfeed onayı değildir.

**DD41:** UGV-MCU-01 CAN fiziksel katmanı için [MCP2562-E/SN](https://www.microchip.com/en-us/product/MCP2562) ön seçildi. 5 V VDD ve 3,3 V VIO, 500 kbit/s klasik CAN'i tek IC ile MCU seviyesine bağlar; STBY reset/Hi-Z sırasında iç pull-up ile standby olur. VIO/VDD güç sırası, TVS, sonlandırma, konnektör ve gerçek EMI testi şematik/PCB kapısıdır. [Arayüz](communication_architecture.md).

**DD42:** Eski `SERVICE` sonrası “giriş precharge” varsayımı, K2 sonrasındaki 4700 µF bulk'u K1 kapanışına karşı korumuyordu. K1/K2 arasına `MID` ölçümü, K2 paralelinde 470 Ω/≥2 W akım sınırlı ön şarj ve ARM öncesi test enjeksiyonu/bleed tasarımı eklendi. 16,8 V/4700 µF için ilk ön şarj akımı35,7 mA, ideal ≤1 V fark süresi6,23 s. K1 ve K2 arızası K1 kapanmadan ayrı sınanır; [işlev ve hata sırası](precharge_and_separator_diagnostics.md) tam analog/gate şematiği ve fiziksel test olmadan onay değildir.

**DD43:** 4700 µF +%20 ve 470 Ω +%5 ile ön şarj yaklaşık7,85 s sürebildiğinden `IDLE→ARMED` tek geçiş yerine hareket izni Low kalan `ARMING` durumu eklendi. SELF_TEST için5 s ve ARMING'de boşalma+tanı+ön şarj için15 s taslak timeout; pil/direnç ±%5 taramasında sağlıklı `MID` 11,17–15,41 V, K2/ön şarj kısa ise1,46–2,36 V. PWR'de TCA9534APWR komut ve ADS1115IDGSR ADC adayları mevcut diferansiyel I²C arayüzüne atanır. İki seri test FET'inden biri NC/WD izinle fiziksel olarak açılır; yalnız gate Low tek FET-kısa arızasını yalıtmaz. [Hesap/sıra](precharge_and_separator_diagnostics.md) test/şematik kapısıdır.

**DD44:** TPS3431'in `CWD=10 kΩ` fabrika 170–230 ms watchdog ayarı ≤100 ms trip hedefini karşılamaz. 100 pF C0G CWD ile veri sayfası formülünden yaklaşık62,74 ms nominal ve +%5 C/IC üst çarpanla yaklaşık69,12 ms ön değer seçildi. `EN`/`SET1` MCU kontrolüne verilmez; `WDO`, `ENOUT` ve ayrı 3,3 V PGOOD birlikte izin zincirini Low'a çekebilir. [Watchdog kapısı](watchdog_design.md) fiziksel osiloskop ve sıcaklık doğrulaması bekler.

**DD45:** `ARMING` fazında `BLEED→TEST→K1→PRECHARGE→K2` sıra ve yeniden arm/reset için yeni giriş kenarı [host C11 güvenlik çekirdeğinde](../firmware/stm32/safety_core.c) uygulanıp [senaryo testiyle](../tests/safety_core_test.c) kontrol edildi. K1/K2 feedback'in komuttan önce High olması veya K1 sonrası ön şarjın zaten bitmiş görünmesi `FAULT` olur; yalnız ön test ve sıralama bitince aktüatör izin isteği çıkar. Bu kod bağımsız PWR donanım gate'inin, ADC kalibrasyonunun, gerçek watchdog'un veya STM32 üzerinde doğrulamanın yerini tutmaz.

**DD46:** K2 için [LM74900QRGERQ1 + 2×CSD18540Q5BT](k2_separator_selection.md) koşullu adaydır. Kontrolcünün `SLEEP=Low, EN=High` modu iç 7 Ω bypass ile akım geçirebildiği için güvenli OFF değildir; SLEEP EN'e bağlanır, bağımsız güvenlik zinciri EN'i Low'a çeker. 15 A'da 25 °C maksimum Rds ile çift FET 0,99 W; sıcak 2×Rds senaryosunda 1,98 W. 50 °C/W termal değer FET başına 1 in²/2 oz bakır ister; min-pad 125 °C/W kabul edilemez dereceye yaklaşır. Ayrı K2 Kelvin şöntü, latch-off, transiyent, gerçek bakır ve ≤150 ms kesme ölçümü PH6 kapısıdır.

**DD47:** Host [safety_core](../firmware/stm32/safety_core.c), yeni ARM isteği sırasında önceki çevrimden kalmış `separator_test_ok`, `precharge_complete` veya K1/K2 feedback High görürse artık `FAULT` verir. ARMING boyunca K1/K2'nin komut edilmeden High olması da fault'tur. [Regresyon senaryosu](../tests/safety_core_test.c) bunu denetler. Bu kontrol girişlerin taze ve elektriksel olarak doğru üretildiği varsayımını kaldırmaz; ADC/feedback kaynak yaşı PH8/PH11 kapısıdır.

**DD48:** 0x110 CAN lease çerçevesi 8 bayta sığacak şekilde `session32 + lease_seq16 + version_mode8 + deadman8` olarak sabitlendi; eski ayrı `protocol16` tarifi çelişkiliydi. 0x100 hız çerçevesinin kendi `cmd_seq16` değeri ve düşük16 bit oturum etiketi vardır; her iki akışın yaşı ≤100 ms olmalıdır. Tekrarlanan/geri sıralı çerçeve tazelik sayacını yenileyemez. [Host çözücü](../firmware/stm32/can_protocol.c) ve [negatif test](../tests/can_protocol_test.c) fiziksel FDCAN, gateway yetkisi veya aktüatör güvenliği kanıtı değildir.

**DD49:** Kullanıcının sıcak sarı/koyu köşeli özgün UGV yönü [A1 kavram CAD](../cad/assembly/generated/UGV-01-A1-concept.step) ve [stil sınırlarına](exterior_language_A1.md) aktarıldı. Kameralı çift göz modülü sonraki revizyona ertelendi; A1 ön duvarda 24×16 mm kavram açıklığı ve üstte düz 50×50 mm flanş bırakır. Kapakların üst kenarı 1 mm pahlandı. İlk 22×20×10 mm kamera zarfının belgeli gerçek modülden küçük olduğu görüldü; [Camera Module 3 Standard](front_camera_A1.md) 11,5×25×24 mm dış tahsisine düzeltildi. Kamera podu için ön x yönünde yalnız 3,25 mm pay kalır; lens/FFC/darbe/montaj ve D2A tekerlerin A1'e entegrasyonu açık olduğundan üretim onayı değildir.

**DD50:** [A1 gövde STEP hacim taraması](body_mass_screen_A1.md), ASA için üretici 1,05 g/cm³ ve seçilmemiş TPU için muhafazakâr 1,25 g/cm³ ile %100 dolu eşdeğerde 738,6 g verir; 700 g gövde tahsisi 38,6 g aşılır. D2A 5,933 kg tahminindeki kâğıt kütle payı aynı varsayımla 28,6 g olur. İnfill/shell oranı veya tampon boşaltması tek başına kabul kararı değildir; 0,25–0,30 kg doğrulanmış marj için slicer hesabı, TPU darbe/ısı testi ve tüm araç tartımı gerekir. CAD geometrisi bu kanıt olmadan yalnız kütle uğruna inceltilmedi.

**DD51:** UGV-PWR-01 için [K2 koşullu KiCad referans şeması](../electronics/ugv_pwr_01/k2_reference.kicad_sch) çizildi. LM74900QRGERQ1'in Rev C pin haritası, CSD18540Q5BT çift FET, 1 mΩ Kelvin şönt, SLEEP=EN, varsayılan EN Low, 100 kΩ TMR latch seçimi ve elektriksel yüzen RTN pad25 netlistte denetlendi. 31,6 kΩ ILIM ile OCP 18,95 A tipik/16,28–21,13 A ön tolerans; SCP 17,68–23,00 A. 15 A tipik OCP, 4 sürücü+servo eşzamanlı giriş yükünün yaklaşık13,94 A üst taramasında alt toleransta yalancı kesme riski verdiği için seçilmedi. Bu yüksek OCP ayarı 15 A sürekli termal veya F1 sigorta koordinasyonu onayı değildir. [Ayrıntı](k2_reference_schematic.md). K1, ön şarj/bleed, bağımsız SAFE_EN, transient/PCB ve fiziksel T13 açık.

## PWR güç/güvenlik yolu KiCad sayfaları — 24.09.2026

**DD52:** UGV-PWR-01'in `F1→K1→MID→K2→ACT_BUS` yolu, ön şarj/bleed/test enjeksiyonu, çift NC E-stop ve watchdog izin zinciri [beş sayfalı kısmi KiCad hiyerarşisine](../electronics/ugv_pwr_01/ugv_pwr_01.kicad_sch) taşındı: arayüz (5xx referans), K2, [aktüatör yolu](../electronics/ugv_pwr_01/actuator_path.kicad_sch), [güvenlik kapısı](../electronics/ugv_pwr_01/safety_gate.kicad_sch), [ARM I/O](../electronics/ugv_pwr_01/arming_io.kicad_sch). Sayfalar arası ağlar global etiket, her sayfa hem kendi hem kök yolunda annotate edilir. KiCad 10 aynı ağda iki PWR_FLAG'i hata saydığından `PWR_3V3`, `5V_CONTROL`, `PGND` yalnız kart girişi olan arayüz sayfasında işaretlendi; bu yüzden K2 sayfasının tek başına ERC'si artık 1 beklenen `PGND` sürücü hatası verir. **Kanıt birleşik ERC'dir: 0 hata, 1 uyarı** (`MOTOR_FEED`, çizilmemiş STAR/INA228 beslemesi). Tam kart, PCB veya üretim onayı değildir. [Ayrıntı](pwr_safety_path.md).

**DD53:** Çift NC kanalları enerji taşır: NC-A, K1 bobininin üst ucunu (`ESTOP_A_5V`) besler; NC-B, K2 `EN=SLEEP`, ön şarj ve test izin sürücülerinin SN74LVC1T45 B tarafını (`ESTOP_B_5V`) besler. Lojik zincir `CHAIN_OK = NC_A ∧ NC_B ∧ WD_OK`, `SAFE_GATE = LATCH_OK ∧ CHAIN_OK ∧ MCU_RUN_REQ`; her komut (`K1/K2/ön şarj/test/ACT_EN`) `SAFE_GATE` ile AND'lenir. Netlistten değerlendirilen 4 096 senaryoda bütün lojik High'a takılı olsa bile tek bir açık NC, `K1 ∧ (K2 ∨ ön şarj)` yolunu keser. Watchdog veya yazılım açık NC'yi veto edemez. LM74900 SLEEP E-stop sayılmadı; `SLEEP=EN` donanımla Low tutulur, pad25 yüzer. Kanallar arası/5 V'a kısa donanımda ayırt edilmez; MCU A/B tutarsızlığı ve test darbeli kanal PH6 FMEA konusudur.

**DD54 (DD44 uygulaması):** TPS3431 `EN` sabit High yerine TPS3808G33 `RAIL_OK` ile sürülür; MCU'ya bağlı değildir. Ray düşünce `ENOUT` Low olur ve `WD_OK = WDO ∧ ENOUT` açık-drenaj bağlantısı izni keser; böylece watchdog belgesindeki ayrı PGOOD şartını karşılar. `SET1` 3,3 V'a bağlı, `CWD` 100 pF C0G, `WDI` 1 kΩ + 100 kΩ pulldown. `SET1` Low kısa arızası watchdog'u sessizce kapatacağı için SELF_TEST'te WDI'yi bilerek durdurup `PWR_WD_OK` düşüşünü görmek PH8 gereksinimi oldu.

**DD55:** Yerel reset latch'i 74LVC2G74'tür: `/CLR=CHAIN_OK`, saat reset butonunun **bırakma** kenarı (Schmitt, 10 kΩ/100 nF). Takılı basılı buton yeniden kurma yapamaz. `MCU_RUN_REQ` latch'i temizlemez; durum makinesi normal disarm→ARM için yerel reset istemediği için bu seçildi. TCA9534A MCU resetinde son çıkışını koruduğundan “ARMING girişinde TCA çıkışları sıfırlanıp geri okunmadan `MCU_RUN_REQ` High yapılmaz” PH8 yazılım gereksinimidir.

**DD56:** Ön şarj BSS84 P-FET (kaynak MID) + 470 Ω ≥2 W; ACT bleed 150 Ω/5 W + BSS138, `PWR_ACT_EN` High iken 2N7002 ile donanımda kilitli; test enjeksiyonu `F1_OUT→Q206 izin→Q208 komut→1 kΩ→MID`. MID bleed 8,25 k/1,65 k %0,1 bölücü oldu. Netlist değerleriyle sağlıklı test penceresi 11,11–15,24 V, K2/ön şarj kısa penceresi 1,46–2,35 V; 8 V eşiğe ±0,3 V ADC ile pay var. Ön şarj ≤7,85 s, bleed ≤2,51 s. Küçük FET'lerin veri sayfaları bu oturumda indirilemedi ve ACT TVS/dump clamp çizilmediği için 50/60 V sınırları korunmuş sayılmaz.

**DD57:** `PWR_K1_FB`/`PWR_K2_FB`, ADS1115'ten bağımsız LM2903 karşılaştırıcılarıdır: `MID > 0,96·F1 + 0,15 V`, `ACT > 0,96·MID + 0,15 V`. Komutla AND'lenmez; kaynaklı kontak görünür kalır. Test enjeksiyonu ve kapalı K1 arasında her iki uçta ≥0,2 V kâğıt payı vardır; histerezis yok. K2 iletimi için ön şarj kapalıyken kısa bleed darbesi (≈29 ms'de %4 düşüş) önerildi; güvenlik çekirdeğine henüz eklenmedi.

**DD58:** TCA9534A haritası: P0 `TEST_CMD`, P1 `PRECHARGE_CMD`, P2 `BLEED_CMD`, P3 `K1_CMD`, P4 `K2_CMD`, P5 `ACT_ENABLE_REQ`, P6 `K2_FLT` girişi, P7 `LATCH_OK` girişi. Komut varsayılanları tüketici tarafında 100 kΩ pulldown. LM74900 `FLT` UVLO'da da düştüğü ve shutdown davranışı veri sayfasında tanımsız olduğu için donanım latch'ine bağlanmadı; OCP sonrası yeniden etkinleştirme şimdilik MCU FAULT/yerel reset kuralına dayanır, EN kenarı blanking'i ölçülünce yeniden açılır.

**DD59 (K1 paketleme toleransı):** K1 şemada genel SPST-NO simgesi, `MPN OPEN` ve **boş footprint** ile kaldı. TE T9AS1D17-5'in 2 mm nominal z payı; raf düzlüğü ±0,5, PCB kalınlığı +0,16, röle yüksekliği +0,3 (doğrulanmamış varsayım), oturma +0,1, IPC eğilme %0,75×120 mm = 0,9 ve kapak baskı ±0,3 mm ile en kötü durumda 2,26 mm tüketilir (−0,26 mm), RSS 1,13 mm'dir. Paketleme kapanmadı; üretici STEP'i ve ölçüm ya da K1'i şasiye kart dışı montaj seçeneği gerekir. BOM `SELECTION-OPEN-K1` olarak kalır.

## Genel tasarım denetimi ve A2 yönü — 24.09.2026

**DD60:** [Denetim R07](design_review_2026-09-24.md): host güvenlik çekirdeği IDLE→ARMING'de ARM kenarını yalnız **500 ms kesintisiz nötr** sonrası kabul eder; zamanlayıcı her durum geçişinde ve nötr bozulduğunda sıfırlanır. Önceki kod anlık nötrü yeterli sayıyordu ve [güvenlik mimarisindeki](safety_architecture.md) 500 ms şartını uygulamıyordu. [Senaryo testi](../tests/safety_core_test.c) önce başarısız oldu, düzeltmeden sonra geçti. Web panel ARM düğmesi bu süre dolmadan etkin gösterilmemelidir (PH12). STM32 üzerinde doğrulama ve HIL açık.

**DD61:** Kullanıcı A2 yönünü onayladı: tekerler kalır; gövde/baş sevimli animasyon robotlarından **ilham alan özgün** tasarım (başka bir karakterin adı/logosu/birebir oranı yok); boyunlu iki kameralı pan/tilt baş; sağ kol işlevsel (DS3218MG omuz + MG90S pençe, ≤150 g), sol kol pasif; toplam 8 kg korunur; hibrit denetimli AI (bulutta `claude-sonnet-5`, araç üstünde refleksler ve 2 ToF), yazılı + sesli komut. Denetim R03 ile baş mevcut 0,30 kg kule tahsisine sığdığından boş ≈6,13–6,16 kg, yük ≈1,85 kg, yüklü CG ≈107–108 mm. [Spec](superpowers/specs/2026-09-24-a2-character-ai-design.md). GitHub/LinkedIn paylaşımı proje tamamlanınca.

## A2 mekanik karakter — 24.09.2026

**DD62:** [A2 CAD](exterior_language_A2.md) 46 katıyla üretildi: pan/tilt boyun (MG90S ×2, Ø32/Ø20 rulman), kaşlı iki göz kabuğu ve Camera Module 3 tahsisi (y±30,5), omuz kuleli işlevsel sağ kol (DS3218MG + MG90S pençe) ve pasif sol kol, A1 ön kamera açıklığının yerine 8×120×6 mm ışık şeridi, ön kapakta kule çentikleri. Uygulamada verilen kararlar: (1) kol boyu spec'teki ≈160 mm yerine **200 mm**, çünkü z176 omuzdan tamponun önünde zemine ancak bu boyla ulaşılır; (2) çalışma açısı **−55°**, −60° pençeyi zemin altına sokuyordu; (3) park açısı **180°**: ilk 150° kolları anten gibi yukarı kaldırıyordu. 180°'de kollar gövde üst kenarı boyunca yatar; karakter hedefine daha yakın ve siluet daha alçak; (4) kol park↔çalışma arasında yalnız **üstten** döner; 5° adımla 48 açıda çakışma yok, eklem aralığı [−55°, 180°] yazılımda zorunlu (R47); (5) tilt −60…+30°, pan ±90°; URDF sınırları config'ten türetilir; (6) faydalı yük, kullanıcının "≈1,5 kg" kararına göre **1,5 kg**. 1,75 kg yüklü CG'yi 109,3 mm'ye çıkarıp 110 mm sınırına 0,7 mm bırakıyordu; 1,5 kg ile 106,7 mm ve brüt 8 kg'a 0,25 kg hesap payı. CAD taraması: baş 195,4/300 g, kollar 186,9/235 g, gövde 730,5/700 g. Boş 6,235 kg, CG x−2,35/z86,67 mm. Bu değerler DD61'deki ön tahminlerin (boş ≈6,13–6,16 kg, yük ≈1,85 kg, CG ≈107–108 mm) yerini alır. A1 ön kamera riski R40 kapandı; R46 (CG payı) ve R47 (kıstırma/kol yolu) açıldı. Artık üretilmeyen üç eski REF STEP dosyası (ön kamera, mast kolonu, A0 kamera) `generated/`'dan çöp kutusuna taşındı; içerikleri arşiv A0/A1 montaj STEP'lerinde duruyor. Servo kornası, rulman tutucu, kablo burulması, omuz yük yolu ve baskı açık; üretim onayı değildir. Sonradan (alt proje 3 sırasında) eklenen karar: servo rayı kesildiğinde park kolunun ilk ≈2 mm kapak kenarına, sonra ön lastiğe düşebileceği görüldü; pençe gövdesi 4 mm içe genişletildi ve `check_cad` gevşek kolun ≤10° içinde kapağa oturmasını ister (185°, orta kapak).

## A2 elektronik — 24.09.2026

**DD63:** [A2 elektronik](a2_electronics.md): 6 V / 4 A servo buck'ı **MCU kartında**, J-PWR ile zaten gelen E-stop kesmeli `ACT_BUS`'tan beslenir; J-SIG değişmez. Ray izni donanımda `SERVO_PWR_REQ AND ACT_PERMIT_BUF` (74LVC1G08, iki giriş pulldown'lı). Ray akımı 10 mΩ + INA180A2 (0,5 V/A, 6,6 A tam ölçek) → ADC2; motor akımları ADC1'de kalır. Servo sinyallerinde 1 kΩ seri direnç; dijital servo PWM'siz pozisyon tutabileceğinden "gevşet" yalnız ray kesmesidir. Işık şeridi `5V_CONTROL`'den 0,2 A PTC ile ayrılır, veri SPI2_MOSI → 74AHCT1G125. Yeni pinler: omuz PB9 TIM17_CH1, pençe PE3 TIM20_CH2, PE8 istek, PC4 akım, PB15 ışık (58 atama); doğrulayıcı PB8/BOOT0'ı ve servo zamanlayıcılarının paylaşılmasını reddeder. İki CSI kamera ve iki VL53L1X (XSHUT adreslemeli) CM5 IO kartına bağlanır. Güç bütçesi 65,0/113,8 W (config'e taşındı), tipik 1,30 saat; BOM V1 2082 USD. [KiCad sayfası](../electronics/ugv_mcu_01/servo_light.kicad_sch) netlist ve ERC testinden geçti; buck IC'si, CubeMX AF teyidi ve kart ERC'si açık. Uygulama sırasında gevşek kolun ön lastiğe düşebileceği görülüp DD62'deki kapak dayanağı eklendi.

## A2 AI ve yazılım — 24.09.2026

**DD64:** [Denetimli AI](ai_control.md) üç katmanlı yazıldı ve ücretsiz host testlerinden geçti. (1) CM5 `ai_bridge`: `claude-sonnet-5` ile **manuel araç döngüsü**. Tool runner seçilmedi: her API çağrısından önce donanım izni ve dur bayrağı kontrol edilmeli, adım/dolar tavanı `usage`'dan uygulanmalı, istemci testte basit bir sahte nesneyle değiştirilebilmeli ve beta bağımlılığı olmamalıydı. `refusal`/`max_tokens` turunda hiçbir araç yürütülmez. (2) İnternetsiz `skill_executor`: katı ama sayısal sınırsız şemaların bütün sınırlarını yerelde zorlar; hareketi dur, izin/lease (>100 ms) kaybı veya ön ToF <0,25 m keser; kol öndeyken sürüş yok. (3) MCU: 0x120/0x121 çerçeveleri, AI modunda/bayat bayrakta 200 mm/s tavan, servo sınır/rampa/ray sıralaması/aşırı akım latch'i, ışık şeridi ≤0,5 W. Panel "dur" sözünü yerelde işler; sesli komut kutuya yazılır ve gönderme operatörde kalır. API anahtarı yalnız araçta (`.gitignore`: `secrets/`, `*.env`). Gerçek API duman testi ücretli olduğundan kullanıcı onayına bırakıldı; sunucu/ROS yapıştırıcısı alt proje 5.

## A3 Lite bütçe ve DeepSeek — 24.09.2026

**DD65:** Kullanıcı robot parça bütçesini **≤10.000 TL** (≈205 USD, kur ≈48,8) ile sınırladı; A2 V1 BOM ≈101.600 TL idi. Kullanıcı kararları: Lite mimari (araçta ESP32-S3 + iki ESP32-CAM göz, AI ve panel MacBook'ta), 330×270 mm ve A2 görünümü korunur, 3D yazıcı hariç, filament tahmini ≈2.000 TL (>1.000 TL eşiği) olduğu için dahil. Tahmini yerel BOM ≈9.200 TL; [A3 Lite spec'i](superpowers/specs/2026-09-24-a3-lite-budget-design.md) uygulama öncesi kullanıcı onayı bekler. AI modeli kullanıcı isteğiyle DeepSeek'e geçti. İstenen V4.1 Pro yayınlanmadı ve `deepseek-v4-pro` görüntü almıyor; bu yüzden görüntü + araç çağırma destekli `deepseek-flash` (V4.1 Flash) varsayılan yapıldı ve DeepSeek'in Anthropic uyumlu uç noktasıyla aynı köprü kullanılıyor. Claude seçenek olarak kaldı. Görev tavanı 0,10 USD. Performans iddiası doğrulanmadı; kullanıcı anahtarıyla ≤0,10 USD duman testi yapılacak. Anahtar yalnız MacBook'ta 600 izinli dosyada ve ortam değişkeninde durur, sohbete yazılmaz.

**DD66:** A3 Lite mekanik (L1, [Lite mekanik](lite_mechanical_A3.md)). A2 [arşivlendi](revisions/A2/README.md); D1/D2A tahrik araçları A2 arşiv config'ini okur. `config/vehicle.json` revision **A3**: JGA25-370 12 V 130 dev/dk (Seeed çizimi; stall 4,4 kg·cm / 1,8 A satıcı verisi; 1:45 ve 11 PPR varsayım), 3S1P 18650 3 Ah, brüt 4 kg, yük 0,5 kg, eğim hedefi 15° yerine **5°** (motor anma torku 0,9 kg·cm; 5°'de 1,11 kg·cm / 0,51 A kısa süreli, 0,6 A tavan), azami hız 0,6 m/s, iletişim Wi-Fi UDP. CAD kararları: 5 mm PETG plaka x=−35'te iki parça + ek yerini bağlayan iki baskı kiriş; motor dişli kutusu yan panel deliğinden geçer, yük plakaya oturan baskı kelepçede; tekerler baskı göbek + TPU lastik, D-mil 7,5 mm; batarya x=−60 (CG x 9,5 mm); E-stop arka kapakta; ön tamponda iki ToF penceresi; göz kabukları ESP32-CAM için 48 mm; omuz MG996R. Kütle taraması katı üst sınıra ek olarak 1,2 mm kabuk + %20 dolgu baskı tahmini verir; bütün gruplar tahsis içinde, filament 1.313 g PETG + 252 g TPU (2 + 1 makara). `calculations.py`'den A2'ye özgü bulk kondansatör enerjisi çıkarıldı, plaka yoğunluğu ve rapor etiketleri config'ten gelir. Elektrik belgeleri (güç bütçesi, pin haritası, KiCad) L2'de A3'e taşınacak; o zamana kadar A2 kaydıdır.

**DD67:** A3 Lite elektronik (L2, [Lite elektronik](lite_electronics_A3.md)). ESP32-S3-DevKitC-1 v1.1 N16R8 üzerinde, Espressif J1/J3 tablolarına göre kullanılabilir **23 GPIO'nun tamamı** atandı (octal PSRAM 35–37, RGB LED 38/48, strapping 0/3/45/46, USB 19/20, konsol 43/44 dışarıda). Pin sayısını tutturmak için: TB6612 PWMA/PWMB 3V3'e bağlı ve hız IN1/IN2'de MCPWM ile; sürücü STBY + servo buck EN tek `ACT_EN` (10 k pulldown); iki ToF tek XSHUT. Test yazılırken bulunan hata: E-stop durumunu dijital girişle okumak için 12,6 V'ta ≤3,3 V ve 9,6 V'ta ≥2,48 V veren tek bölücü yoktur; `ESTOP_SENSE` ADC1'e (GPIO2) alındı, E-stop durumu `VM_ACT`/`VBAT_SW` karşılaştırmasıyla belirlenir, `ACT_EN` GPIO21'e geçti. Güç yolu: 3S1P + BMS → 10 A sigorta → ana anahtar → NC E-stop → TB6612 VM + servo buck; mantık buck E-stop'tan önce. A2'nin INA180 servo akım ölçümü ve harici watchdog'u Lite'ta yok; servo akımı buck sınırına, takılma ESP-IDF watchdog'u + `ACT_EN` pulldown'a, motor stall'ı ön enkoderlere bırakıldı. Parça listesi 9.515 TL (485 TL pay). Modül pin sıraları ve Mini560 EN eşiği satın alınan parçayla doğrulanacak.

**DD68:** Dişli sağ omuz (25.09.2026, kullanıcı kararı "baskı dişli ekle"). L1'de DS3218MG (270°) yerine seçilen MG996R yalnız ≈180° döner; kol park (180°) → çalışma (−55°) 235° ister. Ayrıca A2'nin 24 mm genişliğindeki kulesinde servo, mili kol eksenine (y) bakacak biçimde sığmıyordu. Çözüm: MG996R yatık, mili −y'de; 28:20 düz dişli çifti (modül 1,25, 8 mm yüz, 30,2 mm eksen arası, 0,2 mm boşluk) kolu 1,4 kat hızlı çevirir, servo 168° döner (≤170° tasarım sınırı). Kol, M4×40 aksta iki 624ZZ rulmanla yataklanır; sağ kule 69×62×73 mm, sol pasif kule A2 boyutunda kalır. 150 g yükte kol torku 0,35 N·m; servo tarafında 0,49 N·m, MG996R 0,92 N·m (4,8 V) → 1,9× pay. Kol yolu, park ve gevşek-kol sonuçları değişmedi (5° süpürme çakışmasız). CAD 61 katı / 41 STL; kol grubu baskı tahmini 243 g. 270° servolar (RDS3115MG, DS3218MG 270°; yerelde ≈950–1.700 TL, çoğu stokta yok) bütçeyi aşardı. Servo darbesi ters dişli için 2433 → 567 µs (kol −55° → 180°), cihazda kalibre edilir. Açık: kol dişlisi–kol D-kovan bağlantısı, diş aşınması, dişli boşluğu.

**DD69:** Bağımsız inceleme kapanışı ([rapor](claude_review_2026-09-25.md), [kapanış kaydı](review_closure_2026-09-25.md)). Yazılım: sensör örnekleri kullanılmadan önce sonlu sayı denetlenir (R1); `Permit.generation` her izin kaybını sayar, eski görev yenilenen izinle hareket edemez (R2); CAN/UDP çözücüde tazelik ve sıra geçmişi ayrıldı, mod değişimi eski imzalı komutu kabul ettirmez (R3); dev tamsayı girdisi normal hata döner (R9); görüntü kayıtları görev klasörlerinde (R10). Donanım: TB6612'nin önerilen çalışma akımı 1,0 A/kanal (Toshiba veri sayfası); JGA25 sargısı 12,6 V'ta ≈1,9 A çekeceği için her motora 7,5 Ω 10 W seri balast eklendi (sıkışma 0,89 A, en kötü 0,97 A; süre sınırı yok), yerinde dönüş torku için 1:78 motor seçildi ve dört motorun hepsi enkoderli oldu (arka sıkışma, R4/R7). Bedel: hız sınırı 0,6 → **0,3 m/s**, yerinde dönüş muhafazakâr modelde boş pakette µ≤0,48 zeminle sınırlı. E-stop durumu ikinci NC kontaktan doğrudan dijital okunur, kenar kesmede kilitlenir (R6); batarya bölücüsü 100 k/22 k ile ESP32-S3 ATTEN3 0–2,9 V aralığında (R5). Kütle tahsisi genel paydan kollara, motorlara ve elektronik tepsisine aktarıldı (toplam 3,47 kg); tipik görev gücü 14,0 W (1,50 saat). BOM 9.987 TL (13 TL pay). Akım regülasyonlu 4 × DRV8871 (≈10.970 TL) bütçeyi aşıyordu. Fiziksel sıkıştırma, pivot akımı, balast ısınması ve E-stop testleri NOT_RUN.

**DD70:** Lite çekirdeği ve yeniden kontrol kapanışı ([yeniden kontrol](review_recheck_2026-09-25.md), [kapanış kaydı](review_closure_2026-09-25.md)). `firmware/lite/lite_core.{c,h}`: IDLE/ARMED/DRIVING/ESTOP/FAULT; IDLE el sıkışması + 500 ms nötr ARM; 0,5 m/s² rampa ve ileri besleme; AI'da 200, elle 300 mm/s; ToF ileri kesme; E-stop kenar kilidi; STOP; düşük batarya; dört enkoderle teker başına 300 ms stall; imzalı 20 Hz telemetri (0x190/0x1A0/0x1A1). **F1:** balastlı akım sınırı süresiz ısıl uygunluk değildir (firmware arızasında iki kanal ≈1,22 W > 0,89 W). Koruma zamanla sınırlıdır: 300 mm/s gerilim tavanı (≈9,2 V → duran motor ≈0,62 A), çip başına 0,5 W sürekli + 2 J ısı bütçesi (model: ağır yükte ≈20 s), ters yönde bir tur boşa alma ve geri-EMK sınırlayıcı (≤0,9 A). Bilinen sınır: tek kanallı enkoder dıştan geri sürülmeyi göremez (0,3 m/s itilmede ≈1,08 A). **F2:** pivot hesabına yuvarlanma ve köprü kaybı eklendi; 0,6 rad/s dönüş boş pakette µ≤0,33, nominal µ≤0,40, dolu µ≤0,49; kopma µ≤0,42. Önceki "µ≤0,48" iddiası geri çekildi. **F3:** E-stop basışı 10 k + 1 k üzerinden dolar, τ=1,1 ms, VIH'e en kötü 1,69 ms; bırakma 0,15 ms; kesme `ACT_EN`'i ≤2 ms'de düşürür. BOM filament notu 1,37 kg. Isıl sabitler ve µ fiziksel testte (TL1–TL3) kalibre edilir, NOT_RUN. L3 belgeleri DD71'e kaydı.

**DD71:** A3 Lite yazılım L3 tamam ([Lite yazılım](lite_software_A3.md)). MacBook tarafı `software/ugv_lite/`:
- `frames.py`: C ile bayt bayt aynı imzalı datagramlar.
- `vehicle.py`: yürütücünün araç arayüzü. 50 Hz lease/sürüş/servo gönderir; deadman AI izniyle düşer, yeniden kurulum yalnız açık istekle olur. Bayat telemetri `NaN` okunur.
- `gateway.py`: panel yalnız 127.0.0.1'de; lease → izin, stop → yerel dur + 0x080, talimat → görev, "dur" kelimesi → dur, `ask_operator` cevabı.

Uçtan uca test gerçek C çekirdeğini ctypes ile sürer. Ağ: aynı 2,4 GHz Wi-Fi, bağlantı anahtarı `~/.config/ugv/link.env` + ESP32 NVS. ESP32-CAM `/capture` kimlik doğrulamasız olduğu için ayrı SSID önerilir. ESP-IDF sürücüleri ve bring-up L4'tedir.

## M3 karakter gövdesi ve 5 eksenli kol — 25.09.2026

Kullanıcı gövdeyi büyütmek, motorları içeri almak, kolu yandan çıkarmak ve kolun hareketini "overengineering" ile artırmak istedi. Kararlar bana bırakıldı. [Spec](superpowers/specs/2026-09-25-m3-character-body-arm-design.md), [plan](superpowers/plans/2026-09-25-m3-character-body-arm.md). Hepsi CAD/hesap/host testidir; baskı ve fiziksel test NOT_RUN.

**DD72 — karakter gövdesi:**
- **Gövde:** 300 × 200 × z146 → **300 × 236 × z210**. İz 240 → 278 mm, toplam genişlik 270 → 308 mm; dingil mesafesi ve boy değişmedi.
- **Motorlar:** tümüyle duvar iç yüzünün içinde (yüz \|y\| = 114). Duvardan yalnız teker göbeğinin Ø16 boynu, Ø18 delikten geçer. Mil göbeğe 8,5 mm girer; M3 set vidası gövdeyle teker arasındaki 6 mm aralıktadır.
- **Baş:** bütün boyun zinciri gövde üstüne bağlandı. Eğim ekseni − gövde üstü = **122 mm** korunur (eğim ekseni z268 → z332, baş tepesi z361).
- **Çamurluk:** tekerleklerin üstünde çamurluk var (palet üstü görünümü). Tekere 4 mm'den fazla uzak durur; kolun park yeridir.
- **Kütle ve baskı:**
  - PETG baskı tahmini 1.493 → **2.248 g**; %25 fireyle 2,81 kg, yani 3 makara.
  - Kısma seçeneği: 2,4 mm duvar ile yaklaşık −160 g; uygulanmadı, kol yükü yan duvardan geçiyor.

**DD73 — 5 eksenli kol:**
- **Eklemler:** J1 omuz (DS3218MG 270°, gövde içinde) · J2 üst kol dönüşü (MG996R + 6704-2RS) · J3 dirsek (MG996R) · J4 bilek eğimi (MG996R) · J5 bilek dönüşü (MG90S) · J6 pençe (MG90S).
- **Omuz yük yolu:** yan duvardaki boss'ta 6804-2RS rulman kolun yükünü taşır; servo yalnız tork verir. Servo, yan duvara bağlı bir çerçevededir. Kablolar omuz milinin Ø8 deliğinden geçer.
- **Neden J2:** kol hep \|y\| = 136 düzleminde kalıyordu, yani yalnız ileri-geri hareket edebiliyordu. J2 dirseği gövdeye doğru büker; pençe robotun önünde, iki kameranın altında ortaya (y = −3) iner.
- **Uzunluklar:** 100 / 90 / 86 mm.
- **Tork payları** (katalog stall, 4,8–5 V; kol yatay; 150 g uçta; kütleler CAD'den): omuz 2,09 · dönüş ve dirsek 2,19 · bilek 5,84.
  - MG90S bilekte 1,33 kalıyordu, bu yüzden MG996R seçildi.
  - Tek dişli MG996R omuzda yetmiyordu; A3'teki dişli omuz (DD68) kaldırıldı.
- **Duruşlar ve grafik:** park, kaldır (yalnız planlayıcı), yukarı, hazır, öne, yere, öne-orta, depola.
  - Kenarlar: park–kaldır–{yukarı, depola}, yukarı–hazır–{öne, yere, öne-orta}.
  - CAD her duruşu ve her kenarın eklem-uzayı doğrusunu ≤5° adımla süpürür: 0 çakışma.
  - Doğrudan park↔yukarı geçişi, dirseği yan duvara ve kapağa sürüyordu; "kaldır" ara noktası bu yüzden eklendi.
- **Park:** kol çamurluğun üstünde yatar. Servo rayı kesilince omuz 0,5° içinde çamurluğa oturur. Dirsek ve bilek eksenleri düşeydir, yerçekimi bu eklemleri döndürmez.
- **Sol kol:** aynı dış kabuk, pasif; sürtünme bileziği ve rulmanla elle poz verilir.
- **Eklem sınırları:** firmware tablosunda ve config'te aynıdır (test). MG996R/MG90S eklemleri ≤170° kullanır.

**DD74 — Kargo bölmesi:**
- Ön kapakta 38 × 54 mm atma ağzı; üstünde 1,5 mm TPU çapraz yarıklı kapak.
- Altında 78 × 92 × 97 mm kutu: iki ayakla plakaya, flanşla ön duvara bağlı.
- "Depola" duruşunda kavrama merkezi ağzın 23 mm üstündedir. Ağızdan kutu tabanına düşüş yolu boştur (test).
- Önden sokma denendi ve bırakıldı: yandan gelen kolun bileği en fazla \|y\| = 46'ya iner.
- TPU kapağın nesneyi geçirmesi fiziksel testte sınanır; geçirmezse kapak çıkarılır.

**DD75 — Elektronik, protokol, bütçe:**
- **PCA9685:** 8 servo PCA9685'te (I²C0, 0x40). /OE = GPIO39, 10 k pull-up ile reset ve açılışta kapalı. GPIO40–42 boş.
- **Servo rayları:** iki Mini560 5 V 5 A ray; EN = `ACT_EN`, ikisi de E-stop'tan sonra. A rayı J1, J3 ve başı; B rayı J2, J4, J5 ve pençeyi besler. PCA9685'in V+ ucu kullanılmaz.
- **Sigorta:** 10 → 15 A. E-stop kontağından en kötü ≈9,4 A geçer; kontak 12 V DC ≥10 A kesmeli (açık iş).
- **Protokol:** 0x122 (dönüş, dirsek) ve 0x123 (bilek eğimi, bilek dönüşü) eklendi; her kimlik kendi ileri sırasını tutar. **DD76 ile değişti:** 0x122 kol yolu çerçevesi oldu, 0x123 kalktı.
- **MacBook yürütücüsü:** kolu yalnız grafik üzerinden 45°/s ile yürütür ve kol varana kadar bekler (DD76: yürütmeyi artık çekirdek yapar; MacBook telemetriyle bacak bacak ilerler). "Dur" ya da izin kaybında kol olduğu yerde tutulur. Sürüş yalnız park, kaldır, yukarı ve hazır duruşlarında serbesttir.
- **Tahrik:**
  - Brüt kütle 4,0 → 5,1 kg; boş 4,58 kg; CG z117,8 mm. Yüklü CG z130,8 mm; sınır 110 → 135 mm, statik devrilme açısı 33,7°.
  - Rampa: 5°'de boş pakette 0,158 m/s; rampa sınırı 0,2 → 0,15 m/s.
  - Pivot: yürütücünün dönüş hızı 0,6 → 0,45 rad/s. µ sınırı boş 0,30 / nominal 0,36 / dolu 0,45; kopma 0,38. İz genişlediği için kayıp sınırlı kaldı.
  - Çalışma süresi: tipik 16 W → 1,31 saat; ağır 46 W → 0,46 saat.
- **Bütçe:** tavan 10.000 → **13.500 TL** (kullanıcı: "maliyet biraz daha artabilir"). BOM **13.188 TL**, yani +3.201 TL.
  - Servolar: +1.795 TL. DS3218MG 270° 1.100 TL tahmin, yerel stok belirsiz; yedek RDS3115MG 270° 941 TL, 5 V'ta 1,47 N·m, pay 1,74.
  - Üçüncü PETG makarası: +650 TL.
  - Rulmanlar, PCA9685, buck, vida ve kablo: +756 TL.
- **Açık risk:** servo rayı yeniden açıldığında düşmüş kol, son komut açısına servonun tam hızıyla gider (servoda konum geri bildirimi yok). Yeniden ARM etmeden önce kol elle parka alınır; bu, bring-up'ta (L4) denenir.

**DD76 — M3 inceleme düzeltmeleri N1 ve N2 (25.09.2026).** Codex'in yarım kalan M3 incelemesi iki sorun buldu; ikisi de doğrulandı. Düzeltmeler için kullanıcı kararları: "şimdi düzelt" ve "9,2 V tavanı kaldır". [Plan](superpowers/plans/2026-09-25-m3-fix-n1-n2.md).

- **N1 — kol paket kaybı:**
  - Sorun: DD75'te beş eklem üç ayrı pakete bölünmüştü (0x121/0x122/0x123) ve MacBook "vardım" kararını kendi sayacına göre veriyordu. 0x122 düşünce yürütücü "reach_low" dedi; çekirdekte ise üst kol dönüşü 90°, dirsek 0° kaldı, yani CAD'in hiç süpürmediği bir karışım.
  - Yeni tasarım:
    - Duruş grafiği config'ten `firmware/lite/arm_graph.h` olarak üretilir (`tools/gen_arm_graph.py`). Test başlığın config'le birebir aynı olmasını ister.
    - `firmware/lite/arm_path.c`, kolun grafik üzerindeki konumunu (kaynak, hedef, kesir) tutar. Yalnız şu komutları kabul eder: aynı kenar, ters yön, bulunduğu düğümden yeni kenar ya da düğümde tutma. Beş eklemi tek noktadan, CAD'in süpürdüğü doğru üzerinde ilerletir; en hızlı eklem 45°/s.
    - **0x122** = (kaynak, hedef, hedef kesir); **0x123 kaldırıldı**. 0x121 artık yalnız pençe ve AI bayrağı taşır; omuz alanı yok sayılır.
    - Telemetri **0x1A2** (kaynak, hedef, kesir, hedef, yerleşti) eklendi. MacBook bir sonraki kenara yalnız "yerleşti" gelince geçer.
    - Aktüatörler kapanırsa (lease kaybı, E-stop, disarm) hareket iptal olur; yeniden ARM kolu kendiliğinden yürütmez.
  - Testler:
    - %50 paket kaybında kol yine hedefe tam varır; %100 kayıpta yürütücü zaman aşımı verir ve kol parkta kalır.
    - Her tikte beş eklem kenar doğrusundadır.
    - Kenar dışı ve süreksiz komutlar reddedilir. Mutasyonla bu iki denetimi kaldırmak testte yakalanır.
- **N2 — hız döngüsü yoktu:**
  - Sorun: çekirdek yalnız sabit ileri besleme uyguluyordu (0,135 A'lik gerilim payı). 0,45 rad/s dönüşte µ≥0,10 zeminde dört teker STALL veriyordu. Hesaplar ise tam paket gerilimini varsayıyordu. Bu açık L3'ten (DD70) beri vardı.
  - Yeni tasarım:
    - Motor başına PI hız döngüsü (`LITE_KP_MV_PER_RPM`, `LITE_KI_MV_PER_RPM_S`, anti-windup). Kazançlar host modelinde ayarlandı; TL2'de yeniden ayarlanır.
    - DD70'teki 300 mm/s kaynaklı ≈9,2 V gerilim tavanı kalktı; çıkış paket gerilimine kadar çıkabilir. Akımı geri-EMK sınırlayıcı (tahmin ≤0,9 A, gerçek ≤0,825 A) sınırlar. Dönmeyen tekeri 300 ms stall kesmesi, yavaş dönen yüklü çifti TB6612 ısı bütçesi keser (≈3 s).
    - Hesap artık dönüş akımını aynı sınırla kırpar. Sonuç değişmedi: 0,45 rad/s dönüşte µ≤0,30/0,36/0,45, kopmada µ≤0,38. Bu kez firmware bu gerilimi gerçekten uygulayabiliyor. Host modelinde µ=0,3 zeminde 9,7 V pakette tekerler 10 dev/dk'ya ulaşıyor; µ=0,6'da (kapasite üstü) arıza ≤30 s içinde geliyor.
  - F1 kapanışındaki "gerilim tavanı" katmanı bu kayıtla değişti; diğer katmanlar aynen kalır.

Fiziksel testler NOT_RUN. Codex'in tam incelemesi bu düzeltmeler dahil yeniden yapılacak.

**DD77 — Kol açıklığı: 1° süpürme ve ölçülen açıklık (25.09.2026).** Codex'in yarım kalan 1° kontrolü tamamlandı.
- **Süpürme:** 5° yerine 1° adımla yapılıyor (553 örnek): 0 çarpışma.
- **Açıklık ölçümü:** CAD artık her kenarda, dirsekten sonraki hareketli uzuvların en küçük açıklığını da ölçer (`arm_clearance`, 5° örnek). Test sınırları: hareketli uzuvlarda ≥4,5 mm, park duruşunda ≥1 mm.
- **Bulunan sorun:** park → kaldır geçişinde ön kolun dirsek çatalı yan duvar boyunca yalnız 1,5 mm açıklıkla kayıyordu. Parkta dirsek ekseni düşey olduğu için dirsek servosundaki 1°'lik hata pençeyi duvara ≈3 mm yaklaştırır.
- **Düzeltme:** kol düzlemi \|y\| 136 → 138; dirsek ve bilek çatal diskleri r 16,5 → 13; dönüş rulmanı yuvası 3 → 2,5 mm et. Toplam genişlik 308 mm'de kaldı. Yeni en dar hareketli açıklık 4,5 mm (park → kaldır). Diğer kenarlar ≥7 mm.
- **Yan etki:** gevşek kol artık 1,5° içinde çamurluğa oturuyor (önce 0,5°).
- **Kabul ölçütü:** TL4'e dirsek kalibrasyonu ±1° ve yan duvar açıklığı ≥3 mm eklendi.


**DD78 — M3 baskı arayüzleri, gövde tarafı (25.09.2026).** [Plan](superpowers/plans/2026-09-25-m3-print-interfaces.md). Kullanıcı yokken, kol mimarisinden bağımsız kesin arayüzler çizildi.

- **Göz kabuğu:**
  - ESP32-CAM kartı (27 × 40,5 mm) arka duvardaki bir delikten geçemiyor. Bu yüzden arka duvar sıkı geçmeli bir kapak (UGV-MECH-044-±1) oldu; istenirse yapıştırılır.
  - Kart dört ön tırnak ile kapağın bastırma çerçevesi arasında durur. OV2640, FPC ile öne uzanır; lens borusu (Ø8) pencere eksenindeki yuvaya oturur. Pencere Ø12 oldu; yuvanın dış çapı duvara bağlanır.
  - Kamera zarfı gerçek parçalara ayrıldı (kart, ESP32-S modülü, arka bileşenler, FPC, modül, lens). Ölçüler satıcı çiziminden; parçalar gelince doğrulanır.
- **Çamurluk:** flanş yeniden z140'a çıktı (dirsek çatalları küçüldü, DD77). Her parça 3 × M3 ile yan panele bağlanır; somunlar içeride.
- **Omuz servo çerçevesi:**
  - Kollar 8 mm; uçlarında 4 × M3 ısıl insert, vidalar yan duvardan geçer.
  - DS3218 kulakları için 4 delik (49,5 × 10 mm; doğrulanacak).
  - Servo 3 mm içe alındı (mil ucu \|y\| 94,5), böylece kablo çıkışına yer açıldı.
- **Omuz mili:**
  - Uçta 25T disk korna flanşı: 4 × M3 kılavuz, PCD 14 (doğrulanacak).
  - Eksenel kablo deliği korna tarafında kapalı. Kablolar, flanş ile duvar boss'u arasındaki Ø6 radyal delikten çıkar. 225° dönüş için servis halkası bırakılır (açık iş).
- **Kargo kutusu:** flanşında 2 × M3 insert; vidalar ön duvardan geçer.

**Kol uzuvları henüz baskıya hazır değil; karar bekliyor.** (→ DD81'de çözüldü.)
- Sorun: MG996R kulaklarıyla birlikte 54,5 mm uzunluğunda. Dirsek ve bilek çatalına sığmıyor. Servoyu 90° çevirmek ise parkta kolu yan duvara sokuyor. Kavram zarflarında vida ve insert için yeterli et de yok.
- Seçenekler:
  - (a) Kulaklar kesilir; servo, uzvun iki parçalı kabuğunda sıkıştırılır. Uzuvlar ≈6 mm büyür; park açıklığı yeniden hesaplanır.
  - (b) Hazır alüminyum MG996R servo braketleri iskelet olur, baskı parçalar kaplama olur. En sağlamı; ≈300 TL ek.
  - (c) Uzuvlar kulakları alacak kadar büyütülür ve eklem eksenleri kaydırılır.
- Öneri: (a) ya da (b). Codex incelemesinden ve kullanıcı dönüşünden sonra seçilecek.

**DD79 — Baskı planı ve rehberi (25.09.2026).** `tools/print_plan.py`, baskı parçalarının STL'lerini baskı yönünde, tablaya oturmuş halde yazar ve [baskı rehberini](print_guide_A3.md) üretir. Rehber şunları içerir:
- parça başına yön, destek, duvar ve dolgu ile kütle tahmini;
- sıra: önce deneme parçaları (M3 insert, D delik, 6804/6704/624 yuvaları, göz kapağı geçmesi, TPU lastik), sonra şasi, tekerler, gövde, iç düzen, dış parçalar, baş, kollar;
- vida, insert ve rulman listesi: 26 × M3 insert, 3 × 6804, 1 × 6704, 2 × 624.

Yön kararları:
- Yan paneller ve uç duvarlar dış yüzleri tablada basılır.
- Motor kelepçesi kapağı ters çevrilir.
- Göbekler jant yüzü, çamurluklar flanş yüzü tablada basılır.
- Göz kabuğu ön yüzü tablada basılır; dört tırnak için küçük destek gerekir.
- Kargo kutusu arka duvarı tablada basılır; böylece taban köprü olmaz.

`tests/check_print_plan.py`:
- her baskı parçasının tek plan girdisi olduğunu;
- ≤240 mm zarfını ve tablaya gerçekten oturduğunu (temas alanı);
- STL'lerin güncel olduğunu ve rehberin tablodan üretildiğini

denetler. CAD üreteci artık STL yazmıyor.

Pan/tilt servo yuvaları ve kol uzuvları (13 parça) "bekliyor" olarak işaretli. Tilt köprüsünün servo boşluğu kapalı; baş servo yuvaları M2 Task 4'ün kalan işi. Dilimleyici ayarları başlangıç değeridir ve deneme baskılarıyla ayarlanır.


**DD80 — Codex'in yarım M3 incelemesinden iki güvenlik bulgusu (26.09.2026).** Codex'in yarıda kalan son çıktısında iki bulgu vardı. İkisi de host testinde yeniden üretildi ve düzeltildi. Kullanıcı kararı: Codex'e yeni prompt verilmeyecek.

- **Bulgu 1 — eski kol telemetrisi tekrar kabul ediliyordu:**
  - Kök neden: komut yönü oturum ve ileri sırayla korunuyordu; telemetri yalnız HMAC'liydi. MacBook, kaydedilmiş imzalı bir 0x1A2'yi ("stow'da yerleşti") sonradan da taze sayıyordu. Test bunu yeniden üretti: kol `reach_low`'dayken tekrar gönderilen telemetri durumu "stow" yaptı, böylece sürüş kapısı açıldı. Aynı açık gecikmiş odometriyi de etkiliyordu.
  - Düzeltme: telemetri etiketi artık çekirdeğin son kabul ettiği lease'e bağlı. Bağ, oturum32 ile 32 bite genişletilmiş lease sırasından oluşur (`ugv_lite_pack_bound`).
  - MacBook, telemetriyi yalnız son 0,2 s'te kendi gönderdiği bir lease'le doğrular ve yaşını o lease'in gönderim anından sayar. Bu yüzden kaydedilmiş, gecikmiş ya da başka oturumdan gelen telemetri düşer. 16 bit sıra dönüşünde de eski datagram tutmaz.
  - Komut biçimi değişmedi.
- **Bulgu 2 — yeniden ARM'da kol taranmamış yoldan sıçrıyordu:**
  - Kök neden: servo rayları ACT_EN'i izler, bu yüzden ACT_EN düşünce kol gevşer ve sarkar. Buna karşın çekirdek yeniden ARM'da, açılışta ise stow'da varsayarak eski yol noktasına darbe basıyordu. Test bunu yeniden üretti: izin geri gelince `reach_low` darbeleri aynen döndü.
  - Düzeltme: "gevşek kol" kilidi.
    - Açılışta ve kol stow'da oturmamışken ACT_EN düşerse kilit kurulur. Stow'daki gevşek duruş zaten taranmıştı (çamurluğa ≤3°).
    - Kilit sürerken kol servolarına darbe verilmez (servolar beslenir ama gevşek kalır), 0x122 reddedilir ve 0x1A2'nin bit1'i kurulur. MacBook kolu "limp" görür; yürütücü kol ve sürüş komutlarını reddeder.
    - Kilit yalnız **0x123** ile kalkar: "kol elle park edildi" onayı. Onay yalnız aktüatörler kapalıyken, oturum etiketi ve oturum başına ileri sırayla geçer; çekirdek ardından kol yolunu ve servo konumlarını stow'a kurar.
    - Panelde "Kolu elle park ettim" düğmesi var; ağ geçidinde karşılığı `arm_parked`.
    - 0x123, DD76'da kaldırılan eklem çerçevesinin kimliğidir. A2 servo çözücüsü onu hâlâ reddeder; yeni anlamı yalnız Lite çekirdeğinde vardır.
- **Testler:**
  - C bağlantı vektörü (Python hmac ile aynı bayt) ve yanlış bağ reddi.
  - Çekirdek: açılışta gevşek; kuruluyken, yanlış oturumla ya da tekrar edilen sırayla gelen onay reddedilir; hareket ortasındaki kira kaybından sonra darbe yok ve bit1 kurulu; stow'da oturmuşken kira kaybı kilit kurmaz.
  - Uçtan uca: tekrar gönderilen stow telemetrisi durumu değiştirmez; 100 ms geciken telemetri lease'inden yaşlanır; gevşek kolda kol ve dönüş komutları reddedilir; park onayından sonra kol stow darbelerine döner.
  - Mutasyonlar: kilidi, açılış kilidini, "yalnız aktüatör kapalıyken" koşulunu ve darbe kesmeyi kaldırmak; host'ta lease penceresini kaldırmak ya da yaşı varıştan saymak. Altısı da testte yakalanır.
- **Açık:**
  - TL4'te servoların "beslenmiş ama darbesiz" halde gerçekten gevşek kaldığı doğrulanmalı. Bazı dijital servolar son darbeyi tutar; burada rayın az önce kesilmiş olması bunu engeller, yine de ölçülecek.
  - Sürüş kapısı (kol stow, lift, up ya da ready değilken sürme) hâlâ MacBook yürütücüsünde. Çekirdeğe taşınması önerilir ama bu kayda dahil değil.

Fiziksel testler NOT_RUN.

**DD81 — Kol uzvu arayüzleri: kulaklı servolar, 25T korna, 624 idler (26.09.2026).** [Plan](superpowers/plans/2026-09-26-m3-arm-interfaces.md). Kullanıcı yokken DD78'in açık işi çözüldü ("karar senin").

- **(b) alüminyum braketler bırakıldı:**
  - Çok amaçlı braket 58 × 37 × 26 mm (Robotistan 63,70 TL), uzun U braket 56 × 25 × 64,5 mm (≈143 TL).
  - Twist servosunun çevresinde 58 mm'lik braketin sığacağı yön yok: y'de parkta 154 mm ayak izi ve yan duvar, z'de parkta çamurluk, öne-orta'da ön teker.
  - Satıcılar delik düzenini vermiyor.
- **Seçilen yol:** (c)'nin eksen kaydırmasız türevi.
  - **Dirsek ve bilek:**
    - MG996R kulaklarıyla takılır. Mil içe bakar; kulaklar uzvun iç yüzüne 4 × M3 × 10 ile ısıl insertlere bağlanır.
    - Mile 25T alüminyum disk korna takılır; çatalın 5 mm'lik iç yanağı kornaya 4 × M3 ile bağlanır (PCD 14, başlar havşalı).
    - Dış yanakta 624ZZ yatak var: Ø13 yuva, dış bileziği tutan 0,5 mm dudak. M4 × 12, yatağın iç bileziğinden ve 0,5 mm'lik aralık çıkıntısından geçip servo tabanının altındaki gömme somuna girer (duvar 5,5 mm).
    - Çatal köprüsü eksenden 22 mm uzakta, kulakların süpürdüğü r≈19,8 mm'nin dışında. Yuvanın önü r 20,5 mm ile sınırlı.
  - **Twist:**
    - MG996R'nin kulakları gövde hizasında kesilir. Servo, omuz kabuğunun dışa açık cebine girer; üstüne 2 mm kapak (058) 4 × M2 ile vidalanır.
    - Mil 6 mm geri çekildi. 25T korna adaptöre (059) 4 × M3 ile bağlanır; başlar 6704 iç bileziğinin altında havşalı.
    - Adaptörün Ø20 mili 6704'ten geçer. Üst kolun dış parçası (B) göbeğiyle iç bileziği sıkıştırır ve adaptöre 2 × M3 ile bağlanır; vidalar B'nin dirsek servo cebinden takılır.
    - Kabukta korna ve flanş için r13 boşluk var; 6704 yuvası r13,5 olduğundan arada 0,5 mm'lik bir dudak kalır.
  - **Bilek dönüşü ve pençe:** MG90S kulaklarıyla, 2 × M2 kendinden kılavuzlu vidayla Ø1,6 pilotlara. Pençe, dönüş kornasına 2 × M2 ile bağlanır; merkez vidası için Ø5 erişim deliği var.
- **Boylar ve duruşlar:**
  - Ön kol 90 → 80 mm, kavrama 86 → 96 mm; toplam aynı (parkta uç x −162, ayak izi −165).
  - "depola" duruşu 60/90 → 50/98°: kavrama noktası (125, −26, 233), çeneler TPU kapaktan ≥6 mm yukarıda. `arm_graph.h` yeniden üretildi.
- **Baskı:**
  - Çatal yanaklarının r13 diskleri 25 mm uzuv yüksekliğine düzleştirildi. B, C ve D yan yatarak desteksiz basılır (temas 1.225–3.167 mm²); yataklar ve insertler yatay kalır.
  - Pençe dış yüzünden basılır, çenelerin altına destek gerekir. Kapak düz; adaptör flanşından basılır, %100 dolgu.
- **Sonuçlar:**
  - 93 STEP; 65 baskı parçası, yalnız 3 baş parçası bekliyor; 34 M3 insert.
  - Kesişim yok; 1° kenar taramaları temiz.
  - Hareketli açıklık ≥5,26 mm (park → kaldır 5,65 mm), park 1,0 mm; gevşek duruş çamurlukta.
  - Tork payları: omuz 2,25, dönüş ve dirsek 2,36, bilek 5,39.
  - Kol baskı + katalog 621 g.
  - BOM 13.448 TL (25T disk korna × 3, tahmini 90 TL; yerelde yalnız kol tipi 59–68 TL bulundu).
- **Açık:**
  - Çatal geometrisi dirseği ve bileği ≈120°'de durdurur. Config sınırı 135° olarak kaldı; duruşlar en fazla 103° kullanıyor ve firmware yalnız grafik kenarlarında yürür.
  - Kulak yüksekliği ve delik aralıkları satıcı çiziminden alındı; parçalar gelince doğrulanacak. Kablo yolları çizilmedi.

Fiziksel testler NOT_RUN.

**DD82 — Baş mekanizması: pan ve tilt servo yuvaları, boyun, kaş çubuğu (26.09.2026).** [Plan](superpowers/plans/2026-09-26-m3-head-mechanism.md). Kullanıcı DD80/DD81'i onayladı ("kararını onaylıyorum sen devam et"); M2 Task 4'ün son işi olan üç bekleyen baş parçası çizildi.

- **Sorun:** Tilt MG90S'in mil üstüne kadar yüksekliği 31 mm; iki göz kabuğunun arası ise 19 mm.
- **Karar:** doğrudan tahrik.
  - İtme çubuğu mekanizması gözleri yakın tutardı ama ek parça, boşluk ve iki kamera arasında hizalama riski getiriyordu.
  - Göz merkezleri ±30,5 → ±39 mm (stereo taban 61 → 78 mm; derinlik çözünürlüğü de artar). Gözler boyun eksenine ortalandı; kamera yüksekliği z332 (gövdeden 122 mm) aynı.
- **Pan:**
  - MG90S boyun ekseninde. Kulaklarıyla 32,5 mm uzunluğunda olduğu için Ø32 rulman yuvasından geçmez; bu yüzden tabanın açık altından girer ve kulakları üstteki çıkıntıya alttan 2 × M2 ile vidalanır, sonra taban flanşa oturur.
  - 6804, tabanın tepesindeki yuvada (z252–259, altında dudak) durur. Boyun Ø20 mil olarak yataktan geçer; r12 omzu iç bileziğe oturur, alt yüzü pan kornasına 2 × M2 ile bağlanır.
  - Kornanın merkez vidasına boyundaki Ø8 delikten ulaşılır. Başın yükü yatağa gider, servo yalnız tork verir.
- **Tilt:**
  - MG90S, boyun flanşına 2 × M3 ile bağlı köprüde durur; mili +y yönünde, tilt ekseninde. Kulakları köprünün yüzüne 2 × M2 ile bağlanır.
  - Sol göz kabuğunun iç duvarı kornaya 2 × M2 ile bağlanır; vida başları göz içindedir, arka kapaktan ulaşılır.
  - Sağ göz, köprünün Ø8 saplamasında döner. Göz başına ayrı kaşların yerine tek bir kaş çubuğu (UGV-MECH-045) iki gözü üstten 4 × M2 ile rijit bağlar.
- **Kablolar:** kamera 5 V/GND ve tilt servosu boyun deliğinden iner, boyunun arka penceresinden çıkar, tabanın arka yarığından girer. Pan servosunun arkasındaki delikten (13, 0) flanş, kapak ve kiriş üzerinden gövdeye iner. Eksendeki eski delik kalktı.
- **Doğrulama:**
  - 94 STEP, kesişim yok.
  - Tilt −30…+60° 5° adımla tarandı; kesişim yok, kaş çubuğu köprüden ≥5,24 mm uzakta.
  - Probe testleri: kulak pilotları, 6804 yuvası ve dudağı, boyun mili ve deliği, flanş delikleri, köprü insertleri, saplama, korna ve burç delikleri, kaş vidaları.
  - 66 baskı parçası, hiçbiri beklemede değil; 36 M3 insert.
  - Baş 230 g (tahsis 300 g), PETG 2.251 g. BOM değişmedi (M2 vidalar setin içinde, 6804 zaten sayılıydı).
- **Açık:** MG90S kulak aralığı (28 mm) ve korna delik yarıçapı (7 mm) satıcı çiziminden alındı; gelince doğrulanacak. Kablo döngüsü çizilmedi (TL6).

Fiziksel testler NOT_RUN.

**DD83 — Tilt servosu boyna gizlendi, gözler yeniden yakın (26.09.2026).** [Plan](superpowers/plans/2026-09-26-m3-head-hidden-tilt.md). Kullanıcı DD82'deki ara servoya "orda niye servo var çok çirkin duruyor" dedi ve seçeneklerden "Boyuna gizle"yi seçti. DD82'nin tilt kısmı ile göz aralığı bu kayıtla değişti; pan kısmı aynen kalır.

- **Görünüş:**
  - Göz merkezleri ±39 → ±30,5 mm'ye döndü (stereo taban 61 mm). Gözlerin arasında yalnız 6 mm'lik bir bıçak ve aks göbeği var.
  - Göz başına eğik kaşlar geri geldi; kaş çubuğu kalktı.
- **Tilt mekanizması:**
  - **Gizli servo:** MG90S, boynun rulman üstündeki bloğunda durur (041; x 3–47, y −28…10, z 261–287). Blok pan ile birlikte döner. Servo kulaklarıyla bir plakaya (046) 2 × M2 ile vidalanır; plaka bloğun oluklarına üstten kayar. Bloğun kapağı sütunla tek parçadır (042) ve bloğa 4 × M2 ile bağlanır.
  - **Aktarma:**
    - Ø1,5 mm çelik itme çubuğu, servo kornasından sütun içinden yukarı çıkar, sol gözün iç duvarındaki krank pimine gider. İki uç Z bükümlüdür.
    - Kranklar 8 mm; paralelkenar olduğu için göz, servo ile birebir aynı açıda döner.
    - Sütun tepesi z299, gözlerin en alçak noktasının altında kalır. Çubuğun tilt boyunca x 34–38'deki yolu kanalda boştur.
  - **Aks:** gözler, bıçağın Ø9,4 göbeğinde dönen aksla (045) birbirine rijit bağlıdır. Aksın ortası Ø9, uçları AF7 altıgendir ve gözlerin iç duvarlarına geçer. M4 × 30 iki gözü aksa sıkar.
- **Doğrulama:**
  - 96 STEP, kesişim yok. Tilt −30…+60°'de kesişim yok; en küçük açıklık 2,5 mm (gözler ile sütun arası).
  - Probe testleri: plaka kulak pilotları, oluk, blok kablo penceresi, çubuk kanalı, aks göbeği deliği, gözlerdeki altıgen delikler, krank pimi deliği ve çevresindeki et.
  - 67 baskı parçası, hiçbiri beklemede değil; 34 M3 insert.
  - BOM +30 TL (itme çubuğu): 13.478 TL.
- **Test düzeltmesi:** baskı planı testindeki 400 mm'lik temas plakası, küçük parçalarda (aks) OCC kesişimini boş döndürüyordu. Plaka parça boyuna küçültüldü.
- **Açık:** itme çubuğu, önden bakınca gözlerin arasında ince bir tel olarak görünür. Z büküm boşluğu TL6'da ölçülür.

Fiziksel testler NOT_RUN.

**DD84 — Sürüş kilidi çekirdekte; itme çubuğu gizlendi (26.09.2026).** Kullanıcı: "devam et o zaman tasarıma".

- **Sürüş kilidi:**
  - "Kol sürüş duruşunda değilken sürme" kuralı yalnız MacBook yürütücüsündeydi; bir host hatası kol dışarıdayken sürebilirdi.
  - Duruşlar artık config'te (`arm.drive_poses`: stow, lift, up, ready). `arm_graph.h`'a maske olarak üretilir; yürütücü de aynı listeyi config'ten okur.
  - Çekirdek, kol gevşekse ya da bir sürüş duruşunda oturmuş değilse teker hedeflerini 0,5 m/s² rampayla sıfıra indirir; ani fren yoktur. 0x1A0 bayraklarının bit3'ü kalkar.
  - Testler: `reach_mid`'de sürüş komutu tekeri döndürmez; `ready`'de döner; sürerken kol oynamaya başlarsa rampayla durur; açılışta kol gevşekken sürmez. Kilidi kaldıran mutasyon C testinde yakalanır. Gateway testi bayrağın telemetriyle geldiğini denetler.
- **İtme çubuğu gizlendi:**
  - Sütunun çubuk kanalı, gözlerin arasında z320'ye kadar yükselen U kesitli bir kılıf oldu. Kılıf sol göze doğru açıktır; ön ve arka duvarları çubuğu örter.
  - Kılıfın tepesi, sol gözdeki krank göbeğinin en alçak noktasının (60°'de) 2,6 mm altında. Tilt taramasında açıklık 1,6 mm; gözün iç yüzü ile kılıf kenarı arasındadır.

Fiziksel testler NOT_RUN.

**DD85 — Kablo yolları (26.09.2026).** Tasarımın son açık işlerinden biri. Kolun kablo yolu eksikti: omuz milindeki Ø8 kablo deliği gövde içinden başlıyor ama kolun dışına açılmıyordu.

- **Kol:**
  - Beş servo kablosu kolun dış yüzü boyunca ilerler. Uzuvların çevresine kelepçe (plastik bağ) atılır; parkta bu yüz yukarı bakar, çamurluğa değmez.
  - Kablolar eğim eklemlerini 624/M4 tarafında, eksene yakın bir döngüyle, twist eklemini de eksene yakın bir döngüyle geçer. Gövdeye omuz ekseninden girerler.
  - Omuz deliği A'nın dış yüzüne kadar uzatıldı. Twist kapağı geri çekilip (x ≥ omuz + 5) deliği açık bıraktı; kapağın arka vidaları alt duvara taşındı.
- **Servo çıkışları:**
  - Twist servosunun kablosu, kapağın altındaki 2,5 mm boşluktan ve A'nın dış yüzündeki bir oluktan omuz deliğine iner.
  - Dirsek ve bilek MG996R'lerinin ceplerinde, kablonun çıktığı uçtan (milin uzağı) dış yüze açılan yarıklar var. Bilek dönüşü ve pençe MG90S'lerinde de aynısı.
- **Baş:** her gözün iç duvarında, aksa 11,7 mm uzaklıkta Ø5 kablo deliği var. Kablolar sütunun kablo kanalından iner, bloğun arka penceresinden çıkar, pan tabanının arka yarığından geçip gövdeye girer (DD82/DD83).
- **Testler:**
  - omuz girişi açık ve kapak onu kapatmıyor; twist oluğu var;
  - dört servo yarığı ve iki göz deliği boş;
  - kapak vidaları yeni yerlerinde, çevrelerinde et var.
  - Kesişim ve açıklıklar değişmedi.
- **Açık:** kabloların kendisi, döngüleri ve kelepçeler çizilmedi. Omuz ekseninde 225°'lik dönüş için gövde içinde bir servis halkası bırakılır; ölçü montajda alınır.

Fiziksel testler NOT_RUN.

**DD86 — ESP32-S3 kart katmanı, L4a (26.09.2026).** Kullanıcı: "daha almadım 3d printerı sen devam et yapmaya". Donanım ve ESP-IDF araç zinciri yok. Resmi Docker imajı 3–5 GB, diskte 12 GB boş var; kullanıcıya sorulmadan indirilmedi. Bu yüzden iş ikiye bölündü ([plan](superpowers/plans/2026-09-26-l4a-esp32-board-layer.md)).

- **Host testli hesap (`firmware/lite/board_math.c`):**
  - PCA9685: ön bölücü = round(osc/(4096·50)) − 1 = 121; 1500 µs → 307 sayım.
  - İç osilatör birkaç yüzde hızlı çalışabilir: %4 hızlı bir çip kalibrasyonsuz orta darbeyi ~60 µs (~5°) kısaltır. Ölçülen frekans NVS'e (`pca_osc_hz`) yazılır, sayım ona göre hesaplanır.
  - 0 µs = tam kapalı biti; sıfır genişlikli darbe değil.
  - TB6612: ileri = IN1'de PWM, geri = IN2'de PWM, 0 = serbest (coast); motor başına kutup (−1) ters bağlanmış motoru yazılımda çevirir.
  - Batarya: pin mV × 122/22 × kalibrasyon (‰).
- **Pin başlığı:** `pins.h`, `config/esp32_pinmap.json`'dan üretilir; test elle yazılmış bir sapmayı yakalar.
- **ESP-IDF uygulaması (`firmware/lite/esp32/main/app_main.c`):** güvenlik kararlarının hepsi `lite_core.c`'de kalır; bu dosya yalnız bitleri taşır.
  - E-stop kesmesi `ACT_EN`'i hemen Low, /OE'yi High yapar.
  - Çıkış sırası: kapatırken önce izinler, açarken önce çıkışlar; /OE yalnız `ACT_EN` High ve E-stop bırakılmışken Low.
  - Telemetri yalnız imzası doğrulanmış gönderene gider. Görev watchdog'u 1 s'de paniğe düşürür.
  - VL53L0X sürücüsü yazılmadı: menzil 0 okunur, çekirdek ileriyi engeller (güvenli yön).
- **Durum:** kullanıcı indirmeyi onayladı; `espressif/idf:v5.3.2` imajıyla ilk denemede derlendi. Paylaşılan çekirdek de Xtensa GCC 13.2 altında `-Wall -Wextra -Werror` ile uyarısız. Uygulama 0xCCA40 bayt (1 MB bölümün %20'si boş). Donanımda çalışmadı. L4b: VL53L0X, bring-up, TL1–TL5.

Fiziksel testler NOT_RUN.

**DD87 — Ön VL53L0X sürücüsü, L4b'nin donanımsız kısmı (26.09.2026).** Kullanıcı yer açtı: "yer açtım devam et". İleri hareket bu iki sensör olmadan hep engelli kaldığı için sıradaki iş buydu.

- **Yapı:** `firmware/lite/vl53l0x.{h,c}` ESP-IDF'siz, düz C'dir; I²C, XSHUT ve bekleme dışarıdan verilir. Host testi iki sensörlü bir kayıt modeline karşı çalışır; ESP-IDF yapıştırıcısı `app_main.c`'de ~30 satırdır.
- **Adresleme (tek XSHUT, yalnız solda):**
  - Sol resette tutulur, sağdaki 0x29'dan 0x30'a taşınır, sol bırakılır ve 0x29'da uyanır.
  - Test modeli aynı adrese iki sensör cevap verirse durur; sıra bozulursa test kırılır.
  - ESP32 watchdog'la yeniden başlarsa sağdaki zaten 0x30'dadır. Taşıma NACK alır, kurulum yine iki sensörle biter.
- **Kurulum:** ST API sırası (DataInit, StaticInit ve DefaultTuningSettings, VHV/faz kalibrasyonu), sonra arka arkaya ölçüm. Beklemeler 500 ms ile sınırlı; hazır olmayan sensör açılışı kilitlemez, "yok" sayılır.
- **Okuma:** her 20 ms adımda engellemeden okunur, yeni örnek yoksa son değer kalır. 100 ms yeni örnek gelmezse, sensör hiç kurulamadıysa ya da cevap vermiyorsa değer 0 olur; çekirdek bunu "ileri engelli" sayar. Kayıp sensör boş yol gibi okunmaz.
- **Bilinçli kısaltmalar (ponytail):**
  - ST, MSRC/TCC kapatılınca son menzil süresini 33 ms bütçeye geri uzatır; bu hesap atlandı. Örnek biraz daha kısa ve biraz daha az hassas olur. TL5'te titreşim görülürse eklenir.
  - Beslemesi düşüp yeniden açılan sensör bir sonraki açılışa kadar bayat kalır; ileri engelli, yani güvenli yöndedir.
- **Test:** XSHUT sırası, SPAD haritası, ayar tablosunun iki sayfası, ölçüm ve kesme temizliği, bayat/kayıp/yabancı sensör, sıcak başlatma, sınırlı bekleme. Dört mutasyonun dördü de yakalandı: sıra, bayatlık, SPAD maskesi, bekleme sonucu.
- **Derleme:** ESP-IDF 5.3.2, `-Wall -Wextra -Werror` altında uyarısız; uygulama 0xCD490 bayt.
- **Açık:** kayıt sırası gerçek sensörde denenmedi. İki sensörün adreslemesi ve menzili bring-up'ta (TL5) doğrulanır.

Fiziksel testler NOT_RUN.

**DD88 — Göz firmware'i, ESP32-CAM (26.09.2026).** Kullanıcı: "devam et". Repoda göz yazılımı yoktu; ağ geçidi her göz için bir `/capture` adresi bekliyor (`UGV_EYE_URLS`, 2 s zaman aşımı).

- **Seçim:** Hazır CameraWebServer örneği yerine kendi küçük ESP-IDF projemiz (`firmware/lite/eye/`, ~120 satır). Böylece ayrı bir Arduino ortamı gerekmez, iki gözün ayarı koddan ve NVS'ten kilitlenir, derleme S3 ile aynı Docker imajıyla yapılır.
- **Davranış:**
  - AI-Thinker pinleri, OV2640, VGA JPEG kalite 12.
  - PSRAM'de iki tampon ve "en yeni kare" kipi: istek sıradaki eski kareyi değil en yenisini alır.
  - Wi-Fi güç tasarrufu kapalı, adres yönlendiricideki DHCP kirasından gelir.
  - Beyaz flaş LED'i (GPIO4) kapalı tutulur.
- **Stereo:** pozlama, kazanç ve beyaz dengesi kalibrasyona kadar otomatiktir; kalibrasyon iki göze aynı sabit `aec`/`agc`/`wb_mode` değerlerini yazar.
- **Güvenlik:** uç kimlik doğrulamasızdır (lite_software_A3.md). Gözler robotun kendi SSID'sinde tutulur. Görüntü yalnız okunur; göz hiçbir hareket komutu almaz.
- **Derleme:**
  - `espressif/esp32-camera` 2.1.8'e sabitlendi. Bileşen, konteyner içindeki bir kopyada indirilir; repoya indirme yazılmaz.
  - Uygulama 0xED7E0 bayt. Varsayılan 1 MB bölümün %93'ünü dolduruyordu; 4 MB flash'ta büyük tek-uygulama bölümüne (1,5 MB, %37 boş) geçildi.
  - `-Wall -Wextra -Werror` altında uyarısız.
- **Açık:** donanımda çalışmadı. Kamera açılışı, beyaz dengesi ön ayarlarının OV2640'taki etkisi, görüntü gecikmesi ve 5 V rayındaki akım darbeleri bring-up'ta ölçülür.

Fiziksel testler NOT_RUN.

**DD89 — Kurulum ayarı yardımcısı (26.09.2026).** Kullanıcı: "devam et". İki firmware ayarlarını NVS'ten okuyor (bağlantı anahtarı, Wi-Fi, kalibrasyonlar); bunları kurulum günü elle yazmak hem hataya açık hem sırrı dağıtma riski taşıyordu.

- **Araç:** `tools/make_nvs.py s3|eye` CSV'yi git dışındaki `~/.config/ugv/link.env` ve `wifi.env`'den üretir. Çıktı `~/.config/ugv/nvs/`'e gider: klasör 700, dosya 600. Repoya hiçbir şey yazmaz.
- **Denetim:** anahtar 64 hex (32 bayt), SSID ≤32 bayt, WPA2 parolası 8–63 ASCII (açık ağ için boş), dört motor kutbu ±1, `vbat_cal` 800–1200 ‰, `pca_osc_hz` 23–27 MHz, port, `aec` ≤1200, `agc` ≤30, `wb_mode` ≤4. Hatalı değer yüklemeden önce reddedilir.
- **Tutarlılık testi:** `tests/check_make_nvs.py` firmware kaynaklarındaki `nvs_get_*` çağrılarını okur. CSV'nin tam o anahtarları, o türlerle taşıdığını denetler; bir taraf değişip öbürü değişmezse test kırılır.
- **Gerçek biçim:** uydurma anahtarlı CSV'ler Espressif'in `nvs_partition_gen.py` üreticisinden geçirilip `nvs_tool.py` ile geri okundu; 32 baytlık anahtar, dizeler, u16/u32 ve kutup blob'u (`01 ff 01 ff`) doğru çıktı.
- **Yükleme:** Docker macOS'ta USB seri porta erişemediği için yükleme `esptool` ile Mac'ten yapılır; derleme çıktısı konteynerden `~/ugv-build`'e alınır. Bu adım donanım gelmeden denenemez.

Fiziksel testler NOT_RUN.

**DD90 — Bağımsız M3 incelemesinin açık bulguları N3–N8 (26.09.2026).** Kullanıcı [inceleme raporunu](review_m3_2026-09-25.md) yapıştırdı. Her düzeltmede önce hatayı gösteren test yazıldı, sonra kök neden düzeltildi, ardından mutasyonla sınandı. N1, N2, DD80 ve DD84 kapanışları korundu. 9,2 V tavanına dokunulmadı.

- **N3 — telemetri sırası ve hold (kapalı):**
  - İki kök neden vardı. 0,2 s penceresindeki her imzalı örnek, geliş sırasıyla eskisini eziyordu. "Hedefe varıldı" ve "hold bitti" kararları da son komuttan önce alınmış örnekle veriliyordu.
  - Düzeltme 1: `vehicle.py` her çerçeve kimliği için yalnız daha yeni bir lease'e bağlı örneği kabul eder; geç, sırası bozuk ya da yinelenen örnek atılır.
  - Düzeltme 2: çekirdek 0x1A2'nin boş baytına aldığı son 0x122 sırasının düşük baytını yazar. 0x122 zaten yalnız ileri sırayla alınır, yani eski bir komut sonradan uygulanamaz. Host hedefi ve hold'u yalnız bu hedef için gönderdiği bir komutu yankılayan örnekle bitirir. Yanıt gelene kadar hedef düğümde tutar.
  - Testler:
    - raporun senaryosu (≈150 ms geç "stow" örneği + `arm stow`, ayrıca `hold`);
    - komuttan önce alınmış örnek;
    - geç gelen odometrinin mesafeyi geri sarması;
    - 16 bit sıra sarımı;
    - C'de yankı baytı ve reddedilen komutun yankıyı değiştirmemesi.
  - Mutasyonlar: sıra denetimini kaldırmak odometri testinde, yankı denetimini kaldırmak "komuttan önceki örnek" testinde yakalanır.
- **N4 — duruşa göre ağırlık merkezi (kapalı; tasarım kararı):**
  - `body_mass_screen.py` her kol duruşu ve yük yerleşimi için aracın ağırlık merkezini ve statik devrilme açılarını hesaplar. Kol parçaları CAD ağırlık merkezleriyle ve görüntüleyicinin eklem zinciriyle duruşa taşınır. Aynı 0,5 kg yük kapakta, 0,15 kg'ı kargo kutusunda ya da pençede olacak şekilde yeniden dağıtılır; iki kez sayılmaz.
  - Bütçedeki kol noktası CAD'in stow ağırlık merkezi oldu: x 27 → 38, yeni y −55, z 161 → 163. Eski bütçe y'yi hiç içermiyordu.
  - Sonuç (kapakta 0,5 kg):
    - stow x 9,9 / y −7,9 / z 131,1 mm, öne devrilme 36°;
    - lift ve up z 139,9 mm, ready x 25,7 mm; sınır dışı.
    - Pençede 150 g ile ready'de öne devrilme 26,9°; ≥30° koşulu bozuluyor.
  - Karar: sınırlar yükseltilmedi, sürüş duruşları **yalnız stow** oldu (config → `arm_graph.h` maskesi 0x01, yürütücü aynı listeyi okur). Yürütücü sürüş için pençenin açık olmasını da ister; nesne kargo kutusunda taşınır. Pençede 150 g ile stow'da y −11,9 mm, 10 mm hedefini aşar ama devrilme açıları ≥37,8° kalır; bu yüzden kural çekirdekte değil yürütücüde.
  - AI istemi ve araç açıklamaları güncellendi. İşlev kaybolmaz, sıra değişir: al → depola → pençeyi aç → stow → sür.
  - `check_body_mass.py` her sürüş duruşu ve izinli yük için x/y/z sınırlarını ve ≥30° statik devrilmeyi sınar. Eski duruşların aynı testi bozduğunu da gösterir.
- **N5 — TL4 servo kabulü (kapalı):**
  - Kabul değerleri config'e taşındı: `servo_supply_min_v` 4,8 V (üç veri sayfasının alt sınırı; tork hesabı bunu varsayar), `servo_case_max_c` 55 °C (MG996R çalışma aralığının üst ucu, kasada, motor yanında).
  - TL4 gerilimi servo konektöründe, hareket ve tutma boyunca ölçer. Gerilim düşükse kabul gevşetilmez; buck çıkışı ayarlanır ya da kablo değişir.
  - "ESP32 resetlenmez" garantisi hedefe çevrildi ve TL4'e yük adımında mantık rayı ölçümü eklendi.
  - `check_design.py` TL4 metnini config'e bağlar. Mini560 kapasitesi, ortak besleme empedansı, E-stop'un DC kesme gücü ve sigorta–kablo koordinasyonu ölçülmüş gibi gösterilmedi; bunlar hâlâ açık.
- **N6 — görüntüleyici rotası (kapalı):**
  - Kenar ortasında basılan düğme artık o kenarı bitirir ya da aynı kenardan geri döner; hangisi hedefe daha kısa yoldan ulaştırıyorsa. Başka dala kestirme yapmaz.
  - Serbest kaydırıcılardan sonra önce parka anında geçilir, sonra grafik izlenir.
  - Rota mantığı şablonda saf bir blok; `tests/viewer_route.test.mjs` onu node'da çalıştırır. Eski davranışa dönen mutasyon yakalanır. Tarayıcıda reach_low ortasında reach_center denendi; hata yok, kol grafik üzerinden vardı.
- **N7 — güncel sayılar (kapalı):**
  - README ve elektronik belgesi: 13.478 TL, 22 TL pay. M3 ekleri dökümüne DD81–DD83 kalemleri eklendi (+3.491 TL). TL4 açıklığı CAD'den 5,65 mm.
  - `check_lite_bom.py` ve `check_design.py` bu sayıları kaynaklarına bağlar.
  - 13.500 TL tavanını kullanıcı 26.09.2026'da onayladı ("kararını onaylıyorum"). Rapor bunu karar bekliyor sayıyor; onay geçerli sayıldı, 22 TL payın çok küçük olduğu açıkça yazıldı.
- **N8 — teslim edilen STL (kapalı):**
  - `check_print_plan.py` artık STL'nin içeriğini okur: ikili ya da ASCII üçgenler, tabla konumu, sınır kutusu (≤0,1 mm) ve hacim (≤%0,5). Bunlar yönlendirilmiş katıyla karşılaştırılır. Tarih denetimi kaldırıldı.
  - Boş (`solid EMPTY`), başka parçanın ve 90° döndürülmüş STL mutasyonları yakalanır.
- **Nitelendirme (açık, test bekliyor):**
  - 1° örnekleme ve ±1° uç köşe denemeleri sürekli yol ve tolerans kanıtı değildir; kablo, servo boşluğu ve baskı toleransı dahil değildir.
  - Omuzdaki 225° servis halkası ve göz kapağının 0,15 mm boşlukla tutması TL4, TL6 ve baskı kuponuna kabul kriteri olarak bağlandı.
  - PI'nin yük kalkınca aşımına TL2'de sınır kondu: tepe hız ≤200 mm/s, 1 s'de ±%10'a oturma. Model 174 mm/s veriyor; fiziksel ayar NOT_RUN.
  - Kütle modelindeki 1,2 mm kabuk ve %20 dolgu, planlanan 4–6 duvar ve %25–100 dolgunun yerine geçmez. Dilimleyici çıktısı ya da tartım gelince ağırlık merkezi, tork ve filament bütçesi yeniden hesaplanır.

Fiziksel testler NOT_RUN.

**DD91 — DD86–DD89 firmware'inin öz incelemesi (26.09.2026).** Kullanıcı: "devam et". Bağımsız inceleme DD86–DD88 sürücülerini satır satır okumadığını yazmıştı. Donanım gelmeden bulunabilecek hatalar için `app_main.c`, `vl53l0x.c`, `eye_main.c`, `make_nvs.py` ve N3 değişikliği yeniden okundu.

- **E-stop yarışı (düzeltildi):**
  - `apply()` E-stop hattını okuyup sonra ACT_EN'i High yapıyordu. Kesme bu iki adımın arasına düşerse ACT_EN, sürücüleri bir sonraki 20 ms adıma kadar yeniden açıyordu. Birincil kesme donanımdaki NC kontak olduğundan ikincil bir yoldu, yine de açıktı.
  - Açma sırası `board_math.c`'de saf C oldu (`ugv_enable_actuators`): basılıyken ya da bekleyen kenar varken hiçbir şey açılmaz. Yazmalardan sonra yeniden okunur; kenar araya düştüyse ters sırayla geri alınır. /OE yalnız ACT_EN High iken Low olur.
  - Test, kesmeyi tam kontrol ile yazma arasına koyar. Yeniden kontrolü olmayan sürüm bu satırda kırıldı.
- **PCA9685 yazma hatası (düzeltildi):** başarısız bir I²C yazmasından sonra da kanal "yazıldı" sayılıyor, komut değişene kadar eski darbe kalıyordu. Artık yalnız başarılı yazma kaydedilir; hata bir sonraki adımda yeniden denenir.
- **Kontrol edilip doğru bulunanlar:**
  - enkoder sayımı: PCNT A kanalı iki kenar = 11 × 2 × 78 = 1716, çekirdekle aynı;
  - MCPWM %100 ve %0 davranışı, 20 kHz;
  - ToF yoklamasının adım maliyeti;
  - telemetri yalnız doğrulanmış gönderene gider; Wi-Fi yeniden bağlanır;
  - göz firmware'inin en yeni kare kipi;
  - NVS aracının izinleri ve denetimleri;
  - N3'ün MCU reseti ve kilitsiz durumdaki davranışı.
- **Açık:**
  - ESP32 watchdog'la yeniden başlarsa sağ ToF ölçüm yaparken yeniden kurulur. Model testinde çalışıyor, gerçek sensörde TL5'te denenir.
  - Takılı kalan bir I²C hattı için veri yolu sıfırlaması yok; adım uzar, ToF bayatlar ve ileri engellenir, yani güvenli yöndedir.
  - İkisi de bring-up'ta ölçülür.
- **Derleme:** ESP-IDF 5.3.2, `-Werror` altında uyarısız, 0xCD510 bayt.

Fiziksel testler NOT_RUN.

**DD92 — Tam incelemenin yazılım ve belge bulguları A01–A08 (29.09.2026).** Kullanıcı Codex'in [tam inceleme raporunu](review_full_2026-09-29.md) iletti. Her bulgu önce Codex'in kendi betikleriyle yeniden üretildi (hepsi doğrulandı), sonra kök nedeni düzeltildi ve karşı örnek kalıcı teste taşındı. Kapanış ayrıntısı: [kapanış kaydı](review_full_closure_2026-09-29.md).

- **A01 — anahtarsız hareket:** çekirdek anahtar tam 32 bayt değilse (boş, kısa, uzun) hiçbir datagramı kabul etmez ve telemetri göndermez. Önceden NVS'de Wi-Fi olup `link_key` olmayınca boş HMAC anahtarıyla ARM/DRIVE kabul ediliyordu.
- **A02 — geçersiz ToF:** sürücü 0x14 durum baytını okur. Yalnız durum 11 (geçerli) mesafedir; sinyal/faz hatası + menzil dışı kodu (≥8190) "hedef yok" sayılır, gerisi 0 = ileri engelli. Geçersiz örnek eski geçerli ölçümü canlı tutmaz. Açık alanda gerçek sensörün hangi durumu verdiği TL5'te bakılır; beklenmeyen durum yalnız ileriyi kapatır.
- **A03 — panel soketi:** `/ai` yalnız bu sunucunun kendi sayfasını kabul eder (Host ve Origin bu localhost portu; yabancı sayfa ve DNS rebinding 403). Aynı anda tek bağlantı denetimdedir, ikincisi 1008 ile kapanır, yanıtlar yalnız sahibine gider, sahip kopunca izin düşer. Panel 1 s'de yeniden bağlanır.
- **A04 — pençe:** pençe durumu istekten değil 0x1A2 telemetrisinden (bit2 kapalı komutlu, bit3 hedefinde) okunur; çekirdek sürüş kilidine pençeyi ekler. Yürütücü pençe komutunu telemetri doğrulayana dek bekler, gelmezse isteği geri alır (bağlantı düzelince geç hareket olmaz). DD93 pençe kurallarını genişletti.
- **A05/A06 — kol onayı:** yankı 12 bite genişledi (bayt 7 + bayrak bit4–7) ve yalnız kolun gerçekten aldığı 0x122 ile ilerler; reddedilen komut sırasını yine de yakar (tekrar koruması korunur). MacBook bir örnek kendi komutunu yanıtlayınca bunu kilitler; 255 gönderimde hiçbiri alınmazsa hedef/hold başarı değil `arm_fault` ile biter. 16 bit sarım uçtan uca sınandı. N3 kısa gecikme düzeltmesi korundu.
- **A07 — reset sonrası bağ:** `request_arm()` her seferinde yeni rastgele oturum açar (servo sıraları için düşük 16 biti de farklı), lease sayacı sıfırdan başlar ve el sıkışma ancak yeni oturumda telemetri doğrulanınca sayılır. ESP32 resetinden sonra 65536 lease öncesi ve sonrası bağlantı geri geliyor; eski oturum telemetrisi kabul edilmiyor. DD91'deki "N3'ün MCU reseti doğru" notu 65536 sonrasını kapsamıyordu.
- **A08 — belgeler:** sigorta 15 A (M3), baş açıklığı 1,6 mm, kol açıklığı artık 1° adımla ölçülür (park → kaldır 4,75 mm; 5,65 mm 5° örneklemenin sonucuydu), N4 CG z131,1 mm / 36,1°, panel README'si ve üç buck. Codex'in raporu değiştirilmedi.
- **Doğrulama:** 34/34 masaüstü kontrolü ve iki ESP-IDF derlemesi geçti; Codex betikleri artık güvenli sonuç veriyor. Fiziksel testler NOT_RUN.

**DD93 — Mekanik kapılar M01–M03 ve park toleransı (29.09.2026).** Kullanıcı pençe için önce kayar çeneyi seçti. 50 mm strok için kremayer, kapalıyken gövde duvarına ya da araç dışına taşıyordu; kullanıcı bunun üzerine **ikiz dişli pençeyi** seçti.

- **M01 — ikiz dişli pençe:**
  - Çene A (055) MG90S kol kornasında, çene B (062) avucun direğinde M3 × 16 pim vidasında döner. İki 16T modül 0,625 dişli (eksenler 10 mm), TPU pedler (063/064). Eksen aralığı parkta 308 mm genişlik zarfıyla (|y| ≤ 154) ve yan duvar payıyla sınırlı; modül 1 sığmadı.
  - 60° açıkken uç açıklığı 53,5 mm; ped merkezinde sıkma ≈4,1 N (stall), %50'de 150 g için ≈2,2 kat sürtünme payı; dişte Lewis ≈15 MPa. Hesap [Lite mekanik](lite_mechanical_A3.md)'te.
  - Park duruşunda iç çene açılınca yan duvara çarpar. Bu yüzden: pençe yalnız CAD'in her açıda taradığı açık duruşlarda açılır (`gripper.open_poses`: hazır, öne, yere, öne-orta, depola); açıkken kol yalnız iki açık duruş arasındaki kenarlarda yürür (açık çenelerle 1° tarandı); kavrama duruşunda (öne, yere, öne-orta) kapanış "dolu" sayılır ve araç parkta ancak kapalı + o kapanıştan sonra tam açılmış pençeyle sürer (0x1A0 bit4 "boş"). Çekirdek (`arm_graph.h` maskeleri config'ten üretilir), yürütücü, simülatör ve AI talimatı aynı kuralı uygular. Pençe parkta kapalıdır (servo park 0°).
  - Kullanıcının kayar çene için onayladığı "parkta kapalı sür, depola'da bırak" akışı bu tasarımda da geçerli.
- **M02 — ek kirişi:** her kiriş ek yerinin iki yanında 2'şer M3 × 10 ile plaka altından ısıl insertlerine vidalanır (config `rail_bolt_x_mm`); yapıştırma seçeneği kalktı. Ek yeri eğilmesi 3g payıyla 3,5 N·m, cıvata kesmesi ≈90 N, PETG ezilmesi ≈6 MPa.
- **M03 — sol omuz:** yarıklı bilezik mile M3 ile sıkılıp milla döner; bilezikle duvar göbeğinin iç yüzü arasındaki TPU pul sürtünme çiftidir. 0,24 N·m (1,5 kat pay) için ≈32 N eksenel ön yük; montajda bilezik dışa bastırılıp sıkılır. Sol kolun diğer eklemleri cıvatalarıyla sabittir, sol pençe kapalı yapıştırılır.
- **Park toleransı:** avucun iç (−z) yüzü −12'den −9 mm'ye kırpıldı. Beş eklem birlikte ±1° saparken (32 köşe) yan duvara en az 4,1 mm (önce 2,80 mm; sınır 3 mm). CAD bu taramayı manifeste yazar, test ≥3 mm ister; TL4 her eklemi ±1° kalibre eder.
- **Sonuç:** 103 STEP parça (7 yeni), 74 baskı parçası, 42 insert, kollar 632 g baskı (tahsis 720 g), filament PETG 2.259 g / TPU 283 g, N4 CG z131,1 mm. Dişli çifti önce deneme baskısıyla sınanır. Fiziksel testler NOT_RUN.

**DD94 — DD92/DD93 doğrulamasının açık bulguları R01–R06 ve G01 (30.09–01.10.2026).** Kullanıcı Codex'in [doğrulama raporunu](review_dd92_dd93_2026-09-30.md) iletti. Her karşı örnek önce raporun betikleriyle yeniden üretildi (hepsi doğrulandı), sonra düzeltildi ve kalıcı teste taşındı. Kapanış: [kapanış kaydı](review_dd92_dd93_closure_2026-10-01.md). Rapor ve kanıt betikleri değiştirilmedi.

- **R01 — "hedef yok" açık yol değil:** ToF sürücüsü ham durum 11'i mesafe olarak verir (≤8189). Sinyal/faz hatası + menzil dışı kodu artık `UGV_TOF_NO_TARGET` (0xFFFF): açık yol değil, "kör". Çekirdek kör iken ileriyi 100 mm/s ile sınırlar (0x1A0 bit5); yürütücü kör 0,3 m'den sonra durup yeniden bakmayı ister; geri gitme serbest, geçersiz (0) okuma hâlâ ileriyi hemen keser. Açık odada hiç ileri gidememek yerine bu sınırlı açık alan politikası seçildi. Koyu ya da cam hedefin de böyle okunabileceği bilinçli risk; TL5'te ölçülür.
- **R02 — pençe durumu uzlaştırması:** açılışta ve watchdog resetinden sonra pençe "boş" sayılmaz. Güç, kol parkta ve pençe kapalıyken düşmediyse kol ve pençe "bilinmiyor" kilitlenir; ikisine de darbe gitmez (eski açık PWM parkta geri gelmez). 0x123 park onayı artık iki beyandır: kol parkta **ve** pençe kapalı ve boş (bayt 1 = 1). Panel düğmesi ve `claw_closed_empty` alanı bunu açıkça söyler. Onaydan sonra pençe hedefi ve konumu kapalı, "boş" işareti kalkar, MacBook'un pençe isteği de "kapat"a döner. Yalnız depola'daki kapanış "boş" sayılır (`gripper.release_poses`); hazır dahil başka her kapanış "dolu".
- **R03 — onay alias'ı:** MacBook çekirdeğin aldığı son kol komutunu (`ack`) izler ve bir oturumda ondan en fazla 255 komut ileri gider; hedefler arasında da. 12 bitlik yankı bu yüzden tek bir komutu gösterir. Sınır aşılınca hata oturum boyunca kilitlenir, kol komutu gitmez; yeni görev yeni oturum açar. 17 art arda kayıp hedefte sahte başarı yok.
- **R04 — pasif sol kol:** servo, korna ve rulmanların yerine basılı taklitler (066–069, 074, halka 075, burçlar 076/077; kapak 058 ve adaptör 059 sol kol için de): her eklem sağ kolun kendi arayüzleriyle bağlı, park açılarında sabit. Sol kol ≈219 g, omuz bileziği için ön yük ≈49 N (0,37 N·m, 1,5 kat).
- **R05 — çene B pimi:** Ø5/Ø3,2 × 7,5 mm naylon burç, M3 × 16 + yaylı rondela ile direğe sıkılır; çene burcun üstünde döner (0,5 mm eksenel boşluk, 0,4 N·m). Kupon testi TL5'te.
- **R06 — kavrama noktası:** pedlerin buluştuğu yüzün ortası (bilek ekseninden 101 mm, kol düzleminden 16,5 mm içte, 5 mm yukarıda); manifest, test ve kütle modeli bunu kullanır. Kargodaki nesne kutunun tabanında sayılır. Korna kolu 12 mm'de kesilir (parmak köküne değmez).
- **G01 — şasi eki:** serbest cisim hesabı eksenel çekme ve prying'i de kapsar: kiriş 3,9 MPa, cıvata kesmesi 88 N, uzak cıvatada 47 N çekme, plaka yerel eğilmesi 5,6 MPa, insert için ≈6 kat (katmana dik 300 N kabulüyle). Deney açık.
- **Yan etkiler:** 115 STEP, 84 baskı parçası, 50 insert; kollar 708 g (tahsis 720 g, pay 12 g); PETG 2.335 g (%25 payla 2,92 kg, üç makaraya sınırda); kol bütçe noktası CAD merkezine (x33, y−33, z163) taşındı; yüklü CG z131,1 mm, öne 36,2°. Sol kol taklitleri kolları dengelediği için parkta pençede tutulan nesne artık y sınırının içinde kalıyor; "boş pençeyle sür" kuralı yine de geçerli (pençe zarfı, nesne kutuda).
- **Doğrulama:** 34/34 masaüstü kontrolü, iki ESP-IDF derlemesi. Fiziksel testler NOT_RUN.

**DD95 — DD94 bağımsız kapanış incelemesinin bulguları (01.10.2026).** Kullanıcı Codex'in [DD94 incelemesini](review_dd94_2026-10-01.md) iletti. Codex çalışma ağacını dışarıdan temizlenmiş (DD91) bulmuş ve kurtarılan ara sürümü incelemişti: bir Git Stop kancası (`auto-checkpoint.sh`, `git stash push -u`) 01.10 00:47'de bütün işi stash'e almış, geri uygulamamıştı. Son DD94 sürümü o stash'ten (`stash@{0}`, yedek olarak duruyor) eksiksiz geri yüklendi; üç bulgu son sürümde de yeniden üretildi, sonra düzeltildi. Kapanış: [kapanış kaydı](review_dd94_closure_2026-10-01.md). Rapor ve kanıtları değiştirilmedi.

- **#2 — gevşek pençe başarı sayılmaz:** kol gevşekken (limp) çekirdek pençe komutunu almaz: pençeye darbe gitmediği için modelin hedefi de değişmez. Gevşeme "boş" işaretini siler, gevşekken tam açık model "boş" üretmez. 0x1A2'de gevşekken bit0, bit2 ve bit3 hep 0; MacBook gevşek pençeyi "unknown" okur, yürütücü pençe isteğini göndermeden reddeder ("limp", operatör park onayı gerekir). Park onayından sonra pençe normal çalışır.
- **#3 — yeniden kurma yarışı:** `LiteVehicle.pump()` telemetriyi `request_arm()` oturum sıfırlamasıyla aynı kilit altında doğrular ve kabul eder; soket okuması kilit dışında kalır. Eski oturumda doğrulanan örnek artık yeni oturumun durumuna ya da sıra kapısına yazılamaz. Ek (Codex notu, DD94'ten eski): `disarm()` ve `request_arm()` teker hedeflerini sıfırlar; yeniden kurma hiçbir zaman eski hareketi sürdürmez.
- **#1 — kavrama tablosu:** Lite mekanik duruş tablosu manifestin `grip_mm` değerleridir; `tests/check_cad.py` farkı ≤0,05 mm ile denetler. 96 mm kinematik nominal uzuv boyu, gerçek kavrama noktası bilek + 101 mm, düzlemden 16,5 mm içte ve 5 mm yukarıda.
- **R04 — pasif twist boşluğu:** twist taklidi (066) cebi kapak tarafı dahil her yanda 0,2 mm boşlukla doldurur (servo zarfı 0,5 mm ve kapağa 2,5 mm bırakıyordu: +0,9°/−2,9°). Kabul: ±1° (TL4 eklem bütçesi). CAD, taklidi iki yönde 1° döndürünce A'ya ya da kapağa çakıştığını (≈118 mm³) ve nominalde temassız olduğunu manifeste yazar; nominal boşluk ≈0,4°. Eksende sağ kolun servosu gibi tutulur (adaptör, halka, kapak).
- **R01 — kör modun görünürlüğü:** gateway ön ToF körleşince ve kör mod bitince panele birer durum mesajı gönderir. Politika değişmedi: 0,3 m bütçesi hareket çağrısı başınadır, toplam sınır değildir; her sonuç yeni kamera görüntüleriyle modele döner. Belgeler buna göre düzeltildi.
- **G01 ifadesi:** kuvvet çifti ve prying, momentin tamamını ayrı ayrı taşıyan iki idealize yük yoludur, toplanmaz; 300 N insert tutunması ölçülmemiş bir varsayımdır.
- **Yan etkiler:** kollar 710 g (tahsis 720 g, pay 10 g; ölçülmedi), sol kol ≈221 g (0,25 N·m ve 49 N ön yük aynı), PETG 2.337 g (%25 payla 2,92 kg), öne devrilme 36,1°. 115 STEP, 84 baskı parçası, 50 insert.
- **Doğrulama:** masaüstü kontrolleri ve iki ESP-IDF derlemesi son firmware'den sonra; ayrıntı ve kaynak SHA-256 değerleri kapanış kaydında. Fiziksel testler NOT_RUN.
