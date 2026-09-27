# UGV-01 genel tasarım denetimi — 24.09.2026

[A2 spec'i](superpowers/specs/2026-09-24-a2-character-ai-design.md) alt proje 1, [plan](superpowers/plans/2026-09-24-design-review.md). Kapsam: config ↔ belge ↔ hesap ↔ KiCad ↔ BOM ↔ firmware sayısal tutarlılığı, eskimiş ifade, kırık Markdown bağlantısı ve test/hesap yeniden üretimi. **Fiziksel doğrulama değildir**; T01–T20 NOT_RUN.

## Taban

- `tools/calculations.py` yeniden çalıştırıldı; `calculation_results.md/json` bayt bayt aynı (config ile tutarlı).
- 15 Python kontrolü + 2 C testi başta ve sonda geçti; yeni [bağlantı denetleyicisi](../tests/check_markdown_links.py) eklendi.
- Tutarlı bulunanlar: araç ölçüleri (`config/vehicle.json` ↔ README/mimari), kütle zinciri (5,933 kg, 67 g, 738,6 g → 5,971 kg), A0 yüklü CG 108,03 mm yeniden üretildi, BOM (36 satır, V1 1999 USD, ×1,3 ≈ 2599), 53 benzersiz MCU pini, J-SIG 12/12 satır JSON ile aynı, DRV8874 2,915 A akım sınırı hesabı, firmware zaman sabitleri (E-stop bırakma 500 ms, SELF_TEST 5 s, ARMING 15 s, komut tazeliği 100 ms, DRIVING→ARMED 200 ms).

## Bulgular

| ID | Kaynak | Hata | Düzeltme | Kanıt | Durum |
|---|---|---|---|---|---|
| R01 | docs/revisions/A0/README_snapshot.md | Arşive taşınan A0 README'sindeki 33 göreli bağlantı yeni konumdan çözülmüyordu | `../../../` öneki; `vehicle.json` ve `cad_manifest.json` yanındaki A0 kopyalarına | `tests/check_markdown_links.py` PASS | DÜZELTİLDİ |
| R02 | docs/k2_reference_schematic.md:19 | Motor sürücüsü `DRV8876` yazılmış; tüm diğer belgeler ve BOM C02 `DRV8874PWPR` | `DRV8874`; 2,915 A hesabı DRV8874 450 µA/A kazancıyla doğrulandı | `grep DRV88`, hesap tekrarı | DÜZELTİLDİ |
| R03 | docs/superpowers/specs/2026-09-24-a2-character-ai-design.md | A2 başı ≈225 g yeni kütle sayılmıştı; oysa 6 kg bütçede 0,30 kg "RGB kamera + gelecek kule" tahsisi zaten var ve D1/D2A kütlesi bunu içerir | Boş ≈6,13–6,16 kg, yük ≈1,85 kg (≈1,5 değil), yüklü CG ≈107–108 mm | `config/vehicle.json` mass_budget ile yeniden hesap; `tools/drivetrain_budget.py` "other A0 allowances unchanged" | DÜZELTİLDİ (spec) |
| R04 | docs/electrical_architecture.md:113 | Tipik batarya gücü `≈62.07 W`; formül 62,064 W veriyor | `≈62.06 W` | Python tekrar hesabı | DÜZELTİLDİ |
| R05 | docs/precharge_and_separator_diagnostics.md:31 | ADC/karşılaştırıcı ve test/ön şarj/bleed sürücüsünün "henüz kesinleşmedi" denmesi 24.09 PWR sayfalarıyla çelişiyordu | P0 aday olarak çizildiği, MPN/analog bütçe/ölçümün açık olduğu yazıldı | [pwr_safety_path.md](pwr_safety_path.md) | DÜZELTİLDİ |
| R06 | docs/risk_register.md | PWR çalışmasında bulunan kalıntı riskler kayıtta yoktu | R42 `SET1` gizli arızası, R43 hızlı MCU reseti + eski TCA çıkışı, R44 NC kanal kısası, R45 çizilmemiş ACT clamp/TVS | Risk tablosu | DÜZELTİLDİ |
| R07 | firmware/stm32/safety_core.c | IDLE→ARMING, ARM kenarında `neutral` anlık doğruysa kabul ediliyordu; [güvenlik mimarisi](safety_architecture.md) 500 ms nötr, [iletişim](communication_architecture.md) en az 500 ms taze trafik istiyor | IDLE'da 500 ms kesintisiz nötr zamanlayıcısı; her durum geçişinde sıfırlanır | Yeni senaryo önce başarısız, sonra [safety_core_test.c](../tests/safety_core_test.c) PASS; CAN testi PASS | DÜZELTİLDİ (DD60) |

Araç notu: bağlantı denetleyicisi ilk sürümde kod bloklarındaki örnek bağlantıları kırık sayıyordu; öz-sınamaya eklenip çit içi satırlar atlandı.

## A2'de değişecek, düzeltilmedi

| Konum | Mevcut durum | A2 karşılığı |
|---|---|---|
| docs/front_camera_A1.md, R40, `config/vehicle.json` `front_camera_opening_center_z_mm` | A1 ön kamera podu, x payı 3,25 mm | Ön pod kalkar; görüş iki göz kamerasında |
| docs/exterior_language_A1.md, DD49 | Çift göz/kule sonraki revizyona ertelenmiş | Boyunlu pan/tilt baş A2'de |
| docs/mass_budget.md satır "RGB kamera + gelecek kule" | 0,30 kg tahsis | Baş ≈225 g bu tahsise; kollar ≈0,235 kg ek |
| manufacturing/bom/initial_bom.csv B14, B15 | Tek kamera; 2 servo FUTURE | 2 CSI kamera; 4 servo V1 |
| docs/electrical_architecture.md §6 "RGB kamera", "Servo, gelecek pan/tilt rezervi" | 2 W UVC; servo 2/3 W | ≈0,6 W iki CSI; servo 3/8 W |
| docs/software_architecture.md `ugv_camera` | "Önce UVC" | İki CSI, `ai_bridge`/`skill_executor` |
| README.md A1 paragrafı | Tek ön kamera | A2 tanıtımı |

## Sonuç

7 tasarım/belge hatası düzeltildi, 7 konum A2'ye devredildi, açık karar gerektiren yeni bulgu yok. Tüm testler yeşil. Denetim üretim, baskı veya sürüş onayı vermez.
