# UGV-COMPUTE-01

İlk prototip resmîCM5IO üzerinde çalışır. Kendi carrier'ımız V1 sürüş/telemetri kabulünden sonra geliştirilir; aşağıdaki liste gelecekteki tasarım girdisidir.

## Prototip

CM5 8GB eMMC + aktif soğutucu,160×90mm IO kartı. Bunun üstüne konnektör kablo bükümü,USB-C/USB/Ethernet çıkışları ve hava akışı servis hacmi eklenir. Kart yalnız outline ile yerleşime sığmış sayılmaz. Anten metal motor/batarya muhafazasından uzak konur.

İlk bench bring-up resmî27W PSU. Mobil güç: UGV-PWR ayrı5.1V6A rail → sigortalı,kilitli harness → **resmî belgede izin verilenJ8haricî5V** servis adaptörü. GPIO header üzerindeki5V/GND kontakları arasında akım paylaşımı ve terminal derating ölçülür; gevşek Dupont jumper kullanma. Adaptör vida/mandalla sabitlenir. Haricî güç+USB-C eşzamanlı güç uygulaması yasaklanır veya gerçek power-mux/reverse-blocking devresi tasarlanır. Servis USB veri bağlantısının VBUS backfeed ihtimali de test edilir.

CM5IO USB-C'nin normal5A PD müzakeresini batarya kablosuyla kendiliğinden yaptığı varsayılmaz. J8 beslemesinde imaj/bootloader'ın `PSU_MAX_CURRENT`/USB güç limiti seçilen sürümde doğrulanır; kapasite ölçülmeden uyarı bastırılmaz. Yük adımlarında board ucunda5Vrail ve undervoltage flags kaydedilir. [ResmîCM5IO§2.2](https://datasheets.raspberrypi.com/cm5/cm5io-datasheet.pdf), [güç ayarları](https://www.raspberrypi.com/documentation/configuration/computers/raspberry-pi.html).

CAN: LinuxSocketCAN destekliUSBPEAKPCAN-USBFD(IPEH-004022) ve strain relief. USB adapter/kernel revizyonu teste dahildir. A2: iki Camera Module 3 göz kamerası CM5 IO'nun iki MIPI bağlantısına, iki VL53L1X ToF 40 pin I²C'ye (`XSHUT` ile adres ataması) bağlanır; [A2 elektronik](../../docs/a2_electronics.md). Video CAN'de taşınmaz. Ubuntu/ROS2/CSI kernel desteği bring-up aşamasında birlikte doğrulanır.

## Carrier'a geçiş girdileri

CM5 modül konnektörleri,5Vpowersequencing,inrush/soft-start;EthernetRJ45magnetics;USB3port veESD;USB-Cservis/data;MIPI22pinCSI;MCP2518FD SPI-CAN+transceiver+IRQ;debugUART;I²C/SPI/GPIOgenişleme;fan/RTC;tekPCIelaneM.2M-key gereksinimi. USB-C'ye veri ve güç rolleri açıkça atanır;“servis” etiketi rol tanımı değildir.

Ön hedef6katman,kontrollü empedans,üretici CM5 tasarım kuralları,highspeedreturn-path ve ESD yerleşimi. M.2/USB3/CSI bağlantılarını yalnız silkscreen olarak eklemek yeterli değildir; lanes,pinmap,power bütçesi ve SI incelemesi tamamlanır. Kullanılmayan genişleme portları DNP olabilir. Sistem CAN protokolü ve5Vpowerarayüzü korunacağı için yazılım carrier'a bağımlı olmaz.

Bu revizyonda custom carrier şematiği,PCB,Gerber veya üretilebilirlik iddiası yoktur. [ResmîKiCadreferansı](https://pip.raspberrypi.com/categories/1098-design-files) sonraki aşamada revizyonu sabitlenerek incelenir.
