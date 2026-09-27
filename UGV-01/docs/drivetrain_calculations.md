# UGV-01 — Motor, teker ve hareket ön hesabı

Revizyon A · 2026-09-22 · PHASE 0–3 girdisi. **Kavramsal seçimdir; satın alma/imalat onayı değildir.** Motorun termal rating'i, lastiğin tutunması ve tüm PWM sürücüsünün davranışı ölçülmeden sürüş performansı garanti edilmez. Kaynak veri, mühendislik varsayımı ve hesap sonucu aşağıda ayrılmıştır.

## 1. Karar ve karşılanmayan ilk hedef

Ön aday dört adet **Pololu #4754, 70:1, 12 V, quadrature encoder'lı 37D** motordur. Özgün teker, göbek, dış rulmanlı mil ve motor taşıyıcıları tasarlanacaktır. V1 hız limiti düz zeminde **0.8 m/s**, eğimde **0.6 m/s** seçildi. Kullanıcının 1–1.5 m/s ilk hedefi bu motor ve 120 mm tekerle sürekli yük/termal payıyla birlikte karşılanmıyor; gereksinim sapması olarak kaydedilmelidir. İleride daha büyük motorla veya daha düşük toplam kütle ve eğim hedefiyle yeniden ele alınır.

15° hedefi kuru sert zeminde, 8 kg toplam kütle ve aşağıdaki CG sınırlarıyla koşulludur. Pürüzlü zemin için V1 hedefi 10°'dir. Pürüzlü zeminde 15°, yüksek tutunmada sürekli yerinde dönüş ve enerjisiz eğimde tutma doğrulanmış özellikler değildir. Motor seçimi bu kısıtları saklayarak yapılmamıştır.

## 2. Girdiler ve yerleşim sınırları

| Girdi | Değer | Tür / açıklama |
|---|---:|---|
| Boş araç / taşıma / toplam kütle | 6 / 2 / 8 kg | Tasarım bütçesi; tartım bekliyor |
| Teker dış çapı / genişliği | 120 / 30 mm | Nominal; yük altındaki etkin yarıçap kalibre edilecek |
| İz genişliği B / dingil açıklığı L | 240 / 210 mm | Teker merkezleri arası |
| Dış teker zarfı | 330 × 270 mm | L + D; B + genişlik. Tamponların bu zarfı aşmaması ayrı CAD şartı |
| Yük altında CG | z ≤ 110 mm; abs(x) ≤ 15 mm; abs(y) ≤ 10 mm | z zeminden; x gövde ileri; y sola, teker dikdörtgen merkezi orijin |
| Yerçekimi | 9.81 m/s² | Hesap sabiti |
| İvme | 0.5 m/s² | Başlangıç hedefi; akım sınırına göre azaltılabilir |
| Yuvarlanma katsayısı Crr | 0.03 sert / 0.08 pürüzlü | Varsayım; kum, çamur, çim garantisi değildir |
| Dış aktarım verimi ηext | 0.95 | Kavrama/rulman ön payı. Redüktör kaybı tekrar eklenmez; katalog torku zaten redüktör çıkışındadır |
| Tek teker yük katsayısı k | 1.5 | Eşit dört teker torkuna uygulanan dengesizlik payı |
| Boyuna tutunma µx | Kabul testi ile ≥ 0.45 hedefi | Malzeme özelliği diye varsayılmayacak |

Rijit dört tekerli gövde engebede bir tekeri boşaltabilir. k=1.5 bu olayı kapsamaz; ilk sürüş zarfı dört teker temasını koruyan zemindir. Daha sonra lastik uyumu veya salınan aks modülü ayrı tasarım kararıdır.

## 3. Düz sürüş ve eğim torku

Kuvvet ve torklar:

```text
F = m g (sin θ + Crr cos θ) + m a
T_wheel_equal = F r / 4
T_gearbox_equal = T_wheel_equal / ηext
T_gearbox_worst = k T_gearbox_equal
```

Hava sürüklemesi 0.8 m/s için bu kaba hesapta ihmal edilmiştir. Dönen kütlenin ivme katkısı, yatak keçesi direnci ve teker deformasyonu testte ölçülür; 0.5 m/s² bir açık çevrim PWM emri değildir.

| Durum, 8 kg | F toplam (N) | T teker eşit (N·m) | T redüktör eşit (N·m) | En yüklü redüktör (N·m) | #4754 akım eşit / en yüklü (A) |
|---|---:|---:|---:|---:|---:|
| Düz sert, sabit hız | 2.354 | 0.0353 | 0.0372 | 0.0558 | 0.274 / 0.312 |
| Düz pürüzlü, sabit hız | 6.278 | 0.0942 | 0.0991 | 0.1487 | 0.398 / 0.498 |
| 15° sert, sabit hız | 22.586 | 0.3388 | 0.3566 | 0.5349 | 0.914 / 1.271 |
| 15° pürüzlü, sabit hız | 26.377 | 0.3956 | 0.4165 | 0.6247 | 1.034 / **1.451** |
| 15° sert, 0.5 m/s² ivme | 26.586 | 0.3988 | 0.4198 | 0.6297 | 1.040 / 1.460 |
| 15° pürüzlü, 0.5 m/s² ivme | 30.377 | 0.4556 | 0.4796 | 0.7194 | 1.160 / 1.640 |
| 10° pürüzlü, sabit hız | 19.811 | 0.2972 | 0.3128 | 0.4692 | 0.826 / 1.139 |

Son sütun üretici ölçümü değildir. Eleme için kullanılan doğrusal yaklaşım:

```text
I(T) ≈ I0 + (Istall − I0) T / Tstall
n(T,Veff) ≈ n0,12V (Veff/12 − T/Tstall,12V)
v = n π D / 60
```

Akım-tork yaklaşımı maksimum verim noktasında katalogdan farklı sonuç verebilir: #4754 için 0.3138 N·m'de model yaklaşık 0.828 A, katalog 0.68 A verir. Bu fark eğrilerin yaklaşık olduğunu açıkça gösterir. Nihai tasarım için üretici eğrisi ve dört numunenin dinamometre verisi kullanılacak; tablodaki üçüncü ondalık doğruluk garantisi değildir. Kablo/sürücü düşümleri bu hız modeline ayrıca eklenmelidir.

## 4. Motor adayları

| Aday | Oran gerçek | 12 V yüksüz rpm | Yüksüz / stall A | Stall çıkış N·m | Kütle | Boy Ø × L, mil hariç | Karar |
|---|---:|---:|---:|---:|---:|---|---|
| [Pololu #4753](https://www.pololu.com/product/4753/specs) | 50 | 200 | 0.2 / 5.5 | 2.059 | 205 g | 37 × 70 mm | Hız iyi, sürekli eğim/yerinde dönüş payı zayıf |
| [Pololu #4754](https://www.pololu.com/product/4754/specs) | 70 | 150 | 0.2 / 5.5 | 2.648 | 205 g | 37 × 70 mm | Koşullu ana aday |
| [Pololu #4755](https://www.pololu.com/product/4755/specs) | ≈102.08 | 100 | 0.2 / 5.5 | 3.334 | 210 g | 37 × 72.5 mm | Yükte daha rahat; düz hız yalnız ≈0.62 m/s |
| [ServoCity 5203-2402-0019](https://www.servocity.com/5203-series-yellow-jacket-planetary-gear-motor-19-2-1-ratio-24mm-length-8mm-rex-shaft-312-rpm-3-3-5v-encoder/) | 19.2 | 312 | 0.25 / 9.2 | 2.383 | 437 g | CAD/datasheet ile ayrıca yerleşim gerekir | Dört motorda +0.928 kg; hız/akım yüksek, sürekli rating teyitsiz |

Stall çıkışı seçim için sürekli tork kabul edilmez. [Pololu'nun aile sınırı](https://www.pololu.com/category/116/37d-metal-gearmotors) redüktörde 0.981 N·m sürekli, 2.452 N·m anlık yük önerisidir; motorun genel akım önerisi stall akımının ≤%25'i, yani 1.375 A'dir. Bunların en kısıtlayıcısı dikkate alınır. Tasarım RMS bütçesi 1.3 A seçilirse yaklaşık kullanılabilir motor torku #4753/#4754/#4755 için 0.427/0.550/0.692 N·m olur. Bu, garanti edilmiş sürekli motor rating'i değildir.

15° sert zemindeki 0.535 N·m en yüklü teker ihtiyacı #4753 için yaklaşık 1.577 A, #4754 için 1.271 A, #4755 için 1.050 A ister. Bu nedenle 50:1 seçilip yalnız hız avantajı gösterilmez. 70:1'de de marj küçüktür; zemin ve termal test olumsuzsa 100:1'e geçiş veya daha büyük motor şarttır. Motordan redüktöre iç mekanik tork için ηgear=0.65–0.80 yalnız ön varsayım alınırsa, 0.535/(70ηgear)=9.55–11.76 mN·m rotor torku gerekir; elektrik/termal seçimde doğrulanmamış bu verim yerine ürün çıkış eğrileri esas alınır.

## 5. Hız ve besleme seçenekleri

1.0 m/s için 159.2 rpm, 1.5 m/s için 238.7 rpm teker hızı gerekir. #4754 daha yüksüzken 150 rpm'dir. Akım sınırlaması ve yük altında gerilim payı dikkate alındığında 1–1.5 m/s vaat edilemez.

Tablo çiftleri **yüksüz / düz sert zeminde eşit yükte tahmini hız**, m/s:

| Etkin motor gerilimi | 50:1 | 70:1 | 100:1 | Kullanım yorumu |
|---|---:|---:|---:|---|
| 9.6 V | 1.005 / 0.983 | 0.754 / 0.741 | 0.503 / 0.496 | 3S düşük uç örneği; hücre undervoltage kararı değildir |
| 10.8 V | 1.131 / 1.108 | 0.848 / 0.835 | 0.565 / 0.558 | 3S, 3.6 V/hücre nominal |
| 12.0 V | 1.257 / 1.234 | 0.942 / 0.929 | 0.628 / 0.621 | Önerilen etkin motor gerilimi üst sınırı |
| 12.6 V | 1.319 / 1.297 | 0.990 / 0.976 | 0.660 / 0.653 | 3S tam dolu; 12 V sınırlaması yine uygulanır |
| 14.4 V | 1.508 / 1.485 | 1.131 / 1.118 | 0.754 / 0.747 | 4S ham gerilim; **sürekli motora uygulanmayacak** |
| 16.8 V | 1.759 / 1.737 | 1.319 / 1.306 | 0.880 / 0.873 | 4S tam ham gerilim; **sürekli motora uygulanmayacak** |

12 V etkin gerilimde 15° sert zemin/en yüklü teker hızı 50/70/100 için 0.930/0.752/0.528 m/s'dir. 70:1'in eğim hız emri 0.6 m/s seçilerek regülasyon payı bırakılır. 3S nominal 10.8 V'ta aynı en yüklü koşul 0.658 m/s'ye düşer.

**Tercih:** 4S batarya, ölçülen bus gerilimi üzerinden `duty_max ≤ min(1,12/Vbus)`, hız ve akım kapalı çevrim. Örnek üst duty 14.4 V'ta 0.833; 16.8 V'ta 0.714. Bu oranlar endüktans, PWM decay modu, fırça gerilimi ve serbest dönüş akımı nedeniyle termal güvence değildir. Cycle-by-cycle akım limiti, motor RMS ölçümü, blokaj tespiti ve bus rejenerasyon klempi ayrıca zorunludur. 12 V motor rayı için basit tek yönlü buck seçilirse fren enerjisini geri ememeyeceği ayrıca çözülmelidir; yüksek akım regüle ray V1'de seçilmedi.

3S alternatifi DC motor gerilim riskini azaltır fakat düşük SOC'ta hız düşürür; 12 V yardımcı çıkış için buck-boost ister. 24 V motor + 6S alternatifinin akım avantajı vardır, ancak batarya/konnektör/sürücü mimarisini büyütür; bu sınıfta şimdilik gerekli değildir.

## 6. Ağırlık dağılımı, tutunma ve devrilme

15° eğimde CG teker dikdörtgeninin merkezindeyken ön/arka toplam normal kuvvet:

```text
Nfront = mg (cosθ/2 − h sinθ/L) = 27.26 N
Nrear  = mg (cosθ/2 + h sinθ/L) = 48.54 N
```

CG ayrıca 15 mm arkadaysa arka aks yükü 53.96 N olur. 0.5 m/s² ileri ivme yaklaşık 2.10 N ek arka aks yükü aktarır. Arka teker başına ≈28.03 N, düz zemindeki mg/4=19.62 N'un 1.43 katıdır; 1.5 katsayısı bu boyuna senaryoyu kapsar. Yanal CG kayması da eşzamanlı ise basit sağ-sol paylaştırma 1.55 katsayısına çıkabilir. Bu nedenle k=1.5 yalnız CG sınırlarından garanti edilemez: teker baskülleri ve yük aktarımı testiyle doğrulanacak çalışma zarfı şartıdır. k=1.6 duyarlılığında 15° sert sabit hız motor akımı yaklaşık 1.34 A olur ve 1.3 A bütçesini aşar; böyle bir dağılımda yük/eğim azaltılmalıdır. Çapraz engel ayrıca kapsam dışıdır.

Boyuna gereken tutunma `µrequired = tanθ + Crr + a/(g cosθ)`. 15° sert sabit hızda 0.298; aynı eğimde ivmeyle 0.351; pürüzlü zeminde ivmeyle 0.401 olur. 0.45 test eşiği küçük bir pay bırakır. Kaygan yüzeyde motor torku yeterli olsa da araç çıkamaz. Dönüşte boyuna ve yanal kuvvetler aynı temas sürtünme bütçesini paylaşır; tam eğim ve tam pivot birlikte hedeflenmez.

CG sınırlarıyla ideal statik boyuna devrilme açısı `atan((105−15)/110)≈39.3°`; yanal açı `atan((120−10)/110)=45°`. Bunlar izin verilen sürüş açıları değildir. Lastik esnemesi, çukur, ivme ve kule yükü güvenlik payını tüketir. V1 15°/10° eğim hedefi ve eğimde düşük hız bu nedenle korunur.

## 7. Skid-steer yerinde dönüş

Yanal sürtünmenin tam mobilize olduğu dört noktalı temas modeli kaba bir üst tarama hesabıdır:

```text
M_scrub ≈ µy mg L / 2
T_each ≈ M_scrub r / (2 B ηext)
```

| Varsayılan yanal µy | Toplam scrub momenti (N·m) | Her redüktör torku, yuvarlanma hariç (N·m) | #4754 tahmini akım (A) |
|---|---:|---:|---:|
| 0.30 | 2.472 | 0.325 | 0.851 |
| 0.60 | 4.944 | 0.651 | 1.502 |
| 0.80 | 6.592 | 0.867 | 1.936 |

Sert zemin yuvarlanma payı yaklaşık +0.037 N·m ve +0.074 A/tekerdir. µy=0.6'da yaklaşık 1.58 A sürekli pivot, 1.3 A bütçeyi aşar. µy=0.8 için ≈2.01 A olur. Çok geniş/yumuşak tutucu lastik düz sürüş tutunmasını artırırken pivot ısısını yükseltebilir. Bu model lastik temas yamalarını, düzensiz zemin basıncını ve gerçek dönüş merkezini çözmez; ölçülen dönüş akımı zorunludur.

V1 varsayılan manevrası sonlu yarıçaplı yavaş dönüş ve akım limitlemedir. Yerinde dönüş güvenli düz alanda, test edilen yüzeyde ve süre/RMS/ısı bütçesi izin veriyorsa açılır. 250 ms tepe akım izni, her 250 ms'de sayaç sıfırlanarak sürekli pivot yapma izni değildir. Limitte dönüş gerçekleşmezse kullanıcıya tork/zemin sınırı bildirilir; PID integral birikimi engellenir.

## 8. Akım, ısı ve sürücü girdileri

1.3 A RMS sürekli motor akım bütçesi ve 2.5 A en fazla 250 ms kısa tepe **prototip ayarlarıdır**, üretici garantisi değildir. Dört motorun en kötü aynı anda 2.5 A değeri 10 A toplam motor akımıdır. PWM serbest dolaşım nedeniyle batarya akımıyla motor akımı eşit değildir; özellikle düşük duty'de yalnız batarya sensörü motoru koruyamaz.

Yaklaşık soğuk direnç `R≈12/5.5=2.18 Ω`. 16.8 V'ta kontrolsüz kısa devreye yakın stall yaklaşık 7.7 A/motor, dört motorda 30.8 A verebilir. Motor ve batarya endüktansı, gerilim çökmesi ve fırça etkisi sonucu değiştirir. PCB/sigorta/batarya koordinasyonu 1.3 A nominal akıma bakılarak yapılmaz.

`I²R` sargı bakır kaybı 1.3 A'da ≈3.69 W/motor, 2.5 A'da ≈13.64 W/motordur. Gerçek kayba fırça/demir/redüktör kayıpları eklenir; sıcak direnç artar. 15° sert eşit yük modelinde dört motor elektrik gücü yaklaşık 43.9 W (4×12×0.914); şaft mekanik çıkışı yaklaşık 19.4 W, aradaki ≈24.5 W motor/redüktör kaybı taramasıdır. 4×en-yüklü akımı gerçek eşit tork yükünün nominal tüketimi olarak kullanılmamalıdır; güç kartı için muhafazakâr üst rezerv olabilir.

Kasa sıcaklığı sargı sıcaklığı değildir. İlk laboratuvar durdurma eşikleri örneğin kasa 60°C uyarı/70°C kesme olacak şekilde muhafazakâr ayarlanabilir; üretici sargı/encoder sınırı ve çevresel sıcaklık teyidi bekler. Dış gövde sızdırmazlık ve motor hava akışı birlikte test edilir. 30 dakika yüklü sürüş ve dönüş döngüsünde sıcaklığın kararlı hale gelmesi, kalan ömür garantisi değil V1 kabul testidir. Test süresi boyunca akım, kasa sıcaklığı, ortam, hız, duty ve batarya kaydedilir.

Zorunlu bağımsız korumalar: her H-köprüde cycle current limit; motor RMS/ısı integrali; encoder emri varken hareketsizlik kontrolü; 300 ms bloke teker aday timeout (encoder veri kaybı ayrı100 ms); gate-disable yoluyla kapanma. Encoder arızası ile gerçek blokaj ayrımı belirsizse sürüş kesilir. Akım sınırı yükseltilerek daha hızlı sürüş sağlanmaz.

## 9. Özgün teker, göbek ve yataklama konsepti

- 120 × 30 mm teker: bize ait iki parçalı göbek/jant, değiştirilebilir TPU prototip sırt veya ticari lastiğe uyarlanan özgün jant. Gerçek lastik seçilmeden bead/oturma çapı dondurulmaz.
- Motor 6 mm D mil yalnız tork iletir. Tekerin düşey/yanal yükü motor redüktörüne asılmaz; kendi çelik aksı, iki dış rulman, eksenel tutucu ve şasiye bağlanan yatak kaseti kullanılır. Rulman/aks seçimi katalog yük/ömür hesabı ve paketlemeye göre PHASE 4'te yapılır.
- Motor-göbek arası sökülebilir sıkmalı kavrama; motor miline delinmiş rastgele pim veya yalnız plastik setskur ile tork aktarımı kullanılmaz. Kavrama kayması da fault olarak gözlenebilir.
- Düz statik yük 19.62 N/tekerdir; yük katsayısı 1.5 ve başlangıç düşey darbe katsayısı 3 ile en az ≈88.3 N/teker ön tasarım yükü alınır. Darbe katsayısı varsayımdır. Yanal pivot yükü ve rulmanlar arası konsol momenti ayrıca eklenecek; bu değer hazır bir dayanım doğrulaması değildir.
- Ø37 motor arayüzü, 70 mm gövde, 16 mm şaft ve [en fazla 3 mm vida girişi](https://www.pololu.com/product/4754) CAD'de sürülecek. Rulman kaseti tekeri sökmeden motorun içe/yan servis yönünde çıkmasını sağlamalıdır.

[Pololu teknik desteği](https://forum.pololu.com/t/geared-dc-motor-selection/23225) milin radyal/eksenel ömrünün ayrıntılı karakterize edilmediğini belirtir. Bu nedenle motor milinin robotun bütün yükünü taşıdığı görünüş modeli üretim modeli olarak kabul edilmeyecek.

## 10. Encoder ve düşük hız

#4754 için `N=64×70=4480` count/teker turu; 120 mm teker çevresi 376.991 mm; teorik konum adımı 0.08415 mm/count. Bu odometri doğruluğu değildir; lastik kayması ve etkin çap hatası çok büyüktür. 150 rpm'de 11,200 count/s/motor oluşur; dört kanalda STM32 timer quadrature modu kullanılmalı, her kenara yazılım interrupt'ı gerekmemelidir.

0.03 m/s kontrollü hız hedefi 4.77 rpm teker ve yaklaşık 357 count/s üretir. 20 ms pencerede ≈7.13 count, 1 ms'de yalnız 0.357 count vardır. Düşük hızda uzun pencere/kenar-periyot ölçümü ve filtre, yeterli encoder sayımı olmasına rağmen statik sürtünme için ayrı kalibrasyon gerekir. PWM minimumu, sağ-sol ileri/geri işaret, deadband, lastik çapı ve etkin skid iz genişliği ayarlanabilir kalır. Katalog oranı gerçek; skid odometri `B_effective` ölçüm parametresidir.

Encoder 5 V temiz raydan beslendiğinde çıkışlar 5 V seviyesindedir; [üretici encoder bilgisi](https://www.pololu.com/product/4754) 3.3 V beslemeyi onaylamaz. MCU'ya buffer/seviye uyarlaması, kablo ekran/ESD stratejisi ve uygun timer pinleri gerekir. Motor güç çifti encoder sinyallerinden ayrılır; özgün 0.1 inç motor başlığı kilitli araç konnektörü olarak kabul edilmez.

## 11. Durma mesafesi ve eğimde park

Kontrollü duruş için `s = v τ + v²/(2 a_stop)`. Ön varsayım iletişim algılama ve aktüasyon toplamı 150 ms, kontrollü yavaşlama 0.8 m/s²:

| İlk hız | Gecikmede yol | Yavaşlama yolu | Toplam hesap |
|---|---:|---:|---:|
| 0.6 m/s | 0.090 m | 0.225 m | 0.315 m |
| 0.8 m/s | 0.120 m | 0.400 m | 0.520 m |
| 1.5 m/s | 0.225 m | 1.406 m | 1.631 m |

Bu değerler hedef kontrollü yavaşlama gerçekleşirse geçerlidir; fren torku, yüzey, haberleşme timeout'u ve fren enerjisi ölçülmeden güvenlik mesafesi sayılmaz. Fiziksel E-stop motor enerjisini keserse araç **serbest yuvarlanabilir**. Yalnız Crr=0.03 ile düz zeminde 0.8 m/s'ten teorik coast yolu `v²/(2gCrr)≈1.09 m`, 150 ms ek gecikmeyle ≈1.21 m'dir; düşük sürtünmede daha uzundur. 15° aşağı eğimde yuvarlanma direnci yerçekimini yenmez, sınırlı coast durma mesafesi yoktur.

Sürüş enerjisi kesildiğinde redüktörün kendiliğinden kilitlendiği varsayılmaz. V1'de enerjisiz eğimde güvenli park ancak mekanik takoz/tether veya sonraki fren modülüyle mümkündür; insanlardan bağımsız eğimli otonom görev onayı yoktur. Bu risk yazılım heartbeat'iyle çözülemez. İnişte enerji ayrıca batarya dolu/BMS açıkken de bus klempi ve fren termali tarafından karşılanmalıdır. 8 kg, 0.8 m/s, 15° sürekli inişte potansiyel güç yaklaşık 16.25 W; TVS tek başına sürekli fren yükü olamaz.

## 12. Aşama kapısı — kararı kesinleştirecek deneyler

1. Dört numunede 12 V yüksüz rpm/akım, encoder sayım oranı ve yön doğrulaması; katalog toleransı yoksa ünite yayılımı kaydedilir.
2. Bir motor+dış yataklı teker dinamometresinde 0.04–0.72 N·m çalışma haritası; 0.535 N·m sürekli hedef, 1.3 A bütçe ve kasa sıcaklığı birlikte değerlendirilir. Hasar riski olan gerçek stall testi yapılmaz; akım sınırlı düzenek kullanılır.
3. 4S tam doluda PWM akım ripple/decay ve cycle-limit osiloskop testi; batarya ölçümünün motor akımı olmadığı doğrulanır.
4. 8 kg yükte düz/15° sert ve 10° pürüzlü yüzey testleri; CG tartımı, akım, sıcaklık, hız ve kayma. Sürekli kapı başarısızsa kütle/sürüş zarfı azaltılır veya motor değiştirilir.
5. Lastik adaylarında pivot akımı, yanal kuvvet ve göbek gevşeme testi; koşullar tanımlanmadan yerinde dönüş açılmaz.
6. Kontrollü stop, haberleşme kaybı ve bağımsız fiziksel E-stop ayrı deneylerdir. Eğim testinde fiziksel yakalama tertibatı gerekir.

Ortak fiziksel parametreler ana sistem konfigürasyonundan CAD ve URDF'ye taşınmalıdır. [Motor aday veri kaydı](../config/drivetrain_candidate.json) kaynak ve ön hesap girdi manifestidir; üretim pinout'u, motor sürücüsü konfigürasyonu veya son güvenlik eşiği dosyası değildir.
