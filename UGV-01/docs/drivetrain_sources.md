# UGV-01 — Tahrik kaynak kaydı

Revizyon A, kontrol tarihi 2026-09-22. Bağlantılar üretici sayfalarıdır; fiyat ve stok sipariş sırasında yeniden doğrulanır. Aşağıdaki kısa veri özetleri ile bizim hesaplarımız birbirinden ayrıdır. Ürün tanıtımındaki stall değerleri sürekli çalışma rating'i değildir.

| ID | Birincil kaynak | Tasarıma alınan veri / sınırlama |
|---|---|---|
| D01 | [Pololu #4753, 50:1 özellikler](https://www.pololu.com/product/4753/specs) | 12 V, 200 rpm, 0.20 A yüksüz; ekstrapole stall 5.5 A / 21 kgf·cm; 205 g; Ø37 × 70 mm gövde; 3200 count/çıkış turu. |
| D02 | [Pololu #4754, 70:1 özellikler](https://www.pololu.com/product/4754/specs) | 12 V, 150 rpm, 0.20 A yüksüz; ekstrapole stall 5.5 A / 27 kgf·cm; 205 g; Ø37 × 70 mm; maksimum verim noktasında 130 rpm, 3.2 kgf·cm, 0.68 A, 4.2 W. |
| D03 | [Pololu #4755, 100:1 özellikler](https://www.pololu.com/product/4755/specs) | Gerçek oran 102.08:1; 100 rpm; 34 kgf·cm / 5.5 A ekstrapole stall; 0.20 A yüksüz; 210 g; Ø37 × 72.5 mm; yaklaşık 6533 count/çıkış turu. |
| D04 | [Pololu #4754 ürün / encoder / montaj](https://www.pololu.com/product/4754) | 70:1 tam oran, 6 mm D mil, 16 mm mil boyu; encoder 3.5–20 V besleme ve en fazla 10 mA; A/B çıkışları besleme seviyesinde; 64 sayım motor turu başına iki kanalın bütün kenarları sayılarak elde edilir; önerilen montaj vidası giriş derinliği en fazla 3 mm. |
| D05 | [Pololu 37D aile teknik uyarıları](https://www.pololu.com/category/116/37d-metal-gearmotors) | Sürekli redüktör yükü üst önerisi 10 kgf·cm; anlık 25 kgf·cm. Genel motor akım önerisi stall akımının %25'i veya altıdır. Stall değerleri ekstrapolasyondur; stall birkaç saniye içinde zarar verebilir. |
| D06 | [Pololu 37D veri sayfası Rev 1.2](https://www.pololu.com/file/0J1736/pololu-37d-metal-gearmotors-rev-1-2.pdf) | Ayrıntılı motor eğrileri ve nominal gerilim karşılaştırması için ana referans. Ürün sayfasındaki güncel varyant verileri esas alınır; eğriler bir ünitenin seri üretim garanti toleransı yerine geçmez. |
| D07 | [ServoCity 5203-2402-0019](https://www.servocity.com/5203-series-yellow-jacket-planetary-gear-motor-19-2-1-ratio-24mm-length-8mm-rex-shaft-312-rpm-3-3-5v-encoder/) | Alternatif: 12 V, 312 rpm, 0.25 A yüksüz, 9.2 A stall, 24.3 kgf·cm stall, 437 g, 8 mm REX mil, quadrature encoder. Sayfada sürekli motor/gearbox tork garantisi verilmediğinden stall üzerinden sürekli seçim yapılmadı. |
| D08 | [Pololu teknik destek — mil yükü](https://forum.pololu.com/t/geared-dc-motor-selection/23225) | Üretici çalışanı tarafından ayrıntılı radyal/eksenel ömür karakterizasyonu yapılmadığı ve 1–1.5 kgf seviyesinin ancak pratik tahmin olduğu belirtiliyor. Bu, garantili rating değildir; dış rulmanlı mil seçiminin gerekçesidir. |

## Satın alma notu

#4753/#4754/#4755 sayfaları araştırma anında 60.95 USD/adet ve “Active and Preferred” gösterdi; “backorders allowed” ifadesi stokta dört adet bulunduğunu kanıtlamaz. Dört #4754 için çıplak liste toplamı 243.80 USD; vergi, nakliye ve ithalat dahil değildir. Encoder olmayan #4744 ve eski #2825 ile karıştırılmamalıdır. Motor tedarik toleransı, ülke tedariki ve numune testi satın alma kapısıdır.

## Doğrulanmamış veya projeye ait değerler

8 kg toplam kütle, sürtünme katsayıları, 0.95 dış aktarım verimi, 1.5 teker yük katsayısı, 1.3 A RMS tasarım bütçesi, 2.5 A kısa akım sınırı ve kasa sıcaklık eşikleri UGV-01 mühendislik varsayımlarıdır. Bunlar kaynaklarda verilen sertifikalı çalışma değerleri olarak sunulmaz. Tüm türetilmiş sonuçlar [ön hesap raporundadır](drivetrain_calculations.md).
