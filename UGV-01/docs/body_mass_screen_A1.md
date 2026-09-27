# A1 gövde kütlesi — CAD katı üst sınır taraması

24.09.2026 · PH4 açık. [Tekrar üretilebilir hesap](../tools/body_mass_screen.py), güncel [A1 manifestindeki](../cad/assembly/manifest.json) 6 yan panel, 3 kapak, 2 son duvar ve 2 tampon STEP hacmini okur. ASA için [Bambu Lab ürün verisindeki](https://us.store.bambulab.com/products/asa-filament) **1,05 g/cm³** kullanılır. TPU için kesin filament seçilmediğinden **1,25 g/cm³ ön varsayımı** alınır; gerçek TDS/slicer ve baskı tartımı bunu değiştirebilir. Bütün geometriler **%100 dolu katı** kabul edilmiştir; bu baskı kütlesi iddiası değildir.

| Grup | CAD katı hacmi | Yoğunluk | Katı eşdeğer kütle |
|---|---:|---:|---:|
| ASA panel, kapak ve son duvar | 499,832 cm³ | 1,05 g/cm³ | 524,823 g |
| TPU ön/arka tampon | 171,000 cm³ | 1,25 g/cm³ varsayımı | 213,750 g |
| **A1 gövde toplamı** | | | **738,573 g** |
| `vehicle.json` gövde tahsisi | | | **700,000 g** |
| **Katı eşdeğer aşım** | | | **38,573 g** |

Bu 38,6 g, [D2A](drivetrain_trade_D2.md) için raporlanan 5,933 kg hesabında **0,700 kg gövde tahsisi** kullanıldığı varsayımıyla boş kütleyi yaklaşık **5,971 kg**'a, 6 kg sınırındaki kâğıt payını **28,6 g**'a indirir. Bu bir ölçüm veya birleşik A1+D2A montajı değildir. İnsert, vida, kamera podu, kablo grometi, boya/kaplama ve baskı destek fireleri katı gövde hesabında yoktur. 0,25 kg doğrulanmış montaj marjı hedefi için yaklaşık **221,4 g** ek güvenli tasarruf veya gerekçeli kütle hedefi revizyonu gerekir; 0,30 kg marj için gereksinim **271,4 g** olur.

**Tasarım kararı:** Tam dolu hacimden otomatik olarak ince duvar/oyuk çizilmeyecek. Slicer'da gerçek duvar sayısı, üst/alt katman ve infill ile kütle çıkarılır; tamponun darbe enerjisi, 40 °C sünme ve bağlantı yükü ile birlikte değerlendirilir. TPU-only azaltımla 38,6 g açığı kapatmak için yaklaşık **30,9 cm³** toplam malzeme veya her tamponun mevcut 85,5 cm³ katı hacminin **%18,1**'i kadar hacim azaltmak gerekir; bu oran güç/enerji emme testi olmadan imalat talimatı değildir. Baskı ve parça tartımı henüz **NOT_RUN**.
