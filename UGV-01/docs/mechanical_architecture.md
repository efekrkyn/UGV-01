# Mekanik CAD mimarisi ve üretim yaklaşımı

Rev A0 mühendislik baz çizgisi; [A1 dış görünüş ve ön kamera kavramı](exterior_language_A1.md) CAD'e işlenmiştir. PHASE4 detay CAD ve üretim resmi henüz onaylı değildir. Birincil parametrik kaynak `config/vehicle.json`. Koordinat x ileri,y sol,z yukarı; bütün aşağıdaki ölçüler mm.

## Ölçü zinciri ve bölmeler

| Özellik | A0 nominal | Gerekçe |
|---|---:|---|
| Dış boy / en |330 /270|300mm gövde+2×15mm tampon;240 iz+30 lastik |
| Ana gövde |300×200;z36…146|110mm muhafaza yüksekliği;yerden toplam146mm |
| Alt plaka |300×196×3|6061-T6;tek metal parça baskı sınırına tabi değil |
| Teker |Ø120×30|Yarıçap60;mil z60 |
| Dingil arası / iz |210 /240|Teker x±105,y±120 |
| Statik alt açıklık |36|Lastik ezilmesi/yük altında azalması ölçülecek |
| Gövde–lastik boşluğu |5 her yanda|120−15−100=5;yükte en az3 hedef |
| Motor altı–plaka üstü |2,5|60−18,5−(36+3);toleranslı dar yer kritik |
| Modül ayrımları |x=−50,+50|Üç100mm gövde segmenti |
| Kule arayüz |50×50,40×40 delik deseni|M4;ana kapağa değil travers/şasiye taşınan yük |

Tekerin x boyu105+60=165 ile toplam330'dur. Tamponlar z90…120 aralığında ve gövde eninde çalışır; tekerlerden daha dışa uzanmaz. 330mm hedefi korurken lastiğin en ileri noktası tamponla aynı hizada olduğundan teker tam çarpışma koruması yoktur; saha riskidir.

Yerleşim zarfları çakışmadan bile servis hacmi gerekebilir. A0 kart boyutları tasarım tahsisidir, üretici kart boyutu olarak sunulmaz:

| Bölüm | Dünya koordinatlarında ayrılan hacim | Servis yönü |
|---|---|---|
| Ön/arka motorlar |x merkez±105,Ø37;yan duvar içinden merkeze82mm |±y;motor+encoder kablosu için orta dar bölge korunur |
| UGV-PWR-01 |x−62…58,y−87…−7,z57…81 (120×80×24) |Üst raf çıkarıldıktan sonra+z |
| UGV-MCU-01 |x−62…78,y7…92,z57…81 (140×85×24) |+z;kenar güç konektörleri için ayrıca ölçü |
| CM5 IO+soğutma |x−22…138,y−45…45,z86…121 (160×90×35) |Ön/orta kapak;yan kenarlarda USB/Ethernet kıvrımı |
| Batarya paket tahsisi |x−142,5…−37,5,y−41…41,z83…138 (105×82×55) |Arka ayrı kapaktan+z |
| Kablo kanalları |y≈±95;orta boşluklar|Motor güç dış yanda,sensör/data üst orta |
| Kule |x=30,y=0,z≥146|Ana traverse dört M4;50mm kare arayüz |

**PH4/7 yerleşim engeli:** A0 z57–81 mm kutusu çıplak kart değil, PCB **ve bileşenler** için ayrılmış hacimdir. PCB altı z57 / 1,6 mm stackup varsayımında [Molex 768250004 dik açılı](https://www.molex.com/en-us/products/part-detail/768250004) takılı üstü yaklaşık z75,38 mm'ye ulaşır; önceki z81→z86 “yalnız 5 mm” ifadesi PCB üstünü yanlış yorumluyordu. KiCad 13,06×24,25 mm courtyard'u yatay kablo/mandal/çekip çıkarma hacmi değildir. PWR kartının y−87 ve MCU kartının y+92 mevcut dış kenarları, yönüne göre ±100 mm kabuk dışına taşabilir; iç kenarlar arasında ise yalnız 14 mm var. Kart kenarları veya modül/kanal zarfı gerçek üretici STEP + dişi housing + kablo/takım süpürmesiyle tasarlanmadan PH4/7 kapanmaz. [Kesit ve servis kapısı](electronics_packaging_gate.md), [elektrik pin sözleşmesi](pwr_mcu_interface.md).

Batarya8adet21700 hücreyi iki katta dörderli yatırarak yerleştirir;21,6mm en büyük çap,70,2mm boy ve hücre arası yalıtım hesaba katılır. 105×82×55mm BMS,bara,fishpaper,NTC,kasa dahil agresif bir tahsistir: gerçek paket üreticisi çizimi sığmazsa servis bölmesi yeniden boyutlanır. Hücreler gövdeye yapıştırılarak servis dışı bırakılmaz;sert kenarlar,vida uçları ve ezilme yükleri hücre kutusuna ulaşmaz.

## Datum ve bağlantı sözleşmesi

A: alt plaka üst yüzeyi z39; B: y=0 orta düzlem; C: x=0 orta düzlem. Plaka genel profil ±0,20;delik konumları A/B/C'ye göre±0,10 hedef CNC sonrası; bunlar A0 imalat talebidir, lazer kesimin kendiliğinden sağlayacağı iddia edilmez. Rulman yuvaları işlem görmüş metal insert/taşıyıcıdadır;basılı delik hassas geçme yüzeyi kabul edilmez.

Plaka arabiriminde x={−140,−70,0,70,140},y={−90,+90},10adetØ4,5 M4 geçiş deliği. Parça kenar mesafesi8mm (genişlik196/2−90);baş/pul taşması çizimde kontrol edilir. Kapak M3 bağlantıları her100mm segmentte x=(segment merkezi±38),y=±94. Gövde ayakları ile metal plaka M4;elektronik raflar M3. Somun erişimi içinalttan sürücü açıklığı,kapak vidaları içinüstten≥35mm alet zarfı hedef.

Heat-set insert yalnız ASA/uygun PA baskı kapak ve düşük/orta yük taşıyan muhafazalarda;M3 pilot deliği kullanılan insert datasheet'i+kupon testiyle seçilir (başlangıç örneğiØ4,0–4,2 değildir evrensel ölçü). CAD parametresi belirli insert seçilince doldurulur; A0 delikleri geçiş deliğidir. Motor/rulman ana yükünde metal travers ve somun/cıvata;polimerin sünmesine güvenilmez. Vida torkları M3/M4 diye tek değerle verilmez:malzeme,insert,yağlama ve bağlantı testi belirler.

## Yük yolu ve ilk mukavemet kontrolleri

8kg→78,45N statik. Ön tasarım düşey şok faktörü3g→235,4N;iki teker yük alırsa≈118N/teker. Bu bir düşme testi eşdeğerliği iddiası değil,boyutlandırma yük durumudur.3mm plaka için E=69GPa varsayımı,b=196mm,L=210mm basit mesnetli tüm genişlik kiriş modeli: I=bt³/12=4,41×10⁻¹⁰m⁴,merkezde235,4N ileσ=42,0MPa,δ=1,49mm.3g dağıtılmış yükte≈21MPa/0,93mm. Delikler,konsantre motor bağlantıları ve gerçek sınır şartları bu tarama modelinde yoktur;plaka tek başına rijitlik kabulü almaz. İki metal boyuna taşıyıcı/travers ile rijitlik artırılır; PH4 FEA + T11'de≤1mm geçici sehim/≤0,2mm kalıcı set aranır.

Motor taşıyıcı3mm6061 metal parçalarla 37mm motor gövdesini taşır;dört motorun tork reaksiyonu ve rulman yükü alt plakaya iner. Basılı PA-CF motor ayağı ana seçenek değil:ısı,nem,sünme ve z-yönü ayrılma nedeniyle metal daha öngörülebilir. PA-CF kablo/braket/kule parçalarında şartlı kullanılabilir.

Gövde basit duvar örneği:40mm genişlik,30mm konsol,20N elle bastırma altındaσ=6FL/(bt²). t=2,4mm→15,6MPa;t=3mm→10MPa. A0 ASA duvar3mm+kısa nervür seçimi yapılır;10MPa tasarım çalışma sınırı bir üretici izinli gerilmesi değil,kuponla doğrulanacak konservatif hedef. Darbe ve güneşte sıcaklık için yalnız oda sıcaklığı datasheet dayanımı kullanılmaz.

Kule0,30kg,80mm kol,3g yatay→0,706N·m. M4 desende40mm kuvvet çifti≈17,7N;bağlantı pulları ve metale bağlı travers bunu taşır. Pan/tilt servo seçiminde tilt ekseninden35mm öte150g kamera→0,0515N·m statik;ivme ve sürtünme ile en az3kat→0,155N·m aday tork. Servo stall torku sürekli kapasite değildir. Kütle merkezini tilt eksenine yaklaştırmak servo büyütmekten önceliklidir. Pan±90/tilt±45 sınırlarında kablo çekmesi/takılma yok;mekanik stop ve yazılım limitleri ayrı.

## Teker ve göbek

Ø120×30mm dış zarf;ilk prototipte özgün iki parçalı PAHT-CF/PETG test jantı,TPU değiştirilebilir sırt veya ticari lastikle kendi metal göbek adaptörümüz. TPU95A tutunma katsayısı ve aşınma ölçülmeden saha lastiği sayılmaz. JanttaØ80mm iç sırt referansı ve4×M3,Ø36mm bolt circle kavramı;lastik ve göbek satın alma çizimiyle PH4'te kesinleşir. Jant iki yarım,kontrollü sıkma ve somun yakalama;somun gevşemesine işaret boyası/kilit elemanı.

Motor6mm D-miline yalnız setskurla konsol teker asılmaz. Ayrı yataklı göbek/mil,eksenel tutucu,metal sıkmalı kaplin ve gövdeye bağlı rulman yük yolu ayrılır.35mm'lik radyal/yatak paketi zarfı,5mm lastik–gövde boşluğu ve16mm motor çıkış mili birlikte PH4 kritik tasarım konusudur. A0 teker/motor modeli zarf ve merkezleri gösterir;nihai rulman dizilişini üretime hazırmış gibi sunmaz. Çözüm sığmazsa iz/genişlik veya motor yerleşimi kararı yeniden açılır.

## Parça ve proses listesi

| PN | Adet | İşlev | Malzeme/proses | Parça nominal en büyük zarf | A0 / sonraki kontrol |
|---|---:|---|---|---|---|
|UGV-MECH-001|1|Alt plaka|6061-T6,3mm;CNC veya profil lazer+delik CNC|300×196×3|Metal;baskı değil |
|UGV-MECH-002|2|Boyuna yük taşıyıcı|6061-T6 işlenmiş profil|150×12×15|PH4 kesit/mesnet doğrula |
|UGV-MECH-003|4|Motor taşıyıcı|6061-T6 CNC;3mm başlangıç|50×45×35|37D çizimiyle delik+yuva |
|UGV-MECH-004|4|Rulman taşıyıcı|6061-T6 CNC|45×45×20|Rulman uyumu,koaksiyellik |
|UGV-MECH-005|4|Göbek/kaplin|Alüminyum göbek+çelik mil|Ø40×35|Tork ve aksiyel tutma |
|UGV-MECH-010|1|Ön gövde modülü|ASA baskı|100×200×104|Sensör açıklıkları PH4 |
|UGV-MECH-011|1|Orta gövde modülü|ASA baskı|100×200×104|Servis,kablo kanalı |
|UGV-MECH-012|1|Arka gövde modülü|ASA baskı|100×200×104|Batarya servis |
|UGV-MECH-013|3|Üst kapak|ASA baskı|100×200×3|Conta/insert kuponu |
|UGV-MECH-014|1|Batarya tutucu|Açık tutucu+yalıtım+metal kayış|115×92×8|Isı ve basma yükü,metal kayış |
|UGV-MECH-015|1|MCU/PWR rafı|6061 sheet veya ASA izole adaptör|150×184×8|Hotspotlara metal soğutma |
|UGV-MECH-016|1|CM5 rafı|ASA adaptör+metal mesnet|176×112×8|160×90 kart,delikler üretici |
|UGV-MECH-017|2|Tampon|TPU95A baskı|200×15×30|Değişir,üstüne kaldırma yükü yok |
|UGV-MECH-018|2|Yan kablo kanalı|ASA baskı,her tarafiki segment|140×12×12|Toplam4segment baskı |
|UGV-MECH-019|4|Kablo geçişi|TPU baskı|30×20×10|Gerilim tahliye |
|UGV-MECH-020|8|Teker jant yarısı|PAHT-CF veya testPETG|Ø80×15|Islak/sıcak mekanik kupon |
|UGV-MECH-021|4|Teker sırtı|TPU95A test /satınalma lastik|Ø120×30|µ,sertlik,aşınma ölç |
|UGV-MECH-030|1|Kule tabanı|6061/PAHT-CF koşullu|60×60×15|Yük şasiye |
|UGV-MECH-031|1|Kule kolon|PAHT-CF|50×50×80|Katman yönü,yük testi |
|UGV-MECH-032|1|Pan kızağı|PAHT-CF|70×60×25|Servo ölçüsü sonrası |
|UGV-MECH-033|1|Tilt çatalı|PAHT-CF|80×60×50|Kamera/servo erişimi |
|UGV-MECH-034|4|Kamera izolatörü|TPU|Ø12×8|Aşırı yumuşaklık kalibrasyonu bozar |

## DFM ve sıcaklık

ASA dış kabuk UV için;kapalı bölümde parça sıcaklığı hedef≤60°C,bu uygulama limiti kupon+ısıl testle kalifiye edilir. PETG sadece≥10°C termal pay gösteren serin prototipte (başlangıç≤45°C). PAHT-CF/naylon kuru/ıslak farklı davranır;nem almış en zayıf yön verisi kullanılır;«CF» metal eşdeğeri anlamına gelmez. TPU darbe/kablo/izolasyon için,vida ön yükü veya ana taşıyıcı için değil. Batarya yakını elektriksel yalıtkan kaplama,CF parçalarda iletkenlik/kısa devre riski kontrolü.

Baskı:ASA0,4mm nozzle,0,2mm layer,≥4 perimeter;3mm ana duvar,2mm yardımcı nervür,vida boss çevresi≥3mm et;PAHT-CF için0,6mm sertleştirilmiş nozzle ve0,24–0,28mm layer başlangıcı;üretici filament kurutma profili kullanılır. Filament profili mekanik dayanım onayı değildir. Parçalar taban flanşı düz basılır,yük katmanları ayıracak yöndeyse bölünür/metal eklenir. >45° çıkmalar pah/gusset;ana hassas montaj yüzeyleri destek üzerine basılmaz.3mm kapaklar düz,TPU tampon düz geniş taban;PA parçalar delik çevresini sürekli perimeter ile saracak yön.

FDM genel tolerans başlangıcı±0,30mm;geçmeli muhafaza içinher yanda0,30mm,modül ekinde0,50mm toplam boşluk. Birlikte değişen delik dizilerinde tolerans yığılması:2×0,30 +metal0,10=0,70mm olası uyumsuzluk;bir datum deliği+diğerlerinde uzun delik/boşluk tasarlanır. Rulman H7/h6 benzeri geçmeler yalnız metal işlenmiş parçalar ve seçilmiş rulman datasheet'i ile verilir. Vida çapına bakıp rastgele press-fit atanmaz.

P2S256mm hacim kullanıcı girdisidir. Tasarım≤240mm basılıparça hedefiyle brim/kenar payı bırakır. Filament üretici teknik verisi yön ve nem bağımlıdır; [Bambu filament kılavuzu](https://cdn1.bambulab.com/filament/filament-guide/bcv8wbl4hj/filament-guide-en.pdf) seçilecek belirli malzemenin TDS'sine başlangıçtır. Mekanik mukavemet sayıları burada tedarikçi sertifikası değil mühendislik taramasıdır.

## PH2 ve PH4 ayrımı

PH2 teslimi:ortak geometri,montaj arayüzü,yerleşim zarfları,kavram parametrik CAD,çakışma/print envelope kontrolü. PH4 teslimi:gerçek motor/rulman/konektör STEP'leri,imalat boşlukları,conta/insert,çıkarma yolları,tolerans yığını,FEA/kupon sonuçları veher parça içinSTEP/STL/çizim. PH2 dosyaları üretime gönderilmez.

## A0 inceleme düzeltmeleri

Batarya 105×82×55 mm **kasa dahil** tek zarftır; PN014 ikinci kapalı kutu değildir. Altı z83, üstü z138; kapak altı z143 ile 5 mm nominal pay, arka motor üstü z78,5 ile 4,5 mm pay bırakıldı. Batarya x merkezi−90; arka duvar iç yüzeyi−147 ile paket−142,5 arasında 4,5 mm var. Ana gövde üstü **146 mm** olarak revize edildi: yaklaşık140 mm hedefinden6 mm sapma, hücre/kapak ve motor toleransını sıkıştırmamak için. Bu değişiklik SYS-003/ DD21 ile kayıtlıdır.

İki metal boyuna rijitleştirici x=−75…75,y merkezi±75,z=39…54,kesit12×15 mm. Motor x zarfı86,5…123,5 olduğundan rijitleştirici motorla kesişmez; PCB zarfı z57'de başlar ve3 mm dikey pay kalır. Bu kısa rijitleştirici tüm210 mm dingil açıklığını köprülemez; önceki1,49 mm basit plaka sehimi bu nedenle kapanmış değildir. PH4'te motor taşıyıcı/mesnetlerle bütün yük yolu yeniden analiz edilir.

70 mm gerçek motor gövdesi +12 mm encoder/kablo servis payı=82 mm tahsis. Motor yüzünü gövde duvarında sayıp16 mm mili teker merkezine doğrudan ulaşıyor varsaymak geçersizdir; bağımsız yataklı göbek tasarımı açık PH4 işidir.

PH2 CAD parça ayrımı: PN010/011/012 her modülde iki ayrı yan paneldir; kapak PN013, ön/arka son duvar PN022 olarak ayrı basılır. Böylece her STL tek parça kalır. Kavram modelindeki geniş ayaklar/kapak bossları nihai insert, uzun delik ve kablo detayları değildir.
