# A3 Lite düzeltmelerinin yeniden kontrolü

25.09.2026, yaklaşık 10:19 TRT. İncelenen kapanış: `docs/review_closure_2026-09-25.md`.

**Sonuç: Büyük kısmı doğru; R4 ve R7 tamamen kapatılamaz, R6 zaman hesabı düzeltilmeli.** Kaynak kod/şema/CAD değiştirilmedi; yalnız bu değerlendirme eklendi. Bu inceleme sırasında mevcut olan `firmware/lite/lite_core.c` ve testi de kontrol edildi.

## Kalan bulgular

| # | Öncelik | Konum | Sorun |
|---|---|---|---|
| F1 / R4 | P1 | `docs/lite_electronics_A3.md:58`, `tests/check_lite_wiring.py:66–70` | Akım sınırı, sınırsız süreli termal uygunluk sayılmış |
| F2 / R7 | P2 | `tools/calculations.py:38–42,72–76` | Pivot sınırı yuvarlanma ve köprü kaybını dışlıyor |
| F3 / R6 | P2 | `tests/check_lite_wiring.py:105–113`, `docs/lite_electronics_A3.md:19` | Kontak açılmasında pull-up direnci RC hesabında yok |

### F1 — Balast faydalı, fakat termal kapanış kanıtı eksik

7,5 Ω balastın duran motorda akımı düşürmesi doğru. Dört motorun ayrı enkoderle izlenmesi de eski arka teker algılama sorununu gideren yönde. Ancak dokümanın “süre sınırı olmadan önerilen bölgede” sonucu yalnız kanal akımının 1 A altında olmasından çıkarılamaz: iki kanal aynı IC üzerinde ısı üretir.

[Toshiba veri sayfası](https://toshiba.semicon-storage.com/info/datasheet_en_20141001.pdf?did=10660) s.3, 5–6 hem akım hem toplam güç sınırlarını verir: 25 °C'de IC tek başına 0,78 W; belirtilen 50×50 mm, en az %40 bakırlı kartta 0,89 W. 1 A'daki toplam köprü düşümü tipik 0,5 V, maksimum 0,7 V'dur; sıcaklıkla güç sınırı azalır.

Deponun tolerans varsayımlarıyla kaba iki kanal taraması:

```text
V = 12,6 × 1,01 = 12,726 V
Rw_min = (12 / 1,8) × 0,90 = 6 Ω
Rb_min = 7,5 × 0,95 = 7,125 Ω
Rbridge ≈ 0,7 Ω  [veri sayfası 1 A düşümünden tarama yaklaşımı]
I ≈ 12,726 / (6 + 7,125 + 0,7) = 0,9205 A
Pchip ≈ 2 × I² × 0,7 = 1,186 W
```

Bu bir fiziksel ölçüm veya kesin yanma tahmini değildir. Fakat seçilmemiş küçük modülün sınırsız süreli uygunluğunun mevcut hesapla kanıtlanmadığını gösterir. Tipik 0,5 Ω ile dahi aynı tarama ≈0,872 W verir; anahtarlama kaybı ve sıcak ortam marjı henüz yoktur. Direncin 10 W etiketinin de muhafaza içi sıcaklık/yerleşim şartları vardır.

**Gerekli:** İki kanallı modül için ortam sıcaklığı, bakır/termal yol, iletim+PWM kayıpları, izinli akım/süre/görev oranı hesaplanmalı. 300 ms durdurma bir koruma şartıysa süre sınırı yok denmemeli; tekrar deneme ve hareketli yüksek yük de kapsanmalı. Motor dönüyorken ters komut/back-EMF durumu ayrıca değerlendirilmelidir: duran motorun `V/R` hesabı bütün geçiş akımlarını sınırlandıran kanıt değildir. Yeni Lite çekirdeğinin `slew()` fonksiyonu işaret değişiminde çıkışta bekleyen bir sıfır durumu oluşturmuyor (`lite_core.c:53–57`); tek adımda ters PWM başlayabiliyor. Gerçek akımın darbe sınırlarına uygunluğu henüz gösterilmedi.

### F2 — µ=0,45 için “boş pakette döner” sonucu mevcut modelle bile desteklenmiyor

`pivot_motor_current_a` yalnız yanal scrub torkundan hesaplanıyor. Önceki rapordaki yuvarlanma payı ve sürücü gerilim düşümü dönüş hesabına eklenmemiş.

Güncel config, µ=0,45 için:

```text
scrub akımı = 0,636084 A
yuvarlanma torku/teker = mg Crr r / (4η) = 0,018581 N·m
yuvarlanma dahil gereken akım = 0,679214 A
9,6 V'ta balastlı stall akımı = 9,6 / (6,6667 + 7,5) = 0,677647 A
```

Yalnız yuvarlanmayı eklemek bile `docs/calculation_results.md:61` satırındaki “döner” sonucunu tersine çeviriyor. Köprü kaybı, motor toleransı ve pozitif dönüş hızı için gereken geri EMK eklendiğinde marj daha da daralır. Yuvarlanma dahil, köprü kaybı hariç sıfır hız sınırı µ≈0,44875 olur; belgelerdeki µ≤0,48 genel iddiası korunamaz.

**Gerekli:** Pivot modeline yuvarlanma ve köprü düşümünü ekle; sıfır hızdaki tork eşiği ile belirli dönüş hızında çalışmayı ayır. Kapsanan zemin/gerilim/hız ve kısa süre sınırını yeniden türet. `check_design.py` yanlış sonuçları sabitlemek yerine bu bileşenleri kontrol etsin. Bu hâlâ ön modeldir; fiziksel dönüş başarısı ilan edilmemeli.

### F3 — E-stop açılma filtresi 0,1 ms değil

İkinci NC kontakla doğrudan durum okuma, eski kondansatörlü ray algısına göre doğru düzeltme. Ancak kontak açıldığında 100 nF kondansatör **10 kΩ pull-up + 1 kΩ seri direnç** üzerinden dolar:

```text
tau_open = (10k + 1k) × 100n = 1,1 ms
tau_close ≈ 1k × 100n = 0,1 ms
```

Test yalnız ikinci ifadeyi kullanarak `<=1 ms` açılma iddiasını geçiriyor. Dijital High algılama gecikmesi ayrıca GPIO giriş eşiği, toleranslar, kesme ve kontrol döngüsü gecikmesiyle hesaplanmalı. Bu hata tek başına fiziksel E-stop enerji kesmesinin çalışmadığını veya 20 ms hedefinin mutlaka aşıldığını göstermez.

**Gerekli:** Açılma/kapanma yollarını ayrı hesapla, gerçek netlist C/R değerlerini ve giriş eşiklerini kullan; dokümandaki 0,1 ms ve test çıktısındaki ≤1 ms iddiasını düzelt. Şemayı sırf yanlış metne uydurmak için değiştirmek şart değil; gerçek gecikme hedefi karşılıyorsa hesabı düzeltmek yeterli.

## Önceki bulguların durumu

| Bulgu | Yeniden kontrol sonucu |
|---|---|
| R1 | Sonlu sensör verisi kontrolleri ve hareket ortası bozulma regresyonları PASS |
| R2 | Permit generation ile eski görevin timeout/odak dönüşünde tekrar yetkilenmesi engellenmiş; regresyonlar PASS |
| R3 | Tazelik ve sıra geçmişi ayrılmış; mod değişimi ve geçerli HMAC'li replay testleri PASS |
| R4 | Akım azaltma ve bağımsız stall algısı eklenmiş; F1 nedeniyle termal/geçiş kapanışı eksik |
| R5 | 100k/22k oranı, tolerans payı ve gerçek ADC aralığı kontrolü doğru yönde; kalibrasyon fiziksel iş |
| R6 | İkinci kontak ve Lite çekirdeği latch testi mevcut; F3 zaman hesabı açık |
| R7 | İvme/pivot hesapları eklenmiş; F2 nedeniyle dönüş çalışma zarfı hatalı |
| R8 | Eksik rulman/aks ve ana kütle/CAD değerleri düzeltilmiş; BOM L22 notu hâlâ 1,31 kg diyor, 1,367 kg ile eşlenmeli (küçük belge hatası) |
| R9 | Büyük int, bool, NaN/Inf girdileri normal hata olarak reddediliyor; test PASS |
| R10 | Görev bazlı görüntü klasörleri ve log yolları eklenmiş; ardışık görev testi PASS |

## Doğrulama kapsamı

Yerelde yeniden çalıştırılan 13 kontrol grubu PASS: `check_ai_executor`, `check_ai_bridge`, `check_design`, `check_lite_bom`, `check_esp32_pinmap`, `check_markdown_links`, `panel_logic.test.mjs`, `can_protocol_test`, `lite_link_test`, `check_lite_wiring` (ERC dahil), `check_cad`, `check_body_mass`, `lite_core_test`. CAD sonucu 61 geçerli STEP ve baskı kütlelerinin tahsis içinde olmasıdır. Bunlar fiziksel deney değildir.

Bağımsız alt incelemeler kullanım limiti nedeniyle sonuç üretemedi; yukarıdaki sonuçlar ana inceleyicinin doğrudan kaynak okuması, yerel testleri, hesapları ve üretici veri sayfası kontrolüne dayanır. İnceleme kapsamı önceki R1–R10 kapanışı ve ilgili güncel Lite çekirdeğidir; tamamlanmış bütün sistem doğrulaması değildir.

## Claude'a kısa düzeltme promptu

```text
docs/review_recheck_2026-09-25.md dosyasını oku. Önceki yazılım düzeltmeleri yeniden testte geçiyor; onları gereksiz yeniden yazma.

F1/R4: TB6612'nin iki kanalı aynı anda çalışırken toplam kayıp, ortam sıcaklığı ve gerçek modül termal yolunu hesapla. Seri dirençle I<1A olması “süre sınırı yok” kanıtı değil. İzinli süre/görev oranını ve ters komut/back-EMF geçişlerini kapsayan korumayı tanımla; slew sıfırdan geçiş iddiasını gerçek çıktı ve motor hareketiyle test et. Gerekirse en küçük güvenli donanım veya çalışma zarfı değişikliğini bütçeyle birlikte göster.

F2/R7: Pivot hesabına yuvarlanma direnci ve H-köprü düşümünü ekle. µ=0,45, 9,6V senaryosunu regresyon yap; “sıfır hızda tork yeterli” ile “hedef hızda döner” ayrımını koru. Hesap raporu, testler ve mekanik çalışma zarfını birlikte güncelle.

F3/R6: NC kontak açıldığında tau=(10k+1k)*100n=1,1ms; 0,1ms kapanma yoluna ait. Netlist değerleri, GPIO eşikleri ve toleranslarla iki yönü ayrı hesapla; ≤1ms testini ve belgeleri düzelt. Gerçek toplam gecikme hedefi sağlanıyorsa gereksiz devre değişikliği yapma.

BOM L22 filament notunu da güncel 1,367kg PETG tahminiyle eşleştir. Bu üç bulgu için kanıtlı kapanış ekle; fiziksel termal/pivot/E-stop testlerini NOT_RUN bırak. Mevcut A3 bütçe ve kullanıcı kararlarını koru, kanıtsız sınırsız çalışma veya üretim onayı verme.
```
