# UGV-01 — Claude sonrası bağımsız inceleme ve düzeltme promptu

25.09.2026 · İncelenen çalışma ağacı: `UGV-01`.

## Kapsam ve sonuç

Güncel **A3 Lite** incelendi: ESP32-S3, iki ESP32-CAM, JGA25 motorlar, TB6612, 3S batarya, PETG mekanik ve MacBook AI/panel. A3 bütçe ve mimari kararları mevcut kullanıcı onay kayıtlarıyla uyumlu kabul edildi; eski CM5/STM32 hedefinden farklı olması hata sayılmadı. Depoda commit tabanı olmadığından bu bulguların tamamının Claude tarafından yeni oluşturulduğu ileri sürülmüyor.

**Dört P1, altı P2 bulgu var.** P1: hareket güvenliğini veya donanım korumasını etkileyen, entegrasyondan önce ele alınması gereken sorun. P2: ölçüm, çalışma zarfı, izlenebilirlik veya tutarlılık sorunu. Hesap sonuçları fiziksel test sonucu değildir.

Bu incelemede kaynak kod, CAD, şema veya BOM değiştirilmedi; yalnız bu rapor eklendi. Negatif senaryolar masaüstünde çalıştırıldı. Gerçek donanım veya ücretli model API'si kullanılmadı.

## Bulgular

### R1 — P1: Geçersiz sensör verisi hareketi engellemiyor

Konum: `software/ugv_ai/executor.py:112–135`, özellikle 115, 122 ve 125.

Odometri ve ön ToF verilerinin sonlu sayı olduğu denetlenmiyor. `NaN < FRONT_STOP_M` false olduğu için arızalı mesafe verisi engel kontrolünü atlıyor. NaN odometri de hedef mesafeye ulaşma kontrolünü işlevsiz bırakıyor.

**Tekrarlanan sonuç:** `SimVehicle.front_tof_m()` NaN döndürünce 1 m ileri komutu 1 m gidip başarılı dönüyor. Odometri NaN olduğunda 0,1 m komutu 0,51 m gidip ancak timeout ile duruyor. Bunlar simülasyon mesafeleridir.

**Düzeltme/kabul:** İlk örnek ve her hareket adımındaki odometri/mesafe verisini kullanımından önce doğrula; geçersiz veriyle hız komutu verme, hareket başladıysa dur ve açık hata döndür. NaN ve ±Inf testleri ekle. Gerçek telemetri adaptörü yapılırken geçerli/taze örnek sözleşmesini de açık tanımla; sadece sıfır veya eski değer döndürerek arızayı gizleme.

### R2 — P1: Süresi dolan hareket izni yenilenince eski AI görevi devam ediyor

Konum: `software/ugv_ai/executor.py:39–53`, `software/ugv_ai/bridge.py:119–152`.

`Permit.renew()` önceki izin kaybını kaydetmeden zamanı değiştiriyor. Model yanıtı beklenirken 100 ms izin süresi aşılır, ardından izin yenilenirse eski görevin dönen hareket komutu kabul ediliyor. Geçmişte yaşanan kesinti, yalnız o andaki `ok()` kontrolünde görünmüyor. Benzer biçimde odak/anahtar kapatılıp açılması da aktif görevi kalıcı olarak geçersiz kılmalı.

**Tekrarlanan sonuç:** Mock API içinde saat 200 ms ilerletilip izin yenilendiğinde eski görev 0,1 m hareket ediyor. Executor seviyesinde aynı senaryo da tekrarlandı.

**Düzeltme/kabul:** İzin kaybını görev boyunca kalıcı tut; yenileme eski görev/model yanıtına yetki vermesin. Örneğin izin nesli ve görevin başladığı nesil veya eşdeğer küçük bir çözüm kullan. Yeniden hareket ancak geçerli izin ve açıkça başlatılmış yeni görevle mümkün olsun. Model çağrısı sırasında timeout→renew ve focus off→on senaryolarında eski yanıtın hiçbir hareket üretemediğini test et. Bağımsız MCU timeout korumasını koru.

### R3 — P1: Mod geçişi komut sıra geçmişini sıfırlayıp replay kabul ettiriyor

Konum: `firmware/stm32/can_protocol.c:47,65`; A3 yeniden kullanım kararı: `docs/superpowers/plans/2026-09-25-a3-lite-software.md:10`.

Mod değişince `have_command=0` yapılıyor; aynı değişken sıra numarası kontrolünü de etkinleştiriyor. Dolayısıyla mod değişiminden sonraki ilk komut eski sıra numarasını taşıyabiliyor. A3 planı bu decoder'ı HMAC doğrulanmış UDP yükleriyle aynen kullanıyor. HMAC, daha önce geçerli imzalanmış paketin yeniden oynatılmasını tek başına önlemez.

**C decoder ile tekrarlanan akış:** Aynı `0x12345678` oturumunda IDLE lease seq0 → DRIVE lease seq1 → 200 mm/s command seq100 → ARM lease seq2 → neutral command seq101 → DRIVE lease seq3 → eski command seq100.

Gerçek çıktı: `replay accepted=1 fresh=1 left=200 seq=100`.

Bu bulgu decoder'ın eski komutu taze saydığını gösterir; tamamlanmamış Lite çekirdeğinde fiziksel hareket gözlendiği anlamına gelmez.

**Düzeltme/kabul:** Komutun mevcut mod için tazeliği ile oturum içindeki sıra geçmişini ayrı tut. Mod değişimi tazeliği bozmalı, sıra geçmişini silmemeli. Yeni oturum kuralları ve 16-bit wrap davranışı korunmalı. Yukarıdaki tekrar reddedilmeli ve komut zamanı yenilenmemeli; gerçekten ileri sıradaki komut kabul edilmeli. Lite entegrasyonunda aynı testi geçerli HMAC'li eski UDP datagramıyla çalıştır.

### R4 — P1: Seçilen sürücü için sıkışma koruması yetersiz

Konum: `docs/lite_electronics_A3.md:57`, `manufacturing/bom/lite_bom_A3.csv:7`.

Doküman motor stall akımını 1,8 A, enkoderle durdurma süresini 300 ms veriyor. Toshiba TB6612 veri sayfasında kanal başına 1,2 A mutlak sürekli sınır; 2 A yalnız ≤20 ms ve ≤%20 görev oranlı darbe koşulunda, 3,2 A ise daha kısa tek darbe koşulunda belirtiliyor. 300 ms stall bu koşullarla gerekçelendirilmiyor. Ayrıca arka motor sıkışırken aynı taraftaki bağımsız ön motor dönebilir; ön enkoder arka sıkışmayı güvenilir biçimde algılayamaz. Ortak 10 A sigorta da tek bir 1,8 A kanalı korumaz.

**Düzeltme/kabul:** Her motor kanalı için gerçek batarya üst geriliminde stall/başlangıç akımı, süre ve termal sınırları karşılayan sürücü/akım sınırlama çözümü belirle. Salt 300 ms sabitini azaltma veya sigortayı gerekçe gösterme. İki enkoderin kapsamadığı arka sıkışmayı açıkça çöz. Değişikliklerin GPIO, şema, güç/ısı, BOM ve bütçe etkisini birlikte hesapla. Her bağımsız teker sıkışması için kabul testi tanımla; donanım olmadan geçti yazma.

Kaynak: [Toshiba TB6612FNG veri sayfası, özellikle s.3 ve çalışma koşulları](https://toshiba.semicon-storage.com/info/datasheet_en_20141001.pdf?did=10660). Mutlak maksimum değeri önerilen güvenli sürekli çalışma noktası gibi kullanma.

### R5 — P2: ADC bölücüsü tam dolu bataryada ölçüm aralığını aşıyor

Konum: `tools/build_lite_wiring.py:92–97`, `tests/check_lite_wiring.py:85–90`.

100 kΩ / 33 kΩ bölücüde `12,6 × 33 / 133 = 3,1263 V`. %1 dirençlerin kötü durum birleşiminde yaklaşık **3,1736 V**. ESP32-S3 için IDF ADC dokümanındaki üst ölçüm değeri 3,100 V; güncel çip veri sayfasındaki kalibre edilmiş karakterizasyon aralığı daha da dar (2,9 V'a kadar). Test ise yanlış olarak ≤3,14 V kabul ediyor. 3,3 V beslemenin altında olmak ADC doğruluğunu garanti etmez.

**Düzeltme/kabul:** Kullanılan attenuation/IDF ve çip için desteklenen ölçüm aralığını seç; batarya/şarj üst sınırı ve direnç toleranslarıyla yeterli marj bırak. İki bölücüyü, kalibrasyon sabitlerini, üretilen şema/PDF'yi ve testi birlikte düzelt. Test gerçek aralığa dayanmalı; mevcut oranı geçirmek için eşik büyütülmemeli.

Kaynaklar: [Espressif ESP32-S3 ADC dokümanı](https://docs.espressif.com/projects/esp-idf/en/v4.4.7/esp32s3/api-reference/peripherals/adc.html), [ESP32-S3 veri sayfası](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf).

### R6 — P2, tasarım açığı: E-stop durum algısının süre sınırı yok

Konum: `tools/build_lite_wiring.py:95–99`, `docs/lite_electronics_A3.md:19`.

E-stop durumu `VM_ACT < VBAT_SW/2` ile algılanıyor. VM_ACT üzerinde 470 µF var. ACT_EN düşükken modüllerin kapalı durum yükleri belgelenmemiş; açıkça tanımlı boşalma yolu 133 kΩ bölücü. Yalnız bu yolun modelinde yarıya düşme süresi `ln(2) × 133000 × 470e-6 ≈ 43,33 s`.

**Bu 43 s ölçülmüş gecikme değildir:** gerçek modüller daha hızlı boşaltabilir. Sorun, tasarımın üst gecikme sınırını göstermemesi ve kısa bir basışın yazılım tarafından kaçırılabilmesi. NC kontak batarya yolunu fiziksel olarak kesmeye devam eder; burada eleştirilen şey durumun algılanması ve yeniden kurma mantığıdır.

**Düzeltme/kabul:** Kontak durumunu doğrudan algılayan veya en kötü durumda sınırlı sürede algılamayı kanıtlayan çözüm belirle. ADC filtrelerini, toleransları ve yükleri hesaba kat. IDLE/ARMED/DRIVING ve bas-bırak senaryolarının algılama/yeniden kurma kriterlerini yaz; ölçüm sonrasına kalanları açık bırak.

### R7 — P2: A3 yerinde dönüş ve ivmelenme yükü hesap/test kapsamı dışında

Konum: `tools/calculations.py:28–30,50–54`; eski scrub modeli `docs/drivetrain_calculations.md:116–117`; hareket aracı `software/ugv_ai/tools.py:26`.

A3 hesap kapısı yalnız düz/sabit hızlı eğim yükünü değerlendiriyor. Config'teki sürtünme ve ivme parametreleri bu tork hesabına girmiyor. Oysa arayüz yerinde dönüş sunuyor.

Deponun kaba scrub modeli A3'e uygulanınca (m=4 kg, µ=0,6, L=0,210 m, B=0,240 m, r=0,060 m, η=0,95): `M=µmgL/2=2,4713 N·m`; motor başına `T=Mr/(2Bη)=0,32517 N·m`, config doğrusal akım modeliyle **1,37371 A**. Yuvarlanma payıyla yaklaşık **1,44821 A**. Bu hem 0,6 A motor tasarım tavanını hem 1,2 A sürücü sınırını aşıyor. Mevcut 5° hesabına 0,5 m/s² ivme eklenirse en yüklü motor yaklaşık **0,699 A** oluyor.

Bu model muhafazakâr ön taramadır; aracın kesin dönmeyeceğini veya gerçek akımın bu olduğunu kanıtlamaz. Ancak mevcut kontrollerle dönüş/ivme çalışma zarfı onaylanamaz.

**Düzeltme/kabul:** A3 için scrub/sürtünme duyarlılığı ve ivmeli yükleri hesaplara ekle; motor/sürücü seçimiyle birlikte değerlendir. Dönüş ve ivme sınırlarını açık koşullara bağla. Sadece hız azaltmanın stall torkunu düşürdüğünü varsayma. Fiziksel pivot akımı/ısı testini açık doğrulama kapısı olarak koru.

### R8 — P2: Son omuz CAD'i ile doküman/BOM birbirinden kopmuş

Konum: `cad/assembly/build_concept.py:230–243`, `docs/lite_mechanical_A3.md:19,23,38,42,44`, `manufacturing/bom/lite_bom_A3.csv:19–24`, `README.md:13,63`.

| Kalem | Belgede | Güncel CAD/kütle taraması |
|---|---:|---:|
| STEP parça sayısı | 56 | 61 |
| Baskı parçası | 39 | 41 |
| Kol grubu | 167 g / 250 g tahsis | 242,813 g / 250 g tahsis |
| Kol grubunun kalan payı | yaklaşık 83 g | yaklaşık 7,187 g |
| PETG baskı tahmini | 1313 g | 1366,730 g |
| Gövde grubu | 544 g | 534,928 g |

Yeni omuzda **2 × 624ZZ rulman ve M4 × 40 aks** CAD'de mevcut; Lite BOM'da yok. 6804 boyun rulmanı ve M3 bağlantı seti bunların karşılığı değil. Dolayısıyla 9515 TL / 485 TL kalan bütçe güncel montajın tamamını kapsamıyor; bu, bütçenin kesin aşıldığı anlamına gelmez. Kütle taraması da vida/kablo dahil olmayan tahmindir.

**Düzeltme/kabul:** Eksik satın alma parçalarını miktarlarıyla BOM'a ekle, fiyatların tahmin/kaynak durumunu koru. Kütle/filament/CG tahsislerini yeni montajla kontrol et; dokümanlar ve README'yi aynı kaynak çıktısıyla eşleştir. Geared omuz kararını DD kaydına ekle; kodda kullanılan DD68 ile L3 planının ayırdığı DD68 çakışmasını önle.

Ek küçük doğruluk notu: `docs/lite_mechanical_A3.md:11` D-mil yuvası diyor, mevcut `build_concept.py:151–152,169` deliği dairesel kesiyor. Mil-göbek testinin doğruladığı şey eksenel örtüşme; anahtarlı tork aktarımı değil. Kaplin/set vidası açık iş olduğundan bunu bitmiş bir D-geometri gibi sunma.

### R9 — P2: Çok büyük JSON tamsayısı doğrulamadan exception çıkarıyor

Konum: `software/ugv_ai/executor.py:71–73`, çağıran `software/ugv_ai/bridge.py:152`.

`execute("drive", {"distance_m": 10**400, "speed_mps": 0.2})` çalıştırıldığında `math.isfinite()` büyük tamsayıyı float'a çevirirken `OverflowError` veriyor. Normal hata sonucu dönmüyor; bridge executor çağrısındaki exception'ı yakalamıyor.

**Düzeltme/kabul:** Paylaşılan sayısal doğrulamada sınır dışı büyük int'leri float dönüşümü öncesinde reddet. Hem işaretli çok büyük int hem NaN/Inf ve bool sınırlarını test et; geçersiz tool girdisi normal hata sonucu vermeli ve hareket oluşturmamalı.

### R10 — P2: Yeni görev önceki görevin görüntü kayıtlarını eziyor

Konum: `software/ugv_ai/bridge.py:101–107,124`.

JSONL eklenerek saklanıyor, fakat her görev adım 1'den başlıyor ve dosya adı yalnız `step01_eye0.jpg` gibi. Aynı kayıt dizinine iki görevin ilk adımı yazılınca iki log kaydı kalıyor ama yalnız son görüntü saklanıyor.

**Düzeltme/kabul:** Görev başına benzersiz kimlik/dizin kullan; JSONL içine görev kimliği ve gerçek görüntü yollarını yaz. Aynı dizinde ardışık iki görevin iki farklı görüntüsünün korunmasını test et. Kayıt mimarisini yeniden kurmak gerekmiyor.

## Çalıştırılan kontroller

Aşağıdakiler inceleme sırasında PASS verdi; bu sonuçlar yukarıdaki negatif senaryoları kapsadıkları anlamına gelmez:

- `python3 tests/check_design.py`
- `.venv/bin/python tests/check_cad.py`
- `.venv/bin/python tests/check_body_mass.py`
- `python3 tests/check_esp32_pinmap.py`
- `python3 tests/check_lite_wiring.py` (ERC dahil)
- `python3 tests/check_lite_bom.py`
- `python3 tests/check_markdown_links.py`
- `python3 tests/check_ai_executor.py`
- `python3 tests/check_ai_bridge.py`
- `node --test software/web_ui/panel_logic.test.mjs`
- `cc -std=c11 -Wall -Wextra -Werror tests/lite_link_test.c firmware/lite/lite_link.c firmware/lite/hmac_sha256.c -o /tmp/ugv-review-lite-link && /tmp/ugv-review-lite-link`

Ek olarak C replay senaryosu ve AI NaN/izin senaryoları yukarıdaki hatalı sonuçları üretti. Kütle değerleri `.venv/bin/python tools/body_mass_screen.py` ile okundu.

### R1/R2 için kısa tekrar komutu

Repo kökünde, gerçek donanım/API kullanmadan:

```sh
PYTHONPATH=software python3 - <<'PY'
from ugv_ai.executor import Permit, SkillExecutor
from ugv_ai.sim import SimClock, SimVehicle
for name in ('nan_tof', 'nan_odometry', 'renew_after_expiry'):
    c = SimClock(); v = SimVehicle(c); p = Permit(c)
    p.set(True, True); p.renew()
    c.hooks.append(lambda t: p.renew())
    e = SkillExecutor(v, p, c); e.new_task()
    if name == 'nan_tof': v.front_tof_m = lambda: float('nan')
    if name == 'nan_odometry': v.odometry = lambda: (float('nan'), 0)
    if name == 'renew_after_expiry': c.t = .2; p.renew()
    result = e.execute('drive', {'distance_m': 1.0 if name == 'nan_tof' else .1, 'speed_mps': .2})
    print(name, result, 'distance=', round(v.x, 3))
PY
```

## Hata sayılmayan, açık kalan işler

L3 planındaki `lite_core`, `ugv_lite` gateway, gerçek donanım sürücüleri ve panel sunucusu henüz tamamlanmamış. Plan bunları açıkça yapılacak iş olarak gösterdiği için eksiklikleri gizli hata diye sayılmadı. Düz URDF ağaç yapısı, nihai bağlantı elemanları ve üretim detaylarının bazıları da konsept kısıtı olarak açıklanmış. T01–T20 fiziksel testleri yapılmış sayılmamalı.

## Claude'a kopyalanacak prompt

```text
UGV-01 projesinde kendi kaldığın yerden devam et, fakat yeni özelliklerden önce bağımsız inceleme bulgularını kapat.

Repo: UGV-01
İlk oku: docs/claude_review_2026-09-25.md
Ardından config/vehicle.json, docs/design_decisions.md, güncel A3 Lite spec/planları ve ilgili kaynakları incele. Git commit tabanı yok; bütün untracked dosyaları mevcut çalışma kabul et, reset/clean yapma.

A3 Lite'ın onaylı bütçe/mimarisini koru: ESP32-S3 + iki ESP32-CAM, MacBook AI/panel, 10.000 TL parça bütçesi. Önceki A2/CM5 belgelerini yanlışlıkla güncel kaynak yapma. Sıra tasarım → ileride baskı → satın alma; fiziksel doğrulama yokken üretim veya sürüş onayı verme.

Raporu otomatik doğru kabul etme: her bulguyu mevcut kaynakta tekrar doğrula. Doğrulananları en küçük kök neden düzeltmesiyle kapat; katılmadığın bulguyu somut test veya resmi veri sayfasıyla açıkla. Mevcut testleri hatalı davranışı kabul edecek şekilde gevşetme.

Öncelik sırası:
1. R1: NaN/Inf odometri ve ToF verisiyle hareketi engelle. İlk örneği ve her tick'i doğrula; geçersiz veride dur/hata ver.
2. R2: Lease/focus/AI-switch kaybını aktif görev için kalıcı kıl. Sonradan yenilenen izin eski model yanıtını çalıştırmasın. Model beklerken timeout→renew ve focus off→on testlerini ekle.
3. R3: can_protocol.c içinde komut tazeliği ile sequence geçmişini ayır. Mod değişince eski imzalı hareket paketi kabul edilmesin. Wrap ve yeni oturum davranışını koru; Lite entegrasyonunda HMAC'li replay regresyonunu çalıştır.
4. R4 ve R7 birlikte: Her bağımsız tekerin stall'ını, yerinde dönüşü, 5° rampada ivmeyi ve tam dolu bataryayı hesaba katarak motor/sürücü/akım sınırlamasını düzelt. 1,8 A stall için TB6612 + 300 ms ön enkoder korumasını yeterli sayma. Arka teker sıkışmasının ön enkoderle görünmediğini çöz. GPIO, ısı, güç ve BOM etkilerini hesapla. Salt hız azaltmayı tork çözümü sayma.
5. R5/R6: ESP32-S3 ADC bölücülerini gerçek ölçüm aralığı ve toleranslara göre düzelt. E-stop durum algısına en kötü durumda süre sınırı getir; boşta ve kısa bas-bırak durumlarını kapsa. Şema jeneratörü, üretilen KiCad/PDF, doküman ve testleri eşleştir.
6. R8: Son dişlili omuz CAD'i için 2x624ZZ ve M4 aksı BOM'a ekle. Gerçek CAD parça sayıları, kol kütle payı, filament, bütçe ve gerekirse CG tahsislerini güncelle. D-mil deliği hakkındaki iddiayı gerçek geometriyle eşleştir. DD numaralarını çakıştırma.
7. R9/R10: Dev tamsayı tool girdisini exception atmadan reddet; görevler arasında görüntü dosyalarının üzerine yazılmasını önle ve log-görüntü ilişkisini koru.

Yazılım bulgularında önce hatayı tekrar eden küçük regresyon testi, sonra düzeltme yap. Var olan test dosyalarını kullan; gereksiz framework/soyutlama ekleme. Donanım bulgularını hesap ve birincil üretici verisiyle çöz; eksik donanım deneylerini NOT_RUN bırak. Güvenli çözüm bütçeye sığmıyorsa bunu sayısal göster ve en küçük işlev azaltımını somutlaştır; güvenlik sınırını düşürerek bütçeyi tutturma.

Doğrulanmış düzeltmelerden sonra ilgili mevcut kontrolleri ve negatif senaryoları çalıştır. Raporu değiştirmek yerine ayrı kısa kapanış kaydı oluştur: R1–R10 için düzeltildi / kanıtla reddedildi / donanım testi bekliyor; dosya, test ve kalan koşulları belirt. Yapılmamış fiziksel deneyleri tamamlandı gösterme. Bu düzeltme paketi kapanmadan yeni AI özelliklerine veya L3 entegrasyonunu büyütmeye geçme.
```
