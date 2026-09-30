# Kütle ve ağırlık merkezi bütçesi

## A3 Lite, M3 gövde ve kol (güncel)

Kaynak `config/vehicle.json`, rapor [calculation_results.md](calculation_results.md), CAD taraması [Lite mekanik](lite_mechanical_A3.md). Konumlar CAD katılarının kütle ağırlıklı merkezleridir. Fiziki tartım değildir.

| Grup | kg | x mm | z mm | Dayanak |
|---|---:|---:|---:|---|
| Baskı PETG taban plakası, kirişler, motor kelepçeleri | 0,40 | 0 | 43,5 | CAD baskı tahmini 381 g |
| Gövde panelleri, kapaklar, uç duvarlar, çamurluklar, flanş, köprü, iç tutucular, kargo kutusu (PETG) | 1,20 | 13 | 143 | CAD baskı tahmini 1.139 g (M3: 236 × z210 gövde) |
| TPU tamponlar ve atma ağzı kapağı | 0,12 | 4 | 110 | CAD baskı tahmini 102 g |
| Tekerler: baskı göbek + TPU lastik | 0,50 | 0 | 60 | CAD baskı tahmini 440 g |
| 4 × JGA25-370 1:78 enkoderli motor | 0,42 | 0 | 60 | ≈100 g/adet satıcı verisi + 4 enkoder (DD69) |
| 3S1P 18650 paket, BMS, tutucu | 0,20 | −60 | 53,5 | 3 × ≈48 g hücre + tahsis |
| ESP32-S3, PCA9685, 2 × TB6612, 3 buck, 4 balast direnci | 0,20 | 60 | 61,5 | Tahsis (M3: +PCA9685, +1 buck) |
| Kablo, konnektör, E-stop, sigorta, anahtar | 0,22 | −30 | 100 | Tahsis (M3: kol boyunca servo uzatmaları) |
| Baş: boyun, pan/tilt servo, 2 ESP32-CAM | 0,30 | 35 | 298 | CAD 189 g; baş gövdeyle 64 mm yükseldi |
| Kollar: sağ 5 eksen (DS3218MG + 3 MG996R + 2 MG90S), sol pasif, omuz çerçevesi, 3 rulman | 0,72 | 27 | 161 | CAD baskı + katalog 621 g (DD81) |
| Işık şeridi + 2 ToF | 0,02 | 150 | 120 | Tahsis |
| Vida, insert, küçük braketler | 0,13 | 0 | 100 | Tahsis |
| Belirsizlik rezervi | 0,15 | 0 | 110 | ≈%3 |
| **Boş araç (hesap 4,58)** | **≤4,60** | 9,3 | 117,8 | |
| Faydalı yük (kapak üstünde, muhafazakâr) | 0,50 | 0 | 250 | Kullanıcı kararı (Lite) |
| **Brüt** | **5,10** | | | Hesap yükü |

Yüklü CG z=130,8 mm bu bütçenin tek-nokta modelinden (sınır 135; statik boyuna devrilme 33,7°); N4 kontrolü kolun CAD ağırlık merkeziyle parkta z=131,1 mm ve öne 36,1° verir (DD95 sonrası; kol bütçe noktası x33, y−33, z163; `tests/check_body_mass.py`). A3'ün 3,47 kg / z105,4 mm değerleri M3 ile geçersizdir. Hiçbir değer tartılmadı; baskı kütlesi dolgu ayarına bağlıdır.

## A2 (arşiv)

A2 tahsisleri ([arşiv config](revisions/A2/vehicle.json)); fiziki tartım değildir. Kaynak `config/vehicle.json`; sayısal rapor `calculation_results.md`.

| Grup | kg | Güven düzeyi |
|---|---:|---|
|Alt plaka +metal yük taşıyıcılar|0,80|Plaka brüt0,476kg hesap;geri kalanı tahsis |
|ASA gövde/kapak/TPU tampon|0,70|Slicer hacmi ilePH4'te düzelt |
|4 motor+encoder|0,82|4×205g üretici |
|Teker/göbek/rulman/mil|0,65|Tahsis |
|Batarya hücre+BMS+kasa|0,85|Hücreler≤0,560kg;tamamlayıcılar tahsis |
|CM5+IO+soğutucu|0,24|Tahsis |
|MCU ve PWR kartları|0,24|Tahsis |
|Kablo,konektör,E-stop,sigorta|0,30|Tahsis |
|A2 baş, boyun, pan/tilt servo, iki göz kamerası|0,30|CAD taraması 195,4 g ([A2](exterior_language_A2.md)); vida/kablo hariç |
|Vida,insert,fan,adaptörler|0,20|Tahsis |
|Belirsizlik rezervi|0,90|%15 boş-kütle bütçesi |
|A2 kollar, omuz kuleleri, omuz + pençe servosu|0,235|CAD taraması 186,9 g; vida/kablo hariç |
|**Boş araç (hesap 6,235)**|**≤6,25**|Rezerv dahildir |
|Faydalı yük|1,50|A2 kullanıcı kararı; CG z≤190 mm |
|Brüt 8 kg'a kalan hesap payı|0,25|Ölçülmüş değil |
|**Toplam**|**8,00**|Hesap yükü |

**J-PWR demeti alt sınırı (PH5):** 0,4 m uzunlukta 3×AWG12 + 1×AWG16 için bakır kesitleri 3,31/1,31 mm² ve yoğunluk 8,96 g/cm³ varsayımıyla çıplak iletken kütlesi `3×0,4×3,31×8,96 + 0,4×1,31×8,96 ≈ 40,28 g`. İki [Molex 768250004 header](https://www.molex.com/en-us/products/series-chart/76825) (2×2,836 g), iki [1700010104 housing](https://www.molex.com/en-us/products/part-detail/1700010104) (2×2,118 g), altı [AWG12 terminal](https://www.molex.com/en-us/products/part-detail/768230322) (6×0,380 g) ve iki [AWG16 terminal](https://www.molex.com/en-us/products/part-detail/768230321) (2×0,370 g) ile **en az 53,21 g** çıkar. İzolasyon, J-SIG, diğer motor/encoder/CAN/batarya kabloları, strain relief ve etiketler dahil değildir. Bu 53,21 g, tablodaki **0,30 kg kablo/konektör/E-stop/sigorta tahsisinin içindedir**; D2A'nın 67 g rezervinden ikinci kez düşülmez. Tahsis içinde geri kalan azami 246,79 g'nin bütün diğer kalemlere yettiği henüz kanıtlanmadı; gerçek demet ve bütün araç tartımı gerekir.

D2A hesap kütlesi 5,933 kg ve 6 kg hedefe kağıt üzerindeki boşluk yalnız 67 g'dır. Bu **ölçülmüş rezerv değildir**: kablo/vida tahsislerinin yeterliliği ve gerçek baskı yoğunluğu bilinmiyor. Raporun 6,2–6,4 kg öngörüsü de ölçümsüz bir senaryodur. En az 0,25–0,30 kg doğrulanmış montaj marjı hedeflenir; motor taşıyıcısından dörtte birer 25 g boşaltma, 101 g/parçanın yaklaşık %25'ini kaldırır ve gerilme/yatak yük yolu analizi olmadan çizime işlenmez. Önce kalem bazlı tartım, sonra destekli hafifletme veya 6 kg şartının gerekçeli revizyonu.

**A1 CAD gövde taraması:** [13 gövde parçasının katı hacmi](body_mass_screen_A1.md) ASA 499,832 cm³ + TPU 171 cm³'tür. ASA 1,05 g/cm³ ve TPU için 1,25 g/cm³ ön varsayımıyla **738,6 g** çıkar; 700 g tahsisi **38,6 g** aşar. D2A'daki 67,2 g hesap payı aynı gövde varsayımı korunursa yaklaşık28,6 g'a düşer. Gerçek slicer doluluğu bu katı üst sınırı azaltabilir, ancak kamera podu/bağlantılar hesabın dışındadır; ölçülmüş marj hâlâ yoktur. **A2:** ön kapaktaki iki omuz kulesi çentiği gövdeyi **730,5 g**'a indirdi (aşım 30,5 g).

x_CG=Σm_ix_i/Σm_i; z_CG=Σm_iz_i/Σm_i. A2 tahsisleriyle boş z≈86,67 mm, x≈−2,35 mm. 1,5 kg yükün CG'si z190 mm olduğunda toplam z≈106,71 mm (110 mm sınırına 3,3 mm); yük z200 mm'de 108,65 mm. 1,75 kg yük z190'da 109,32 mm ile yalnız 0,7 mm pay bırakırdı; bu yüzden A2 yükü 1,5 kg'dır (DD62). A0 değerleri (boş z≈80,71 mm, 2 kg yük) [A0 arşivindedir](revisions/A0/vehicle.json). Rezerv kütlesinin gerçek konumu ölçüldüğünde hesap yenilenir. Yük kapasitesi yalnız kütle değil bu CG zarfıyla sınırlıdır.

Düz zeminde nominal19,6N/teker. Eğime göre Nf=mg[((L/2+xCG)cosθ−h sinθ)/L],Nr=mgcosθ−Nf;ivme ma h/L aktarır.1,5 teker yük katsayısı tartımla doğrulanacak varsayımdır;eşzamanlı boyuna/enine CG ve ivme1,6 duyarlılık durumunu gerektirebilir. Teker havalanması/diyagonal tümseklerde eşit yük paylaşımı kabul edilmez.

Her teker altında tartı ile CG x/y, bilinen eğimde yük aktarımı ile CG yüksekliği ölçülür. Statik devrilme açısı dinamik güvenli eğim belgesi değildir.
