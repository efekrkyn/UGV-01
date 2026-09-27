# UGV-PWR-01

> **A2 kaydı.** A3 Lite (≤10.000 TL, DD65–DD67) bu kartları ve pinleri kullanmaz; güncel elektronik: [Lite elektronik](../../docs/lite_electronics_A3.md).

Durum: PHASE6 **kısmi** [KiCad hiyerarşisi](ugv_pwr_01.kicad_sch) ([PDF](ugv_pwr_01.pdf)): [PWR↔MCU arayüzü](pwr_mcu_interface.kicad_sch), [K2 referansı](k2_reference.kicad_sch), [aktüatör yolu](actuator_path.kicad_sch) (F1–K1–MID, ön şarj, bleed, test enjeksiyonu), [güvenlik kapısı](safety_gate.kicad_sch) (çift NC, TPS3431, reset latch, izin zinciri) ve [ARM I/O](arming_io.kicad_sch) (TCA9534A, ADS1115, K1/K2 karşılaştırıcıları). Birleşik ERC 0 hata/1 dış-ağ uyarısı; [inceleme](../../docs/pwr_safety_path.md). INA228/giriş koruması, regülatörler, TVS/dump clamp, K1 MPN/footprint, layout ve üretim çıktısı **yok**; T01/T13 NOT_RUN. [Güç mimarisi ve hesaplar](../../docs/electrical_architecture.md) referanstır.

Kart işlevleri: ana20A sigorta/servis,ters polarite,K1/K2 arası MID tanısı ve K2 çevresi [470 Ω ön şarj](../../docs/precharge_and_separator_diagnostics.md),INA228+2mΩ şönt,always-on logic/compute ve kesilebilir aktüatör yolları,5.1V6A compute,5V2A control,6V4A servo,12V2A auxiliary buck-boost,LED ve test noktaları. 2mΩ şönt20A'da40mV/0.8W; ≥3W Kelvin tip aday, thermal derating ve sense-range ayarı doğrulanacak.

INA228 şöntün hemen yanında yerel I²C ile kalır; J-SIG için PCA9615 diferansiyel tampon/iki bükümlü çift kısmi şematiğe işlendi. Bu tamponun arızası fiziksel E-stop/ayırıcı zincirini etkilememelidir. İzin/watchdog/E-stop devreleri ve `PWR_PGOOD` kaynağı (TPS3808G33) çizildi; `PWR_3V3` regülatörü ve MCU tarafı PGOOD hâlâ açık. J-PWR dik açılı 768250004 adayına geçti; kart kenarı, mandal ve kablo hacmi tam CAD'de çözülmeden PCB yerleşimi serbest bırakılmaz.

K1 DC röle + K2 back-to-back FET, çift NC E-stop ve manuel-reset latch. K1 için [bobin/kontak seçim kapısı](../../docs/k1_relay_selection.md) açık; ham 4S'e 12 V bobin doğrudan bağlanmaz. K2 için [LM74900-Q1 + 2×CSD18540Q5B koşullu adayı](../../docs/k2_separator_selection.md) ve [K2 pin seviyesi şeması/eşik taraması](../../docs/k2_reference_schematic.md) var; gerçek PCB bakır/ısı, Kelvin şönt MPN ve güvenli EN sürücüsü açık. Motor tarafında bağımsız regen clamp: 1,5 Ω direnç/17,8 V ön eşik, ≥20 J gerçek darbe kapasitesi; direnç şasiye bağlı metal parça, PCB/plastik içine gömülmez. TVS son transient katmanıdır. Clamp, ayırıcı feedback ve haricî watchdog davranışı yalnız firmware'e emanet edilmez.

Ön şarj/tanı için PWR kartında aday TCA9534APWR komut expander ve ADS1115IDGSR üç ray ADC bulunur; haricî Low bias ve [TPS3431 100 pF/PGOOD güvenlik izni](../../docs/watchdog_design.md) gerekir. Test enjeksiyonu K1'i baypas ettiğinden iki seri anahtarın biri fiziksel NC/WD izninde kalır. Bunlar 24.09.2026'da `actuator_path`, `safety_gate` ve `arming_io` sayfalarına çizildi; NC-A K1 bobin enerjisini, NC-B K2 EN/ön şarj/test izin sürücülerinin beslemesini taşır ([DD52–DD59](../../docs/design_decisions.md)). Netlist/ERC testleri: `tests/check_pwr_actuator_path.py`, `tests/check_pwr_safety_gate.py`, `tests/check_pwr_board.py`.

Batarya paketi, BMS ve haricî16.8V CC/CV charger ticari/doğrulanmış alt bileşenlerdir. Bu kartta özel hücre BMS'si veya ilk revizyonda onboard charger geliştirilmeyecek. BMS/charger exactMPN,TVS/clamp/röle/fuseI²t ve connector seçimleri PHASE6 öncesi kapanır.

PHASE6 teslimatları: KiCad schematic, hesap ekleri,DC kesme ve fault injection review;PHASE7: PCB/thermal/DFM ve üretim dosyaları. Bugünkü doküman PCB siparişi vermek için yeterli değildir.

[K1→K2→güvenlik izin yolu uygulama planı](../../docs/superpowers/plans/2026-09-24-pwr-safety-path.md) bu açık işleri ölçülebilir netlist/ERC ve fiziksel gate'lere ayırır. Plan şema veya parça onayı değildir.

MCU'ya ortak dönüşlü güç ve ayrı sinyal bağlantısının net/pin/aday MPN sözleşmesi [PWR↔MCU arayüzünde](../../docs/pwr_mcu_interface.md). Kısmi sayfa ERC'si 0 hata ve diğer sayfalara devredilen 9 izole-net uyarısı verir; [pin/net testi](../../tests/check_board_interface_sheets.py) bunu denetler. Fiziksel çift NC E-stop sinyal konektöründen geçmez; PWR üzerinde doğrudan donanım zinciridir.
