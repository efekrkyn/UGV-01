# UGV-01 geliştirme planı

Rev A0 · Goal: Hesaplanmış ve fiziksel olarak doğrulanmış modüler bir UGV.
Architecture: CM5 + bağımsız STM32 kontrol; metal yük yolu, basılı servis modülleri, ayrı güç kartı.
Tech Stack: Parametrik CAD, KiCad, C/C++, Ubuntu 24.04 arm64, ROS 2 Jazzy, yerel web.
Spec: system_requirements.md

Writing-plans becerisiyle iş paketlerine ayrıldı. Kullanıcının «önce 16 çıktı, sonra mekanik CAD mimarisi» talimatı çalışma sırasıdır. Donanım gerektiren fazlar doküman yazılarak tamamlanmış sayılmaz. Üretim veya satın alma siparişi verilmez.

| PHASE | Çıktılar | Çıkış kapısı |
|---|---|---|
| 0 Requirements | SRS, kütle bütçesi, varsayımlar ve riskler | Kimlikli gereksinimler ve 16 çıktı kapsam eşlemesi |
| 1 System Architecture | Blok diyagram, güç/CAN/güvenlik, alt sistemler | Enerji/sinyal arayüzleri ve sorumluluklar tutarlı |
| 2 Concept CAD | Ortak JSON, modüler parametrik CAD, montaj datumları | Zarf, baskı hacmi, çakışma ve servis ön incelemesi |
| 3 Motor and Drivetrain Calculations | Ön hesap raporu + tek motor yük testi | Hız/tork/akım/ısı ölçülür; motor seçimi kesinleştirilir |
| 4 Mechanical CAD | Her PN için STEP/STL/DXF/teknik resim | Tolerans, rulman/mil, kupon, FEA ve montaj doğrulaması |
| 5 UGV-MCU-01 Schematic | KiCad şematik, pinmap, ERC, test noktaları | Encoder/PWM/ADC/CAN ve reset güvenliği incelemesi |
| 6 UGV-PWR-01 Schematic | Koruma, regülatör, kesici, klemp şemaları | Sigorta I²t, kablo, DC kesme kapasitesi, regen doğrulaması |
| 7 PCB Layout | PCB, stackup, Gerber, drill, BOM, PnP, assembly drawing | ERC/DRC, üretici toleransları, termal/EMI ve bağımsız release incelemesi |
| 8 Firmware Skeleton | Derlenen startup, state machine, sürücüler, HIL testleri | T03–T09; başlangıç PWM pasif ve watchdog çalışır |
| 9 ROS 2 Simulation | URDF/Xacro, TF, odometri, simüle CAN/fault enjeksiyonu | CAD ölçüleri, aks yönleri, birimler ve çarpışma kontrolü |
| 10 3D Printed Prototype | Kupon, baskı ve montaj ölçüm kayıtları | Insert pullout, servis erişimi, malzeme ve baskı yönü |
| 11 Electronics Integration | T01–T09 ölçüm kayıtları | Akım sınırlı kaynakla tek motor; STOP geçmeden zemin testi yok |
| 12 Manual Driving | Deadman, gamepad ve T10/T13/T14/T16 | 0,2 m/s'den başlayarak kontrollü hız artırma |
| 13 Camera and Telemetry | Kamera, log, CPU yükü, batarya raporu | Görüntü yükü ve dolu disk güvenlik döngüsünü engellemez |
| 14 LiDAR + SLAM | T19 harita/trajectory ve kalibrasyon | LiDAR güç/kütle bütçesi güncel; localization ölçülür |
| 15 Autonomous Navigation | T20 goal/cancel/engel/sensör kaybı | Geofence, hız limiti, gözlemci ve tüm stop testleri |
| 16 AI Perception | V2 algılama, V5 görev planlama modülleri | Offline ölçüm → gözetimli saha; AI hareket güvenliğini yönetmez |

PHASE 3 ön hesabı, kullanıcı talebiyle CAD'den önce yapılır; fazın fiziksel yük/ısıl doğrulaması daha sonra kapanır. V2–V5 ürün yetenekleridir, PHASE numaraları iş paketidir. Algılama offline araştırması donanım fazlarıyla paralel yürüyebilir.

Her faz sonunda beş kontrol: teknik tutarlılık; üretilebilirlik; montaj/alet erişimi; ölçülebilir test; servis edilebilirlik. Sonuçlar phase_reviews.md içinde AÇIK, KOŞULLU veya GEÇTİ olarak kaydedilir. Analizden geçen bir maddeye deneyden geçti yazılmaz.

## Bu teslimin uygulama sırası

- [x] SRS, varsayımlar, alt sistemler ve tasarım kararları.
- [x] Motor, CM5, MCU, hücre kaynakları ve mühendislik ön hesapları.
- [x] Güç, CAN, güvenlik, ilk BOM, üretim ayrımı, test ve faz planı.
- [x] Sayısal hesap aracı: önce bilinen fiziksel sonuçlara karşı küçük regresyon kontrolü, sonra standart Python uygulaması.
- [x] Aynı JSON'dan kavram STEP ve geometri modelini üret; CAD ölçü ve baskı zarflarını kontrol et.
- [x] Tahrik/mekanik bağımsız ön inceleme ve bulguların düzeltilmesi; son CAD kontrolleri yerel yapıldı.

Kod kontrolü: `python3 tests/check_design.py`. CAD kontrolü ve yeniden üretme komutları ana README içindedir. Fiziksel donanım testleri bu teslimde yapılmadı.

23.09.2026 çalışma sırası: baskı bir süre mümkün olmadığı için PH4'ün kupon/montaj kapısı açık tutulur. Paralel masaüstü iş olarak PH5 pin kaynak incelemesi, PWR↔MCU bağlantı sözleşmesi, J-PWR KiCad ayak izi kontrolü ve pasif PWR↔MCU kablo şematiği hazırlandı. Sonraki somut adım **kartların** gerçek KiCad şematik/ERC'si ve güçsüz giriş geri besleme incelemesidir; kablo çiziminin ERC'si bu kapıyı kapatmaz. Faz numarası atlanarak üretim release verilmez. [Tasarım ilerleme kestirimi](design_progress.md) fiziksel testleri içermez.
