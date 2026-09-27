# K1 motor barası rölesi — seçim kapısı

23.09.2026 · PH6 tasarım girdisi. **K1 MPN'si henüz serbest bırakılmadı.** K1, K2 MOSFET yolu kısa devre kalmış olsa bile dört motor ve servo beslemesini açabilmelidir. F1'in 15 A değeri ani kesme akımını 15 A ile sınırlamaz; sigorta zaman-akım eğrisi ve sürücü transient'i ayrıca hesaba katılır. E-stop torku kaldırır, eğimde aracı tutmaz.

## Zorunlu elektrik zarfı

- Kaynak: 4S Li-ion, 12,4–16,8 V normal çalışma; BMS/regen geçişleri daha yüksek olabileceği için kontak gerilimi yalnız “12 V” kabul edilmez.
- Beklenen dört köprü: 4×2,7 A nominal donanım limiti = 10,8 A; bu, PWM/blanking ve hata akımının matematiksel üst sınırı değildir. Servo girişi ve motor barası bulk şarj akımı da K1'den geçer. T01/T13'te K2-kısa arıza enjeksiyonunda gerçek `I_break`, `V_contact`, dI/dt ve kontak arkı ölçülür.
- K2 sonrası 4700 µF bulk'un doğrudan K1 kapanışına bağlanması reddedildi. [Ayrı ön şarj/tanı sırası](precharge_and_separator_diagnostics.md) K2 veya ön şarj FET'i kısa iken K1'i **kapatmaz**; sağlıklı durumda K1 küçük MID hacmine kapanır, bulk 470 Ω üzerinden dolar. Bu sıralama şematik ve tek arıza testleriyle kanıtlanana dek katalog “30 A” ifadesi kontak inrush garantisi değildir.
- K1 normalde açık, bobin enerjisizken açık; bobin izni çift NC E-stop + manuel reset + haricî watchdog + UV/OV zincirinden gelir. MCU High çıkışı tek başına röleyi kapatamaz. Bobin TVS/Zener bastırma ve sürücü arızası bırakma süresiyle birlikte sınanır; çıplak rölenin katalog bırakma süresi toplam güvenlik süresi değildir.
- Kontak kaynaması için K1 sonrası/K2 öncesi ara düğüm ayrı ölçülür. Rölede yardımcı kontak yoksa yüksek empedanslı bölücü ile tek başına kesin “kontak açık” hükmü verilmez: kaçak, bulk ve motor geri EMK'sı ayırt edilir; sınırlı tanılama akımı ve boşalma süresiyle iki yönde hata enjeksiyonu gerekir.

## Aday taraması

| Aday | Bobin / mekanik | Kaynakta kanıtlanan kontak bilgisi | Sonuç |
|---|---|---|---|
| [TE T9AS1D17-5](https://www.te.com/en/product-1-2071229-4.html) | 5 V, 25 Ω, 1 W; 32,51×27,43×20,4 mm; PCB tipi | Ürün sayfasında 30 A genel akım sınıfı ve en çok 30 V DC switching. [T9A seri veri sayfasının](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=T9A&DocType=Data+Sheet&PartCntxt=1-2071229-4) NO DC ömür tablosu 20 A/28 V **rezistif** koşul verir. | 5 V kontrol rayıyla beslenebilir; 4S motor yükünü K2-kısa halinde açma ömrü/arkı kanıtlanmadığından **yalnız paketleme ve bobin bütçesi adayı**. TE sayfası şu an doğrudan temin edilemediğini belirtiyor. |
| [Panasonic ACTE3CH2A05V](https://na.industrial.panasonic.com/products/relays-contactors/mechanical-power-relays/lineup/automotive/series/2979/model/144141) | 12 V, 160 Ω, 0,9 W; yaklaşık 6,5 g; çalışma bobin aralığı 10–16 V | 25 A/14 V DC motor kilit testi; 20 A/14 V DC NO rezistif; bırakma ≤10 ms **diyotsuz** koşul | Ham 4S 16,8 V bobini aşar. Regüle 12 V ister; 16,8 V temas/ark durumu 14 V katalog testinden çıkarılamaz. 1 Form C×2 kontakları paralel bağlayarak akım ikiye bölünecek varsayılmaz. **Koşullu alternatif.** |
| [Omron G4A-1A-PE DC12](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g4a.pdf) | 12 V/0,9 W; yaklaşık 23 g; PCB tipi | Başlıktaki 80 A inrush/20 A motor break deneyi **250 VAC**. Belgelenen 15 A/30 VDC onay değeri **rezistif**, 40 °C; motor DC değil. | İlk bakışta uygun görünen “motor 20 A” sayısı 4S DC kesme kanıtı değildir. 12 V regülasyon ve 26,8 mm gövde yüksekliği de mevcut zarfı zorlar; **reddedildi**. |

12 V bobini doğrudan ham 4S'e bağlamak kabul edilmez: Panasonic örneğinde 16,8 V > 16 V çalışma üstü; 4S alt ucunda da sıradan buck ile 12 V regülasyon marjı yoktur. 12 V aday kullanılacaksa 12 V buck-boost PH6'da gerçek bobin sürücüsü olarak tasarlanıp UV'de kapalı kalma davranışı doğrulanır. TE 5 V adayı için `I=5/25=0,20 A`, `P=1,00 W`; 5 V/2 A kontrol hattının 10 W kapasitesinde mevcut 3 W ağır kontrol bütçesi 4 W'a çıkar, **6 W kuramsal pay** kalır. Bu pay PCB sıcaklığı ve başlatma akımı ölçülmeden nihai değildir. K1 enerjiliyken batarya görev bütçesine yaklaşık `1/0,90=1,11 W` eklenir. 

TE gövdesi z=57 mm PCB altı + 1,6 mm PCB + 20,4 mm gövde varsayımıyla z=79 mm'ye ulaşır; ayrılan elektronik hacim z=57–81 mm içinde **yalnız 2 mm nominal pay** kalır. PCB üzeri lehim/üretim toleransı, kontak pimi, raf esnemesi ve servis boşluğu bu payı tüketebilir. Gerçek üretici STEP'i, footprint, giriş/çıkış bakırı ve vida/raf konumu ile yeniden değerlendirilir. [Paketleme kapısı](electronics_packaging_gate.md).

**PH6 kapanış koşulu:** kesin MPN ve üretici onayı/uygun DC motor yük eğrisi; 16,8 V, worst-case akım ve K2-kısa arıza koşulunda açma; bobin tüm gerilim/sıcaklıkta çalışma-bırakma; coil clamp dahil ≤150 ms toplam fault-to-bus-off hedefi; K1 kaynaklı kontak algılama; ölçülmüş PCB/kontak ısısı; tedarik ve ağırlık. Bu kapı geçmeden röle footprint'i veya PCB Gerber'i üretim adayı değildir.

## 24.09.2026 şema ve paketleme ara durumu

K1 [aktüatör yolu sayfasında](../electronics/ugv_pwr_01/actuator_path.kicad_sch) KiCad genel `Relay_SPST-NO` simgesiyle, `K1 relay MPN OPEN` değeri ve **boş footprint** ile çizildi; T9AS1D17-5 yalnız alan notunda paketleme adayıdır. Bobin üst ucu NC-A kontağının döndürdüğü `ESTOP_A_5V`, alt ucu `SAFE_GATE ∧ K1_CMD` ile sürülen AO3400A'dır; 1N4148W + 12 V zener kelepçe bobin enerjisini söndürür (Q201 `Vds` ≈18,9 V). [Netlist testi](../tests/check_pwr_actuator_path.py) footprint'in boş kaldığını denetler.

Üretici tablo karşılaştırması değişmedi: ne TE (20 A/28 V **rezistif**) ne Panasonic (14 V motor kilidi, 16 V bobin üst sınırı) 16,8 V DC motor yükünü K2 kısa iken 50 °C bölmede açma kanıtı vermez. Bu nedenle BOM `SELECTION-OPEN-K1` kalır.

| z tolerans katkısı (varsayım) | mm |
|---|---:|
| Raf düzlüğü | 0,5 |
| PCB 1,6 mm +%10 | 0,16 |
| Röle gövde yüksekliği (TE çizimi toleransı doğrulanmadı) | 0,3 |
| Oturma/lehim | 0,1 |
| IPC-6012 eğilme %0,75 × 120 mm | 0,9 |
| Basılı kapak iç yüzü | 0,3 |
| **En kötü toplam / RSS** | **2,26 / 1,13** |

2 mm nominal pay en kötü durumda −0,26 mm'dir; RSS pozitif olsa da serbest bırakma için yetmez. Seçenekler: üretici STEP'i ve ölçülmüş kart/raf ile yeniden hesap, K1'i metal şasiye kart dışı vidalı montaj (ek kablo ve bağlantı direnci) veya bölme yüksekliği revizyonu. Hiçbiri seçilmedi.

**T13 K1 ölçüm satırları (NOT_RUN):** K2-kısa dummy yükünde `I_break` ve dI/dt; kontak gerilimi `V(TP201)−V(TP202)`; `TP204` bobin alt ucu ile komut Low → kontak açılma süresi, hem sürücü kapanarak hem NC-A açılarak (lojik High'a zorlanmış jig); kaynaklı kontak simülasyonunda `K1_FB=1, K1_CMD=0` ve ARM reddi; 12,4/16,8 V ve 50 °C tekrarları.
