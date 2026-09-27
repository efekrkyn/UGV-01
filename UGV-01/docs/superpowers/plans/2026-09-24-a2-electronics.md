# A2 elektrik/elektronik (alt proje 3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A2 baş/kol/ışık/kamera/ToF donanımının MCU pinlerini, MCU kartı kısmi KiCad sayfasını, güç bütçesini ve BOM'unu netlist/ERC/pin testleriyle doğrulanmış biçimde tamamlamak.

**Architecture:** 6 V/4 A servo buck'ı **MCU kartında**, J-PWR üzerinden gelen E-stop'la kesilen `ACT_BUS`'tan beslenir; J-SIG değişmez. Servo rayı, PWR izni (`ACT_PERMIT_BUF`) ve MCU isteği (`SERVO_PWR_REQ`) ile AND kapısından açılır. Ray akımını INA180A2 ölçer (ADC2). Işık şeridi verisi 3,3 V SPI2_MOSI → 74AHCT1G125 → 5 V; şerit beslemesi PTC ile 5V_CONTROL'den ayrılır. Kameralar ve ToF, CM5 IO kartına doğrudan bağlanır (özel KiCad yok). Buck regülatörün kendisi alt proje 5'tedir; sayfada `SERVO_6V_BUCK`/`SERVO_BUCK_EN` etiketleriyle arayüzlenir.

**Tech Stack:** KiCad 10 `kicad-cli`, mevcut `tools/pwr_sheet.py` sayfa yazıcısı, Python 3 testleri.

**Commit:** Kullanıcı git'i proje sonuna bıraktı; commit yok.

**Durum (24.09.2026):** Tamamlandı ([DD63](../../design_decisions.md)). Sapma: B20 ve C10–C13 zaten kullanıldığından yeni BOM kimlikleri **B21–B26** ve **C14–C17**; ayrıca B25 kamera kabloları ve B26 servo buck eklendi. Uygulama sırasında gevşek kol kapak dayanağı (DD62 eki) eklendi.

---

### Task 1: MCU pinleri

**Files:** Modify `config/mcu_pinmap.json`, `tools/check_mcu_pinmap.py`, `tests/check_mcu_pinmap_integration.py`

- [x] Test önce: gerekli sinyaller `SERVO_PAN/TILT/SHOULDER/GRIPPER`, `LIGHT_DATA`, `SERVO_I_SENSE`, `SERVO_PWR_REQ`; PB8 (BOOT0) yasak; servo zamanlayıcıları (TIM15/17/20) servo dışı sinyalle paylaşılmaz (50 Hz tek frekans). Çalıştır → FAIL.
- [x] Ata: `SERVO_SHOULDER` PB9/96 TIM17_CH1, `SERVO_GRIPPER` PE3/2 TIM20_CH2, `LIGHT_DATA` PB15/54 SPI2_MOSI, `SERVO_I_SENSE` PC4/30 ADC2_IN5 (motor akımları ADC1'de), `SERVO_PWR_REQ` PE8/39 GPIO. Validator'a `FORBIDDEN={"PB8": "BOOT0"}` ve servo sinyallerini ekle. → PASS.

### Task 2: MCU kısmi sayfası `servo_light`

**Files:** Modify `tools/pwr_sheet.py` (Page'e `board`/`board_dir`/`globals_` varsayılanlı parametre; PWR çıktısı bayt bayt aynı kalır). Create `tools/build_mcu_servo_light.py`, `electronics/ugv_mcu_01/servo_light.kicad_sch`, `tests/check_mcu_servo_light.py`.

- [x] Test önce (sayfa yok → FAIL): netlist'te
  - U701 74LVC1G08: A=`SERVO_PWR_REQ`, B=`ACT_PERMIT_BUF`, Y=`SERVO_BUCK_EN`, VCC=`MCU_3V3`; R701 10k `SERVO_PWR_REQ`→PGND; R702 100k `SERVO_BUCK_EN`→PGND.
  - R703 10 mΩ `SERVO_6V_BUCK`→`SERVO_6V`; U702 INA180A2 IN+=`SERVO_6V_BUCK`, IN−=`SERVO_6V`, VS=`MCU_3V3`, OUT→R704 1k→`SERVO_I_SENSE`, C701 10 nF; tam ölçek 3,3 V/(50×0,01) = 6,6 A ≥ 1,5×4 A.
  - J701–J704 servo başlıkları: pin1 sinyal (R705–R708 1 kΩ seri, MCU tarafı `SERVO_*`), pin2 `SERVO_6V`, pin3 PGND; C702 470 µF `SERVO_6V`.
  - F701 PTC 0,2 A `5V_CONTROL`→`LIGHT_5V`; U703 74AHCT1G125 VCC=`LIGHT_5V`, OE=PGND, A=`LIGHT_DATA` (R709 100k pulldown), Y→R710 33 Ω→`LIGHT_DIN`; J705 1: `LIGHT_5V`, 2: `LIGHT_DIN`, 3: PGND; C703 100 µF, C704/C705 100 nF.
  - ERC: yalnız sayfa dışı sürülen giriş/ray uyarıları (beklenen liste testte sabit), 0 hata dışı ihlal yok.
- [x] `build_mcu_servo_light.py` yaz, sayfayı ve PDF'i üret → PASS.

### Task 3: Güç bütçesi

**Files:** Modify `config/vehicle.json` (`battery.duty_power_typical_w`, `duty_power_heavy_w`), `tools/calculations.py`, `tests/check_design.py`, `docs/electrical_architecture.md`.

- [x] Satırlar: servo 3/8 W (A2 dört servo), kamera satırı iki CSI (beklenen ≈0,6 W; 2 W tahsis korunur), yeni "ışık şeridi (≤0,5 W tavan) + 2 ToF" 0,6/0,6 W. Tipik `33.6+0.686+(15+3+1+2+2+3+0.6)/.9 ≈ 63.84 W`, ağır `62.4+2.366+(25.5+3+1+2+2+8+0.6)/.9 ≈ 111.54 W`; aynı ≈%2 pay ile görev bütçesi **65,0 / 113,8 W**. Çalışma süresi anahtarları `runtime_typical_h`/`runtime_heavy_h`; güçler config'ten.
- [x] `python3 tools/calculations.py && python3 tests/check_design.py` → PASS.

### Task 4: BOM ve belgeler

- [x] BOM: B14 → 2× Camera Module 3 Standard + 2 kamera kablosu; B15 → 3× MG90S; yeni B20 DS3218MG, B21 pan rulmanı 6804 (20×32×7), B22 8 LED ışık şeridi, B23 2× VL53L1X modülü; C10–C13 (INA180A2, 74LVC1G08, 74AHCT1G125, 10 mΩ şönt) B09 içinde. V1 toplamı yeniden hesaplanıp README'ye.
- [x] `docs/a2_electronics.md`: blok şema, pin tablosu, servo rayı/E-stop davranışı (dijital servo PWM kesilince pozisyon tutabilir → gevşetme ray kesmeyle), kamera CAM0/CAM1 ve FFC, ToF XSHUT ile adres ataması, ışık şeridi, açık işler.
- [x] `electrical_architecture.md` §9 servo satırları, `mcu_pinmap_review.md`, MCU/compute README, risk (R48 ray kesiminde kol düşmesi, R49 3,3 V servo sinyal seviyesi), DD63, faz kaydı, `tests/README.md`.
- [x] Tüm testler → PASS; plan kutuları işaretlenir.
