# UGV-PWR-01 güç ve güvenlik izin yolu — KiCad P0 sayfaları

> **A2 kaydı.** A3 Lite (≤10.000 TL, DD65–DD67) bu kartları ve pinleri kullanmaz; güncel elektronik: [Lite elektronik](lite_electronics_A3.md).

24.09.2026 · PH6 şema incelemesi. **Üretim, PCB, fonksiyonel güvenlik veya sürüş onayı değildir.** K1 MPN/footprint'i, F1 sigorta ailesi/I²t koordinasyonu, şönt MPN'i, TVS/rejeneratif clamp, güç direnci parçaları ve PCB termali açıktır. T01/T03/T13 fiziksel testleri **NOT_RUN**. Bu sayfalar tam kart değildir: INA228/giriş koruması, regülatörler, servo/aux rayları ve dump clamp çizilmedi.

## Sayfalar ve doğrulama

`F1 → K1 → MID → K2 → ACT_BUS` yolu, anahtarlı ön şarj, ACT bleed, iki anahtarlı test enjeksiyonu, çift NC E-stop, TPS3431 watchdog ve izin zinciri beş kısmi sayfa ve bir kök hiyerarşide çizildi. [Birleşik PDF](../electronics/ugv_pwr_01/ugv_pwr_01.pdf) altı sayfadır.

| Sayfa | İçerik | Tek sayfa ERC | Test |
|---|---|---|---|
| [pwr_mcu_interface](../electronics/ugv_pwr_01/pwr_mcu_interface.kicad_sch) | J-SIG/J-PWR, PCA9615; `PWR_3V3`, `5V_CONTROL`, `PGND` için **tek** PWR_FLAG (kart girişi). Referanslar 5xx. | 0 hata, 9 dış-ağ uyarısı | [check_board_interface_sheets](../tests/check_board_interface_sheets.py) |
| [k2_reference](../electronics/ugv_pwr_01/k2_reference.kicad_sch) | LM74900 + 2×CSD18540 + 1 mΩ Kelvin şönt | 1 beklenen hata: U1 GND pin13 `PGND` sürücüsü arayüz sayfasında; 4 uyarı | [check_k2_reference](../tests/check_k2_reference.py) |
| [actuator_path](../electronics/ugv_pwr_01/actuator_path.kicad_sch) | F1, K1, bobin sürücü/clamp, ön şarj, bleed, test enjeksiyonu, ray bölücüler, TP201–204 | 0 hata, 5 dış-etiket uyarısı | [check_pwr_actuator_path](../tests/check_pwr_actuator_path.py) |
| [safety_gate](../electronics/ugv_pwr_01/safety_gate.kicad_sch) | J-ESTOP, NC-A/NC-B, TPS3431, TPS3808, reset latch, AND fan-out, LVC1T45, durum tamponları | 2 beklenen ray hatası (`PWR_3V3`, `PGND`), 9 dış-etiket + 1 yerel kütüphane uyarısı | [check_pwr_safety_gate](../tests/check_pwr_safety_gate.py) |
| [arming_io](../electronics/ugv_pwr_01/arming_io.kicad_sch) | TCA9534A komut, ADS1115 üç ray + IMON, LM2903 K1/K2 geri bildirim | 3 beklenen ray + 1 SCL (pull-up arayüz sayfasında) hatası, 12 dış-etiket uyarısı | check_pwr_actuator_path |
| [ugv_pwr_01](../electronics/ugv_pwr_01/ugv_pwr_01.kicad_sch) kök | Beş sayfanın global etiketlerle birleşimi | **0 hata, 1 uyarı** (`MOTOR_FEED`: çizilmemiş STAR/INA228 beslemesi) | [check_pwr_board](../tests/check_pwr_board.py) |

Tek sayfa ERC'sindeki hatalar yalnız başka sayfada tanımlı raylar/sürücülerdir ve testlerde **ağ adıyla** kilitlenmiştir. Kanıt olarak birleşik ERC kullanılır. KiCad 10 aynı ağda iki PWR_FLAG'i güç-çıkışı çakışması saydığı için her ray tek sayfada işaretlenir; regülatör sayfaları çizildiğinde bu bayraklar gerçek çıkışlarla değiştirilecektir.

`check_pwr_board`, KiCad netlistindeki gerçek kapı pinleri, seri dirençler ve pull'larla izin mantığını 2 048 giriş kombinasyonunda (NC-A, NC-B, WD, ray, MCU isteği, latch, beş komut) ve ayrıca **bütün lojik çıkışları High'a takılı** modda değerlendirir: toplam 4 096 senaryo. Altı mutasyon (MCU_RUN_REQ'i SAFE_GATE'ten çıkarmak, LVC1T45 B beslemesini 3,3 V'a almak, latch /CLR'yi sabitlemek, test FET'ini MID'e kaydırmak, TPS3431 EN'i MCU hattına bağlamak, LM74900 pad25'i PGND'ye bağlamak) testlerce yakalandı. Bu kontrol bağlantı ve Boole niyetini kanıtlar; zamanlama, analog eşik, SOA veya fiziksel davranışı kanıtlamaz.

```sh
cd tools && python3 build_differential_i2c_reference.py && python3 build_k2_reference.py && python3 build_pwr_safety_path.py && cd ..
python3 tests/check_k2_reference.py && python3 tests/check_board_interface_sheets.py
python3 tests/check_pwr_actuator_path.py && python3 tests/check_pwr_safety_gate.py && python3 tests/check_pwr_board.py
```

## Güç yolu, ön şarj, bleed ve test

- **K1**: KiCad genel `Relay_SPST-NO`, değer `K1 relay MPN OPEN`, footprint **boş**. T9AS1D17-5 yalnız paketleme adayı olarak alan notunda. Kontak 13=`F1_OUT`, 14=`MID`. Bobin üst ucu `ESTOP_A_5V` (NC-A kontağından gelen 5 V), alt ucu AO3400A (Q201) ile PGND'ye. 1N4148W + BZT52C12 clamp: kapatmada Q201 `Vds ≈ 5,25+1,0+12,6 ≈ 18,9 V` (<30 V); röle bırakma süresi ölçülmedi.
- **Ön şarj**: BSS84 (Q202) kaynağı `MID`'de, 470 Ω ≥2 W darbe direnci `ACT_BUS`'a. Kapalıyken gövde diyotu `MID→ACT` iletimini bloke eder; `ACT>MID` olduğunda ACT enerjisi 470 Ω üzerinden MID'e sızabilir; bu nedenle ARMING önce ACT'yi boşaltır. Gate: 100 kΩ G–S, 12 V zener, 10 kΩ + 2N7002 (Q203). Q203 gate'i `PCH_DRV`, NC-B beslemeli LVC1T45'ten gelir.
- **ACT bleed**: 150 Ω/5 W + BSS138 (Q204), `BLEED_CMD` 1 kΩ/100 kΩ ile. **Donanım kilidi:** `PWR_ACT_EN` High iken Q205 bleed gate'ini Low'a çeker; sürüşte bleed açılamaz. ARMING'de `PWR_ACT_EN` Low olduğundan bleed kullanılabilir.
- **Test enjeksiyonu**: `F1_OUT → Q206 (izin) → Q208 (komut) → 1 kΩ ≥1 W → MID`; iki P-FET'in kaynağı da `F1_OUT` yönündedir, biri tek başına F1→MID akımını keser. Q206 gate'i `TEST_PERMIT_DRV` (NC-B'den beslenen LVC1T45, SAFE_GATE), Q208 gate'i `TEST_CMD` (100 Ω + 100 kΩ varsayılan Low).
- **Ölçüm**: MID bleed artık 8,25 k + 1,65 k (%0,1) bölücüdür (9,9 kΩ); F1/ACT 100 k/20 k, karşılaştırma bölücüleri 105 k/20 k. MID toplam yükü 9,17 kΩ. ADS1115 girişleri 1 kΩ seri dirençle beslenir; güçsüz ADC'ye enjeksiyon bölücü empedansıyla sınırlıdır ama PH6 ölçümü ister.

Netlist değerlerinden hesaplanan (1 kΩ ±%5, bölücü ±%1, 150 Ω ±%5, 12,4–16,8 V) test penceresi: sağlıklı açık K2'de `MID` **11,11–15,24 V** (nominal 15,15 V), K2 veya ön şarj kısa + ACT bleed açıkken **1,46–2,35 V** (nominal 2,16 V). ±0,3 V ADC hatası eklenince 8 V ayırım eşiğine iki tarafta pay var. Ön şarj +%20 C ve +%5 R ile ≤7,85 s (nominal 6,23 s), bleed ≤2,51 s; toplam 15 s ARMING taslağının içinde. ACT bölücüsü ön şarj sonunu 16,73 V'ta bırakır (MID−0,07 V). Test direnci en kötü 0,30 W (1 W parça), bleed 1,98 W (5 W), MID bölücü 28,5 mW.

## K1/K2 geri bildirimi

`PWR_K1_FB` ve `PWR_K2_FB`, MCU'nun ADS1115 okumalarından bağımsız LM2903 karşılaştırıcılarıdır: K1_FB High ⇔ `MID > 0,96·F1_OUT + 0,15 V`; K2_FB High ⇔ `ACT > 0,96·MID + 0,15 V`. 0,15 V ofset, 3,3 V'tan 2,2 MΩ ile karşılaştırma düğümüne verilen 25 mV'tur; iki ray 0 V iken çıkışı Low tutar. Eşik 12,4 V'ta 12,05 V, 16,8 V'ta 16,28 V. Test enjeksiyonunun en yüksek MID'i (15,24 V) eşikten ≥0,2 V aşağıda; kapalı K1 (≤0,05 V düşüm) eşikten ≥0,2 V yukarıda kalır. 0,2 V hata bütçesi LM2903 ofset/bias akımı ve %0,1 oran hatasının kâğıt tahminidir. Histerezis yoktur; MCU komut, zaman ve iki ölçümü birlikte değerlendirir. Bu hatlar ölçülen durumu raporlar; komutla AND'lenmez, böylece kaynaklı K1 (`K1_CMD=0`, `K1_FB=1`) görünür.

**K2 iletim tanısı önerisi (PH8 açık):** K2 EN açık ve ön şarj kapalıyken kısa bleed darbesi verilir. K2 iletmiyorsa `τ=150 Ω·4700 µF=0,705 s` ile ACT yaklaşık 29 ms içinde MID'in %4 altına iner ve `PWR_K2_FB` Low olur. Güvenlik çekirdeği henüz bu adımı içermiyor.

## İzin zinciri

| Sinyal | Tanım |
|---|---|
| `NC_A_OK`, `NC_B_OK` | Her NC kontağı kendi PTC'li 5 V'unu geri getirir (`ESTOP_A_5V`, `ESTOP_B_5V`); 10 kΩ pulldown, 10 kΩ/100 nF (~1 ms) filtre, SMAJ6.0CA aday TVS |
| `RAIL_OK` | TPS3808G33 (3,07 V, CT açık ≈20 ms); TPS3431 `EN` girişini ve PCA9615 `PWR_PGOOD` tamponunu sürer |
| `WD_OK` | TPS3431 `WDO ∧ ENOUT` açık-drenaj, 10 kΩ pull-up; `SET1=PWR_3V3`, `CWD=100 pF C0G`, `WDI` 1 kΩ + 100 kΩ pulldown |
| `CHAIN_OK` | `NC_A_OK ∧ NC_B_OK ∧ WD_OK` (74LVC1G11) |
| `LATCH_OK` | 74LVC2G74: `/CLR=CHAIN_OK`, `D=CHAIN_OK`, saat = reset butonunun **bırakılması** (74LVC1G17 Schmitt, 10 kΩ/100 nF). Takılı basılı buton kenar üretmez; latch kurulamaz |
| `SAFE_GATE` | `LATCH_OK ∧ CHAIN_OK ∧ MCU_RUN_REQ` |
| `K1_DRV` | `SAFE_GATE ∧ K1_CMD`; enerji ayrıca NC-A'dan |
| `SAFE_EN` (K2 EN=SLEEP) | LVC1T45 B çıkışı, `VCCB=ESTOP_B_5V`: `SAFE_GATE ∧ K2_CMD` ve NC-B fiziksel olarak kapalı |
| `PCH_DRV`, `TEST_PERMIT_DRV` | Aynı şekilde NC-B beslemeli LVC1T45; komut sırasıyla `PRECHARGE_CMD` ve yalnız `SAFE_GATE` |
| `PWR_ACT_EN` | `SAFE_GATE ∧ ACT_ENABLE_REQ ∧ SAFE_EN`, 1 kΩ + 100 kΩ; hiçbir MCU pinine doğrudan bağlı değil |

**Fiziksel kesme:** NC-A bobin enerjisini, NC-B K2 EN/ön şarj/test izin sürücülerinin beslemesini taşır. Bütün lojik High'a takılsa bile NC-A açıkken K1, NC-B açıkken K2/ön şarj/test izni enerjisizdir; hiçbir tek NC açıkken `K1 ∧ (K2 ∨ ön şarj)` yolu oluşamaz. Watchdog veya yazılım çıkışı yalnız AND girişidir; açık NC'yi veto edemez. LM74900 `SLEEP` modu E-stop sayılmaz: `SLEEP=EN=SAFE_EN` ve donanım Low tutar. LM74900 pad25 elektriksel olarak yüzer. NC-B yükü ≈1,1 mA (F302 0,1 A PTC), NC-A yükü K1 bobini ≈0,2 A (F301 0,5 A PTC).

**MCU yeniden başlatma:** `MCU_RUN_REQ` latch'i temizlemez; durum makinesinde normal disarm sonrası yeniden ARM yerel reset istemez. TCA9534A'nın reset pini yoktur ve MCU resetinde son çıkışlarını korur. Watchdog ≥56,8 ms duraklamada latch'i temizler; daha hızlı bir yeniden başlatmada koruma yazılım sırasına kalır. **PH8 gereksinimi:** ARMING'e girerken TCA çıkış kaydı sıfırlanıp geri okunmadan `MCU_RUN_REQ` High yapılmaz.

**SET1 gizli arızası:** `SET1` Low'a kısa kalırsa watchdog kapanır ve `WD_OK` High kalır; bu durum izni açmaz ama korumayı sessizce kaldırır. **PH8 gereksinimi:** SELF_TEST'te WDI bilerek durdurulur, `PWR_WD_OK` Low görülür, sonra yerel reset istenir. `EN` Low arızası `ENOUT` üzerinden güvenli yönde izni keser.

**Zaman bütçesi (kâğıt):** NC açılması → `NC_x_OK` ≈1–2 ms → K2 EN Low (lojik ve LVC1T45 yolu; LM74900 kapanması µs düzeyi) ve K1 bobin sürücüsü kapalı. Watchdog: son WDI → `WDO` en çok 69,12 ms. K1 bırakma süresi rölenin ve 12 V clamp'in ölçümüne bağlıdır. ≤150 ms hedefi kâğıt üstünde pay bırakır; T13 osiloskop izi yok. NC-A lojik takılıyken açılırsa bobin akımı Q201 ve çift yönlü TVS üzerinden söner; bu daha yavaş bırakma T13'te ayrıca ölçülmelidir.

## Tek-arıza masaüstü tablosu

| Senaryo | Donanım sonucu | Masaüstü kanıtı | Fiziksel test |
|---|---|---|---|
| NC-A veya NC-B kablo kopması | İlgili kanal fiziksel keser; `CHAIN_OK` Low latch'i temizler, tüm AND çıkışları Low | check_pwr_board, takılı lojik modu | T13 NOT_RUN |
| MCU donması / WDI yok | ≤69,12 ms `WD_OK` Low → latch temiz → yerel reset gerekir | netlist + TI formülü | T03/T13 NOT_RUN |
| MCU enerjisiz | `MCU_RUN_REQ` 100 kΩ ile Low; durum hatları Ioff tampon + 1 kΩ ile Ioff alıcıya | netlist | T01/T03 NOT_RUN |
| TCA çıkışı takılı High | `SAFE_GATE` ile AND; NC fiziksel kesme | check_pwr_board | T13 NOT_RUN |
| K2 veya ön şarj FET'i kısa | ARMING test enjeksiyonunda MID/ACT 1,46–2,35 V → FAULT, K1 komut edilmez | pencere hesabı; [host sırası](../firmware/stm32/safety_core.c) | T01/T13 NOT_RUN |
| Test komut FET'i (Q208) kısa | Q206 izni NC-B/SAFE_GATE'e bağlı; NC açılınca akım kesilir | netlist + mantık | T13 NOT_RUN |
| Test izin FET'i (Q206) kısa | Q208 varsayılan Low komutla açık | netlist | T13 NOT_RUN |
| K1 kaynaklı | Test öncesi MID yüksek ve `K1_FB=1, K1_CMD=0` → ARM reddi | karşılaştırıcı eşikleri | T01/T13 NOT_RUN |
| NC kanalları arası veya 5 V'a kısa | Aynı polariteli kanallar donanımda ayırt edilmez; MCU A/B tutarsızlığını FAULT sayar | — | T13; test darbeli kanal PH6 FMEA açık |
| K2 OCP/SCP (`FLT` Low) | LM74900 latch-off; MCU TCA P6'dan okur | netlist | T13; donanım latch girişi açık |

K2 kısa iken K1'in boş bulk'a kapanmaması **MCU sırası ve tanı ölçümüne** dayanır; donanım yalnız izin zincirini ve gözlenebilirliği sağlar. Ayrı bir donanım kilidi (K1 kapanışını test sonucu tutucusuna bağlamak) açık tasarım seçeneğidir.

## Ölçüm satırları (T01/T03/T13'e eklendi)

K1 için K2-kısa dummy yükünde `I_break`, kontak gerilimi `V(TP201)−V(TP202)`, bobin alt ucu `TP204` ile bırakma süresi, kaynaklı kontak sonrası ARM reddi. NC-A ve NC-B ayrı ayrı açıkken ve `SAFE_GATE` jiglerle High'a zorlanmışken `SAFE_EN`, `PCH_DRV`, `TEST_PERMIT_DRV`, `TP203` (ACT_BUS). WDI durdurma → `WD_OK` → `SAFE_EN`/`TP204` zaman damgası. Q202/Q206/Q208 kısa jigleriyle MID/ACT ve test akımı. `SET1` Low ve `EN` Low enjeksiyonu.

## Açık kapılar

1. K1 exact MPN, 16,8 V DC motor kesme kanıtı ve footprint ([seçim kapısı](k1_relay_selection.md)).
2. F1 ailesi/I²t ve kablo koordinasyonu; şönt MPN/footprint.
3. ACT_BUS TVS ve rejeneratif dump clamp çizilmedi. Clamp çizilene dek BSS84/BSS138 (50 V) ve CSD18540 (60 V) Vds sınırı korunmuş sayılmaz.
4. Küçük sinyal FET'lerin (BSS84, BSS138, 2N7002, AO3400A) üretici veri sayfaları bu oturumda indirilemedi; değerler bilinen katalog sınıfıdır, PH6'da doğrulanacak.
5. J-ESTOP konnektörü, PTC'ler ve TVS'lerin MPN'i; E-stop butonunun iki NC kontak MPN'i.
6. `K2_FLT` donanım latch girişi: FLT UVLO'da da düşer ve shutdown davranışı veri sayfasında tanımsızdır; EN kenarı blanking'i ölçülmeden bağlanmadı.
7. PCB termali: 50 °C/W için her FET 1 in² 2 oz → iki FET 1 290 mm², 120×80 mm kartın %13,4'ü; şönt, K1 ve bağlantılar ayrıca. Yerleşim yapılmadı.
8. PH8 yazılım gereksinimleri: TCA sıfırlama sırası, SELF_TEST watchdog kanıt testi, K2 iletim bleed darbesi, A/B tutarsızlık FAULT'u.
