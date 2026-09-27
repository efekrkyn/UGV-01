# Elektrik kaynak kaydı

Erişim: 2026-09-22. Teknik veri için üretici belgeleri kullanılmıştır. “Aktif ürün” tedarikçinin yerel stoğu demek değildir. Katalogdaki tipik değer ile tasarım varsayımı ayrı tutulur. Fiyatlar satın alma teklifi değildir; sistem BOM'undaki tahmini kalemlerin stok ve fiyatı siparişten önce yenilenir.

| ID | Birincil kaynak | Kullanılan kapsam |
|---|---|---|
| E01 | [ST STM32G474VE](https://www.st.com/en/microcontrollers-microprocessors/stm32g474ve.html) | G4 kaynakları: timer, FDCAN, USB ve paket seçimi |
| E02 | [ST DS12288 Rev6](https://www.st.com/resource/en/datasheet/stm32g474ve.pdf) | Tablo12/13 pin/AF; LQFP100; timer encoder fonksiyonları |
| E03 | [Pololu 4754](https://www.pololu.com/product/4754) | 70:1 12 V 37D encoder'lı motor; akım, boyut, hız girdileri |
| E04 | [TI DRV8874 veri sayfası](https://www.ti.com/lit/ds/symlink/drv8874.pdf), [ürün](https://www.ti.com/product/DRV8874) | §6 elektrik değerleri; akım limiti/RMS/thermal; 450 µA/A elektrik tablosu ile örnekteki455 farkı |
| E05 | [Raspberry Pi CM5IO veri sayfası](https://datasheets.raspberrypi.com/cm5/cm5io-datasheet.pdf), [CM5IO product brief](https://datasheets.raspberrypi.com/cm5/cm5io-product-brief.pdf) | §2.2 USB-C5V5A ve haricî5V J8;160×90 mm referans envelope |
| E06 | [PEAK PCAN-USB FD](https://www.peak-system.com/products/hardware/external-pc-interfaces/pcan-usb-fd/), [Linux](https://www.peak-system.com/fileadmin/media/linux/can-implementation.php), [manual](https://www.peak-system.com/produktcd/Pdf/English/PCAN-USB-FD_UserMan_eng.pdf) | USB-A IPEH-004022; SocketCAN peak_usb; yeni hardware/kernel sınırlaması |
| E07 | [Microchip MCP2518FD](https://www.microchip.com/en-us/product/MCP2518FD), [datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/External-CAN-FD-Controller-with-SPI-Interface-DS20006027B.pdf) | Carrier için SPI CAN denetleyicisi; ayrıca transceiver gereklidir |
| E08 | [Molicel P45B](https://www.molicel.com/product/inr-21700-p45b/), [P45B v1.4 datasheet](https://www.molicel.com/wp-content/uploads/INR21700P45B_1.4_Product-Data-Sheet-of-INR-21700-P45B-80109.pdf) | Hücre3.6V4.5Ah tipik4.3Ah min;4S2P9Ah129.6Wh türetilmiştir |
| E09 | [TI LM61495](https://www.ti.com/product/LM61495) | 36 V giriş/10 A IC; bizim compute rail hedefimiz6A, PCB termal test gerekir |
| E10 | [TI TPS55288](https://www.ti.com/product/TPS55288) | 12 V auxiliary için buck-boost aday; katalog switch/current başlığı çıkış garantisi sayılmaz |
| E11 | [TI TPS56837](https://www.ti.com/product/TPS56837) | İncelenen28V8A alternatif; transient marjı nedeniyle ilk compute adayıLM61495 |
| E12 | [TI TCAN1042HV-Q1](https://www.ti.com/product/TCAN1042HV-Q1) | MCU CAN fiziksel katmanı;5V VCC/3.3V IO; exact ordering suffix teyidi gerekiyor |
| E13 | [Bosch BMI088](https://www.bosch-sensortec.com/en/products/motion-sensors/imus/bmi088), [datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmi088-ds001.pdf) | SPI IMU, titreşimli robot ortamına uygun aday; stok satın alma koşulu |
| E14 | [Molex Mini-Fit Jr5557 series](https://www.molex.com/en-us/products/series-chart/5557) | Konnektör aile adayı; tek housing ile elektrik/akım derecesi belirlenmez |
| E15 | [JST GH datasheet](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf) | Kilitli1.25mm signal connector,1A sınıfı; motor gücü için değil |
| E16 | [AMASS XT60H üretici çizimi, dağıtıcı arşivi](https://www.marutsu.co.jp/contents/shop/marutsu/datasheet/XT60H-M.pdf) | Üretici kaynaklı30A nominal/12AWG önerisi; kilit ayrıca tasarlanır |
| E17 | [Vishay darbe direnç seçimi](https://www.vishay.com/en/resistors/resistor-pulse-selector/), [darbe kapasitesi notu](https://www.vishay.com/docs/50060/pulsecapabilities.pdf) | Gerçek darbe süresi ve enerjiye göre seçim;100W etiketi tek başına yeterli değil |
| E18 | [TI TPS3431 veri sayfası](https://www.ti.com/lit/ds/symlink/tps3431.pdf), [TPS3431](https://www.ti.com/product/TPS3431) | 100 pF CWD formülü ve tolerans; WDO/ENOUT/PGOOD güç sırası; fiziksel zaman testi açık |
| E19 | [TI INA228](https://www.ti.com/product/INA228) | Paket şönt ölçümü,enerji/coulomb accumulator; BMS yerine geçmez |
| E20 | [Raspberry Pi yapılandırma belgesi](https://www.raspberrypi.com/documentation/configuration/computers/raspberry-pi.html) | PSU_MAX_CURRENT ve USB current limit; CM5 image/bootloader'da doğrulanacak |
| E21 | [CM5 IO resmî KiCad design files](https://pip.raspberrypi.com/categories/1098-design-files) | Prototip J8 pinout ve gelecekte carrier için referans; üretim dosyaları bu revizyonda kopyalanmamıştır |
| E22 | [Molex Mega-Fit PS-76823-100](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/768/76823/PS-76823-100-001.pdf), [76825 dik açılı header](https://www.molex.com/en-us/products/series-chart/76825), [170001 housing](https://www.molex.com/en-us/products/series-chart/170001), [76823 terminal](https://www.molex.com/en-us/products/series-chart/76823) | J-PWR 4 pin aday; tam yüklü/çıplak bakır AWG12 18 A, AWG14 15 A referansı; tek GND ve ortam derating'i gerekir |
| E23 | [Molex Micro-Fit PS-43045](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/430/43045/PS-43045-001.pdf) | İlk ayrı J-CTRL taslağında incelendi, paralel düşük akım GND yolu yüzünden kullanılmıyor |
| E24 | [JST GH ürün sayfası](https://www.jst-mfg.com/product/index.php?lang=2&series=105), [GH veri sayfası](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf) | J-SIG 12 pin düşük akım arayüzü; 1 A/50 V aile sınıfı, motor gücü yok |
| E25 | [Molex 768250004 parça sayfası](https://www.molex.com/en-us/products/part-detail/768250004), KiCad 10 `Connector_Molex:Molex_Mega-Fit_76825-0004_2x02_P5.70mm_Horizontal` | Dik açılı MPN ve aday PCB pad/clearance geometrisi; dişi housing kablo tarafı cavity yönü ve takma zarfı ayrıca doğrulanacak |
| E26 | [NXP PCA9615 veri sayfası](https://www.nxp.com/docs/en/data-sheet/PCA9615.pdf) | Kabloda iki diferansiyel I²C çifti, kart içi tek uçlu I²C; ayrı 3,3 V besleme ve sonlandırma hesabı açık |
| E27 | [TI LM74900-Q1 veri sayfası](https://www.ti.com/lit/ds/symlink/lm74900-q1.pdf), [LM74900QRGERQ1](https://www.ti.com/product/LM74900-Q1/part-details/LM74900QRGERQ1) | K2 common-drain NFET kontrolcüsü; EN shutdown, SLEEP iç bypass, OCP latch/TMR, RTN pad floating; stok ve tam şema açık |
| E28 | [TI CSD18540Q5B veri sayfası](https://www.ti.com/lit/ds/symlink/csd18540q5b.pdf), [CSD18540Q5BT](https://www.ti.com/product/CSD18540Q5B/part-details/CSD18540Q5BT) | K2 Q1/Q2 60 V, 2,2 mΩ maksimum @10 V/25 °C, FET başına bakır alanına bağlı 50–125 °C/W örnekleri; sıcaklık ve stok açık |

Web PDF görüntüleyicisi CM5IO PDF'sini bazı erişimlerde açamadı; üretici PDF'sinin arama metninde §2.2 haricî5V J8 ifadesi okundu. Carrier pinleri üretim aşamasında dosyanın yerel kopyası/revizyonu üzerinden yeniden doğrulanır. Bu kaynak listesi parça onay listesi değildir.
