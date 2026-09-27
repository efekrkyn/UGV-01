# UGV-01 A3 Lite mekanik

24.09.2026 · L1 ([spec](superpowers/specs/2026-09-24-a3-lite-budget-design.md), [plan](superpowers/plans/2026-09-24-a3-lite-mechanical.md)). 25.09.2026 · **M3 karakter gövdesi ve 5 eksenli kol** ([spec](superpowers/specs/2026-09-25-m3-character-body-arm-design.md), [plan](superpowers/plans/2026-09-25-m3-character-body-arm.md), DD72–DD75). [3D görüntüleyici](renders/UGV-01-A3-viewer.html) STEP katılarından üretilir. **Üretim, baskı veya sürüş onayı değildir;** baskı ve fiziksel test yapılmadı. A2 kaydı: [revisions/A2](revisions/A2/README.md).

## Yerleşim

| Bölge | Karar | Parça |
|---|---|---|
| Gövde (M3) | 300 × **236** mm, üst **z210** (A3: 200 × z146). Ön görünüş kareye yakın. Tekerlekler gövde yüksekliğinin yaklaşık yarısını örter (palet görünümü gibi). Yan paneller 3 × 100 mm modül, kapaklar M3 ısıl insertli boslara vidalanır | UGV-MECH-010/011/012-±1, 013-1…3, 022-±1 |
| Alt plaka | 5 mm PETG, iki parça (115 + 185 mm). Ek yeri x=−35'te, hiçbir bağlantı deliğine denk gelmez. Ek yerini üstten 150×12×15 mm iki baskı kiriş bağlar | UGV-MECH-001-R/F, UGV-MECH-002-±1 |
| Motorlar | 4 × JGA25-370 12 V 77 dev/dk 1:78, **dördü de enkoderli**, her biri 7,5 Ω seri balastla ([DD69](design_decisions.md)). **M3:** motor bütünüyle gövdenin içinde (dişli kutusu yüzü \|y\|=114, duvar iç yüzü 115); duvardan yalnız teker göbeğinin boynu Ø18 delikten geçer. Yük, eksenden ikiye bölünmüş 40×30 mm baskı kelepçeye (alt yuva + kapak) biner. İki M3×45 cıvata kapak, yuva ve plakayı sıkar; somunlar plakanın altında | REF-MOTOR-xx, UGV-MECH-003/004-xx |
| Tekerler | Ø110×30 mm PETG göbek + Ø120/Ø110 TPU lastik. İz **278 mm**, toplam genişlik **308 mm**. Göbeğin Ø16 boynu duvardan motora uzanır. D-mil boyna **8,5 mm** girer; düzlüğe inen M3 sıkma vidası gövde–teker arasındaki **6 mm** aralıkta, alttan ya da yandan 1,5 mm alyanla sıkılır. Somunu motor tarafından yuvasına kayar. 8 kanatçık lastiği döndürmez | UGV-MECH-060-xx, UGV-MECH-061-xx |
| Çamurluk (M3) | Tekerlerin üstünde, tekere ≥3 mm uzakta 4 mm raf; yan duvar boyunca flanş ve teker arasında bir destek. Kolun park yeridir. Her yanda iki parça | UGV-MECH-015-xx |
| Batarya | 3S1P 18650 paket zarfı 70×60×24 mm, x=−60 | REF-BATTERY |
| Elektronik | ESP32-S3 + 2 × TB6612FNG + PCA9685 + 3 × Mini560, tepsi zarfı **100×76×25 mm**, x=+60 | REF-ELECTRONICS |
| İç tutucular (M2) | Batarya beşiği (kayış yuvalı), elektronik tepsisi (4 × M3 insertli ayak), ön duvar arkasında 4 balast direnci için havalandırmalı raf; hepsi M3 ile plakaya. Kablo geçişleri: boyun ekseninde Ø10, ön duvarda iki ToF için Ø6 | UGV-MECH-070/071/072, REF-BALLAST-1…4 |
| Kargo bölmesi (M3) | Ön kapakta 38 × 54 mm atma ağzı ve üstünde 1,5 mm TPU çapraz yarıklı kapak. Altında 78 × 92 × 97 mm açık kutu: iki ayakla plakaya, flanşla ön duvara bağlı. Kol "depola" duruşunda nesneyi ağzın 23 mm üstünde bırakır | UGV-MECH-073, UGV-MECH-018 |
| E-stop | Ø40 mantar baş arka kapağın 22 mm üstünde (x=−115), gövdesi kapaktaki Ø23 delikten içeri | REF-ESTOP |
| ToF | Ön TPU tamponda y=±50 mm'de 27×13 mm iki pencere; modül zarfı 25×11 mm | REF-TOF-±1 |
| Baş | Boyun zinciri gövde üstüne bağlıdır. Göz kabuğunun arkası sıkı geçmeli kapaktır (UGV-MECH-044-±1); ESP32-CAM kartı ön tırnaklarla kapak çerçevesi arasında durur, lens pencere yuvasına oturur (DD78). **Eğim ekseni ile gövde üstü arası 122 mm**, A3 ile aynı (z268 → z332). Göz kabukları 40×42×48 mm, içeride ESP32-CAM + OV2640 (26×27×40,5 mm zarf), lens pencereye ortalı. DD82/DD83: gözler boyun eksenine ortalı, merkezleri ±30,5 mm (stereo taban 61 mm). Pan MG90S boyun ekseninde, tabana alttan girer; boyun Ø20 mili 6804'e oturur, alt yüzü pan kornasına bağlıdır. Tilt MG90S görünmez: boynun rulman üstündeki bloğunda, bir plakada; Ø1,5 mm itme çubuğu boyun sütunundan çıkıp sol gözün krankını 1:1 sürer. Gözlerin arasında yalnız ince bir bıçak var; iki göz bıçakta dönen altıgen uçlu aksla birbirine bağlı. Tilt −30…+60° taramada kesişim yok, gözler sütundan ≥2,5 mm uzakta | UGV-MECH-040…046, REF-EYE-CAMERA-±1 |

## Kol (M3, DD73)

Sağ kol **5 eksen + pençe**; omuz gövdenin yan duvarından çıkar. Sol kol aynı dış kabukta, pasiftir ve elle poz verilir.

| Eklem | Eksen (sıfır duruş: kol öne yatay) | Servo | Sınır | Yük yolu |
|---|---|---|---|---|
| J1 omuz | y, yan duvardan | DS3218MG 270°, **gövdenin içinde**, yan duvara bağlı çerçevede | −45…180° | 6804-2RS rulman ön yan paneldeki boss'ta. Mil Ø20; içinden Ø8 kablo deliği geçer |
| J2 üst kol dönüşü | kol ekseni | MG996R, kulakları kesilmiş, üst kolun kapaklı cebinde (058) | −80…90° | 6704-2RS ince rulman; 25T korna → adaptör (059) → üst kolun dış parçası |
| J3 dirsek | y | MG996R, kulaklarıyla 4 × M3 insert, mil içe | −30…135° (çatal geometrisi ≈120°'de durur) | Çatalın iç yanağı 25T alüminyum kornaya 4 × M3; dış yanakta 624ZZ, M4 uzuvdaki gömme somuna |
| J4 bilek eğimi | y | MG996R, dirsekle aynı bağlantı | −70…100° | Dirsekle aynı |
| J5 bilek dönüşü | kol ekseni | MG90S, kulaklarıyla 2 × M2 | −85…85° | Pençe servo kornasına 2 × M2 |
| J6 pençe | — | MG90S | aç/kapa | İki çene (çizimde sabit) |

- **Boyutlar:** omuz–dirsek 100, dirsek–bilek 80, bilek–kavrama merkezi 96 mm (DD81; toplam 276 mm aynı, parkta uç ayak izinde); omuz (x125, z163), kol düzlemi \|y\|=138 (DD77: 136'dan dışarı alındı).
- **Neden J2:** J1, J3 ve J4 aynı yöne paralel eksenlerdir, kol tek düzlemde kalır. J2 bu düzlemi kolun ekseni etrafında çevirir: dirsek gövdeye doğru bükülür, pençe robotun önünde ortaya iner.
- **Tork payları** (katalog stall 4,8–5 V; kol yatay ve düz; 150 g uçta; parça kütleleri ve ağırlık merkezleri CAD'den):

| Eklem | Tutma yükü (N·m) | Pay |
|---|---:|---:|
| Omuz | 0,784 | 2,25 |
| Dönüş ve dirsek | 0,390 | 2,36 |
| Bilek | 0,171 | 5,39 |

Tek dişli MG996R omuzda 1,5 payını vermiyordu; A3'ün dişli omzu (DD68) bu yüzden kaldırıldı.

| Duruş | Eklemler (°) | Kavrama merkezi (mm) | Ne için |
|---|---|---|---|
| park | 180, 90, 0, 0, 0 | (−151, −138, 163) | Çamurluğun üstünde, gövde yanında yatar |
| kaldır | 90, 90, 0, 0, 0 | — | Yalnız planlayıcı ara noktası |
| yukarı | 90, 0, 0, 0, 0 | (125, −138, 439) | El sallama |
| hazır | 45, 0, 45, 0, 0 | (372, −138, 234) | Önde, yukarıda |
| öne | 0, 0, 0, 0, 0 | (401, −138, 163) | Düz ileri |
| yere | 20, 0, 103, 7, 0 | (229, −138, 22) | Sağ tekerin 65 mm önünde, yerde |
| öne-orta | −40, 90, 90, −60, 0 | (265, −10, 45) | Robotun önünde ortada, iki kameranın altında |
| depola | 90, 90, 50, 98, 0 | (125, −26, 233) | Kargo ağzının üstü (DD81: çeneler kapaktan ≥6 mm yukarıda) |

Duruş grafiği: park–kaldır–{yukarı, depola} ve yukarı–hazır–{öne, yere, öne-orta}. Robotun çekirdeği (firmware) kolu yalnız bu kenarlar üzerinden, eklem uzayında doğru çizgiyle yürütür ve kenar dışı komutları reddeder (DD76). CAD de aynı çizgileri ≤5° adımla süpürür. Doğrudan park → yukarı geçişi, dönen dirseği yan duvara ve kapağa sürüyordu; "kaldır" ara noktası bu yüzden eklendi.

Duruşlar ve geçişler **1° adımla** süpürülür (uçta ≤5 mm). Çarpışmasızlığın yanında açıklık da ölçülür:
- Dirsekten sonraki hareketli uzuvlar her kenarda başka parçalardan **≥4,5 mm** uzakta kalır. Yalnız park duruşunda kol, çamurluğa 1 mm açıklıkla yaslanır.
- En dar geçişler: hazır → öne-orta 5,3 mm ve park → kaldır 5,7 mm (DD77'de park → kaldır 4,5 mm; önceki 1,5 mm yetersizdi).

Servo rayı kesilince (E-stop) park halindeki kol 1,5° içinde çamurluğa oturur. Dirsek ve bilek eksenleri parkta düşeydir, yerçekimi onları döndürmez.

## Kontrol

`.venv/bin/python cad/assembly/build_concept.py && .venv/bin/python tests/check_cad.py` → **PASS**. Kapsam:
- 96 geçerli STEP katısı, izinsiz çakışma yok; 330 × 308 mm park zarfı, baş tepesi z361.
- Gövde ölçüleri. Motorun duvar dışında hiç katısı yok (mil ve burç hariç). Duvar deliği yalnız göbek boynu kadar. Mil göbeğe ≥7 mm giriyor; set vidası 6 mm aralıkta.
- Çamurluk teker üstünü örtüyor ve tekerden ≥3 mm uzakta.
- Eğim ekseni − gövde üstü = 122 mm.
- 8 duruş ve 7 kenar çakışmasız; gevşek kol çamurluğa oturuyor.
- Tork payları. Omuz servosu gövde içinde, rulman duvar boss'unda. Sol kol sağın aynası.
- Kol uzvu arayüzleri (DD81): kulak insertleri ve çevresindeki et, korna delikleri, 624 yuvası ve dudağı, M4 yolu ve somun cebi, çatal köprüsünün eksenden ≥22 mm uzaklığı, twist cebi kapak pilotları, adaptörün korna/merkez/B delikleri, MG90S pilotları.
- Kargo ağzı açık, altında kutu, düşüş yolu boş; "depola" duruşu ağzın üstünde.
- URDF eklem sınırları config'e eşit.
- Önceki M2 arayüz kontrolleri: kelepçe, göbek, kapak insertleri, boyun cıvataları, iç tutucular, E-stop, ToF, ışık şeridi, göz kameraları.

## Baskı

[Baskı rehberi](print_guide_A3.md) `tools/print_plan.py` ile üretilir (DD79). İçeriği:
- 67 baskı parçasının her biri için yön, destek, duvar ve dolgu ile kütle;
- baskı sırası ve önce basılacak deneme parçaları;
- vida, insert ve rulman listesi (34 × M3 insert).

STL'ler baskı yönünde, tablaya oturmuş halde üretilir. Kol uzuvları (DD81) ve baş mekanizması (DD82, DD83) çizildi; bekleyen baskı parçası yok. B, C ve D yan yatarak desteksiz basılır.

## Kütle, CG ve hareket (hesap, ölçülmedi)

[Hesap](calculation_results.md) (`tests/check_design.py`):

| Büyüklük | Değer | Sınır / not |
|---|---|---|
| Boş kütle | **4,58 kg** | ≤4,6 kg |
| Boş CG | x=9,3 mm, z=117,8 mm | |
| Yüklü CG (0,5 kg yük kapakta, z250) | **z=130,8 mm** | 135 mm; statik devrilme 33,7° |
| Brüt kütle | 5,1 kg | |
| Batarya | 32,4 Wh | |
| Çalışma süresi | tipik 16 W'ta **1,31 saat**, ağır 46 W'ta 0,46 saat | |

Tahrik (DD69 balastı ve 1:78 motorlar değişmedi):
- **5° rampa:** en yüklü motor 0,139 N·m ve 0,39 A çeker. 0,5 m/s² ivmeyle 0,53 A (0,6 A sürekli tavanın içinde).
- **Hız:** 0,3 m/s; boş pakette düzde 0,31 m/s ulaşılır. Rampada boş pakette 0,158 m/s, bu yüzden **rampa sınırı 0,15 m/s** (A3: 0,2).
- **Yerinde dönüş:** kaba ve muhafazakâr modelle hesaplandı. Ağırlaşan araçta yürütücünün dönüş hızı **0,45 rad/s**'ye indi (A3: 0,6). Bu hızda µ sınırı:

  | Paket | µ sınırı |
  |---|---:|
  | Boş | 0,30 |
  | Nominal | 0,36 |
  | Dolu | 0,45 |
  | Kopma | 0,38 |

  Genişleyen iz (278 mm) kaybın bir kısmını karşılar. Daha sürtünmeli zeminde teker sınırlı akımda durur ve çekirdeğin korumaları keser.
- **Doğrulama:** gerçek µ, akım ve ısınma TL2'de ölçülür (NOT_RUN).

## Kütle taraması ve filament

`.venv/bin/python tools/body_mass_screen.py` (test: `tests/check_body_mass.py`). Baskı tahmini için bütün yüzeyde 1,2 mm kabuk + içeride %20 dolgu varsayıldı; yoğunluk PETG 1,27, TPU 1,21 g/cm³. Satın alınan parçalar katalog kütlesiyle. Vida ve kablo dahil değil.

| Grup | Katı üst sınır | Baskı tahmini | Tahsis |
|---|---:|---:|---:|
| Taban plakası, kirişler, motor kelepçesi (12) | 647 g | 381 g | 400 g |
| Gövde panelleri, kapaklar, uç duvarlar, çamurluklar, flanş, köprü, iç tutucular, kargo kutusu (21) | 1.339 g | 1.149 g | 1.200 g |
| TPU tamponlar ve ağız kapağı (3) | 238 g | 102 g | 120 g |
| Tekerler: göbek + lastik (8) | 593 g | 440 g | 500 g |
| Baş: pan tabanı, boyun, köprü, kabuklar, kapaklar, kaş çubuğu, 2 servo, 2 ESP32-CAM, rulman (13) | 310 g | 230 g | 300 g |
| Kollar: 10 uzuv, twist kapağı ve adaptörü, omuz çerçevesi, sol bilezik, 6 servo, 3 rulman (23) | 836 g | 621 g | 720 g |

**Filament (CAD'den):** PETG baskı tahmini **2.251 g**, TPU 281 g. %25 fire/destek payıyla ≈2,81 kg PETG ve ≈0,35 kg TPU gerekir: **3 × 1 kg PETG** + 1 TPU makarası. İstenirse 2,4 mm duvarla ≈160 g azaltılabilir; uygulanmadı, çünkü kol yükü yan duvardan geçiyor.

## Açık işler (üretim onayı yok)

1. **Baskı hazırlığı:**
   - Bütün baskı arayüzleri çizildi: DD78 (göz kapağı, ESP32-CAM tırnakları, lens yuvası; çamurluk, omuz servo çerçevesi ve kargo vidaları; omuz mili), DD81 (kol uzuvları), DD82 (baş mekanizması). Baskı rehberi DD79.
   - Kablo yolları DD85'te çizildi (çıkış yarıkları, omuz girişi, göz delikleri, boyun kanalı); kabloların kendisi ve döngüleri montajda. Satın alınan parçaların ölçüleri geldiğinde doğrulanır.
   - Sürüş kilidi çekirdekte (DD84): kol sürüş duruşunda değilken tekerler dönmez.
2. **İki parçalı plaka:** rijitliği, kiriş ve panel ayak bağlantıları gerçek baskıyla sınanır.
3. **TPU:** lastik–göbek tutunması (yapıştırma ya da geçme dişi); tampon penceresi kapakları; atma ağzı kapağının nesneyi geçirip geçirmediği.
4. **Motor:** JGA25 redüksiyonu, enkoder PPR'si ve 5° rampada ısınma ölçülür.
5. **E-stop:** 12 V DC ≥10 A kesme değeri (M3'te en kötü ≈9,4 A); kablo, sigorta ve anahtar yerleri.
6. **Göz kamerası:** ESP32-CAM anten yeri ve FPC bükülmesi göz kabuğu içinde; Wi-Fi sinyal testi.
7. **Kol:**
   - Servo kornası bağlantıları; omuz mili–korna kaplini.
   - Kol içindeki kablo yolu ve J2'de kablo burulması.
   - Çene kinematiği ve ped malzemesi.
   - Servo rayı yeniden açılınca düşmüş kolun hızla dönmesi: yeniden ARM öncesi kol elle parka alınır (L4'te denenir).
   - Parkta dirsek ve bilek eksenleri düşeydir. Dirsek servosunun 1°'lik hatası pençeyi yan duvara ≈3 mm yaklaştırır; 4,5 mm açıklık için dirsek kalibrasyonu ±1° içinde olmalı (TL4).
8. **Balast dirençleri:** havalandırılan yerleri ve ısınması (sıkışmada direnç başına ≈5,9 W, kısa süre).
