# UGV-PWR-01 Güvenlik Güç Yolu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** UGV-PWR-01'in kesilebilir aktüatör yolunu ve bağımsız güvenlik iznini, üretime gönderilmeyecek aday KiCad şemasından incelemeye açık tam kart tasarımına taşımak.

**Architecture:** `F1 → K1 → MID → K2 → ACT_BUS`; K2 çevresinde yalnız ARMING'de açık 470 Ω ön şarj. Çift NC E-stop, yerel reset, ray gözetimi ve haricî watchdog donanımda K1/K2 iznini düşürür. MCU yalnız istek üretir; aktüatör izninin sahibi PWR donanımıdır.

**Tech Stack:** KiCad 10, kicad-cli ERC/netlist, Python 3 stdlib; ölçüm kapısında osiloskop/akım probu.

**Spec:** [Güç mimarisi](../../electrical_architecture.md), [PWR↔MCU sözleşmesi](../../pwr_mcu_interface.md), [ön şarj ve tek arıza sırası](../../precharge_and_separator_diagnostics.md), [watchdog](../../watchdog_design.md), [K1](../../k1_relay_selection.md), [K2](../../k2_separator_selection.md).

## Global Constraints

- Batarya 4S, normal zarf 12,4–16,8 V; motor kolu 15 A tasarım taraması ve 20 A geçici hata taraması.
- T01/T13 fiziksel testleri yapılmadan hiçbir KiCad ERC veya netlist sonucu güvenlik onayı değildir.
- K1'in 16,8 V motor yükünde K2-kısa arızasıyla açma kanıtı mevcut değil; footprint üretim seçimi olamaz.
- K2 LM74900QRGERQ1 ve 2×CSD18540Q5BT koşullu aday; `SLEEP=Low,EN=High` güvenli OFF değildir.
- `PWR_ACT_EN` ARMING boyunca Low; geribildirim yalnız ACT_BUS seviyesinden türetilemez.

## Review Focus

- MCU güçsüzken PWR durum hatları 3,3 V rayını geri beslememeli.
- Bir NC kablosu koparken watchdog veya yazılım çıkışı kesmeyi veto edememeli.
- K2 veya ön şarj anahtarı kısa kaldığında K1, boş 4700 µF'e kapanmamalı.
- Test enjeksiyon anahtarı kısa kaldığında NC açılması test akımını kesmeli.
- `ACT_BUS` rejenerasyonu K2 açıldıktan sonra FET/TVS sınırını aşmamalı.

---

### Task 1: K1 parça ve paketleme kapısı

**Files:** `docs/k1_relay_selection.md`, `docs/electronics_packaging_gate.md`, `manufacturing/bom/initial_bom.csv`.

**Interfaces:** K1 bobin rayı ve kontak `F1/MID` bağlantısı, Task 2–4 için giriş; tedarikçi DC motor kesme kanıtı yoksa sonuç açık gate olarak kalır.

- [x] **Step 1:** Mevcut TE T9AS1D17-5 ve Panasonic ACTE3CH2A05V üretici tablolarını 16,8 V DC, K2 kısa, gerçek 4 motor + servo transient yükü ve 50 °C bölme koşuluyla karşılaştır. *(24.09: kanıt yok; K1 açık.)*
- [x] **Step 2:** K1 üst yüzeyi ve mandal/terminal servis hacmini `REF-PWR-PCB` z57–81 ve y−87…−7 tahsisine yerleştir; `2 mm nominal` payı tolerans zinciriyle değerlendir. *(En kötü −0,26 mm, RSS +0,87 mm; kapanmadı, STEP/ölçüm gerekir.)*
- [x] **Step 3:** Veri sayfası motor yükünü doğrulamıyorsa CSV'de K1'i koşullu bırak; üretime aday MPN atama. Gerekirse kart dışı metal bağlantı veya 330×270 mm zarf revizyonunu ayrı seçenek olarak hesapla. *(CSV `SELECTION-OPEN-K1`; şemada boş footprint. Kart dışı/zarf seçenekleri listelendi, sayısal hesap yapılmadı.)*
- [x] **Step 4:** T13 için K2-kısa dummy yükte `I_break`, `V_contact`, bırakma süresi ve kaynaklı kontak tekrar-arm reddi ölçüm satırlarını güncelle; fiziksel sonuç gelene dek gate `NOT_RUN`.

### Task 2: K2, şönt, ön şarj ve bleed KiCad sayfası

**Files:** `electronics/ugv_pwr_01/actuator_path.kicad_sch`, `tests/check_pwr_actuator_path.py`, `docs/k2_separator_selection.md`.

**Interfaces:** `F1_OUT`, `MID`, `ACT_BUS`, `PGND`, `SAFE_GATE`, `PRECHARGE_REQ`, `BLEED_REQ`, `K2_FLT` netleri; Task 3 donanım izni `SAFE_GATE`'i üretir.

- [x] **Step 1:** `tests/check_pwr_actuator_path.py` içinde netlistten iki CSD18540Q5BT, bir LM74900QRGERQ1, MID→470 Ω→anahtarlı ACT_BUS ön şarj yolu ve ayrı Kelvin şönt beklentisi yaz; kaynak devre yokken testi çalıştırıp başarısızlığını gör.
- [x] **Step 2:** KiCad 10 üretici pinleriyle K2 sayfasını çiz; LM74900 `SLEEP` ve `EN` ilişkisini, EN pasif Low bias'ı, `FLT` latch bağlantısını, floating thermal pad'i ve MOSFET gate-source sınır elemanlarını veri sayfası devresiyle birebir incele.
- [x] **Step 3:** K2 güç yolu ile 470 Ω ön şarj bypass'ının ayrı anahtarını ve 150 Ω ACT bleed'i ekle; netlist testini ve `kicad-cli sch erc` kontrolünü çalıştır; yalnız diğer sayfalara uzanan beklenen net uyarılarını belgeli istisna say.
- [ ] **Step 4:** 15/20 A şönt + FET sıcaklık hesabını gerçek bakır alanı, 2 oz dış katman ve via yolu ile güncelle; 50 °C/W katalog değeri sağlanmadıkça sürekli 15 A onayı verme. *(24.09: yalnız alan bütçesi — iki FET 1 290 mm², kartın %13,4'ü; yerleşim yok, AÇIK.)*

### Task 3: Fiziksel NC ve watchdog izin sayfası

**Files:** `electronics/ugv_pwr_01/safety_gate.kicad_sch`, `tests/check_pwr_safety_gate.py`, `docs/watchdog_design.md`.

**Interfaces:** `ESTOP_A_NC`, `ESTOP_B_NC`, `MCU_RUN_REQ`, `MCU_WDI`, `PWR_3V3_OK`, `SAFE_GATE`, `PWR_ACT_EN`, `PWR_WD_OK`.

- [x] **Step 1:** Netlist testiyle her NC'nin bağımsız seri izin yolunda bulunduğunu, `SAFE_GATE`'in MCU isteği yokken Low olduğunu ve `PWR_ACT_EN`'in doğrudan MCU çıkışına bağlı olmadığını reddet/izin ver örnekleriyle tanımla; test önce başarısız olsun.
- [x] **Step 2:** TPS3431 `CWD=100 pF C0G`, `WDO`, `ENOUT` ve ayrı `PGOOD` kaynağını üretici pinlerine göre çiz; tüm gate girişlerini reset/güçsüz durumda pasif bias ile tut.
- [x] **Step 3:** K1 bobini, K2 EN, ön şarj ve test-enjeksiyon ikinci anahtarına donanım izin fan-out'u ekle; bir kısa kalan komut FET'inin NC/WD zincirini bypass edemediğini ayrı ağ olarak doğrula.
- [x] **Step 4:** Netlist ve ERC'den sonra T01/T03/T13'te NC açık, WDI durmuş, PGOOD düşmüş, MCU yok ve test FET'i kısa enjeksiyonlarını fiziksel ölçüm için açık bırak.

### Task 4: Kart birleştirme ve üretim öncesi inceleme

**Files:** `electronics/ugv_pwr_01/ugv_pwr_01.kicad_sch`, `electronics/ugv_pwr_01/ugv_pwr_01.kicad_pcb`, `tests/check_pwr_board.py`, `docs/phase_reviews.md`.

**Interfaces:** Mevcut J-PWR/J-SIG sayfası, Task 2/3 güç ve izin sayfaları, INA228 + regülatör/TVS/sigorta sayfaları.

- [x] **Step 1:** *(24.09: beş kısmi sayfa `ugv_pwr_01.kicad_sch` kökünde birleşti; 12 J-SIG ağı ve güvenlik ağları denetlendi, birleşik ERC 0 hata. `5V_CONTROL`/`PGND` gerçek kaynak sayfaları çizilmediği için PWR_FLAG ile işaretli.)* Kısmi sayfaları tek KiCad proje hiyerarşisinde birleştir; `ACT_BUS`, `5V_CONTROL`, `PGND` ve tüm 12 J-SIG ağlarının yalnız bir tanımlı sürücüsü olmasını netlistte kontrol et.
- [ ] **Step 2:** INA228, 5,1 V/5 V/6 V rayları, TVS, ana sigorta, test noktaları ve servis konnektörlerini tam şematikte kapat; tam kart ERC'de sıfır hata ve gerekçeli uyarı listesi çıkar.
- [ ] **Step 3:** 120×80 mm tahsis içine resmi housing/terminal STEP'i, bakır/ısı alanı, konektör çıkarma süpürmesi ve kart montaj deliklerini koy; sığmıyorsa kart/geçit boyutunu gerekçeli revize et.
- [ ] **Step 4:** PCB DRC, Gerber, drill, BOM, PnP ve assembly çizimini yalnız tam ERC/yerleşim/DFM incelemesi sonrası üret; T01/T02/T13 fiziksel sonuçları gelmedikçe imalat ve sürüş kapısını açık işaretle.
