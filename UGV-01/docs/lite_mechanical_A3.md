# UGV-01 A3 Lite mekanik

24.09.2026 · L1 ([spec](superpowers/specs/2026-09-24-a3-lite-budget-design.md), [plan](superpowers/plans/2026-09-24-a3-lite-mechanical.md)). 25.09.2026 · **M3 karakter gövdesi ve 5 eksenli kol** ([spec](superpowers/specs/2026-09-25-m3-character-body-arm-design.md), [plan](superpowers/plans/2026-09-25-m3-character-body-arm.md), DD72–DD75). [3D görüntüleyici](renders/UGV-01-A3-viewer.html) STEP katılarından üretilir. **Üretim, baskı veya sürüş onayı değildir;** baskı ve fiziksel test yapılmadı. A2 kaydı: [revisions/A2](revisions/A2/README.md).

## Yerleşim

| Bölge | Karar | Parça |
|---|---|---|
| Gövde (M3) | 300 × **236** mm, üst **z210** (A3: 200 × z146). Ön görünüş kareye yakın. Tekerlekler gövde yüksekliğinin yaklaşık yarısını örter (palet görünümü gibi). Yan paneller 3 × 100 mm modül, kapaklar M3 ısıl insertli boslara vidalanır | UGV-MECH-010/011/012-±1, 013-1…3, 022-±1 |
| Alt plaka | 5 mm PETG, iki parça (115 + 185 mm). Ek yeri x=−35'te, hiçbir bağlantı deliğine denk gelmez. Ek yerini üstten 150×12×15 mm iki baskı kiriş köprüler; her kiriş ek yerinin iki yanında 2'şer M3 × 10 ile plaka altından kendi insertlerine vidalanır, yapıştırıcı yok (M02, DD93). Yük (G01, serbest cisim: 5,1 kg, aks aralığı 210 mm, ek yeri arka akstan 70 mm; düzgün yayılı): ek yerinde statik 1,17 N·m, 3g darbe payıyla 3,5 N·m, kiriş başına 1,75 N·m. Ek yerinde plaka kesik, momenti yalnız kiriş taşır: 3,9 MPa. Plakadan kirişe iki ayrı idealize yük yolu; her biri momentin tamamını tek başına taşır varsayılır, sonuçları toplanmaz (gerçek paylaşımı deney gösterir): (a) eksenel kuvvet çifti (kol 10 mm) 175 N → cıvata başına 88 N kesme, PETG ezilmesi 5,8 MPa; (b) prying (plaka yarısı ek kenarında döner, cıvatalar 15/30 mm) → uzak cıvatada 47 N, yakında 23 N eksenel çekme, plaka yerel eğilmesi ≈5,6 MPa. Katmanlara dik insert tutunması ≈300 N varsayımıyla (ölçülmedi) ≈6 kat. Hepsi hesap: insert çekme ve ek yeri sehimi deneyle ölçülür; paneller de ek yerini köprüler, hesaba katılmadı | UGV-MECH-001-R/F, UGV-MECH-002-±1 |
| Motorlar | 4 × JGA25-370 12 V 77 dev/dk 1:78, **dördü de enkoderli**, her biri 7,5 Ω seri balastla ([DD69](design_decisions.md)). **M3:** motor bütünüyle gövdenin içinde (dişli kutusu yüzü \|y\|=114, duvar iç yüzü 115); duvardan yalnız teker göbeğinin boynu Ø18 delikten geçer. Yük, eksenden ikiye bölünmüş 40×30 mm baskı kelepçeye (alt yuva + kapak) biner. İki M3×45 cıvata kapak, yuva ve plakayı sıkar; somunlar plakanın altında | REF-MOTOR-xx, UGV-MECH-003/004-xx |
| Tekerler | Ø110×30 mm PETG göbek + Ø120/Ø110 TPU lastik. İz **278 mm**, toplam genişlik **308 mm**. Göbeğin Ø16 boynu duvardan motora uzanır. D-mil boyna **8,5 mm** girer; düzlüğe inen M3 sıkma vidası gövde–teker arasındaki **6 mm** aralıkta, alttan ya da yandan 1,5 mm alyanla sıkılır. Somunu motor tarafından yuvasına kayar. 8 kanatçık lastiği döndürmez | UGV-MECH-060-xx, UGV-MECH-061-xx |
| Çamurluk (M3) | Tekerlerin üstünde, tekere ≥3 mm uzakta 4 mm raf; yan duvar boyunca flanş ve teker arasında bir destek. Kolun park yeridir. Her yanda iki parça | UGV-MECH-015-xx |
| Batarya | 3S1P 18650 paket zarfı 70×60×24 mm, x=−60 | REF-BATTERY |
| Elektronik | ESP32-S3 + 2 × TB6612FNG + PCA9685 + 3 × Mini560, tepsi zarfı **100×76×25 mm**, x=+60 | REF-ELECTRONICS |
| İç tutucular (M2) | Batarya beşiği (kayış yuvalı), elektronik tepsisi (4 × M3 insertli ayak), ön duvar arkasında 4 balast direnci için havalandırmalı raf; hepsi M3 ile plakaya. Kablo geçişleri: boyun ekseninde Ø10, ön duvarda iki ToF için Ø6 | UGV-MECH-070/071/072, REF-BALLAST-1…4 |
| Kargo bölmesi (M3) | Ön kapakta 38 × 54 mm atma ağzı ve üstünde 1,5 mm TPU çapraz yarıklı kapak. Altında 78 × 92 × 97 mm açık kutu: iki ayakla plakaya, flanşla ön duvara bağlı. Kol "depola" duruşunda nesneyi ağzın 23 mm üstünde bırakır | UGV-MECH-073, UGV-MECH-018 |
| E-stop | Ø40 mantar baş arka kapağın 22 mm üstünde (x=−115), gövdesi kapaktaki Ø23 delikten içeri | REF-ESTOP |
| ToF | Ön TPU tamponda y=±50 mm'de 27×13 mm iki pencere; modül zarfı 25×11 mm | REF-TOF-±1 |
| Baş | Boyun zinciri gövde üstüne bağlıdır. Göz kabuğunun arkası sıkı geçmeli kapaktır (UGV-MECH-044-±1); ESP32-CAM kartı ön tırnaklarla kapak çerçevesi arasında durur, lens pencere yuvasına oturur (DD78). **Eğim ekseni ile gövde üstü arası 122 mm**, A3 ile aynı (z268 → z332). Göz kabukları 40×42×48 mm, içeride ESP32-CAM + OV2640 (26×27×40,5 mm zarf), lens pencereye ortalı. DD82/DD83: gözler boyun eksenine ortalı, merkezleri ±30,5 mm (stereo taban 61 mm). Pan MG90S boyun ekseninde, tabana alttan girer; boyun Ø20 mili 6804'e oturur, alt yüzü pan kornasına bağlıdır. Tilt MG90S görünmez: boynun rulman üstündeki bloğunda, bir plakada; Ø1,5 mm itme çubuğu boyun sütunundan çıkıp sol gözün krankını 1:1 sürer. Gözlerin arasında yalnız ince bir bıçak var; iki göz bıçakta dönen altıgen uçlu aksla birbirine bağlı. Tilt −30…+60° 5° adımlı taramada kesişim yok; en küçük açıklık 1,6 mm (manifest `head_tilt_sweep`; DD85'teki baş değişikliğinden beri, eski 2,5 mm geçersiz). İtme çubuğunun tam hareket zarfı ve kablolar bu taramada yok | UGV-MECH-040…046, REF-EYE-CAMERA-±1 |

## Kol (M3, DD73)

Sağ kol **5 eksen + pençe**; omuz gövdenin yan duvarından çıkar. Sol kol aynı dış kabukta, pasiftir ve elle poz verilir.

| Eklem | Eksen (sıfır duruş: kol öne yatay) | Servo | Sınır | Yük yolu |
|---|---|---|---|---|
| J1 omuz | y, yan duvardan | DS3218MG 270°, **gövdenin içinde**, yan duvara bağlı çerçevede | −45…180° | 6804-2RS rulman ön yan paneldeki boss'ta. Mil Ø20; içinden Ø8 kablo deliği geçer |
| J2 üst kol dönüşü | kol ekseni | MG996R, kulakları kesilmiş, üst kolun kapaklı cebinde (058) | −80…90° | 6704-2RS ince rulman; 25T korna → adaptör (059) → üst kolun dış parçası |
| J3 dirsek | y | MG996R, kulaklarıyla 4 × M3 insert, mil içe | −30…135° (çatal geometrisi ≈120°'de durur) | Çatalın iç yanağı 25T alüminyum kornaya 4 × M3; dış yanakta 624ZZ, M4 uzuvdaki gömme somuna |
| J4 bilek eğimi | y | MG996R, dirsekle aynı bağlantı | −70…100° | Dirsekle aynı |
| J5 bilek dönüşü | kol ekseni | MG90S, kulaklarıyla 2 × M2 | −85…85° | Pençe servo kornasına 2 × M2 |
| J6 pençe | kol düzlemine dik | MG90S, avuçta | kapalı 0°…açık 60° | İkiz dişli pençe (M01, DD93): çene A 12 mm'de kesilmiş MG90S kol kornasına 2 × M2, çene B avucun direğinde naylon burç üstünde (R05); iki 16T m0,625 dişli, eksenler 10 mm aralıklı |

- **Pençe (M01, DD93):** iki çene dişliyle birlikte, ters yönde döner; TPU pedler z = 5 mm'de buluşur. 60° açıkken çene uçları arası **53,5 mm**, ped merkezleri arası 41,4 mm (TL5'in 50 mm nesnesi uçlarda). Sıkma kuvveti MG90S stall 0,176 N·m ile ped merkezinde τ/(2 × 21,6 mm) ≈ **4,1 N**; %50 stall'da iki TPU yüzü (µ≈0,8) 3,3 N sürtünme verir, 150 g (1,47 N) için ≈2,2 kat pay. Dişli dişi: B çenesinin torku 88 N·mm, 5 mm hatve yarıçapında 17,6 N; Lewis gerilmesi ≈15 MPa (7 mm diş genişliği), baskı PETG'de ≈2 kat pay. Dişli çifti önce deneme baskısı (boşluk, sıkışma). Park duruşunda çenelerin açılma yönü gövdenin yanına bakar (iç çene duvara çarpar), bu yüzden:
  - pençe yalnız CAD'in her çene açısında taradığı **açık duruşlarda** açılır: hazır, öne, yere, öne-orta, depola (config `gripper.open_poses`); çekirdek başka yerde "aç"ı yok sayar;
  - pençe açıkken kol yalnız iki açık duruş arasındaki kenarlarda yürür (hazır ↔ öne/yere/öne-orta, açık çenelerle 1° tarandı); kapalı değilken diğer kenar komutları reddedilir;
  - kavrama duruşlarında (öne, yere, öne-orta) kapanan pençe nesne tutuyor sayılır; araç parkta ancak pençe kapalı ve o kapanıştan sonra bir kez tam açılmışsa (depola'da, kargo kutusunun üstünde) sürer. 0x1A0 bit4 bu "boş" işaretidir.
  Pençe konumu servo modelidir; nesnenin gerçekten bırakıldığını ölçen sensör yok.
- **Pasif sol omuz (M03, DD93):** yarıklı bilezik (057) mile M3 × 12 + somunla sıkılır ve milla döner; bilezik ile duvar göbeğinin iç yüzü arasındaki TPU pul (065) sabit yüze sürtünür. Sol kolun baskı kütlesi taklitlerle ≈221 g, yatayda ağırlık merkezi omuzdan ≈115 mm: 0,25 N·m. 1,5 kat payla 0,37 N·m için pulda (ortalama sürtünme yarıçapı 15,2 mm, µ≈0,5) ≈49 N eksenel ön yük gerekir: montajda bilezik dışa doğru bastırılıp sıkılır; M3 sıkma vidası bileziği mil üstünde bunun birkaç katı kuvvetle tutar.
- **Sol kolun diğer eklemleri (R04, DD94):** sağ kolun aynı arayüzleriyle, servo, korna ve rulman yerine basılı taklitlerle bağlanır ve park açılarında sabittir. Twist: MG996R + 25T korna taklidi (066) A'nın cebinde kapakla (058) tutulur, adaptör (059) ona 4 × M3, B adaptöre 2 × M3; 6704 yerine halka (075). Dirsek ve bilek: MG996R taklitleri (067/068) kulaklarıyla 4'er × M3 insertlere, korna diskleri çatalın iç yanağına 4'er × M3; dış yanak 624 yerine burçtan (076/077) M4 ile sıkılır. Dönüş: MG90S taklidi (069) kulaklarıyla D'ye 2 × M2, diski pençeye merkez M3 ve iki pimle. Pençe: MG90S taklidi (074) kulaklarıyla 2 × M2, kesilmiş korna taklidine çene A 2 × M2; çene B pimde, dişliler onu kilitler. Yalnız omuz döner. Twist taklidinin (066) dönmesini servo değil cep duvarları durdurur (DD95): taklit cebi kapak tarafı dahil her yanda 0,2 mm boşlukla doldurur (servo zarfı 0,5 ve 2,5 mm bırakıyordu, +0,9°/−2,9° dönüyordu). Kabul ±1° (TL4 eklem bütçesi): CAD taklidi iki yönde 1° döndürünce A'ya ya da kapağa çakıştığını gösterir, nominal boşluk ≈0,4°. Eksende sağ kolun servosu gibi tutulur: adaptöre (059) cıvatalı, adaptör halkayla (075) A'nın yuvasında, cebi kapak (058) kapatır.
- **Çene B pimi (R05, DD94):** M3 × 16 vida, yaylı rondela ve pulla, Ø5/Ø3,2 × 7,5 mm naylon burcu avuç direğinin yüzüne sıkar; çene B (7 mm, Ø5,2 delik) burcun üstünde döner. Eksenel boşluk 0,5 mm (iki yanda 0,25). Vida çeneyi değil burcu sıkar; 0,4 N·m (PETG kılavuz). Kupon testi: son montaj koşulunda 0–60° serbest dönüş ve boşluk (TL5).
- **Kavrama noktası (R06, DD94):** kapalı pedlerin buluştuğu yüzün ortası; bilek ekseninden 101 mm önde, kol düzleminden 16,5 mm içte, 5 mm yukarıda (manifest `grasp_datum_local_mm`, `grip_mm`). Eski "bilek + 96 mm, kol ekseninde" noktası 18 mm farklıydı. Kütle modeli tutulan nesneyi bu noktaya, kargodaki nesneyi kutunun tabanına koyar (bırakma noktasına değil).
- **Boyutlar (kinematik nominal):** omuz–dirsek 100, dirsek–bilek 80, bilek–uzuv ucu 96 mm (DD81; toplam 276 mm, parkta uç ayak izinde); omuz (x125, z163), kol düzlemi \|y\|=138 (DD77: 136'dan dışarı alındı). Gerçek kavrama noktası bundan farklıdır: bilek + 101 mm, düzlemden 16,5 mm içte, 5 mm yukarıda (R06, aşağıdaki tablo).
- **Neden J2:** J1, J3 ve J4 aynı yöne paralel eksenlerdir, kol tek düzlemde kalır. J2 bu düzlemi kolun ekseni etrafında çevirir: dirsek gövdeye doğru bükülür, pençe robotun önünde ortaya iner.
- **Tork payları** (katalog stall 4,8–5 V; kol yatay ve düz; 150 g uçta; parça kütleleri ve ağırlık merkezleri CAD'den):

| Eklem | Tutma yükü (N·m) | Pay |
|---|---:|---:|
| Omuz | 0,784 | 2,25 |
| Dönüş ve dirsek | 0,390 | 2,36 |
| Bilek | 0,171 | 5,39 |

Tek dişli MG996R omuzda 1,5 payını vermiyordu; A3'ün dişli omzu (DD68) bu yüzden kaldırıldı.

| Duruş | Eklemler (°) | Kavrama noktası x / y / z (mm) | Ne için |
|---|---|---|---|
| park | 180, 90, 0, 0, 0 | (−156 / −143 / 146,5) | Çamurluğun üstünde, gövde yanında yatar |
| kaldır | 90, 90, 0, 0, 0 | (108,5 / −143 / 444) | Yalnız planlayıcı ara noktası |
| yukarı | 90, 0, 0, 0, 0 | (120 / −121,5 / 444) | El sallama |
| hazır | 45, 0, 45, 0, 0 | (376,7 / −121,5 / 238,7) | Önde, yukarıda |
| öne | 0, 0, 0, 0, 0 | (406 / −121,5 / 168) | Düz ileri |
| yere | 20, 0, 103, 7, 0 | (233,7 / −121,5 / 16,8) | Sağ tekerin önünde, yerde |
| öne-orta | −40, 90, 90, −60, 0 | (281,1 / −11,8 / 53,5) | Robotun önünde ortada, iki kameranın altında |
| depola | 90, 90, 50, 98, 0 | (108,5 / −19 / 231,4) | Kargo ağzının üstü (DD81: çeneler kapaktan ≥6 mm yukarıda) |

Kavrama noktası, CAD manifestinin `grip_mm` değeridir: kapalı pedlerin buluştuğu yüzün ortası (R06). Tablo ile manifest arasındaki fark `tests/check_cad.py` ile denetlenir (≤0,05 mm). Uzuv boyları (100/80/96 mm) kinematik nominaldir, kalibrasyon referansı değildir.

Duruş grafiği: park–kaldır–{yukarı, depola} ve yukarı–hazır–{öne, yere, öne-orta}. Robotun çekirdeği (firmware) kolu yalnız bu kenarlar üzerinden, eklem uzayında doğru çizgiyle yürütür ve kenar dışı komutları reddeder (DD76). CAD de aynı çizgileri ≤5° adımla süpürür. Doğrudan park → yukarı geçişi, dönen dirseği yan duvara ve kapağa sürüyordu; "kaldır" ara noktası bu yüzden eklendi.

Duruşlar ve geçişler **1° adımla** süpürülür (uçta ≤5 mm). Açıklık da artık aynı 1° adımla ölçülür (önce 5° idi; tam inceleme A08):
- Dirsekten sonraki hareketli uzuvlar her kenarda başka parçalardan **≥4,5 mm** uzakta kalır. Yalnız park duruşunda kol, çamurluğa 1 mm açıklıkla yaslanır.
- En dar geçişler: park → kaldır **4,75 mm** ve hazır → öne-orta 5,26 mm (5° örneklemenin verdiği 5,65 mm iyimserdi).
- **Park toleransı:** beş eklem aynı anda ±1° saparken (32 köşe) hareketli uzuvlar yan panellerden **≥4,1 mm** uzakta (sınır 3 mm; DD93'te avucun iç yüzü 3 mm kırpıldı, önce 2,80 mm idi). Bu, TL4'te her eklemin ±1° içinde kalibre edilmesini varsayar.

Servo rayı kesilince (E-stop) park halindeki kol 1,5° içinde çamurluğa oturur. Dirsek ve bilek eksenleri parkta düşeydir, yerçekimi onları döndürmez.

## Kontrol

`.venv/bin/python cad/assembly/build_concept.py && .venv/bin/python tests/check_cad.py` → **PASS**. Kapsam:
- 115 geçerli STEP katısı, izinsiz çakışma yok; 330 × 308 mm park zarfı (pençe dahil), baş tepesi z361.
- Gövde ölçüleri. Motorun duvar dışında hiç katısı yok (mil ve burç hariç). Duvar deliği yalnız göbek boynu kadar. Mil göbeğe ≥7 mm giriyor; set vidası 6 mm aralıkta.
- Çamurluk teker üstünü örtüyor ve tekerden ≥3 mm uzakta.
- Eğim ekseni − gövde üstü = 122 mm.
- 8 duruş ve 7 kenar çakışmasız; gevşek kol çamurluğa oturuyor.
- Tork payları. Omuz servosu gövde içinde, rulman duvar boss'unda. Sol kol sağın aynası.
- Pençe (DD93): dişliler kavrar, çeneler avuca ve servolara 0–60° boyunca değmez; açık duruşlarda her açı, açık kenarlarda açık çeneler çakışmasız; uç açıklığı ≥50 mm. Park toleransı ≥3 mm. Ek kirişi insertleri ve plaka delikleri; sol bileziğin yarığı, sıkma vidası ve pulun göbek yüzüne oturması. DD94: kavrama noktası pedlerin buluştuğu yüzde; çene B burcu ve deliği; sol kolun her taklidi bağladığı parçaya değiyor.
- Kol uzvu arayüzleri (DD81): kulak insertleri ve çevresindeki et, korna delikleri, 624 yuvası ve dudağı, M4 yolu ve somun cebi, çatal köprüsünün eksenden ≥22 mm uzaklığı, twist cebi kapak pilotları, adaptörün korna/merkez/B delikleri, MG90S pilotları.
- Kargo ağzı açık, altında kutu, düşüş yolu boş; "depola" duruşu ağzın üstünde.
- URDF eklem sınırları config'e eşit.
- Önceki M2 arayüz kontrolleri: kelepçe, göbek, kapak insertleri, boyun cıvataları, iç tutucular, E-stop, ToF, ışık şeridi, göz kameraları.

## Baskı

[Baskı rehberi](print_guide_A3.md) `tools/print_plan.py` ile üretilir (DD79). İçeriği:
- 84 baskı parçasının her biri için yön, destek, duvar ve dolgu ile kütle;
- baskı sırası ve önce basılacak deneme parçaları;
- vida, insert ve rulman listesi (50 × M3 insert).

STL'ler baskı yönünde, tablaya oturmuş halde üretilir. Kol uzuvları (DD81) ve baş mekanizması (DD82, DD83) çizildi; bekleyen baskı parçası yok. B, C ve D yan yatarak desteksiz basılır.

## Kütle, CG ve hareket (hesap, ölçülmedi)

[Hesap](calculation_results.md) (`tests/check_design.py`):

| Büyüklük | Değer | Sınır / not |
|---|---|---|
| Boş kütle | **4,58 kg** | ≤4,6 kg |
| Boş CG | x=9,3 mm, z=117,8 mm | |
| Yüklü CG (0,5 kg yük kapakta, z250) | **z=131,1 mm** (N4 kontrolü: kolun CAD ağırlık merkeziyle, parkta; bütçe modelinin tek noktası z130,8) | 135 mm; öne statik devrilme 36,1° (DD94/DD95: sol kol taklitleriyle; kargodaki nesne kutunun tabanında: z127,7) |
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
| Taban plakası, kirişler, motor kelepçesi (12) | 645 g | 382 g | 400 g |
| Gövde panelleri, kapaklar, uç duvarlar, çamurluklar, flanş, köprü, iç tutucular, kargo kutusu (21) | 1.339 g | 1.149 g | 1.200 g |
| TPU tamponlar ve ağız kapağı (3) | 238 g | 102 g | 120 g |
| Tekerler: göbek + lastik (8) | 593 g | 440 g | 500 g |
| Baş: pan tabanı, boyun, köprü, kabuklar, kapaklar, kaş çubuğu, 2 servo, 2 ESP32-CAM, rulman (15) | 297 g | 229 g | 300 g |
| Kollar: 10 uzuv, 4 çene, 2 ped, iki twist kapağı ve adaptörü, omuz çerçevesi, sol bilezik ve pulu, sol kolun 8 taklidi, 2 çene burcu, 6 servo, 3 rulman (42) | 999 g | 710 g | 720 g |

**Filament (CAD'den):** PETG baskı tahmini **2.337 g**, TPU 283 g. %25 fire/destek payıyla ≈2,92 kg PETG (üç makaraya sınırda) ve ≈0,35 kg TPU gerekir: **3 × 1 kg PETG** + 1 TPU makarası. İstenirse 2,4 mm duvarla ≈160 g azaltılabilir; uygulanmadı, çünkü kol yükü yan duvardan geçiyor.

## Açık işler (üretim onayı yok)

1. **Baskı hazırlığı:**
   - Bütün baskı arayüzleri çizildi: DD78 (göz kapağı, ESP32-CAM tırnakları, lens yuvası; çamurluk, omuz servo çerçevesi ve kargo vidaları; omuz mili), DD81 (kol uzuvları), DD82 (baş mekanizması). Baskı rehberi DD79.
   - Kablo yolları DD85'te çizildi (çıkış yarıkları, omuz girişi, göz delikleri, boyun kanalı); kabloların kendisi ve döngüleri montajda. Satın alınan parçaların ölçüleri geldiğinde doğrulanır.
   - Sürüş kilidi çekirdekte (DD84): kol sürüş duruşunda değilken tekerler dönmez.
2. **İki parçalı plaka:** kirişler cıvatalı (M02); rijitlik ve ek yerinin sehimi gerçek baskıyla sınanır.
3. **TPU:** lastik–göbek tutunması (yapıştırma ya da geçme dişi); tampon penceresi kapakları; atma ağzı kapağının nesneyi geçirip geçirmediği.
4. **Motor:** JGA25 redüksiyonu, enkoder PPR'si ve 5° rampada ısınma ölçülür.
5. **E-stop:** 12 V DC ≥10 A kesme değeri (M3'te en kötü ≈9,4 A); kablo, sigorta ve anahtar yerleri.
6. **Göz kamerası:** ESP32-CAM anten yeri ve FPC bükülmesi göz kabuğu içinde; Wi-Fi sinyal testi.
7. **Kol:**
   - Servo kornası bağlantıları; omuz mili–korna kaplini.
   - Kol içindeki kablo yolu ve J2'de kablo burulması.
   - Pençe: dişli çiftinin deneme baskısı (boşluk, sıkışma), kornaya bağlantı delik aralığı ve gerçek nesnede kavrama (TL5).
   - Sol omuz bileziğinin ön yükü ve TPU pulun zamanla gevşemesi; sol kol taklitlerinin eklemleri elle zorlanınca oynamaması (TL5).
   - Kollar grubunun baskı payı 12 g'a indi: dilimlenmiş kütle tahsisi aşarsa sol kol taklitleri daha seyrek dolguyla basılır.
   - Servo rayı yeniden açılınca düşmüş kolun hızla dönmesi: yeniden ARM öncesi kol elle parka alınır (L4'te denenir).
   - Parkta dirsek ve bilek eksenleri düşeydir. Dirsek servosunun 1°'lik hatası pençeyi yan duvara ≈3 mm yaklaştırır; beş eklem birlikte ±1° saparken yan duvara 4,1 mm kalır (≥3 mm), bu yüzden her eklem ±1° içinde kalibre edilir (TL4).
8. **Balast dirençleri:** havalandırılan yerleri ve ısınması (sıkışmada direnç başına ≈5,9 W, kısa süre).
