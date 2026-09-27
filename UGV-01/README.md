# UGV-01

Modüler dört tekerlekten tahrikli skid-steer Ar-Ge aracı · A3 Lite (M3: ≤13.500 TL) / A2 karakter kaydı · 25.09.2026

**Başlangıç:** [Sistem gereksinimleri](docs/system_requirements.md), [sistem mimarisi](docs/system_architecture.md), [karar kaydı](docs/design_decisions.md).

**D1 tahrik adayı:** [Detay mühendislik raporu](docs/drivetrain_detail_D1.md), [modül önizlemesi](cad/drivetrain/module_preview.png), [modül STEP](cad/drivetrain/generated/UGV-01-D1-drivetrain.step), [75 parçalı araç yerleşimi STEP](cad/drivetrain/generated/UGV-01-D1-packaging.step). 10 mm bağımsız mil, iki rulman ve özgün jant/lastik; 300 mm genişlik adayı. Kütle rezervi, nihai toleranslar ve fiziksel testler açık olduğundan aşağıdaki A0 baz çizgisi korunuyor.

**D2A devamı:** [Dayanım/kütle karşılaştırması](docs/drivetrain_trade_D2.md) ile Ø8/608 elendi. Ø10 mil için sertifikalı 42CrMo4+QT malzeme ve [hafifletilmiş jant/lastik STEP+STL](cad/drivetrain/generated/lightweight/) adayı oluşturuldu. Hesaplanan boş kütle5,933 kg, rezerv67 g; üretim ve gerçek6 kg kabulü açık.

**A3 Lite (güncel, animasyon robotlarından ilham alan özgün tasarım):** [3D görüntüleyici](docs/renders/UGV-01-A3-viewer.html), [Lite mekanik](docs/lite_mechanical_A3.md) ve [A2 biçim sınırları](docs/exterior_language_A2.md). **M3 (25.09.2026, DD72–DD75):** gövde 300 × 236 × z210 ve kareye yakın; motorlar bütünüyle gövdenin içinde; tekerleklerin üstünde çamurluk; baş gövdenin 122 mm üstünde (kamera mesafesi korundu). Sağ kol yan duvardan çıkıyor: 5 eksen (omuz DS3218MG 270°, üst kol dönüşü, dirsek, bilek eğimi, bilek dönüşü) + pençe, ≤150 g. 8 duruş ve 7 geçiş CAD'de çakışmasız süpürüldü. Pasif sol kol; ön kapakta atma ağzı ve gövde içinde kargo kutusu. Pan/tilt boyunlu baş ve iki ESP32-CAM göz, ön ışık şeridi, baskı PETG şasi, 4 × enkoderli JGA25 motor (1:78, 7,5 Ω balast).

**Kütle kapısı:** [CAD taraması](docs/lite_mechanical_A3.md) bütün baskı gruplarının tahmini kütlesini (1,2 mm kabuk + %20 dolgu) tahsislerin içinde buldu; filament ≈2,25 kg PETG + 0,28 kg TPU (3 PETG + 1 TPU makara). M3: boş 4,58 kg, yük 0,5 kg, yüklü CG z130,8 mm (sınır 135). Gerçek dilimleme ve tartım henüz yapılmadı.

**Baskı beklerken elektronik çalışma:** [58 pin manifesti](config/mcu_pinmap.json), [PWR↔MCU sözleşmesi](docs/pwr_mcu_interface.md), 16 net [KiCad kablo şematiği](electronics/interconnect/pwr_mcu_harness.kicad_sch), [diferansiyel I²C referansı](electronics/interconnect/differential_i2c_reference.kicad_sch) ve ayrı [MCU](electronics/ugv_mcu_01/pwr_mcu_interface.kicad_sch)/[PWR](electronics/ugv_pwr_01/pwr_mcu_interface.kicad_sch) **kısmi** kart arayüz sayfaları var. MCU'nun [altı kanallı güçsüz durum alıcısı](electronics/ugv_mcu_01/status_receiver.kicad_sch) da kısmi KiCad sayfası olarak çizildi. Kablo ve I²C referansı ERC 0; kart sayfalarının bütün şematiği birleştirilmedi. [K1 röle seçim kapısı](docs/k1_relay_selection.md), [K2 FET/denetleyici aday hesabı](docs/k2_separator_selection.md), [K1/K2 ön şarj ve tekil arıza tanısı](docs/precharge_and_separator_diagnostics.md), [≤100 ms watchdog seçimi](docs/watchdog_design.md) ve [elektronik yerleşim kesiti](docs/electronics_packaging_gate.md) kaydedildi. [Host güvenlik çekirdeği](firmware/stm32/safety_core.c) ve [senaryo testi](tests/safety_core_test.c) başlangıç kodudur. **Tam kart şematikleri/layout/Gerber, STM32 build ve fiziksel doğrulama yok.** [İlerleme kapsamı](docs/design_progress.md).

**Son çalışma — PWR güç/güvenlik yolu (24.09.2026):** `F1→K1→MID→K2→ACT_BUS`, anahtarlı 470 Ω ön şarj, kilitli 150 Ω bleed, iki anahtarlı test enjeksiyonu, enerji taşıyan çift NC E-stop, TPS3431 watchdog, bırakma kenarlı reset latch'i ve `SAFE_GATE` izin zinciri [beş sayfalı kısmi KiCad hiyerarşisinde](electronics/ugv_pwr_01/ugv_pwr_01.kicad_sch) ([PDF](electronics/ugv_pwr_01/ugv_pwr_01.pdf), [inceleme](docs/pwr_safety_path.md)). Birleşik ERC 0 hata; netlist testleri ve 4 096 senaryoluk izin mantığı kontrolü geçiyor. K1 `MPN OPEN`/boş footprint; F1 I²t, şönt MPN, TVS/dump clamp ve PCB termali açık. **Tam kart, PCB, üretim veya sürüş onayı değildir; T01/T13 NOT_RUN.**

**Genel denetim ve A2 yönü (24.09.2026):** [Denetim raporu](docs/design_review_2026-09-24.md) 7 hatayı düzeltti. Onaylanan [A2 spec'i](docs/superpowers/specs/2026-09-24-a2-character-ai-design.md): tekerli gövdeye animasyon robotlarından ilham alan özgün baş (iki kamera göz, pan/tilt), işlevsel sağ kol ve insan denetimli Claude AI kontrolü. A2 mekanik CAD (DD62) ve [A2 elektronik P0](docs/a2_electronics.md) (DD63: MCU kartında servo rayı, INA180 akım ölçümü, ışık şeridi, iki CSI kamera, iki ToF; [KiCad sayfası](electronics/ugv_mcu_01/servo_light.kicad_sch)) tamamlandı; [denetimli AI](docs/ai_control.md) (DD64: AI köprüsü — DD65 ile varsayılan model `deepseek-flash`, internetsiz yürütücü, MCU servo/ışık/CAN, web paneli) mock testlerle hazır, gerçek API ve araç üstü çalıştırma yapılmadı. Baskı ve fiziksel test yok.

**Bütçe revizyonu — A3 Lite (24.09.2026, onaylandı):** Parça bütçesi ≤10.000 TL. Araçta ESP32-S3 + iki ESP32-CAM göz, AI ve panel MacBook'ta, JGA25 motorlar, 3S 18650, baskı şasi; 330×270 mm ve A2 görünümü korunur. AI modeli `deepseek-flash` (DeepSeek V4.1 Flash; görüntü + araç). [Spec](docs/superpowers/specs/2026-09-24-a3-lite-budget-design.md), DD65/DD66. L1 mekanik ve [L2 elektronik](docs/lite_electronics_A3.md) tamam (ESP32-S3 pin haritası 23/23, modül bağlantı şeması ERC temiz, [parça listesi](manufacturing/bom/lite_bom_A3.csv) A3'te 9.987 TL; M3'te 13.478 TL, tavan 13.500 TL); L3 yazılım tamam: [Lite yazılım](docs/lite_software_A3.md) (imzalı UDP, ESP32 çekirdeği, MacBook ağ geçidi; host testleri). L4'ün donanımsız kısmı: ESP32-S3 kart katmanı, ön ToF sürücüsü ve ESP32-CAM göz firmware'i ESP-IDF 5.3.2 ile uyarısız derlenir (DD86–DD88); donanımda çalışmadı. **Bağımsız inceleme (25.09.2026):** [rapor](docs/claude_review_2026-09-25.md) ve [kapanış kaydı](docs/review_closure_2026-09-25.md): R1–R10 yazılım/tasarım düzeltmeleri (DD69); fiziksel testler NOT_RUN.

Bu repository ilk 16 çıktı ile mekanik CAD mimarisini içerir. Çalışır araç, tamamlanmış PCB/STM32 firmware veya üretim release'i değildir. Fiziksel test yapılmadı; doğrulanan masaüstü kontrolleri [faz incelemesinde](docs/phase_reviews.md) listelenir.

## İlk 16 çıktı

| İstenen çıktı | Dosya |
|---|---|
| 1. System Requirements Specification | [SRS](docs/system_requirements.md) |
| 2. Sistem blok diyagramı | [Mimari](docs/system_architecture.md), [Mermaid kaynak](docs/system_block_diagram.mmd) |
| 3. Alt sistem listesi | [Mimari](docs/system_architecture.md) |
| 4. Tahmini boyutlar | [Mekanik mimari](docs/mechanical_architecture.md), [ortak ölçüler](config/vehicle.json) |
| 5. Ağırlık bütçesi | [Kütle/CG](docs/mass_budget.md) |
| 6. Motor/tahrik konsepti | [Tahrik](docs/drivetrain_calculations.md) |
| 7. Motor/teker hesapları | [Hesaplar](docs/drivetrain_calculations.md), [tekrar üretilebilir rapor](docs/calculation_results.md) |
| 8. Elektrik güç bütçesi | [Elektrik mimarisi §6](docs/electrical_architecture.md) |
| 9. İletişim mimarisi | [CAN/arbitraj/protokol](docs/communication_architecture.md) |
| 10. Güvenlik/hata yönetimi | [State machine ve fault matrix](docs/safety_architecture.md) |
| 11. İlk BOM | [BOM açıklaması](docs/initial_bom.md), [36 satır CSV](manufacturing/bom/initial_bom.csv) |
| 12. Geliştirme aşamaları | [PHASE 0–16](docs/development_plan.md) |
| 13. Teknik riskler | [Risk kaydı](docs/risk_register.md) |
| 14. Basılacak parçalar | [PN/proses/DFM tablosu](docs/mechanical_architecture.md) |
| 15. CNC/lazer parçaları | [Metal yük yolu ve parça tablosu](docs/mechanical_architecture.md) |
| 16. Satın alınacak parçalar | [BOM](manufacturing/bom/initial_bom.csv) |

Ekler: [20 test prosedürü](docs/test_plan.md), [yazılım/ROS/web mimarisi](docs/software_architecture.md), [elektronik kaynaklar](docs/electrical_sources.md), [motor kaynakları](docs/drivetrain_sources.md).

## A0 kararları

- Dış ölçü330×270mm; ana gövde üstü146mm. Başlangıç140mm'den6mm sapma batarya/kapak montaj boşluğu için kayıtlıdır.
- 6kg boş,2kg yük,8kg toplam hedef; kütle/CG henüz ölçülmedi.
- Dört Pololu4754,70:1,12V koşullu aday; Ø120mm teker;0,8m/s düz ve0,6m/s eğim sınırı.15° sert zeminde tork/ısıl test şart.
- 4S2P P45B,14,4V/9Ah/129,6Wh; ham motor barasında efektif gerilim ve bağımsız akım limiti.
- STM32G474VET6 + CM5;500kbit/s CAN. Fiziksel STOP motor/servo enerjisini keser; eğimde tutma freni değildir.
- A2 V1 yaklaşık 2.082 USD ön bütçe (A2 kameralar, servolar, ışık şeridi ve ToF dahil). **A3 Lite hedefi ≤10.000 TL; M3'te kullanıcı izniyle ≤13.500 TL**; güncel [parça listesi](manufacturing/bom/lite_bom_A3.csv) 13.478 TL, tavana 22 TL pay (filament dahil, fiyatların çoğu tahmin); [spec](docs/superpowers/specs/2026-09-24-a3-lite-budget-design.md) onaylandı. Vergi/kargo/işçilik/laboratuvar ve gelecek sensörler hariç. Açık MPN'ler siparişe hazır değildir.

## CAD çıktıları

[Montaj ve iç yerleşim önizlemesi](cad/assembly/concept_preview.png)

[A3 kavram montaj STEP](cad/assembly/generated/UGV-01-A3-concept.step) (kol park duruşunda; duruşlar ve geçişler manifest'te), [manifest](cad/assembly/manifest.json), [parametrik üretici](cad/assembly/build_concept.py), [geometri URDF](simulation/ugv_geometry.urdf). [A2](docs/revisions/A2/UGV-01-A2-concept.step), [A1](docs/revisions/A1/UGV-01-A1-concept.step) ve [A0 STEP](cad/assembly/generated/UGV-01-A0-concept.step) arşiv olarak korunur.

96 güncel A3 STEP parçası/yerleşim zarfı, 67 baskı parçasının STL'si ve alt plaka kavram DXF'i `cad/assembly/generated` içindedir. `REF-` parçaları gerçek komponent detayları değil tahsis zarflarıdır (motor, servo, rulman, göz kamerası, batarya, elektronik, E-stop, ToF, ışık şeridi). Vida/insert yerleri, göbek set vidası, kablo yolları, batarya tutucu ve elektronik tepsisi bağlantısı açık ([Lite mekanik](docs/lite_mechanical_A3.md)). Çakışmasızlık üretim veya montaj onayı değildir.

## Yeniden üretme ve kontrol

Python3.12/3.13 ve CadQuery2.6.1 ile kontrol edildi. Geometri üretimi ilk çalıştırmada birkaç dakika sürebilir. Ayrı bir sanal ortam kullanılır.

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-cad.txt
python3 tools/calculations.py
python3 tests/check_design.py
.venv/bin/python cad/assembly/build_concept.py
.venv/bin/python tools/print_plan.py
.venv/bin/python tests/check_cad.py
.venv/bin/python tests/check_print_plan.py
.venv/bin/python tests/check_body_mass.py
```

`tools/print_plan.py`, baskı parçalarının STL'lerini baskı yönünde yazar ve [baskı rehberini](docs/print_guide_A3.md) üretir (M3: 67 baskı parçası; bekleyen yok).

İlk iki kurulum komutu yalnız ortam yoksa gerekir. `config/vehicle.json` değişince hesap ve CAD yeniden üretilir. URDF yalnız geometri ön modelidir; inertial/collision, Xacro ve ROS paket derlemesi PH9 kapsamındadır. KiCad kaynak/Gerber ve final STL/STEP/DXF release alanları sonraki fazlar için ayrıdır.

STEP kaynaklı PNG önizlemeyi de yeniden üretmek için aynı ortama `matplotlib` kurup `.venv/bin/python tools/render_concept.py` çalıştırın. Bu yalnız görselleştirme bağımlılığıdır; CAD katılarının kaynağı değildir.
