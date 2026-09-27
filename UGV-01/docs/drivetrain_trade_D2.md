# D2 tahrik kütlesi ve dayanım kararı

23.09.2026 · A0 üretim baz çizgisi değildir; D1 ve D2A PH4 tasarım adaylarıdır.

## Karar

8 mm mil +608 rulman daha hafif olsa da 9 kg mekanik tarama ve yüksek tutunmalı zeminde seçilmiyor. D2A, D1'in 10 mm mil +iki6000 rulman yerleşimini korur. Mil malzemesi sertifikalı **42CrMo4+QT** adayı olur; jant ve lastiğin yalnız yük aktarımı dışındaki malzemesi çıkarılır. Bütün değerler statik ilk elemedir; yorulma, baskı ve sürüş doğrulaması değildir.

## Karşılaştırma koşulları

9 kg yapısal tarama kütlesi, 3g düşey eşdeğer yükün iki tekerde paylaşılması, 60 mm teker yarıçapı, 1,5 Nm mil torku, 1,8 varsayılan çentik katsayısı. Yanal tutunma katsayısı **μ=1,0** ve hassasiyet için **μ=1,2**. 9 kg değeri sürüş kütlesi ilanı değildir; motorun 15° eğimdeki termal sınırı yeniden incelenmelidir. Akma/statik rulman ön hedefi≥2; gerçek güvenilirlik ve yorulma için bu tek başına yeterli değildir.

| Seçenek | Mil/yatak | μ=1,0: mil / rulman payı | μ=1,2: mil / rulman payı | Kütle etkisi |
|---|---|---:|---:|---|
| D1 mevcut | Ø10 C45 normal, SKF6000 |2,07 /2,80|**1,73** /2,39| Başlangıç6,025 kg |
| D1.1 malzeme | Ø10 42CrMo4+QT, SKF6000 |4,40 /2,80|3,69 /2,39| İhmal edilebilir geometri değişimi |
| Dar yatak alternatifi | Ø8 42CrMo4+QT, SKF608 |2,26 /2,08|**1,89 /1,79**| Yaklaşık109 g/araç tasarruf |

SKF608 için iç rulman merkezi123, dış merkez137,5 mm; 7 mm yatak genişliği merkez açıklığını14,5 mm'ye çıkarır. SKF6000 için merkezler123,5/137 mm, açıklık13,5 mm. Geliştirilmiş açıklığa rağmen608'in1,37 kN statik C0 değeri μ=1,2 taramasında yetersiz kalır. Dar paketin yaklaşık27,15 g/teker tasarrufu sadece yaklaşık0,109 kg/araçtır; diğer parçaların ölçüsü ve tasarımı henüz çizilmedi. Kütle yararı dayanım kaybını haklı çıkarmıyor.

42CrMo4+QT için650 MPa minimum akma, **Ø56 mm tek parça mil/flanşın üretileceği Ø40–100 mm kaynak kesit sınıfının koşullu alt sınırıdır**. İnce Ø8 soğuk çekilmiş mil verisini Ø56 mm billet için kullanmıyoruz. Satın almada ısıl işlem ve malzeme sertifikası, parça üzerinde sertlik ve kritik omuz/segman yorulma incelemesi şart. Malzeme değişimi C45 modelini otomatik kalifiye etmez.

## D2A hafifletme CAD'i

Özgün [UGV-MECH-046-B jant STEP](../cad/drivetrain/generated/lightweight/UGV-MECH-046-B.step) dış webinde, dört M3 cıvatanın arasına dört adet Ø22 mm pencere açıldı. Cıvata çevresi, dış jant namlusu ve sekiz lastik tırnağı korundu. [UGV-MECH-047-B lastik STEP](../cad/drivetrain/generated/lightweight/UGV-MECH-047-B.step) sırtının kaburgalar arasındaki bölgesi2 mm inceltildi; sekiz tahrik kaburgası tam kalınlıkta bırakıldı. [UGV-MECH-042-B mil STEP](../cad/drivetrain/generated/lightweight/UGV-MECH-042-B.step) geometri olarak D1 ile aynıdır; B revizyonu malzeme şartını işaretler. Basılacak parçaların STL dosyaları aynı klasördedir.

Yeni jant ve lastik katıları D1 katılarının **alt kümesidir**: dış zarf büyümez. Bu nedenle D1'in dört modüllü araç yerleşiminde yeni hacimsel çakışma yaratmaz. Alt küme kontrolü gerçek STEP katılarıyla yapıldı; bunun mukavemet kanıtı olmadığı açıktır.

| Kütle hesabı | Sonuç |
|---|---:|
| Jant tasarrufu |5,47 g/teker|
| Lastik tasarrufu |17,57 g/teker|
| Toplam dört teker tasarrufu |92,16 g|
| D2A tahmini boş kütle |**5,933 kg**|
| 6 kg hedefe kalan rezerv |**67 g**|
| Sağlam bir0,30 kg geliştirme rezervi için ek gereken tasarruf |**yaklaşık233 g**|

Kütle yoğunluğu iki polimer için1,2 g/cm³ kabulüdür; gerçek filament, baskı doluluğu, bağlantı elemanı ve kablo kütleleri tartılmadı. Bu nedenle6 kg SYS-004 sınırının gerçek araçta geçtiği iddia edilmez. Güvenli bir rezerv olmadan PH4 kapatılamaz. Taban veya taşıyıcıda rastgele boşaltma yapıp bu açığı kapatmayacağız; metal yük yolunda kesit/FEA ve fikstür testi gerekir.

## Üretim ve test geçiş koşulları

1. Jant B parçasını PAHT-CF ile dik teker ekseninde bas. Önce M3 havşadaki katman ezilmesi, dört pencere köşe/katman çatlağı ve göbek web sehimini ölç. Keskin kesişimlere CAD filleti ve gerçek nozul ölçüsüne göre minimum et kalınlığı geçişi sonraki revizyonda eklenecek.
2. Lastik B parçasını TPU95A ile bas. Pencere yerine lastikte kaburga arası sırt kalınlığı4 mm nominal; ilk baskıda köprülenme/kapalı destek, yan duvar sürekliliği ve boyutsal geçme incelenecek. Abrasif zeminde aşınma ve sıcaklık denemesi olmadan sürüşe verilmez.
3. Jant–lastik çiftini en az ±1,5 Nm ve1000 ters çevrimde ön taramadan geçir. Sekiz tırnakta kesilme, cebin yırtılması veya jantta kalıcı çatlak reddir. 3g/9kg yanal+düşey fikstür yükünde kalıcı şekil değişimi ve rulman sıkışması olmamalı; fikstür kuralları D1 raporundadır.
4. Mil B için malzeme/ısıl işlem sertifikası ve işlenmiş kritik kesit ölçüsü alınmadan çelik stok siparişi kilitlenmez. Ø10/6000 geçmesi, segman kanalı ve omuz yarıçapları ayrıca çizime işlenecek.
5. D2A jant/lastik baskı kuponlarını tart; ardından tüm aracı gerçek BOM ile tart. 67 g hesabı gerçek rezerv sayılmaz.

## Kaynak ve yeniden üretim

- [42CrMo4 tedarikçi mekanik tablo](https://www.interacciai.it/prodotti/acciai-da-bonifica/42crmo4/) (Ø40–100 mm +QT akma alt sınırı650 MPa).
- [SKF rulman kataloğu](https://www.skf.com/binaries/pub12/Images/0901d196807026e8-100-700_SKF_bearings_and_mounted_products_2018_tcm_12-314117.pdf) (6000 ve608 ana ölçü/C0); [608-2RSH tedarikçi verisi](https://www.tme.com/Document/fcfecc3f5c77dbee246da0f6ca843c15/608-2RSH.pdf) (8×22×7 mm,0,012 kg).

```sh
python3 tools/drivetrain_trade.py
.venv/bin/python cad/drivetrain/build_lightweight.py
.venv/bin/python tests/check_lightweight.py
```

Hesap makinesi [JSON sonuçlarını](drivetrain_trade_D2.json) ve CAD üretici [kütle/koşul raporunu](../cad/drivetrain/lightweight_report.json) yazar. Üretim release'i için şu anda açık olan esas iş: metal yük yolu, geçmeler, yorulma, baskı kuponu, gerçek kütle ve fiziksel sürüş testleri.
