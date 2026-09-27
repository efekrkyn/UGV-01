# UGV-01

Modüler dört tekerlekten tahrikli skid-steer Ar-Ge aracı · A0 ön mühendislik teslimi · 22.09.2026

**Başlangıç:** [Sistem gereksinimleri](../../../docs/system_requirements.md), [sistem mimarisi](../../../docs/system_architecture.md), [karar kaydı](../../../docs/design_decisions.md).

Bu repository ilk 16 çıktı ile mekanik CAD mimarisini içerir. Çalışır araç, tamamlanmış PCB/firmware veya üretim release'i değildir. Fiziksel test yapılmadı; doğrulanan masaüstü kontrolleri [faz incelemesinde](../../../docs/phase_reviews.md) listelenir.

## İlk 16 çıktı

| İstenen çıktı | Dosya |
|---|---|
| 1. System Requirements Specification | [SRS](../../../docs/system_requirements.md) |
| 2. Sistem blok diyagramı | [Mimari](../../../docs/system_architecture.md), [Mermaid kaynak](../../../docs/system_block_diagram.mmd) |
| 3. Alt sistem listesi | [Mimari](../../../docs/system_architecture.md) |
| 4. Tahmini boyutlar | [Mekanik mimari](../../../docs/mechanical_architecture.md), [ortak ölçüler](vehicle.json) |
| 5. Ağırlık bütçesi | [Kütle/CG](../../../docs/mass_budget.md) |
| 6. Motor/tahrik konsepti | [Tahrik](../../../docs/drivetrain_calculations.md) |
| 7. Motor/teker hesapları | [Hesaplar](../../../docs/drivetrain_calculations.md), [tekrar üretilebilir rapor](../../../docs/calculation_results.md) |
| 8. Elektrik güç bütçesi | [Elektrik mimarisi §6](../../../docs/electrical_architecture.md) |
| 9. İletişim mimarisi | [CAN/arbitraj/protokol](../../../docs/communication_architecture.md) |
| 10. Güvenlik/hata yönetimi | [State machine ve fault matrix](../../../docs/safety_architecture.md) |
| 11. İlk BOM | [BOM açıklaması](../../../docs/initial_bom.md), [29 satır CSV](../../../manufacturing/bom/initial_bom.csv) |
| 12. Geliştirme aşamaları | [PHASE 0–16](../../../docs/development_plan.md) |
| 13. Teknik riskler | [Risk kaydı](../../../docs/risk_register.md) |
| 14. Basılacak parçalar | [PN/proses/DFM tablosu](../../../docs/mechanical_architecture.md) |
| 15. CNC/lazer parçaları | [Metal yük yolu ve parça tablosu](../../../docs/mechanical_architecture.md) |
| 16. Satın alınacak parçalar | [BOM](../../../manufacturing/bom/initial_bom.csv) |

Ekler: [20 test prosedürü](../../../docs/test_plan.md), [yazılım/ROS/web mimarisi](../../../docs/software_architecture.md), [elektronik kaynaklar](../../../docs/electrical_sources.md), [motor kaynakları](../../../docs/drivetrain_sources.md).

## A0 kararları

- Dış ölçü330×270mm; ana gövde üstü146mm. Başlangıç140mm'den6mm sapma batarya/kapak montaj boşluğu için kayıtlıdır.
- 6kg boş,2kg yük,8kg toplam hedef; kütle/CG henüz ölçülmedi.
- Dört Pololu4754,70:1,12V koşullu aday; Ø120mm teker;0,8m/s düz ve0,6m/s eğim sınırı.15° sert zeminde tork/ısıl test şart.
- 4S2P P45B,14,4V/9Ah/129,6Wh; ham motor barasında efektif gerilim ve bağımsız akım limiti.
- STM32G474VET6 + CM5;500kbit/s CAN. Fiziksel STOP motor/servo enerjisini keser; eğimde tutma freni değildir.
- V1 yaklaşık2.049USD ön bütçe; vergi/kargo/işçilik/laboratuvar ve gelecek sensörler hariç. Açık MPN'ler siparişe hazır değildir.

## CAD çıktıları

[Montaj ve iç yerleşim önizlemesi](../../../cad/assembly/concept_preview.png)

[Kavram montaj STEP](../../../cad/assembly/generated/UGV-01-A0-concept.step), [manifest](cad_manifest.json), [parametrik üretici](../../../cad/assembly/build_concept.py), [geometri URDF](../../../simulation/ugv_geometry.urdf).

31 STEP parçası/yerleşim zarfı, basılı panel/kapak/tampon STL'leri ve alt plaka kavram DXF'i `cad/assembly/generated` içindedir. `REF-` parçaları gerçek komponent detayları değil tahsis zarflarıdır. Motor yatakları, kaplin, gerçek konnektör/kablo servis hacimleri, batarya/compute raf mesnetleri, E-stop/klemp direnci yerleşimi ve kule yük yolu henüz detaylandırılmadı. Dolayısıyla modelin çakışmasız olması aracı monte edilebilir veya üretilebilir ilan etmez. PH4 öncesi bu dosyaları üretime göndermeyin.

## Yeniden üretme ve kontrol

Python3.12 ve CadQuery2.6.1 kullanıldı. Geometri üretimi ilk çalıştırmada birkaç dakika sürebilir. Mevcut ortam `.venv` içindedir.

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-cad.txt
python3 tools/calculations.py
python3 tests/check_design.py
.venv/bin/python cad/assembly/build_concept.py
.venv/bin/python tests/check_cad.py
```

İlk iki kurulum komutu yalnız ortam yoksa gerekir. `config/vehicle.json` değişince hesap ve CAD yeniden üretilir. URDF yalnız geometri ön modelidir; inertial/collision, Xacro ve ROS paket derlemesi PH9 kapsamındadır. KiCad kaynak/Gerber ve final STL/STEP/DXF release alanları sonraki fazlar için ayrıdır.
