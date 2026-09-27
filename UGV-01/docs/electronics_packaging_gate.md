# Elektronik kat yerleşimi — nominal kesit ve servis kapısı

23.09.2026 · PH4/7. Kaynak [A0 ölçüleri](../config/vehicle.json) ve [kavram CAD](../cad/assembly/build_concept.py). `REF-PWR-PCB` ve `REF-MCU-PCB` **kart + üzerindeki bileşenlere ayrılan 24 mm hacimlerdir**; kutunun z=81 mm üst yüzü çıplak PCB yüzeyi değildir. Bir önceki incelemede z=81 ile CM5 altı z=86 arasındaki 5 mm, yanlışlıkla çıplak PCB üstü açıklığı olarak yorumlanmıştı. Bu belgenin hesabı yalnız **z yönünde nominal uygunluğu** gösterir; yatay takma, kablo, vida ve fiziksel tolerans onayı değildir.

| Arayüz | z aralığı (mm) | Kaynak/varsayım |
|---|---:|---|
| Alt metal plaka üstü | 39 | 36 mm alt + 3 mm plaka |
| Kısa metal ray üstü | 54 | plaka üstü + 15 mm |
| PWR/MCU ayrılan hacim | 57–81 | CAD REF z=69 ±12 |
| **Önerilen çıplak PCB alt/üstü** | **57–58,6** | 1,6 mm stackup varsayımı; stand-off ve kart mesnetleri **henüz çizilmedi** |
| [Molex 76825-0004](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/768/76825/768250004_sd.pdf) takılı üst sınır | 75,38 | 58,6 + 16,78 mm; 5,62 mm ayrılan hacim payı |
| [TE T9AS1D17-5](https://www.te.com/en/product-1-2071229-4.html) gövde üstü, yalnız aday | 79,0 | 58,6 + 20,4 mm; 2,0 mm ayrılan hacim payı |
| CM5 IO ayrılan hacim altı | 86 | 103,5 − 35/2 |
| CM5 IO ayrılan hacim üstü | 121 | 103,5 + 35/2 |
| Kapak altı | 143 | 146 − 3 |

Bu hesap `PCB altı=57` ve üretici yüksekliklerinin **PCB üst yüzünden** ölçüldüğü varsayımına bağlıdır. K1 için 2 mm pay imalat, standoff, kablo veya titreşim payı olarak onaylanmaz. Mega-Fit üretici çizimi 16,78 mm takılı yüksekliği, 28,80 mm takılı uzunluğu ve 4–12 pin için PCB kenarından `20,6 mm max` yerleştirme koşulunu verir. KiCad courtyard yalnız lehim/komponent çakışması için; mating housing, AWG12 kablo bükümü, mandal ve krimp çıkarma süpürmesi içermez.

**Yatay yerleşim hâlâ açık/P0.** A0 PWR tahsisi y=−87…−7, MCU tahsisi y=7…92: iki iç kenar arasında yalnız **14 mm** nominal koridor vardır. Bu, 28,8 mm takılı uzunluğu ve kablo çıkışını iki karşılıklı kart kenarında otomatik olarak barındırmaz. Dış kenarlarda ise gövdenin y=±100 mm sınırına PWR'de 13 mm, MCU'da 8 mm kalır. Dolayısıyla gerçek connector/housing 3B modelleriyle kart üzeri yön, latch parmak/alet erişimi, her kablonun minimum büküm yarıçapı ve kartı yerinden çıkarmadan unplug yolu çizilmeden “sığıyor” denmez. Kablonun 0,4 m olması yerel büküm hacmini azaltmaz.

PH4/7 çıkış kontrolü: (1) kart kalınlığı ve standoff ölçüsünü CAD'e bağla; (2) resmi header + mating housing STEP'lerini ayrı solidler olarak yerleştir; (3) dört AWG12/16 damar için üretici tel dış çapı ve izinli minimum büküm ile gerçek demet süpürmesi çiz; (4) K1 ve dump direnci ısıl boşluğunu yerleştir; (5) cover açık/kapalı, kart takma/çıkarma ve alet yaklaşımını çakışma+tolerans ile doğrula; (6) ölçülü 1:1 makette ve ilk kartta yeniden sınama. Bu kapı geçmeden A0 montaj CAD'i üretim geometrisi değildir.
