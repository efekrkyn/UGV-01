# PWR → MCU durum hatları: güçsüz alıcı taslağı

23.09.2026 · PHASE 5 şematik girdisi; PCB/üretim onayı değil. Kaynak arayüz: [J-SIG sözleşmesi](pwr_mcu_interface.md). Fiziksel çift NC E-stop bu dijital alıcıdan geçmez.

## İşlev ve aday

PWR kartından gelen altı 3,3 V durum/izin sinyali, MCU'nun 3,3 V rayı kapalıyken doğrudan STM32 GPIO/ESD diyotlarına ulaşmamalı. MCU kartında, J-SIG ile STM32/nSLEEP arasında **SN74LVC244APWR** sekiz kanallı tampon adayı kullanılır. [TI veri sayfasına](https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf) göre VCC çalışma aralığı 1,65–3,6 V, giriş aralığı 0–5,5 V ve VCC=0 iken `Ioff` üst sınırı pin başına ±20 µA (−40…125 °C). TSSOP20 `PW` paketinde iki ayrı aktif-Low `OE` vardır. Bu özellik, tek başına seri dirençten daha güçlü bir güçsüz giriş sınırı sağlar; motor izin zincirinin tek güvenlik katmanı değildir.

| J-SIG girişi | A pini | Y pini | Yerel çıkış |
|---|---:|---:|---|
| `PWR_ACT_EN` | 1A1, 2 | 1Y1, 18 | `ACT_PERMIT_BUF` → dört nSLEEP donanım yolu ve PD10 readback; TIM1/TIM8 BKIN bağlantı polaritesi ayrıca çözülecek |
| `PWR_K1_FB` | 1A2, 4 | 1Y2, 16 | PD11 |
| `PWR_K2_FB` | 1A3, 6 | 1Y3, 14 | PD12 |
| `ESTOP_A_CLOSED` | 1A4, 8 | 1Y4, 12 | PD13 |
| `ESTOP_B_CLOSED` | 2A1, 11 | 2Y1, 9 | PD14 |
| `PWR_WD_OK` | 2A2, 13 | 2Y2, 7 | PD15 |

VCC pin20 → `MCU_3V3`, GND pin10 → `PGND`. Boş 2A3(pin15), 2A4(pin17) girişleri GND'ye; boş 2Y3(pin5), 2Y4(pin3) çıkışları açık bırakılır. Her kullanılan **çıkışta** 10 kΩ yerel GND pulldown bulunur; tampon High-Z/MCU kapalıyken ACT izni de Low'a döner. TI'nin 20 µA uç kaçak sınırında `V_Y ≤ 20 µA × 10 kΩ = 0,20 V`; bu bir pin düzeyi hesabıdır, bütün girişlerin toplam akımı ve gerçek sıcaklık ayrıca ölçülür. Tampon High sürerken pulldown akımı en fazla `3,3 V/10 kΩ = 0,33 mA/kanal`, altı çıkış birlikte yaklaşık 2 mA'dır.

Her iki `OE` pinini 10 kΩ ile `MCU_3V3`'e çek; iki `OE`'yi ancak `MCU_RAILS_OK` sağlandıktan sonra yerel transistor açık-kollektör katıyla Low'a sür. TI, power-up/down sırasında `OE`'lerin VCC'ye pull-up ile High-Z tutulmasını önerir. `MCU_RAILS_OK` için 3,3 V ve 5 V gözetimi, eşikler/histerezis, reset gecikmesi ve transistor MPN'si PH5 tam kart şematiğinde seçilecek. PCA9615 `EN` de yalnız iki yerel ray kararlı ve bus idle iken açılacak. 0–1,65 V VCC ara bölgesindeki davranış veri sayfasında garanti edilmediği için 10 kΩ nSLEEP pulldown ve PWR K1/K2 kesici zinciri bu durumda bağımsız kalır.

## Mantık ve kabul sınırı

- Tampon girişinde VCC=2,7–3,6 V için `VIH(min)=2,0 V`, `VIL(max)=0,8 V`. PWR High alt sınırı ve kablo/PGND düşümü birlikte `VIH`'yi; PWR Low üst sınırı ile ortak mod sıçraması `VIL`'i sağlamalı. Yavaş kenar, negatif transient ve EMI osiloskopla ölçülmeden bu aday kabul edilmez.
- `Ioff`, VCC **tam 0 V** şartında verilen bir sınırdır. Brownout, 0–1,65 V ara rayı, `OE` belirsizliği ve çıkışa başka karttan geri sürme ayrıca fault-injection testidir. Sinyal yalnız telemetri olduğunda hat kaybı FAULT; `PWR_ACT_EN` için kayıp doğrudan nSLEEP Low yapar.
- `ACT_PERMIT_BUF` çıkışından dört DRV8874 nSLEEP girişine ve PD10'a toplam fan-out/RC, 10 kΩ pulldown, sürücü `VIH/VIL`, kablo transient'i ve TIM break kutbu tam şematikte doğrulanır. Tamponun arızalı High çıkışı K1/K2 donanım kesicilerini aşamaz.
- T01/T03/T13/T14 testlerinde PWR açık-MCU kapalı, MCU açık-PWR kapalı, brownout, tek damar kopuğu ve J-SIG sökme koşullarında MCU 3,3 V rayı geri beslenmeyecek; nSLEEP izin çıkışı yanlış High olmayacak. Giriş/çıkış akımı, gerilim ve K1/K2 durumu kaydedilecek. Bu masaüstü seçimi bu testlerin yerine geçmez.

Bu devre [ayrı kısmi KiCad sayfasına](../electronics/ugv_mcu_01/status_receiver.kicad_sch) ve [PDF'e](../electronics/ugv_mcu_01/status_receiver.pdf) çizildi. Altı giriş, altı 10 kΩ çıkış pulldown, iki OE ve bir 10 kΩ OE pull-up gerçek netlistte [denetlenir](../tests/check_status_receiver.py). ERC'de 6 `pin_not_driven` hatası ve 6 `isolated_pin_label` uyarısı, PWR sürücü/konnektör sayfaları henüz birleşmediği için açık kalır; 1 yerel `UGV` symbol-library yapılandırma uyarısı da var. Bu **tam kart ERC onayı değildir**. `MCU_RAILS_OK_N` açık-drenaj sürücüsü, ray gözetimi, brownout davranışı ve nSLEEP/TIM break fan-out tam kartta bağlanıp doğrulanmadan P0 geri besleme bulgusu kapanmaz.
