# D1 — bağımsız yataklı tahrik modülü

22.09.2026 · Detay tasarım adayı; PH3/PH4 üretim geçişi **açık**.

## Sonuç ve revizyon sınırı

Bir teker için 8 özgün parça ve 5 ticari komponent zarfı modellendi. Dört modülün değiştirilmiş gövdeyle yerleşimi 75 katı parça içerir. Modül içinde ve araç yerleşiminde >0,01 mm³ hacimli çakışma bulunmadı. Bu sonuç cıvata başı, takım erişimi, kablo hareketi ve yük altındaki deformasyonu kapsamaz.

D1 dış genişlik **300 mm**, iz **270 mm** adayıdır; uzunluk330, dingil arası210 ve Ø120 teker korunur. İki rulman ve 31,8 mm kaplini 270 mm dış genişliğe sıkıştırmak yerine kullanıcının 250–300 mm aralığının üst sınırı kullanılır. Ana A0 `vehicle.json`, URDF ve kavram CAD korunmuştur. D1 yalnız `config/drivetrain_module.json` ve `cad/drivetrain` altındadır; henüz A0'ın yerine üretim baz çizgisi olarak geçirilmedi.

## Üretici çiziminden gelen düzeltme

[Pololu ölçü çizimi, encoder'lı sayfa](sources/pololu-37d-dimensions.pdf): 70:1 için redüktör24 + motor30,7 + encoder15,4 = **70,1 mm**. Ön yüzden mil ucuna22 mm, Ø12 merkezleme çıkıntısı6 mm; dışarıda kullanılabilir Ø6 D mil **16 mm**. Bunlar aynı ölçü değildir.

Çıkış mili gövde merkezinden7 mm kaçık. Motoru çıkış ekseni çevresinde90° çevirerek gövde merkezini z yönünde yükseltmeden x yönünde dışarı alıyoruz. Ön motorda merkez x=112, arka motorda−112 mm; teker eksenleri±105 mm. Ø31 PCD üzerinde altı M3 delikten dördü kullanılır. Yerel x koordinatları−6,423 ve20,423; z52,25 ve67,75 mm. Üreticinin **3 mm azami vida girme derinliği** aşılmayacak. Başlangıç M3×6 + 0,5 mm pul + 3 mm taşıyıcı ≈2,5 mm diş angajmanı; tolerans ve pul gerçek kalınlığı kontrol edilecek.

Motor gövdesi modelde tam boy Ø36,8 zarfla muhafazakâr temsil edilir; gerçek motor/encoder basamakları ve kablo çıkışı modellenmedi. Motorlar arası merkez boşluğu9,8 mm; encoder kabloları radyal yönde yönlendirilmeli, fiş bu boşluğa zorlanmamalı.

## Yük yolu ve hesap

Lastik → sekiz jant tırnağı → jant/göbek cıvataları → çelik mil → iki rulman → alüminyum taşıyıcı → dört M4 → alt plaka. Motor mili yalnız sürüş torku aktarır. Kaplinin radyal kaçıklığı karşılama kapasitesi montaj hatasını sınırsız kabul etmez.

Ön eleme varsayımları:8 kg toplam,3g düşey eşdeğer yük iki tekerde, yanal sürtünme katsayısı1,0; teker yarıçapı60 mm. **Bu bir düşürme testi veya yorulma hesabı değildir.** 3g ve μ=1 deneyle doğrulanmamış tasarım yükleridir.

Fz=8×9,80665×3/2=117,680 N; Fa=Fz. Yanal temas kuvvetinin devrilme momenti M=Fa×0,06=7,061 Nm. Rulman merkezleri123,5 ve137 mm, temas düzlemi135 mm. Mesnet açıklığı13,5 mm. En kötü radyal reaksiyon = max(|Fz(b−yc)/L|, |Fz(yc−a)/L|)+M/L =623,267 N.

| Kontrol | Sonuç | Sınır / kapsam |
|---|---:|---|
| Rulman statik payı C0/P0 | 3,145 | Ön hedef≥2; P0=max(Fr;0,6Fr+0,5Fa) |
| 8 mm mil akma payı | 1,186 | Yetersiz; adaydan çıkarıldı |
| 10 mm mil akma payı | 2,317 | Ön hedef≥2; yorulma henüz yok |
| 5 mm taşıyıcı taban gerilmesi | 82,376 MPa | Efektif genişlik54 mm ve1,5 gerilme katsayısı varsayımı |
| Taşıyıcı akma payı | 2,913 | 6061-T6 minimum240 MPa varsayımı; sertifika şart |
| Kaplinin mil tutma boyu | 11,5 mm | Üretici üst sınırı11,9 mm; aksiyel yığılma incelemesi açık |

Mil hesabı: σ=32M/(πd³), τ=16T/(πd³), σeq=1,8√(σ²+3τ²), T=1,5 Nm. C45 normalize malzemede minimum305 MPa akma varsayılmıştır; stok çapı/ısıl işlem sertifikasıyla doğrulanmalıdır. 1,8 çentik katsayısı ölçülmüş değer değildir. Tam devrilme momenti rulmanlar arasına uygulanır; iç rulmanın gerisindeki segman kanalı bu modelde aynı eğilme momentini taşımaz. Gerçek omuz radyüsleri, kanal, kaplin yan kuvveti ve yorulma için ayrı kontrol zorunlu.

8 kg nominal brüt hedef aşılabileceği için aynı mekanik tarama **9 kg** ile de çalıştırılır: 10 mm milin ön akma payı yaklaşık2,06, statik rulman payı yaklaşık2,80 ve taşıyıcı payı yaklaşık2,59. Bunlar 9 kg çalışma kapasitesi ilanı değildir; eğim sürüşü ve motor ısısı 8 kg için bile ayrıca kapanmalıdır.

Taşıyıcı kök momenti Fz×45 mm+M=12,357 Nm. Basit kiriş modeli taban/delik/yuva birleşimindeki 3B gerilmeyi doğrulamaz. Fillet, delik kenarları, taban esnemesi, rulman eksen kaçıklığı ve 3 mm ana plaka FEA + yük testiyle kapanacak.

## Aksiyel istasyonlar — sol modül, mm

| Unsur | y başlangıç–bitiş |
|---|---|
| Motor gövdesi | 4,9–75 |
| Motor merkezleme çıkıntısı | 75–81 |
| Motor kullanılabilir D mili | 81–97 |
| Oldham kaplin dış zarfı | 85,5–117,3 |
| Özgün mil başlangıcı | 105,8 |
| Segman zarfı / kanal | 117,8–118,7 /117,7–118,8; nihai değil |
| İç bilezik destek pulu | 118,8–119,5 |
| İç rulman | 119,5–127,5 |
| İki ayrı ara bilezik | 127,5–133 |
| Dış rulman | 133–141 |
| Mil omzu / taşıyıcı dış dudağı | 141–143,5 /141–143 |
| Milin göbek flanşı | 143,5–147 |
| Jant dış gövde bağlantı yüzeyi | 147–150 |
| Lastik | 120–150 |

Ø26 ortak rulman deliği tek bağlamada işlenecek. İç ve dış bilezik için ayrı çelik ara bilezikler vardır. Mil dıştan, rulmanlar iç taraftan yerleştirilebilir; kesin işlem sırası seçilen geçmelere bağlıdır. Flanşın ve dış halkanın taşıyıcıya sürtünmemesi için nominal0,5 mm boşluk ayrılmıştır. Rulman ön yükü rastgele sıkılan kapakla ayarlanamaz; gerçek parçalar ölçülüp şimlenecek.

**Açık toleranslar:** 10 mm mil rulman geçmesi, Ø26 taşıyıcı deliği geçmesi, segman üretici/kanal ölçüsü, yatak omuz çapı/radyüsü ve termal genleşme. CAD'deki yuvarlak nominal ölçüler H7/k5 kabulü veya üretim talimatı değildir. Sızdırmaz rulmanın keçe yüzeyine omuz/bilezik temas etmeyecek; gerçek SKF kesit çizimiyle omuzlar kontrol edilecek.

### Ölçü zinciri ve montaj fizibilitesi

Motor milinin Ø6 kullanılabilir ucu16 mm; 85,5 mm kaplin başlangıcıyla nominal11,5 mm göbek tutması, üreticinin11,9 mm azami değerine yalnız0,4 mm pay bırakır. Motor mil uzunluğunun toleransı çizimde verilmediğinden seri siparişten önce gerçek dört motor ölçülecek. Aksiyel kaplin pozisyonu ve disk boşluğu üreticinin montaj talimatına göre ayarlanacak; motor milini kaplin diskiyle eksenel olarak sıkıştırmak yasaktır.

Yatak dış bilezik zinciri8+5,5+8=21,5 mm; taşıyıcının kapak yüzü119,5 ile dış dudak141 arası da21,5 mm nominal. İç bilezik zinciri de omuz ile tutma pulu arasında aynı nominal uzunluktadır. **Nominal eşitlik gerçek ön yük ayarı değildir.** Katalog toleransları, alın paralelliği ve alüminyum/çelik genleşmesi nedeniyle sıkışma veya boşluk oluşabilir. İlk numunede iki rulman, iki ara bilezik, omuz ve kapak gerçek ölçülüp seçici şim kullanılacak. Eksenel endplay ve sıcaklık artışı ölçülmeden çizime hedef boşluk konmayacak.

Mil iç bileziğe interferanslı, gövde dış bileziğe kayar geçme seçilirse çıplak mil dışarıdan sokulur, rulmanlar iç taraftan iç bilezik destekli fikstürle mile geçirilir; dış bilezikler gövdeye düşük kuvvetle kayar. **Bu sıra geçme ve takım onayı koşulludur.** Hem mil hem gövde sıkı geçme seçilirse bilyalar üzerinden pres kuvveti geçirilmemesi için farklı fikstür ve işlem gerekir. Serviste iç bileziği kavrayabilen çekici erişimi de gerçek donanımla kontrol edilecek.

Taşıyıcı tabanındaki M4 deliklerin ikisi x=−22, ikisi x=35 mm; y=70/90 mm. Dört modülde16 bağlantı vardır. Eski alt plakadaki x=±140,y=±90 konumlu **dört delik aynen yeniden kullanılır**;12 yeni delik açılır. Böylece1 mm kayık deliklerin birleşmesi önlendi. Taşıyıcının x=35 tarafında delik merkezinden dış kenara5 mm, Ø4,5 delik kenarından dış kenara2,75 mm kalır. Cıvata başı/oturma yüzeyi ve3 mm şasinin cıvata çekmesi ayrıca incelenecek. D1 DXF'leri yalnız taban ve motor yüzü delik arayüzünü gösterir; yükseltilmiş yatak bloğu için tam işleme çizimi değildir.

## Parça listesi ve imalat

| PN | İşlev / adet araçta | Proses | Yaklaşık tek kütle |
|---|---|---|---:|
| UGV-MECH-040 | Motor ve iki yatak taşıyıcısı /4 | 6061-T6 CNC; taban5 mm, motor yüzü3 mm |101 g |
| UGV-MECH-041 | Rulman dış bilezik kapağı /4 | Alüminyum CNC veya levha + delik |3,2 g |
| UGV-MECH-042 | Mil ve tek parça göbek flanşı /4 | C45 torna + delik freze; omuz/kanal final değil |91,8 g |
| UGV-MECH-043 | İç bilezik mesafesi /4 | Çelik torna |4,2 g |
| UGV-MECH-044 | Dış bilezik mesafesi /4 | Çelik torna |4,8 g |
| UGV-MECH-045 | İç tutma pulu /4 | Çelik hassas şim/torna |0,5 g |
| UGV-MECH-046 | Tırnaklı jant /4 | PAHT-CF aday; baskı kuponu şart |56,1 g |
| UGV-MECH-047 | Kaburgalı lastik /4 | TPU95A aday; elastik davranış testi şart |95,6 g |

Katı hacim yoğunlukları: Al2,7, çelik7,85, polimerler şimdilik1,2 g/cm³. Polimer doluluk ve gerçek filament yoğunluğu ayrıca ölçülecek. Taşıyıcı ön/arka ve sağ/sol aynalanır; dört yön için işleme tanımı gereklidir. Motor, kaplin ve rulmanlar ticari bileşenlerdir.

Jantta çevresel üç mm nominal namlu, üç mm dış web, sekiz tırnak bulunur. TPU lastikte altı mm dış sırt, iki mm yan duvar ve sekiz radyal kaburga vardır. Tırnak ceplerinde0,2 mm/yan nominal boşluk; nominal CAD temas/boşluğu baskı geçmesi garantisi değildir. Torku yalnız sürtünmeye bırakmadık. 1,5 Nm için sekiz tırnağa eşit dağılım yaklaşık4 N/tırnak; gerçekte yalnız iki tırnak yük alabilir:16 N/tırnak ve tekrarlı ters tork kuponda denenir.

İki mevcut jant omzu TPU yanağını **pozitif eksenel kilitlemez**. D2A lastik sırtı inceltmesi de bu sorunu çözmez. PH4'te sökülebilir dış tutucu halka veya baskı toleransı doğrulanmış mekanik kanal tasarlanacak; 40 N/teker yanal ön tarama ve yüklü pivotta yanağın yer değiştirmediği gösterilecek. Bu ek parçanın kütlesi 67 g araç rezervine sığacak diye varsayılmaz.

Jant ekseni baskıda dik; dış web aşağı. TPU aynı eksende basılır; kapalı yan duvar ve üst kaburga geçişlerinde köprüleme/sökülemeyen destek riski var. Baskı denemesi başarısızsa lastik kesiti açık nervürlü veya iki parçalı tasarıma döner. Bu STL'ler **fit/DFM adayıdır**, işlevsel lastik kalifikasyonu değildir. Başlangıç sertleştirilmiş0,6 mm nozzle,0,2 mm katman; kurutma/sıcaklık filament üreticisine göre. Metal taşıyıcı yerine PA-CF basıp aynı yük değerlerini kabul etmiyoruz. Baskı anizotropisi nedeniyle metal burç/pul, web ezilmesi ve sürünme testi açık.

## Montaj ve servis sırası

1. Taşıyıcı ortak yatak deliğini, motor deliklerini ve taban düzlüğünü ölç; mil ve her bilezik geçmesini ölç. Pres/kayar geçme kararı verilmeden deneme montajı yapma.
2. Koşullu kayar dış bilezik çözümünde mil dış taraftan yerleştirilir. Dış rulman iç taraftan milin iç bileziği desteklenerek omza götürülür; sonra iki ayrı bilezik ve iç rulman yerleştirilir. Dış halka gövdeye sürtünmeli presleniyorsa bu sıra geçerli değildir ve takım planı yeniden çizilir.
3. İç tutma pulu, nihai seçilmiş segman ve ölçüye göre şimle eksenel tutmayı kur. Kapağı dış halkaya oturt, keçeyi sıkıştırma. Pres yükünü bilyalardan geçirme.
4. Motoru dört M3 ile tak; girme derinliğini ölç. Kaplin göbeklerini iki mile tak, üreticinin montaj açıklığı ve sıkma torkunu uygula. Diskin belirtilen montaj sırası gerçek komponentle doğrulanacak.
5. Jant ve TPU'yu sekiz tırnak eşleşecek şekilde birleştir; Ø44 PCD dört M3 havşa vida + somunla flanşa sabitle. Baş çapı, havşa standardı, boy ve kilitleme henüz satın alma çizimiyle kapanmadı.
6. Modülü şasiye dört M4 ile bağla. Gövde modül pencereleri ve eski uç ayakların kaldırılması D1 araç yerleşiminde işlenmiştir. Kalan gövde ayaklarının dayanımı açık.
7. Teker elle sürtünmesiz dönmeli. Rulman boşluğu, jant salgısı, segman oturması ve vida erişimi ölçülmeden motor enerjisi verme.

Tek tekerin dışarı sökülmesi için jant cıvataları dışarıdan erişilir; komple modül için üst servis kapağından dört M4 erişimi gerekir. Kaplin/segman servisi teker+modül sökülerek yapılır. CAD'de tornavida, segman pensesi ve cıvata başı hareket zarfları henüz yoktur; erişim onayı verilmedi.

## Kütle, maliyet ve durdurulan geçiş

A0'ın0,65 kg teker/göbek/yatak bütçesi bu detayla yaklaşık1,33 kg olur (kaplin40 g ve segman2 g/adet varsayımı dahil). Metal ana plaka/iki ray/dört taşıyıcı/kapak yaklaşık1,04 kg; önceki0,80 kg bütçesini aşar. Diğer A0 kalemleri değişmezse0,90 kg rezerv tüketildiğinde bile yaklaşık**6,02 kg boş kütle** çıkar; başlıkların yuvarlanması nedeniyle bu hassas bir tartım tahmini değildir. Eksik bağlantı elemanları ve kablolarla daha da artabilir. **6 kg hedefi henüz sağlanmıyor; kütle rezervi sıfır.** D1'i ana baz çizgiye geçirmeme nedenlerinden biri budur. Metal boşaltma/teker hafifletme ancak yük yolu yeniden kontrol edilerek yapılacak.

Ek BOM `manufacturing/bom/drivetrain_D1.csv` içindedir. Eski BOM'daki teker/göbek/yatak kalemlerinin **yerine** geçecek adaydır, toplam bütçeye doğrudan eklenmez. CNC işçilikleri teklif değil tahmindir; stok garantisi yok. Pololu4754 resmi sayfada bu incelemede60,95 USD/adet görünüyordu; önceki55 USD/adet tahmini güncellenecek.

`cad/drivetrain/budget_report.json` güncel geometri hacminden metal ve polimer kütlesini yeniden hesaplar:6,025 kg boş kütle (rezerv hariç) ve hedefe göre25 g açık. Aday tahrik alt BOM'u1.333,80 USD tahmindir; A0 toplam BOM'unun üzerine eklenmez. Kütle azaltma hedefi yalnız25 g değildir: ölçülmemiş parçalar için en az0,3 kg rezerv istenirse mevcut varsayımlarla yaklaşık0,325 kg tasarruf gerekir. Bu ancak tartım ve yük testiyle güvenli boşaltma doğrulandıktan sonra tasarım kararı olur.

## Faz kapanışı için testler

| Kontrol | Ölçüm / kabul hedefi | Durum |
|---|---|---|
| Hesap regresyonu ve tek parça sürekliliği |13 pozitif/hatasız STEP; tüm özgün parçalar tek katı | Masaüstü kontrolü geçti |
| Modül ve dört teker yerleşimi | Katı çakışma>0,01 mm³ yok; 16 M4 şasi deliği | Masaüstü kontrolü geçti |
| Rulman/kaplin montaj numunesi |11,5 mm tutma boyu; üretici aksiyel açıklığı; serbest dönüş | Fiziksel test yapılmadı |
| Mil/yatak tolerans numunesi | Ölçülmüş geçme, keçe temas etmiyor; radyal/aksiyel boşluk limitleri çizimde dondurulacak | Açık |
| Lastik/jant kuponu | ±1,5 Nm ters torkta ayrılma/kayma yok; en az1000 çevrim ön tarama | Açık |
| Eşdeğer yük fikstürü |9 kg brüt tarama için132,4 N düşey +132,4 N yanal; kalıcı şekil değişimi/hedef dışı salgı yok | Limit ve fikstür tasarımı açık |
| Sıcaklık ve akım | Önce havada tek teker; sonra yüklü test,1,3 A motor RMS hedefi | Açık |
| Kütle ve servis |6 kg ve ölçülmüş rezerv; dört M4, kaplin ve segman takım erişimi | Hedef sağlanmadı / açık |

## Kaynaklar

- [Pololu4754 özellikleri](https://www.pololu.com/product/4754/specs) ve [resmi ölçü çizimi](https://www.pololu.com/file/0J1735/37d-metal-gearmotors-dimension-diagram.pdf), encoder'lı sayfa.
- [SKF rulman kataloğu](https://www.skf.com/binaries/pub12/Images/0901d196807026e8-100-700_SKF_bearings_and_mounted_products_2018_tcm_12-314117.pdf):6000 boyut10×26×8 mm, C4,75 kN, C0 1,96 kN. Sızdırmaz6000-2RSH nihai varyant/omuz çizimi satın alma öncesi kontrol edilecek.
- [Ruland metrik Oldham ailesi](https://www.ruland.com/servo-couplings/oldham-couplings/oldham-bundle/metric-dimensions.html), [6 mm göbek](https://www.ruland.com/moct25-6-a.html), [10 mm göbek](https://www.ruland.com/moct25-10-a.html). Aday MOCT25-6-A + OD16/25-AT + MOCT25-10-A;31,8 mm montaj zarfı. Yuvarlak göbek kullanılır; üreticinin6/5,5D göbeği motorun5,4 mm düzlüğüyle aynı değildir.
- [AT diskli ürün teknik verisi](https://www.ruland.com/mocc25-10-a-od16-25-at-mocc25-8-a.html): disk4,75 Nm kılavuz nominal tork, azami65°C. Göbek kayması ayrıca sınırlandırabilir;19 Nm kırılma değeri çalışma torku değildir. Kaplin bölgesinde≤60°C tasarım hedefi, test şart.

## Yeniden üretim

Repository kökünde:

```sh
.venv/bin/python cad/drivetrain/build_module.py
.venv/bin/python cad/drivetrain/check_packaging.py
python3 cad/drivetrain/export_interfaces.py
.venv/bin/python tests/check_drivetrain.py
.venv/bin/python cad/drivetrain/render_module.py
python3 tools/drivetrain_budget.py
```

İstasyonlar ve delik yerleşimi bu D1 geometri revizyonuna bağlıdır; üretici değişimi yalnız JSON'daki bir çapı değiştirmekle tamamlanmaz. Regresyon testi kritik istasyonların gerçek STEP geometrisiyle eşleşmesini kontrol eder. [Taban delik DXF](../cad/drivetrain/generated/UGV-MECH-040-base-interface-D1.dxf) ve [motor yüzü DXF](../cad/drivetrain/generated/UGV-MECH-040-motor-face-interface-D1.dxf) nominal arayüz profilleridir. Çıktılar nihai `manufacturing/step` alanına taşınmadı.
