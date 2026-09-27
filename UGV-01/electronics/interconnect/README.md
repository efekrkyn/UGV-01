# PWR ↔ MCU kablo arayüzü — P0

[KiCad şematiği](pwr_mcu_harness.kicad_sch) ve [PDF çizimi](pwr_mcu_harness.pdf) iki kart arasındaki **kablo sürekliliğini** gösterir. J1/J3 PWR kartı ucundaki, J2/J4 MCU kartı ucundaki dişi kablo housing'leridir. J1↔J2 dört damar Mega-Fit; J3↔J4 on iki damar JST GH (iki bükümlü diferansiyel çift dahil). Her iki uçta aynı pin numarası birbirine gider. Elektrik net ve AWG kaynağı [`config/pwr_mcu_connector.json`](../../config/pwr_mcu_connector.json), güvenlik davranışı [arayüz sözleşmesinde](../../docs/pwr_mcu_interface.md).

`Conn_01x04` ve `Conn_01x12` genel sembolleri yalnız kablo uçlarını temsil eder; bu dosya PWR/MCU kart şematiği, PCB footprint, PCA9615 tampon/sonlandırma devresi veya krimp yüzü çizimi değildir. Kart üzerindeki erkek header MPN'leri 768250004 ve BM12B-GHS-TBT'dir; kablo dişi housing'leri 1700010104 ve GHR-12V-S'dir. Dişi housing'e **kablo tarafından bakıldığında** cavity numaraları gerçek üretici çizimi/örnek üzerinde onaylanmadan krimp yapılmaz. İki NC E-stop fiziksel güvenlik hattı bu konnektörlerden geçmez.

[Ayrı diferansiyel I²C referans şematiği](differential_i2c_reference.kicad_sch) ve [PDF](differential_i2c_reference.pdf), iki PCA9615'in kart içi I²C'den J-SIG'deki dört diferansiyel tele geçişini gösterir. Her kartta `VDD(A)=3,3 V`, `VDD(B)=5 V`; her çiftte iki uçta da 600 Ω / 120 Ω / 600 Ω bias-sonlandırma, kart içinde 4,7 kΩ pull-up ve her raya 100 nF bypass vardır. `EN`, yerel `PGOOD` kaynağı oluşana kadar 10 kΩ ile Low tutulur. NXP'nin 54 µA azami EN Low giriş akımında bu direnç için `V_EN≤0,54 V`, 3,3 V beslemeyle `VIL(max)=0,99 V` olur. `PGOOD` üreticisi ve güç rayları bu çizimin **dışındadır**. Çizim iki ayrı üretim kartını bir sayfada anlatır; doğrudan PCB'ye dönüştürülmez. 1–8 numaralı güvenlik sinyalleri bu referansta yoktur.

5 V ve 600/120/600 Ω ile her uçtaki diferansiyel DC bias yaklaşık `5×120/(600+120+600)=0,455 V`; diferansiyel AC yük yaklaşık `120||(600+600)=109 Ω` olur. NXP bunu 100 Ω sınıfı kablo örneği olarak verir; gerçek kablo empedansı ve yansıma osiloskopla ölçülecek. 4,7 kΩ ile varsayılan 100 pF yerel kapasite için ideal 30–70% yükselme yaklaşık `0,8473×4,7 kΩ×100 pF=0,398 µs`; bu yalnız 100 kHz başlangıç değeri, kapasite ve `VOL` kabulü ölçülür. NXP'nin 5,5 V/iki kanal Low/sonlandırma sürme tablosunda `VDD(B)` akımı üst sınırı 91 mA'dır; iki kartın yerel 5 V tasarımında **kart başına ≥0,1 A** ayrıca ayrılır. Bu değer çip termal kaybı veya bütün kart akımı değildir. [Üretici veri sayfası](https://www.nxp.com/docs/en/data-sheet/PCA9615.pdf).

```sh
python3 tools/build_pwr_mcu_harness.py
python3 tests/check_pwr_mcu_harness.py
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch export pdf -o electronics/interconnect/pwr_mcu_harness.pdf electronics/interconnect/pwr_mcu_harness.kicad_sch
python3 tools/build_differential_i2c_reference.py  # ayrıca iki kısmi kart arayüz sayfasını üretir
python3 tests/check_differential_i2c_reference.py
python3 tests/check_board_interface_sheets.py
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch export pdf -o electronics/interconnect/differential_i2c_reference.pdf electronics/interconnect/differential_i2c_reference.kicad_sch
```

Başka KiCad kurulumunda kablo üretici/testi için `UGV_KICAD_CONNECTOR_LIBRARY` ve `UGV_KICAD_CLI` ortam değişkenleriyle sembol kütüphanesi/CLI yolu verilir; diferansiyel üretici şu anda KiCad 10 macOS yolunu kullanır. Kablo testi 16 adlandırılmış ağın sürekliliğini, diferansiyel referans testi PCA9615 pinlerini ve direnç ağını, kart arayüz testi J-PWR/J-SIG pin eşleşmesini denetler. Kablo ve iki uçlu referans ERC'si sıfır ihlaldir. Kısmi kart sayfalarının her birinde diğer sayfalara devredilen dokuz ağ için uyarı vardır; bunlar tam kart ERC'si değildir. Güç sırası ve EMI/sinyal bütünlüğü ayrıca doğrulanacaktır.
