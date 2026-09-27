# UGV-PWR-01 ↔ UGV-MCU-01 arayüz sözleşmesi — P0

> **A2 kaydı.** A3 Lite (≤10.000 TL, DD65–DD67) bu kartları ve pinleri kullanmaz; güncel elektronik: [Lite elektronik](lite_electronics_A3.md).

23.09.2026 · PHASE 5/6 şematik girdisi. Bu tablo **net adlarını ve hata halinde beklenen davranışı** sabitler; soketlerin PCB yerleşimi, krimp takımı, kart ERC'si ve termal kabul henüz yapılmadı. İki kartın şematiği aynı net adlarını kullanacak. Fiziksel çift NC E-stop hattı PWR kartına doğrudan gider; aşağıdaki durum sinyalleri güvenlik döngüsünün yerine geçmez.

## İki ayrı bağlantı

| Bağlantı | Uçlar ve akış | Ön seçim | Sınır |
|---|---|---|---|
| J-PWR, 4 pin | PWR K2 sonrası `ACT_BUS` ve kesintisiz `5V_CONTROL` → MCU; iki eş uzunlukta `PGND` dönüşü | Her iki kartta [Molex Mega-Fit 768250004](https://www.molex.com/en-us/products/part-detail/768250004) **dik açılı aday**, iki uçta 1700010104 housing; ACT ve iki GND için AWG12/768230322, 5 V için AWG16/768230321 dişi krimp | Motor 15 A + kontrol 2 A tasarım zarfı; F1 15 A aday; enerjiliyken sökülmez |
| J-SIG, 12 pin | MCU izin/watchdog → PWR; PWR güvenlik/geri bildirim → MCU; diferansiyel I²C telemetri | Her iki kartta [JST GH BM12B-GHS-TBT](https://www.jst-mfg.com/product/index.php?lang=2&series=105), iki uçta GHR-12V-S + SSHL-002T-P0.2, AWG26 | Yalnız düşük akım sinyal; motor/servo gücü yok |

| J-PWR pin | Net | Tel | Not |
|---:|---|---|---|
| 1 | `ACT_BUS` | AWG12 | K2 sonrası kesilen motor beslemesi |
| 2 | `PGND_A` | AWG12 | Güç dönüşü, her bir kontak tek başına 17 A fault zarfı için incelenir |
| 3 | `PGND_B` | AWG12 | `PGND_A` ile iki kartta da ortak, eş tel boyu ve ayrı krimp |
| 4 | `5V_CONTROL` | AWG16 | E-stop'ta açık kalan ≤2 A kontrol beslemesi |

KiCad 10'daki `Connector_Molex:Molex_Mega-Fit_76825-0004_2x02_P5.70mm_Horizontal` ayak izinde pad merkezleri mm olarak `1=(0,0)`, `2=(5,7;0)`, `3=(0;5,5)`, `4=(5,7;5,5)`; iki pozitif pin **çaprazdır**. Courtyard `x=−3,68…9,38`, `y=−16,4…7,85 mm` (13,06×24,25 mm); gövde yerleşim yönüne göre dönüştürülür. Bu yalnız PCB gövde zarfıdır: yatay takma/çıkarma ve AWG12 bükülme hacmi, mandal ve takım erişimi tam montaj CAD'inde henüz çözülmedi. [Molex](https://www.molex.com/en-us/products/series-chart/76825) 16,78 mm **mated height** belirtir; bunu PCB üstü dikey çıkıntı sanmayız. Denetlenen pad/net/AWG kaydı [JSON](../config/pwr_mcu_connector.json), KiCad pad düzeni regresyonu [test](../tests/check_pwr_mcu_connector.py). **Dişi housing'in kablo tarafından bakıldığında ayna dönüşü ve cavity numaraları hâlâ üretici çizimi/gerçek örnekle doğrulanmalıdır; bu çizim krimp talimatı değildir.**

PWR ve MCU kartı aynı pin numarasını kullanır; montajda her damar için pin↔pin süreklilik ve ters polarite kontrolü zorunludur. İki GND bilerek aynı yüksek akım konnektöründedir; ayrı düşük akımlı kontrol dönüşü yoktur. Eşit akım paylaşımı varsayılmaz: her GND kontağı tek başına 15 A motor + 2 A kontrol zarfına dayanabilmelidir. J-SIG'de fazladan GND damarı yoktur; sinyal referansı J-PWR GND üzerinden taşınır. Güç ve sinyal kabloları ayrı kanaldadır; 5 V damarı ACT_BUS ve sürücü anahtarlama düğümlerinden uzak tutulur. Kilit mandalı servis açıklığı CAD'de ölçülür. Başka bir CAN/shield/sensör dönüşü PWR↔MCU arasında düşük empedanslı paralel yol oluşturursa aynı akım analizi yeniden yapılır.

| J-SIG pin | Net | Sürücü → alıcı | Sağlıklı/etkin seviye | Kopuk kablo veya reset davranışı |
|---:|---|---|---|---|
| 1 | `MCU_RUN_REQ` | MCU PD8 → PWR donanım izin zinciri | 3.3 V High, ARMING/ARMED/DRIVING boyunca taze güvenlik turu varsa | PWR pulldown: Low; K1/K2 izni yok |
| 2 | `MCU_WDI` | MCU PD9 → PWR haricî watchdog | Sağlıklı kontrol turu ardından kenar/darbe | Kenar kaybı watchdog latçi; K1/K2 ve nSLEEP kesilir |
| 3 | `PWR_ACT_EN` | PWR donanım izin çıkışı → MCU nSLEEP, TIM1/TIM8 BKIN, PD10 readback | 3.3 V High yalnız fiziksel izin + watchdog + MCU isteği + K1/K2 tanısı ve ön şarj tamam | MCU tarafı pulldown: Low; dört sürücü sleep, iki timer break etkin |
| 4 | `PWR_K1_FB` | PWR bağımsız K1 tanısı → MCU PD11 | High, K1 kapalı teyit | Low/uyuşmazlık: arm yok veya FAULT |
| 5 | `PWR_K2_FB` | PWR bağımsız K2 tanısı → MCU PD12 | High, K2 iletimde teyit | Low/uyuşmazlık: arm yok veya FAULT |
| 6 | `ESTOP_A_CLOSED` | PWR NC-A durumu → MCU PD13 | High, kanal kapalı/sağlıklı | Low: E_STOP; fiziksel zincir zaten keser |
| 7 | `ESTOP_B_CLOSED` | PWR NC-B durumu → MCU PD14 | High, kanal kapalı/sağlıklı | Low: E_STOP; fiziksel zincir zaten keser |
| 8 | `PWR_WD_OK` | PWR haricî WD durumu → MCU PD15 | High, watchdog sağlıklı | Low: arm yok/FAULT; actuator izni donanımda kesilmiş |
| 9 | `DI2C_SCL_P` | MCU PCA9615 ↔ PWR PCA9615 | SCL diferansiyel çift + | Hat/ölçüm kaybı: FAULT; fiziksel izin zinciri bağımsız |
| 10 | `DI2C_SCL_N` | MCU PCA9615 ↔ PWR PCA9615 | SCL diferansiyel çift − | Aynı |
| 11 | `DI2C_SDA_P` | MCU PCA9615 ↔ PWR PCA9615 | SDA diferansiyel çift + | Aynı |
| 12 | `DI2C_SDA_N` | MCU PCA9615 ↔ PWR PCA9615 | SDA diferansiyel çift − | Aynı |

MCU PA9/PA8 ile PWR üzerindeki INA228 arasındaki **tek uçlu I²C yalnız kart üzerinde** kalır; kabloda NXP PCA9615'in iki diferansiyel çifti kullanılır. Her çift kendi bükümlü teliyle taşınır. PCA9615'in kart tarafı `VDD(A)` her kartın yerel 3,3 V rayından, diferansiyel kablo tarafı `VDD(B)` ise yerel 5 V rayından beslenir. [İki uçlu KiCad referans devresi](../electronics/interconnect/differential_i2c_reference.kicad_sch) 600 Ω/120 Ω/600 Ω sonlandırma-bias, yerel 4,7 kΩ pull-up, besleme bypass ve `PGOOD` kontrollü `EN` girişinde 10 kΩ pulldown çizer. Bu devre üretim kartlarının şematiği değildir; iki yerel `PGOOD` kaynağı, kablo empedansı, 100 kHz hata oranı ve bus recovery PH5/6'da şematik ve jigle doğrulanır. Bu bağlantı akım sınırlamasının veya E-stop'un tek emniyet kaynağı değildir. Uzun yüksek ortak-modlu Kelvin hattını MCU kartına taşımak paket ölçümünün doğruluğu ve kablo arıza gerilimi açısından tercih edilmedi.
PCA9615 **galvanik izolasyon sağlamaz**; ortak PGND ve güvenlik sinyallerinin ground-bounce/backfeed analizi ayrı kalır.

`PWR_ACT_EN` **MCU'nun yazılımsal talebinin kopyası değildir**. PWR donanımı çift NC, manuel reset latçi, haricî watchdog, OV/UV ve MCU isteğini birleştirir. K1/K2 ayrı seri kesici olarak kalır. PWR_ACT_EN Low olduğunda DRV8874 nSLEEP doğrudan donanım yolundan Low olur; STM32 timer break ek tanıdır. Hat sökülmesi/kısa devre/MCU resetinde izin High'a düşmemelidir. K1/K2 feedback devreleri yalnız son ACT_BUS gerilimini örnekleyerek “iki yol da açıldı” sonucunu veremez; K1 yardımcı kontak/ara düğüm ve K2 ayrı tanı yöntemi PHASE 6 şematiğinde kanıtlanacak. Toplam enerji kapatma ve mekanik durma farklı ölçümlerdir.

Ön şarj nedeniyle `MCU_RUN_REQ` **ARMING başında** istenir; bu istek `PWR_ACT_EN` üretmez. PWR'nin yerel [ADC/GPIO ve iki seri test anahtarı adayı](precharge_and_separator_diagnostics.md), K1/K2 ön testini mevcut diferansiyel I²C üzerinden sıralar. I²C komut çıkışı stuck-High olsa bile [haricî watchdog/NC/PGOOD](watchdog_design.md) K1/K2 ve ön şarj/test izin yolunu kesmelidir. Bu davranış J-SIG pin sayısını değiştirmeden 24.09.2026'da [PWR P0 sayfalarına](pwr_safety_path.md) çizildi ve netlistten mantık olarak denetlendi; fiziksel fault enjeksiyonu (T01/T13) yapılmadı.

## Ön elektrik ve termal hesap

- Mega-Fit [PS-76823-100](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/768/76823/PS-76823-100-001.pdf) **4 devre, hepsi yüklü** testte çıplak bakır AWG12 için **18 A**, AWG14 için **15 A** referans verir. ACT hattı 15 A hedefte AWG14 ile sınıra oturduğundan AWG12 seçildi; her GND kontağı olası tek kontak arızasında 17 A taşıyabilsin diye AWG12'dir. 18 A bir ürün garanti akımı değildir: 30 °C artış testi, 50 °C bölme, PCB bakırı ve krimp derating'i ayrıca incelenir. İki GND ile akımın eşit bölüneceği iddia edilmez.
- 0,4 m AWG12 ACT+ ve her biri 0,4 m AWG12 iki GND varsayımı, 20 °C'de 15 A motor akımında dengeli GND paylaşımı için yaklaşık `0,047 V / 0,70 W` tel kaybı verir; bir GND açıkken yaklaşık `0,063 V / 0,94 W`. Bunlar temas/PCB kaybını ve 2 A kontrol akımını içermez. AWG16 5 V pozitif telde 0,4 m/2 A için yaklaşık `0,011 V` ek düşüm vardır; ortak GND düşümü yükle ayrıca ölçülür. D2A'nın 67 g kütle rezervi bu ağırlaşmayı karşılamayabilir; gerçek demet tartılır ve hedef revize edilir.
- JST [GH](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf) 26 AWG ile 1 A/50 V sınıfı; bu konnektörde hiçbir pin 1 A güç hattı taşımaz. Sinyallerin gerçek pull-up/pulldown ve giriş filtre değerleri şematikte seçilir.

## Şematik ve masaüstü geçiş kapıları

1. Eski ayrı J-ACT/J-CTRL dönüşlerinde 0,4 m AWG14 GND yaklaşık 3,32 mΩ, 0,3 m AWG20 GND yaklaşık 9,99 mΩ idi. İdeal paralel paylaşım bile AWG20 kontrol dönüşüne `15 A × 3,32/(3,32+9,99) ≈ 3,7 A` motor akımı yönlendiriyordu; bu 2 A kart tasarım zarfını aşıyordu. Bu nedenle tek J-PWR ve iki AWG12 dönüş seçildi. PCB'de yüksek akım dönüşü sürücü kenarında tutulur; iki GND pininin her biri, kontrol referans kayması, ADC/CAN/IMU gürültüsü ve başka paralel dönüşler T02'de ölçülür. “Star ground” sözü tek başına çözüm değildir.
2. PWR kaynaklı High sinyaller MCU kapalıyken GPIO/3.3 V rayını geri besleyemez. Seri 1–4,7 kΩ **tek başına** altı girişin toplam enjeksiyonunu güvenli yapmaz. [SN74LVC244APWR güçsüz alıcı taslağı](powered_off_status_receiver.md), `Ioff` ve yerel çıkış pulldown'u ile seçildi; henüz gerçek kart şematiği/bench kabulü değil. Giriş akımı ve brownout sıralaması ERC/bench ile doğrulanır. `PWR_ACT_EN` için yerel pulldown ve donanım yolları, diferansiyel I²C için iki kartın açık/kapalı birleşimleri sınanır.
3. `MCU_RUN_REQ` ve WDI boot/high-Z durumunda PWR pulldown ile pasiftir. Haricî watchdog veya tek hat kopuğu sürüşe izin veremez. Status High sinyallerinde kablo kopması MCU'da Low görünür; durum geçişleri [güvenlik matrisi](safety_architecture.md) ile aynı kalır.
4. Krimp, housing, iki kartın header orientation/footprint'i, konnektör arası yanlış eşleşme, tek GND kopuğu, 50 °C sıcaklık, titreşim/çekme, servis erişimi ve 15 A motor + 2 A kontrol yükünde temas sıcaklığı gerçek örnekte doğrulanır. Exact MPN'ler **adaydır**, tedarik ve üretim onayı değildir.
5. J-PWR pin1 `ACT_BUS` ile pin4 `5V_CONTROL` arasında yanlış krimp/ezilme/kısa devre 5 V rayından kesilmiş motor barasına geri besleme yapamaz; 5 V dalı akım sınırlama/sigorta ve gerekirse ters akım bloklamasıyla korunur. E-stop altında bu kısa devre akım sınırlı jig ile sınanır; nSLEEP ve iki fiziksel kesici izin vermeden motor sürme yoktur.

Pad kontrolü: `python3 tests/check_pwr_mcu_connector.py`. macOS KiCad 10 dışındaki kurulumda `UGV_J_PWR_FOOTPRINT` ortam değişkeniyle aynı 76825-0004 `.kicad_mod` dosyasını göster. Bu kontrol footprint pad konumunu kanıtlar; dişi housing'in kablo tarafı cavity sırasını, krimp takımını veya gerçek 15 A termalini kanıtlamaz.

İki kablo grubunun 1↔1 pin sürekliliği [KiCad P0 kablo şematiğinde](../electronics/interconnect/pwr_mcu_harness.kicad_sch) çizildi; [PDF](../electronics/interconnect/pwr_mcu_harness.pdf) ve [16 net + ERC kontrolü](../tests/check_pwr_mcu_harness.py) mevcuttur. [Diferansiyel I²C referansı](../electronics/interconnect/differential_i2c_reference.kicad_sch) ve ayrı [MCU](../electronics/ugv_mcu_01/pwr_mcu_interface.kicad_sch)/[PWR](../electronics/ugv_pwr_01/pwr_mcu_interface.kicad_sch) kısmi arayüz sayfaları da pin/net kontrolünden geçer. Kısmi kart sayfaları başka sayfalara gidecek dokuz net için beklenen ERC uyarısı verir. 24.09.2026'dan beri PWR arayüz sayfası [kısmi PWR hiyerarşisinin](pwr_safety_path.md) parçasıdır (referanslar 5xx, global etiket): birleşik ERC 0 hata ve [check_pwr_board](../tests/check_pwr_board.py) J-SIG'in 12 ağının her birinin PWR tarafında tek tanımlı elemana gittiğini doğrular. `PWR_K1_FB`/`PWR_K2_FB` LM2903 karşılaştırıcı çıkışlarıdır; `PWR_ACT_EN` yalnız `SAFE_GATE ∧ ACT_ENABLE_REQ ∧ SAFE_EN` AND çıkışından 1 kΩ ile sürülür. Bu kontroller gerçek kartlarda 5 V geri besleme, E-stop, watchdog, `PGOOD`, sürücü nSLEEP veya diğer koruma devrelerini doğrulamaz; bunlar PH5/6 şematiklerinde açıktır.
