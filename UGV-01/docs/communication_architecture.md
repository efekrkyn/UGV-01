# İletişim arayüzü — A0

**A3 Lite (güncel, DD70/DD71):** araç içinde CAN yok. MacBook ile ESP32-S3 arasında aynı çerçeve anlamları (0x080/0x100/0x110/0x120/0x121, M3'te 0x122 kol yolu ve 0x190 durum) 21 baytlık, HMAC-SHA256 imzalı UDP datagramlarıyla taşınır; Lite telemetrisi 0x1A0 (batarya/ToF), 0x1A1 (odometri) ve 0x1A2 (kol yolu durumu) eklenir. DD80: telemetri etiketleri son kabul edilen lease'e bağlıdır (tekrar/gecikme koruması); 0x123 kol park onayıdır. DD84: 0x1A0 bayraklarının bit3'ü "kol sürüşü engelliyor" (kol bir sürüş duruşunda oturmuş değil ya da gevşek). Ayrıntı: [Lite yazılım](lite_software_A3.md). Aşağısı A0–A2 CAN kaydıdır.

## CAN kararı ve alternatifler

| Yol | Güçlü taraf | UGV bağlamında sınır | Karar |
|---|---|---|---|
| CAN500kbit/s | Diferansiyel,CRC,arbitraj,hata sayaçları,çok düğüm |8byte klasik frame; Linux gerçek zamanlı garanti değil | Motor komut/telemetri ana yolu |
| TTL UART | Basit,düşük maliyet |Tek uçlu,gürültü/toprak farkı; özel framing+CRC gerekir | Kısa kart içi debug |
| RS-485 | Diferansiyel,uzun hat |Arbitraj/protokol/fault recovery bize ait | CAN'e belirgin üstünlük yok |
| USB | Yüksek hız,CM5 hazır host |Host reset/re-enumeration ve konektör; kilitli sabitleme gerek | V1 CAN adaptörü,kamera,servis |
| SPI | Kart içinde hızlı |Kablo mesafesi/EMI/çok çevre birimi yönetimi | Carrier üzeri CAN denetleyicisi |
| Ethernet | Kamera/ağ için yüksek bant |Motor MCU tarafında fazladan yığın/donanım | CM5–MacBook ve payload |

CAN elektromanyetik bağışıklığı mutlak sağlamaz; dönüş yolu,terminasyon,kablo ve transceiver common-mode sınırı tasarlanır. A0 klasik11bit ID,500kbit/s;FD kabiliyeti rezerv,prototip FD'ye bağımlı değil. İki uç120Ω;enerjisiz toplam≈60Ω;stub<100mm hedef,toplam dahili omurga<1m. CAN_H/CAN_L bükümlü çift ve sinyal GND;ekran ayrı şasi bağlantısı. Ayrı güç alanı/toprak farkı varsa izole USB–CAN tercih edilir; adaptör bağlantı şeması çift terminasyonu önleyecek şekilde kaydedilir.

**MCU transceiver ön seçimi:** [Microchip MCP2562-E/SN](https://www.microchip.com/en-us/product/MCP2562), SOIC-8. [Üretici veri sayfasında](https://ww1.microchip.com/downloads/en/DeviceDoc/20005167C.pdf) VDD 4,5–5,5 V, VIO 1,8–5,5 V, en çok 1 Mbit/s ve 8 pin işlevi verilir: 1 TXD, 2 VSS, 3 VDD, 4 RXD, 5 VIO, 6 CANL, 7 CANH, 8 STBY. Böylece `5V_CONTROL` transceiver hattı ve `MCU_3V3` GPIO düzeyi ayrı beslenir; STM32'nin 3,3 V TXD/RXD'sine ek seviye kaydırıcı gerekmez. STBY High standby, Low normal moddur; veri sayfasındaki iç pull-up ile reset/Hi-Z'de standby hedeflenir. MCU ancak raylar/oturum sağlıklıysa STBY'yi Low sürer. CAN hattı MCU-E-stop'tan bağımsız `5V_CONTROL` rayındadır; iletişimin sürmesi aktüatör izni vermez. Bu seçim **şematik ve EMC onayı değildir**: VIO/VDD güç sırası, TXD reset seviyesi, ayarlanabilir iki uç terminasyonu, CAN TVS/CMC MPN ve tek-GND fault deneyi PH5/7'de kapanır. PEAK USB–CAN üzerindeki terminasyon var/yok ayarı montajda açıkça etiketlenir; uçta yalnız bir adet 120 Ω vardır.

## İlk protokol sözleşmesi

Aşağıdaki tablo PH8 DBC/C kodu için bağlayıcı taslak; gerçek encoder/akım akışı ölçüldükten sonra sürüm alanı artırılarak değişir. Little endian,iki tümleyen signed integer; fiziksel değerler SI. Bus CRC uygulama oturum kimliğinin yerini tutmaz.

| CAN ID | Kaynak→hedef | Hz | DLC | İçerik |
|---|---|---:|---:|---|
|0x080|CM5→MCU|olay|8|opcode=1 STOP,sebep,session32,seq16; geçerli STOP en yüksek öncelikle latch'lenir |
|0x100|CM5→MCU|50|8|left_mm_s int16,right_mm_s int16,seq16,session_tag16 |
|0x110|CM5→MCU|50|8|session32,lease_seq16,version4+mode4,deadman8 |
|0x120|CM5→MCU|≤20|8|A2 baş: pan_cdeg int16, tilt_cdeg int16, seq16, session_tag16 |
|0x121|CM5→MCU|10|8|A2 kol: shoulder_cdeg int16, gripper8 (0 açık/1 kapalı), flags8 (bit0 AI modu, diğerleri 0), seq16, session_tag16 |
|0x122|MacBook→ESP32|25|8|M3 kol yolu (DD76): from_pose8, to_pose8, target_frac16 (65535 = to_pose'ta), seq16, session_tag16; çekirdek yalnız duruş grafiğinin kenarlarını kabul eder. Lite'ta 0x121'in shoulder alanı yok sayılır |
|0x123|MacBook→ESP32|olayda|8|DD80 kol elle park edildi: 1,0,0,0, seq16, session_tag16; yalnız aktüatörler kapalıyken (ARMED/DRIVING değil), oturum başına ileri sırayla |
|0x1A2|ESP32→MacBook|20|8|M3 kol durumu: from8, to8, frac16, target16, flags8 (bit0 yerleşti, bit1 gevşek: park onayı bekliyor), echo8 (N3: çekirdeğin aldığı son 0x122 sırasının düşük baytı) |
|0x180|MCU→CM5|50|8|4 teker mm/s int16 |
|0x181|MCU→CM5|50|8|4 delta encoder int16; her20ms örneklemi,ortak sıralama ayrı heartbeat |
|0x182|MCU→CM5|50|8|ax,ay,az int16 milli-g,örnek sıra16 |
|0x183|MCU→CM5|50|8|gx,gy,gz int16 milli-rad/s,aynı örnek sıra16 |
|0x184|MCU→CM5|20|8|4 akım int16 mA |
|0x185|MCU→CM5|10|8|paket mV uint16,net mA int16,kart°C×100 int16,motor max°C×100 int16 |
|0x186|MCU→CM5|10|8|4 hücre grubu mV uint16; BMS verisi yoksa ilgili alan `0xFFFF` |
|0x190|MCU→CM5|20|8|state8,fault8,seq16,MCU monotonic_ms32 |
|0x191|MCU→CM5|olay≤10|8|fault_bits32,event_counter16,details16 |

V1 `0x110` baytları sırasıyla `session32` little-endian [0..3], `lease_seq16` [4..5], `version_mode` [6] ve `deadman` [7]'dir. `version_mode` üst nibble'ı **1**; alt nibble `0=IDLE`, `1=ARM isteği`, `2=DRIVE` olur. Deadman yalnız0/1 kabul edilir. 16 bit lease sıra farkı modüler olarak `1..32767` ise ileridir; tekrar/geri sıra tazelik sayacını yenilemez. Yeni session yalnız güvenlik çekirdeği IDLE'da ve yerel reset koşulları sağlanırken `IDLE,deadman=0` lease ile başlar. `0x100` baytları iki signed `mm/s`, `cmd_seq16` ve session32'nin düşük16 bitidir; bu kısa tag kimlik doğrulaması değildir. ARM modunda hızlar sıfır, V1 hız sınırı ilk parametre olarak ±800 mm/s; geçersiz çerçeve zamanı yenilemez. `0x080` doğru DLC/opcode ile gelirse oturumdan bağımsız **STOP isteği** latch'lenir; doğrulanmamış ağ düğümlerinin CAN hattına erişimi ayrıca engellenir.

İzin almak yalnız0x110 göndermek değildir: yeni boot/session,protokol eşleşmesi,yerel reset,E-stop sağlıklı,nötr hız,en az500ms taze trafik ve ayrı ARM isteği gerekir. Ayrıntı safety_architecture.md. Komut yönü tekerin ileri yüzey hızına göredir; motor montaj polaritesi/encoder işareti dört ayrı kalibrasyonda tutulur. [Host C11 komut çözücüsü](../firmware/stm32/can_protocol.c) framing, sıra ve kaynak yaşını denetler; STM32 FDCAN sürücüsü/ISR, gerçek CAN transceiver ve güvenlik çekirdeğine bağlanması henüz yapılmadı.

0x100 ve 0x110 son GEÇERLİ frame alınışının MCU monotonic zamanı100ms aşılırsa komut taze sayılmaz. Geçersiz aralık,tekrarlanan/geriye giden seq,eski oturum veya timeout paketleri timer'ı yenilemez. 16bit sıra sarımı modular fark ile sınanır; reconnect'te yeni oturum gerekir. CAN kaybında kontrollü frenin uygulanabilirliği garantilenmez; izin kapanışı donanım davranışına tabidir. Session_tag16 güvenlik kimlik doğrulaması değildir; ağdan CAN gateway'e yalnız yetkili yerel süreç erişir.

## Bant ve zaman bütçesi

360 periyodik frame/s; konservatif160bit/frame (stuff/interframe paylı)→57,6kbit/s=%11,52 bus yükü. 10fault/s dahil%11,84; yeniden iletim/debug/genişleme için%30 sürekli sınır. Bir160bit frame320µs; bit hızı Linux/USB scheduling gecikmesini kapsamaz. T04'te1 saat motor PWM altında kayıp,hata sayaçları ve99,9 yüzdelik gecikme ölçülür. IMU timestamp eşlemesi,tam encoder toplam sayacı ve frame kayıp algısı PH8 protokol testinde tamamlanır; delta frame kaybı odometri güvenini düşürür, sessizce sıfır sayılmaz.

## Kablolar

J_CAN:1 CAN_H,2 CAN_L,3 GND,4 ayrılmış/bağlanmaz; güç aynı CAN konektöründe V1'de taşınmaz. Farklı gerilimli motor/encoder/CAN fişleri mekanik olarak anahtarlanır; renk tek savunma değildir. Encoder beslemesi üreticiye göre5V,MCU girişi3,3V ise seviyelendirme şart. Konnektör pin numaraları bu mantıksal sözleşmedir; footprint eşlemesi PH5'te çizimle doğrulanır.

**A2 servo/AI çerçeveleri (24.09.2026):** `0x120`/`0x121` yalnız taze (≤100 ms) ARM/DRIVE lease'i, deadman, oturumun düşük 16 biti ve ileri sıra ile kabul edilir; yeni oturum sıra geçmişini sıfırlar. Açı aralığı servo modülünde ayrıca sınanır. `0x121` AI bayrağı taşır ve **en az 10 Hz** gönderilir: AI modunda ya da `0x121` 300 ms bayatsa MCU tekerlek hız tavanını 200 mm/s yapar (`ugv_can_speed_cap_mm_s`); manuel sürüşte tam hız için gateway bu çerçeveyi sürekli yollar. Kaynak: [can_protocol.c](../firmware/stm32/can_protocol.c), [AI kontrolü](ai_control.md).
