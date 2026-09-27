# M3: karakter gövdesi ve 5 eksenli kol — tasarım

25.09.2026. Kullanıcı isteği (özet):
- Motorlar bu kadar büyükse gövde de büyüsün ve motorlar gövdenin içine girsin.
- Kameranın gövdeye uzaklığı aynı kalsın; robot karakter hedefine daha çok benzesin.
- Kol yandan çıksın. Kol yalnız ileri-geri hareket etmesin; bunun için "overengineering" isteniyor.
- Boş hacim değerlendirilebilir; maliyet biraz artabilir.

Kullanıcı **bütün kararları bana bıraktı** ve bilgisayar başında değil; bu belge verdiğim kararların kaydıdır. A3 Lite mimarisi değişmez: robotta ESP32-S3 ve iki ESP32-CAM, AI ve panel MacBook'ta. Fiziksel test yapılmadı; hepsi NOT_RUN.

## Kararlar

### 1. Gövde (DD72)

| | A3 (önce) | M3 |
|---|---|---|
| Gövde U × G × üst | 300 × 200 × z146 | 300 × **236** × **z210** (yükseklik 110 → 174 mm) |
| İz genişliği / toplam genişlik | 240 / 270 | **278 / 308** |
| Dingil mesafesi / toplam boy | 210 / 330 | değişmez |
| Motor | Dişli kutusu yüzü duvarın 1 mm dışında | Yüzü duvarın **içinde** (\|y\| = 114). Duvardan yalnız göbek boynu (Ø16) geçer, delik Ø18 |
| Baş | Eğim ekseni z268 | **z332**: eğim ekseni ile gövde üstü arası **122 mm** korunur |
| Tekerlek üstü | Açık | Tekerlekleri örten **çamurluk** (palet üstü görünümü gibi); kolun park yeri |

- Ön görünüş kareye yaklaşır (236 × 174). Tekerlekler gövde yüksekliğinin yaklaşık yarısını örter; palet görünümünde de oran budur.
- Gövdenin iç hacmi yaklaşık 2,6 kat büyür.
- JGA25'in D-mili 11,5 mm'dir. Motor yüzü içeride olduğu için göbek, duvardaki delikten içeri uzanan bir boyunla mile ulaşır. Mil göbeğe 8,5 mm girer.
- Sıkma vidası, gövdeyle teker arasındaki 6 mm'lik aralıktadır.

### 2. Kol (DD73)

A3 kolu tek eksenliydi (omuz, ileri-geri). M3'te sağ kolda **5 eksen ve bir pençe** var; omuz gövdenin yan duvarından çıkar.

| Eklem | Eksen (sıfır duruşta) | Servo | Neden |
|---|---|---|---|
| J1 omuz | y (yan duvardan geçer) | **DS3218MG 270°**, gövdenin içinde. Kolun yükünü duvardaki **6804-2RS** rulman taşır | Park (180°, geriye) → yukarı → öne (−45°): 225° dönüş. Dişlisiz, doğrudan tahrik |
| J2 üst kol dönüşü | Kol ekseni | MG996R + 6804-2RS | Dirseği içe ya da dışa büker; kol gövdenin önüne ve ortasına uzanır |
| J3 dirsek | y | MG996R | Erişim ve yükseklik |
| J4 bilek eğimi | y | MG996R | Pençenin yaklaşma açısı. MG90S, 150 g yükte 1,5 kat tork payı vermiyordu |
| J5 bilek dönüşü | Kol ekseni | MG90S | Nesneyi döndürür |
| J6 pençe | — | MG90S | Açar, kapatır |

- **Boyutlar:** omuz–dirsek 100 mm, dirsek–bilek 90 mm, bilek–kavrama merkezi ≈85 mm. Omuzdan parmak ucuna ≈285 mm. Parkta kol gövdenin yanı boyunca uzanır ve arka tekerleğin arkasından taşmaz.
- **Park:** J1 = 180°, J2 = 90°. Kol çamurluğun üstünde yatar; servo rayı kesilince ağırlığı çamurluğa biner. Dirsek ve bilek eksenleri düşey olduğu için yerçekimi bu eklemleri döndürmez.
- **Sol kol:** dıştan sağ kolla aynıdır ama **pasiftir**. Eklemleri sürtünmeyle tutulur, elle poz verilir. Omuzunda aynı rulman var. Servo yuvası ihtiyaç olunca eklenir (YAGNI).
- **Duruş grafiği:** park ↔ yukarı ↔ hazır ↔ {öne, yere, öne-orta}, ayrıca yukarı ↔ depola.
  - MacBook iki duruş arasında eklem uzayında doğrusal geçer; bütün eklemler hedefe aynı anda ulaşır ve hız sınırlıdır.
  - CAD her kenarı örnekleyerek çakışma arar.
  - Yürütücü kolu yalnız bu grafik üzerinde hareket ettirir.
  - Firmware eklem sınırlarını ve hızı ayrıca uygular.
- **Tork ölçütü:** kol yatay ve 150 g yük uçtayken her eklemde katalog stall torkunun (4,8/5 V) en az 1,5 katı gerekir. Test bunu config'ten hesaplar.

### 3. Boş hacim: kargo bölmesi (DD74)

Robot topladığı şeyleri gövdesinde saklar. M3'te de:
- Ön kapakta, sağ kolun erişebildiği bir **atma ağzı** açılır.
- Ağzın altına askılı bir **kutu** konur. Kutu ön-üst bölgededir; elektronik tepsisinin ve balast rafının üstünde kalır.
- Kol "depola" duruşunda nesneyi ağzın üstünde bırakır.
- Ağızdaki esnek TPU yarıklı kapak tozu tutar, düşen nesneyi geçirir.
- Kutu, kapak kaldırılarak boşaltılır.

Ön duvarda açıklık yok. Yandan gelen kol, önden sokma açısına ulaşamıyordu: dirsek hep kol düzleminde kalıyor (\|y\| = 136).

### 4. Elektronik (DD75)

- **PCA9685:** 8 servo var ama ESP32'de boş GPIO kalmadı. PCA9685 8 kanal PWM verir; I²C0 hattında, 0x40 adresinde, VL53L0X'lerle aynı hatta.
  - GPIO39 = `SERVO_OE`. 10 k pull-up sayesinde reset ve açılış sırasında çıkışlar kapalıdır.
  - GPIO40–42 boşa çıkar.
- **Servo rayları:** Servo akımı arttığı için iki Mini560 5 V 5 A servo rayı var; ikisinin de EN'i `ACT_EN`'e bağlı.
  - A rayı: J1, J3 ve baş servoları.
  - B rayı: J2, J4, J5, J6 (uygulamada tutma akımını dengelemek için J2 B'ye alındı).
  - Servolar gücü yalnız bu raylardan alır; PCA9685'in V+ hattı kullanılmaz.
- **Sigorta:** 10 A → 15 A. E-stop kontağının 12 V DC'de ≈10 A kesebildiği doğrulanmalı; bu önceden de açık bir işti.
- **Protokol:** 0x121 aynı kalır (omuz, pençe, bayrak). Yeni çerçeveler **0x122** (J2, J3) ve **0x123** (J4, J5). Oturum etiketi ve ileri sıra numarası aynı kurala uyar. **DD76 ile değişti:** 0x122 kol yolu çerçevesi (kaynak, hedef, kesir) oldu, 0x123 kalktı; kolu çekirdek yürütür.

### 5. Bütçe, kütle, tahrik

- **Bütçe:** tavan **10.000 → 13.500 TL** (ilk tahmin 12.500 TL'ydi; J1 servosunun yerel fiyatı 1.100 TL çıktı). Kullanıcı "maliyet biraz daha artabilir" dedi ve kararı bana bıraktı. Ek kalemler servolar, PCA9685, rulmanlar, üçüncü PETG makarası ve buck. Kullanıcıya fark kalem kalem ve kısma seçenekleriyle raporlanır.
- **Kütle:** brüt kütle 4,0 kg'dan yaklaşık 4,9 kg'a çıkar.
- **Pivot:** iz genişlediği için pivot sınırı pek değişmez.
- **Rampa:** boş pakette 5° rampada hız düşer; config'teki rampa hız sınırının güncellenmesi gerekebilir.
- **CG:** yüklü CG sınırı 110 mm'den 130 mm'ye çıkar; statik devrilme açısı ≥30° kalır.

## Başarı ölçütleri (test)

- `check_cad`:
  - Gövde ölçüleri.
  - Motorlar bütünüyle duvar iç yüzünün içinde; göbek boynu delikten geçer; mil göbeğe ≥7 mm girer; sıkma vidası aralıkta.
  - Çamurluk tekerleğin üstünü örter.
  - Eğim ekseni − gövde üstü = 122 mm.
  - Bütün duruşlar ve grafik kenarları çakışmasız.
  - Parktaki gevşek kol çamurluğa oturur.
  - Her eklemde tork ≥1,5 kat.
  - Kutu ağzın altında; ağızdan kutuya düşüş yolu açık.
- `check_design`: yeni kütle, CG ve tahrik sınırları.
- `check_body_mass`: grup tahsisleri ve makara sayısı.
- `check_esp32_pinmap`, `check_lite_wiring`, `check_lite_bom`: PCA9685, OE, iki servo rayı, adetler, 13.500 TL tavanı.
- C ve Python testleri: 8 servo, 0x122/0x123 çerçeveleri ve duruş grafiği yürüyüşü (yalnız kenarlar üzerinden).
