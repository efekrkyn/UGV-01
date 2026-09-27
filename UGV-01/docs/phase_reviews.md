# A0 teknik gözden geçirme kaydı

22.09.2026. PH0/PH1 yazılı ön tasarım tamamlandı; PH2 mekanik kavram üretildi ve aşağıdaki sınırlar ile koşullu tutuldu. PH3 fiziksel motor doğrulaması ve PH4 detay imalat tasarımı açık.

| Kontrol | Kanıt / sonuç | Durum |
|---|---|---|
| İlk16 çıktının kapsamı | README'de16 madde dosyalara eşlendi | DOKÜMAN TAMAM |
| Tahrik verileri | Üretici70:1 aday; stall/sürekli ayrımı;1,5/1,6 yük duyarlılığı | KOŞULLU; test yok |
| Sayısal araç | tests/check_design.py: birimler, enerji, yük ölçekleme, geçersiz çap | GEÇTİ |
| Geometri |31 ayrı STEP yeniden açıldı, geçerli ve pozitif hacimli | GEÇTİ |
| Kesişmeler | Modeldeki31 parçanın bütün çiftlerinde hacimsel boolean; izinsiz kesişme0 | GEÇTİ; yalnız modellenen kapsam |
| Baskı zarfı |13 panel/kapak/son duvar/tampon STL; her parça≤240mm tasarım sınırı | GEÇTİ; slicer/kupon yapılmadı |
| CAD–URDF | JSON manifest eşleşmesi, dört teker merkezi ve+Y aksları | GEÇTİ; dinamik simülasyon yok |
| Teknik tutarlılık | Akım1,3/2,5A; hardware2,7/3A; heartbeat50Hz/100ms; termal eşikler hizalandı | Ön masaüstü inceleme |
| İmalat | PN/proses/DFM tablosu,metal yük yolu,geçiş delikleri | PH4 tolerans/FEA/insert/yatak açık |
| Montaj | Batarya/kapak gerçek boşluk revizyonu; servis sırası yazıldı | 1:1 maket ve gerçek konektörler açık |
| Test edilebilirlik |20 prosedür, ölçüm noktaları, fault eşlemesi | Plan hazır; T01–T20 NOT_RUN |
| Servis | Ayrı kapaklar; batarya çıkarma; alt kart için compute rafı erişimi | Fiziksel gösterim yapılmadı |

## İncelemede düzeltildi

1. Motor mil uzunluğu22mm varsayımı16mm üretici verisine düzeltildi. Motor gövdesi70mm,82mm tahsis servis payıyla ayrıldı.
2. Batarya ikinci kutuyla çift sayılmadı; kasa dahil55mm. z83–138,kapak altı143;gövde üstü146mm. Başlangıç140mm hedeften6mm sapma DD21'de.
3. Motorlarla çarpışacak280mm rijitleştirici yerine motorlar arasında150×12×15mm iki eleman. Kısa elemanların tam plaka rijitliği çözülmüş sayılmadı.
4. Boş CG hesabı yeniden üretildi:6kg, x−8,18mm,z80,71mm.2kg yük CG190mm örneği toplam108,03mm; yanlış eski tahminler kaldırıldı.
5. CAN trafik tablosu tek dosyaya alındı;360frame/s ve160bit/frame ile%11,52,10fault/s dahil%11,84.
6. Motor termal ve blokaj eşikleri, donanım/yazılım akım limitleri ayrıldı; yaşlanmalı enerji hesabı yeni-hücre hesabından ayrı sunuldu.

## Açık ve sonraki fazı sınırlayan konular

Motor/rulman/kaplin eksenel paketi, gerçek motor taşıyıcıları, teker göbeği, ayrı teker yük yolu; batarya/compute raf mesnetleri; kule yükünün metale aktarımı; K1/DC röle ve20J klemp direnci hacmi/termal yolu; kablo/konektör alet ve çıkarma hacimleri;3mm plaka sehim/motor altı toleransı. Bunlar CAD manifestinde modellenmemiş olarak açıkça listelenir.

Pololu motor adayı15°/8kg için dar termal marj taşır:1,6 yük katsayısında1,3A sınırı aşılır. Başlangıç hedefi gözetimli,düz alan,yay dönüşü; rampada tether. E-stop coast davranışı park/fail-safe fren değildir.60dakika görev hedefi ağır106W profilde karşılanmaz.

Bu teslimin kapsamı dışında:KiCad şematik/layout/Gerber,çıplak kart üretimi,fiziksel prototip,derlenen STM32 firmware,ROS paketleri/Nav2 ve çalışan web panel. A0 dosyaları için üretim/sürüş onayı verilmedi.
# D1 ek inceleme — 22.09.2026

Tahrik modülü için8 özgün parça +5 tedarikçi zarfı,13 STEP ve2 STL üretildi; dört modüllü75 parçalı araç yerleşimi ayrıca STEP olarak kaydedildi. A0 korunmuştur. Hesap regresyonu, katı sürekliliği, baskı zarfı ve çakışma kontrolleri çalıştırılır; sonuçların kaynağı `cad/drivetrain/manifest.json` ve `packaging_report.json` dosyalarıdır.

PH3 motorun fiziksel ısıl/tork testi nedeniyle açık. PH4 kütle rezervi, rulman geçmeleri, segman seçimi, vida erişimi, yük altında deformasyon ve baskı kuponları nedeniyle açık. [D1 teknik inceleme ve test hedefleri](drivetrain_detail_D1.md). Çakışmasız nominal CAD üretim yeterliliği değildir.

23.09 ek kontrol: D1 için8 ve9 kg mekanik taramalar kayıtlıdır.9 kg koşulunda mil2,067, rulman2,795, taşıyıcı2,590 ön dayanım payı verir. Motor yüzü ve taban deliklerinin iki nominal DXF'i üretildi. Güncel kütle hesabı6,025 kg boş kütle ve rezervin kalmadığını gösterir. Geometri regresyonu tekrar geçti; fiziksel test durumu değişmedi.

## D2A ek inceleme — 23.09.2026

9 kg/3g ve μ=1,2 hassasiyet taraması açıldı. Ø8/608 hafifletme seçeneğinde mil1,89, rulman1,79 ön payıyla reddedildi. D1 C45 mil de1,73 payda kaldığı için Ø10 geometriyi koruyarak sertifikalı 42CrMo4+QT malzeme adayı seçildi; yatak6000. Yeni jant ve lastik STEP/STL'leri D1 katılarının alt kümesi olarak doğrulandı; bu yüzden yeni yerleşim çakışması oluşturmaz. Tahmini kütle5,933 kg, kalan rezerv67 g. PH4 kütle/DFM/yorulma/yatak geçmesi ve fiziksel test kapıları açık. [Karar ve hesap](drivetrain_trade_D2.md).

## Baskı beklerken PH5 masaüstü incelemesi — 23.09.2026

Baskı kuponu, gerçek montaj ve PH4 kabulü ertelenmiştir. Bağımsız elektrik işinde STM32G474VET6 pin atamaları KiCad 10 LQFP100 sembolüyle denetlendi; eski PB10/PB11 I²C2 hatası bulunup PA8/PA9 AF4'e taşındı. TI sürücü truth table incelemesinde PH/EN sıfır komutunun frenleme yaptığı bulundu; nötr/coast için PMODE=High ve dört motorun her birine iki PWM kanalı (TIM1+TIM8) ayrıldı. Negatif test eski I²C atamasını ve yinelenen/eksik kritik pinleri reddediyor. [Pin incelemesi](mcu_pinmap_review.md). Teknik kaynak uygunluğu **GEÇTİ**; PH5 **AÇIK**: CubeMX incelemesi, şematik, ERC, güç ve güvenlik bağlantıları henüz yok. Fiziksel testler NOT_RUN.

PWR↔MCU arayüzünde kesilebilir motor ve sürekli kontrol tek 4 pin J-PWR, revize 12 pin J-SIG ile aday net/pin sözleşmesine bağlandı. İlk ayrı motor/kontrol toprakları 15 A yükte hesaplanan yaklaşık3,7 A kontrol GND akımı nedeniyle reddedildi; J-PWR'de 2×AWG12 ortak dönüş, AWG12 motor ve AWG16 kontrol pozitif damarı seçildi. MCU güvenlik/geri bildirim PD8–PD15 atamalarıyla toplam **53 pin** KiCad sembol testinden geçti. 50 °C konnektör/tek GND arızası termali, başka paralel dönüşler, kütle ve power-off backfeed çözülmedi. Bu sonuç [net sözleşmesidir](pwr_mcu_interface.md), kart şematik/ERC tamamlanması değildir.

J-PWR kart tarafındaki KiCad ayak izi 2×2 pad merkezi ve pozitiflerin çapraz ayrımı bakımından otomatik denetlendi. Dişi housing cavity numaralarının kablo tarafından görünüşü ve krimp sırası henüz doğrulanmadı; PH5/6 açık kalır. [Tasarım yüzdesi ve kapsamı](design_progress.md).

PWR↔MCU P0 kablo KiCad şematiği revize edildi: 4 güç + 12 sinyal ağının her biri iki uçta aynı numaralı pine gidiyor; **yalnız kablo şematiği** ERC 0 ihlal. Kart düzeyindeki MCU/PWR şematik ve ERC hâlâ yok; harness ERC'si güvenlik devresine kanıt sayılmaz. [Çizim ve doğrulama](../electronics/interconnect/README.md).

## Bağımsız Tasarım İncelemesi (Design Review) — 23.09.2026

Gelen [incelemenin](design_review_findings.md) sekiz ana maddesi ve ayrıca TIM1/TIM8 senkron başlığı, [teknik karşılıkta](design_review_response.md) ayrı ayrı doğrulandı. J-PWR dik açılı 768250004 adayına, J-SIG 12 pine ve kablo I²C'si PCA9615 diferansiyel arayüzüne geçirildi; KiCad pasif kablo 16 net/0 ERC ihlali verdi. Tam montaj hacmi, iki kartın tampon/koruma şematiği, kütle ve fiziksel emniyet testleri **açık**; PH4/5/6/7 geçiş onayı yok.

## K1 ve elektronik kat düzeltmesi — 23.09.2026

İki kısmi [kart arayüz sayfası](../electronics/ugv_mcu_01/pwr_mcu_interface.kicad_sch) ve [PWR eşleniği](../electronics/ugv_pwr_01/pwr_mcu_interface.kicad_sch) 0 ERC hatası / sayfa başına 9 beklenen dış-net uyarısı verir. Ayrı [güçsüz alıcı sayfasında](../electronics/ugv_mcu_01/status_receiver.kicad_sch) altı kanal netlist ve 10 kΩ pasifler denetlenmiştir; altı haricî sürücü henüz bağlanmadığı için altı ERC `pin_not_driven` hatası **beklenen açık iş** olarak kalır. Bunlar tam kart şematiği değildir. [K1 aday taramasında](k1_relay_selection.md) ham 4S'in 12 V bobin üst sınırını aşacağı ve 5 V TE adayının DC rezistif derecesinin 16,8 V motor açma kanıtı olmadığı kaydedildi. 5 V aday bobini güç bütçesine 1 W olarak eklendi; [hesap raporu](calculation_results.md) yeniden üretildi. [Elektronik kesitte](electronics_packaging_gate.md) z=57–81 kutusunun PCB+bileşen hacmi olduğu düzeltildi; nominal dikey açıklık var, yatay kablo ve servis kapısı **açık/P0**. PH4/5/6/7 kapanmadı; baskı ve T01–T20 hâlâ NOT_RUN.

## Ön şarj, ARMING ve watchdog incelemesi — 23.09.2026

4700 µF bulk K2 sonrasında olduğu için K1 önündeki genel precharge ifadesi güvenli kapanış kanıtı değildi. [Yeni K1/K2 tanı ve ön şarj sırası](precharge_and_separator_diagnostics.md) ile K1 kapanmadan kaynaklı/kısa ayırıcı taraması, K2 çevresinde 470 Ω ön şarj, üç ray ölçümü ve iki seri test-enjeksiyon anahtarı taslak olarak tanımlandı. Direnç/kondansatör toleransında yaklaşık7,85 s şarj gereksinimi `ARMING` durumunu ve `PWR_ACT_EN` Low tutulmasını gerektiriyor. [Watchdog veri sayfası incelemesinde](watchdog_design.md) varsayılan 170–230 ms sürenin ≤100 ms hedefe uymadığı belirlendi; 100 pF CWD/PGOOD/ENOUT ön tasarımı açıldı. T01/T03/T13 prosedürlerine karşılık gelen arıza enjeksiyonları eklendi. Bunlar doküman/hesap incelemesidir: PWR gerçek şematik, K1/K2 MPN, analog hata bütçesi, watchdog osiloskop izi ve fiziksel tek-hata kanıtı **açık/P0**; PH6/11 serbest değil.

`firmware/stm32/safety_core.c` host C11 olarak uyarısız derlenip `tests/safety_core_test.c` senaryosunu geçti: sıralama, erken feedback/stale-high reddi, 15 s timeout, komut kaybı, 200 ms nötr dönüşü, E-stop sonrası 500 ms ve yeni reset/arm kenarı. Bu **PH8 kısmi kod kanıtıdır**; STM32 startup/HAL, gerçek GPIO/ADC/CAN, watchdog darbesi, HIL ve kart testleri yoktur. Güç devresi güvenli sayılmaz.

[K2 aday taramasında](k2_separator_selection.md) LM74900-Q1 ile iki 60 V/2,2 mΩ FET'in 15 A için 0,99 W soğuk maksimum kaybı hesaplandı. Denetleyicinin SLEEP modundaki iç 7 Ω bypass'ı güvenli OFF sayılmadı; EN'in donanımla Low yapılması ve SLEEP=EN kaydedildi. 50 °C/W katalog termali FET başına 1 in² bakıra bağlıdır; gerçek 120×80 mm PWR kart yerleşimi, ayrı şönt, gate/latch şematiği ve sıcaklık ölçümü olmadan K2 **seçilmiş ama onaylanmış parça değildir**. PH6/7/11 açık.

24.09.2026 PH6 ara gözden geçirme: [K2 referans KiCad şeması](../electronics/ugv_pwr_01/k2_reference.kicad_sch) üretici pinleri, iki FET, Kelvin şönt ve EN/SLEEP yolunu gösterir; [netlist testi](../tests/check_k2_reference.py) başarılı, ERC 0 hata/4 açıklanmış uyarı. [Hesapta](k2_reference_schematic.md) 31,6 kΩ OCP yaklaşık16,28–21,13 A, varsayılan SCP17,68–23 A aralığındadır. K1, ön şarj/bleed, güvenlik izin sürücüsü, shunt MPN ve PCB termali olmadan bu **tam kart ERC veya üretim onayı değildir**. PH6/7/11 hâlâ açık, T01/T13 NOT_RUN.

Host güvenlik çekirdeğinde arm öncesi eski test/ön şarj sonucu High ve ARMING'de komut öncesi K1/K2 feedback High durumu artık `FAULT` yapıyor; yeni negatif senaryolar önce başarısız, düzeltmeden sonra başarılı oldu. Girişlerin fiziksel doğruluğu, örnek yaşı ve fault pin polaritesi hâlâ gerçek donanım entegrasyonunda kanıtlanacak.

## A1 dış görünüş ve CAN sözleşmesi — 24.09.2026

[A1 montaj CAD](../cad/assembly/generated/UGV-01-A1-concept.step) 30 STEP katısından yeniden üretildi; kapak üst pahı, sarı paneller, ön RGB açıklığı ve tek kamera zarfı içerir. Çift göz/kule montajı kullanıcı kararıyla sonraki revizyona bırakıldı; mevcut düz flanş korunur. İlk kamera kutusu üretici ölçüsünden küçük olduğu için [Camera Module 3 Standard boyutuna](front_camera_A1.md) düzeltildi. `tests/check_cad.py` 30 katının geçerliliğini, ≤240 mm baskı tasarım zarfını, sıfır katı çakışmasını, ön açıklığı, kamera zarfını ve URDF konumlarını kontrol eder. Bu denetim optik görüşü, dış pod montajını, conta, gerçek kamera MPN'sini, vida yükünü veya fiziksel baskıyı doğrulamaz. Pod x payı yalnız 3,25 mm; A1, D2A tahrik yerleşim STEP'iyle henüz birleştirilmedi; PH4 açık.

0x110/0x100 CAN alanları tutarlı 8 bayt sözleşmesine indirildi; host C11 çözücüsünde tekrarlanan lease'in komut tazeliğini yenileyemediği senaryo geçti. STM32 FDCAN, ROS gateway, gerçek aktüatör donanım kapısı ve HIL yapılmadığından PH8 açık. T01–T20 fiziksel testler **NOT_RUN**.

## A1 gövde kütle taraması — 24.09.2026

[CAD kaynaklı hesap](body_mass_screen_A1.md) 13 ASA/TPU gövde katısında 738,6 g %100 dolu eşdeğer buldu; 700 g tahsis 38,6 g aşılıyor. `tests/check_body_mass.py` hacimleri ve aşımı denetledi. D2A'nın kâğıt 67,2 g kütle payı bu üst sınırla yaklaşık28,6 g olur. TPU MPN/slicer gerçek doluluk, bağlantılar, kamera podu ve parça tartımı açık; bu sonuç **PH4 kütle kabulü değildir**. T10/11/12 ve baskı kuponları **NOT_RUN**.

## PWR güç/güvenlik yolu KiCad sayfaları — 24.09.2026

PH6 plan Task 2/3 masaüstü kapsamı tamamlandı: [aktüatör yolu](../electronics/ugv_pwr_01/actuator_path.kicad_sch) (F1, K1 `MPN OPEN`/boş footprint, bobin sürücü ve 12 V clamp, BSS84 anahtarlı 470 Ω ön şarj, kilitli 150 Ω bleed, iki P-FET'li 1 kΩ test enjeksiyonu, ray bölücüler), [güvenlik kapısı](../electronics/ugv_pwr_01/safety_gate.kicad_sch) (enerji taşıyan NC-A/NC-B, TPS3431 100 pF, TPS3808 ray gözetimi, bırakma kenarlı reset latch'i, `SAFE_GATE` AND fan-out, NC-B beslemeli LVC1T45) ve [ARM I/O](../electronics/ugv_pwr_01/arming_io.kicad_sch) (TCA9534A, ADS1115, LM2903 K1/K2 geri bildirimi) çizildi. K2 ve arayüz sayfalarıyla [kısmi kök hiyerarşide](../electronics/ugv_pwr_01/ugv_pwr_01.kicad_sch) birleştirildi (Task 4 Step 1). [PDF](../electronics/ugv_pwr_01/ugv_pwr_01.pdf), [inceleme](pwr_safety_path.md), DD52–DD59.

| Kontrol | Sonuç | Durum |
|---|---|---|
| Sayfa netlist testleri | [aktüatör+ARM I/O](../tests/check_pwr_actuator_path.py), [güvenlik kapısı](../tests/check_pwr_safety_gate.py), K2 ve arayüz testleri pin düzeyinde | GEÇTİ |
| Birleşik ERC | 0 hata; 1 uyarı `MOTOR_FEED` (çizilmemiş STAR/INA228) | GEÇTİ; tam kart değil |
| Tek sayfa ERC | Yalnız başka sayfada sürülen raylar/etiketler; testlerde ağ adıyla kilitli | AÇIKLANDI |
| İzin mantığı | [Netlistten 4 096 senaryo](../tests/check_pwr_board.py); lojik High'a takılıyken tek açık NC enerji yolunu keser | GEÇTİ; Boole/bağlantı kanıtı |
| Mutasyon | 6 kasıtlı bozulma (RUN_REQ, NC-B beslemesi, latch /CLR, test FET yönü, WD EN→MCU, pad25→PGND) yakalandı | GEÇTİ |
| Analog pencere | Test 11,11–15,24 V / arıza 1,46–2,35 V; K1_FB eşiği 12,05/16,28 V; ön şarj ≤7,85 s | Kâğıt hesabı; ölçüm yok |
| K1 | MPN/footprint yok; 16,8 V DC motor kesme kanıtı yok; z payı en kötü −0,26 mm | AÇIK/P0 |
| Güç bileşenleri | F1 I²t, şönt MPN, ACT TVS/dump clamp, küçük FET veri sayfaları, PCB termali | AÇIK |
| Fiziksel | T01/T03/T13 | NOT_RUN |

İnceleme bulguları: KiCad 10 aynı ağdaki iki PWR_FLAG'i hata saydı; her ray tek sayfada işaretlendi. ERC, ADS1115 için yanlış VSSOP-10 footprint adını yakaladı; KiCad'in `TSSOP-10_3x3mm` DGS karşılığına düzeltildi. LM74900 `FLT`'in UVLO'da da düşmesi nedeniyle donanım latch girişi bağlanmadı. `SET1` Low gizli arızası ve MCU'nun hızlı resetinde TCA'nın eski çıkışı PH8 yazılım gereksinimlerine yazıldı. K2 kısa iken K1'in kapanmaması donanım kilidi değil, MCU sırası + tanı ölçümüdür.

**Kapı kararı:** PH6 şema incelemesi **ilerledi ama kapanmadı**; PH7 PCB, üretim dosyası ve sürüş **onaylanmadı**. Tam kart şematiği (INA228, regülatörler, dump clamp), K1 kanıtı ve fiziksel T01/T13 izleri gelmeden serbest bırakma yok.

## Genel tasarım denetimi — 24.09.2026

[Denetim raporu](design_review_2026-09-24.md): 7 hata düzeltildi (A0 arşiv bağlantıları, K2 belgesinde yanlış sürücü MPN'i, A2 spec kütle çift sayımı, güç bütçesi yuvarlama, eskimiş ön şarj ifadesi, eksik PWR kalıntı riskleri, güvenlik çekirdeğinde eksik 500 ms nötr şartı). 7 konum A2 revizyonuna devredildi. Hesaplar bayt bayt yeniden üretildi; 16 Python kontrolü (yeni bağlantı denetleyicisi dahil) ve 2 C testi geçti. A2 [tasarım spec'i](superpowers/specs/2026-09-24-a2-character-ai-design.md) kullanıcı tarafından onaylandı (DD61). Hiçbir faz kapısı bu denetimle kapanmadı; T01–T20 **NOT_RUN**, baskı ve sürüş onayı yok.

## A2 mekanik karakter — 24.09.2026

[Plan](superpowers/plans/2026-09-24-a2-mechanical.md) uygulandı. A1 kaydı [revisions/A1](revisions/A1/README.md) altına arşivlendi. `tests/check_cad.py` A2 için yeniden yazıldı; önce eski CAD ile başarısız oldu, sonra `build_concept.py` ile 46 geçerli STEP katısı, ≤240 mm baskı zarfı, sıfır izinsiz çakışma, 330×270 park zarfı, baş ≤300 mm (292,8), çalışma pozu (x263,4 / z4,7) ve 5° kol süpürmesi, ışık şeridi penceresi, göz kamera zarfları ve URDF eklemleri geçti. `tests/check_body_mass.py` baş (195,4 g) ve kol (186,9 g) taramasını tahsislere karşı denetler. `tests/check_design.py` yüklü CG için ≥2 mm pay ister; 1,75 kg yükte başarısız oldu, 1,5 kg ile geçti (DD62). [Önizleme](../cad/assembly/concept_preview.png) STEP'lerden yeniden çizildi. Gevşek kol denetimi (1° adım) kolun 185°'de orta kapağa oturduğunu gösterir. Doğrulanmayanlar: servo/rulman montajı, kablo yolu, omuz yük yolu, sürekli süpürme (yalnız 5° örnek), dinamik servo yükü, baskı, tartım ve optik görüş. T01–T20 **NOT_RUN**.

## A2 elektronik — 24.09.2026

[Plan](superpowers/plans/2026-09-24-a2-electronics.md) uygulandı. Test önce yazıldı ve başarısız oldu, sonra geçti: `tests/check_mcu_pinmap_integration.py` (58 atama, A2 sinyalleri zorunlu, PB8/BOOT0 ve paylaşılan servo zamanlayıcısı reddi) ve yeni `tests/check_mcu_servo_light.py` (netlist, şönt tam ölçeği, yalnız sayfa dışı sürücüler için ERC). `tools/pwr_sheet.py` kart parametresi aldı; PWR ve diğer şematik dosyaları SHA ile bayt bayt aynı yeniden üretildi. Güç bütçesi `tests/check_design.py` ile 60 dakika tipik hedefini (1,30 saat) doğrular. Gevşek kol CAD denetimi eklendi (185°, orta kapak). Doğrulanmayanlar: buck IC/manyetik, CubeMX AF ve DMA, servo 3,3 V sinyal eşiği, ToF/kamera bring-up, kart ERC, PCB. T01–T20 **NOT_RUN**.

## A2 AI ve yazılım — 24.09.2026

[Plan](superpowers/plans/2026-09-24-a2-ai-software.md) uygulandı; her görevde test önce yazıldı ve başarısız olduğu görüldü. Geçenler: `tests/check_ai_executor.py`, `tests/check_ai_bridge.py` (mock Claude, ağ/anahtar/ücret yok), `tests/servo_light_test.c`, genişletilmiş `tests/can_protocol_test.c`, değişmeyen `tests/safety_core_test.c` ve `node --test software/web_ui/panel_logic.test.mjs`; panelin satır içi betiği `node --check` ile sözdizimi denetiminden geçti. Doğrulanmayanlar: gerçek Claude API (önbellek, görüntülü tool_result, maliyet, gecikme), sunucu/gateway, STM32 üzerinde çalışma, gerçek servo/ToF/kamera, tarayıcıda konuşma tanıma. T01–T20 **NOT_RUN**.

## A3 Lite mekanik (L1) — 24.09.2026

[Plan](superpowers/plans/2026-09-24-a3-lite-mechanical.md) uygulandı. Testler önce A3 beklentileriyle yazıldı ve başarısız oldu, sonra geçti: `tests/check_design.py` (32,4 Wh, 20,93 Wh, 1,64 saat, 5° rampada 0,109 N·m / 0,51 A, 1.980 sayım/tur, 0,72 J, PETG plaka), `tests/check_cad.py` (56 katı, çakışmasız, motor mili ≥7 mm, E-stop, ToF pencereleri, ESP32-CAM zarfı, baş 296,8 mm, kol pozları), `tests/check_body_mass.py` (baskı tahminleri tahsis içinde, filament 2 + 1 makara). `tests/check_drivetrain.py` A2 arşiv config'iyle geçer. Artık üretilmeyen A2 STEP dosyaları çöp kutusuna taşındı (A2 arşiv montajında duruyor). Doğrulanmayanlar: baskı, dilimleme, tartım, plaka rijitliği, motor ısınması, E-stop DC kesme, Wi-Fi. T01–T20 **NOT_RUN**.

## A3 Lite elektronik (L2) — 25.09.2026

[Plan](superpowers/plans/2026-09-25-a3-lite-electronics.md) uygulandı; testler önce yazıldı ve başarısız oldu: `tests/check_esp32_pinmap.py` (23/23 GPIO, saklı pinler, ADC2, çevre birimi taşması reddi), `tests/check_lite_wiring.py` (her atama doğru başlık pininde, güç yolu, E-stop kesmesi, `ACT_EN` pulldown, bölücüler, ışık tamponu; ERC 0 ihlal), `tests/check_lite_bom.py` (9.515 TL ≤ 10.000 TL; adetler config/pin haritasıyla tutarlı). Şema ızgaraya oturtuldu, etiket çakışmaları giderildi. Doğrulanmayanlar: modül pin sıraları, Mini560 EN, E-stop DC kesme, servo 3,3 V sinyal, TB6612 ısınması, gerçek fiyatlar. T01–T20 **NOT_RUN**.

## A3 Lite yazılım (L3) — 25.09.2026

[Plan](superpowers/plans/2026-09-25-a3-lite-software.md) uygulandı. Testler her adımda önce yazıldı ve başarısız oldu:
- `tests/lite_link_test.c`: RFC 4231, datagram, imzalı tekrar.
- `tests/lite_core_test.c`: motor modeliyle ARM, rampa, AI tavanı, ToF, lease, E-stop, STOP, batarya, teker başına stall, sıfır geçişi ve ısı bütçesi.
- `tests/check_lite_gateway.py`: C çekirdeği ctypes ile uçtan uca.

Bozulmuş sürümlerle denendi: boşa alma, ısı bütçesi, stall, izin kaybı ve NaN sözleşmesi kaldırılınca testler başarısız oluyor. Bağımsız inceleme R1–R10 ve yeniden kontrol F1–F3 kapatıldı ([kapanış](review_closure_2026-09-25.md)). Doğrulanmayanlar: ESP-IDF sürücüleri, gerçek Wi-Fi/UDP, ESP32-CAM, ücretli API, bütün fiziksel testler. T01–T20 ve TL1–TL3 **NOT_RUN**.
