# UGV-01 System Requirements Specification

Rev A0 · 22 Eylül 2026 · PHASE 0 ön gereksinim tabanı

## Amaç ve kapsam

UGV-01; eğitim, çevre inceleme, uzaktan görüntüleme, robotik Ar-Ge, SLAM ve otonom navigasyon araştırması için dört bağımsız tahrikli, skid-steer kara platformudur. Hazır robot kiti kullanılmaz. Özgün şasi, gövde, bağlantılar, kartlar, kablo demeti ve yazılım geliştirilir; MCU, işlemci modülü, motor, hücre ve sensör gibi bileşenler satın alınır. Bu revizyon gereksinim, ön hesap ve mekanik mimari teslimidir; tamamlanmış araç veya üretim onayı değildir.

Kullanıcı isteği ile mühendislik varsayımı ayrımı: 330 × 270 mm, CM5, STM32G4, dört motor, kilitli konnektörler ve 256 mm baskı hacmi kullanıcı girdileridir. 6 kg boş / 8 kg yüklü kütle, 2 kg yük, 15° eğim, 0–40 °C ortam, 60 dakika görev ve 0,8 m/s V1 sınırı bu revizyondaki tasarım varsayımlarıdır. Önemli değişiklikler hesapları yeniden açar.

## Kullanım zarfı

İlk doğrulama kuru, düz, kapalı test alanında yapılır. V1 kuru sert zemin ve sıkışmış toprak içindir; gevşek kum, çamur, merdiven, su geçişi ve yağmur altında kullanım kalifiye değildir. Toz/sıçrama önlemleri tasarlanır fakat IP derecesi beyan edilmez. Araç gözetimli çalışır; insan taşımaz. Sensör kulesinin yüksekliği ana gövde sınırına dahil değildir.

## Doğrulanabilir gereksinimler

Yöntemler: A=analiz, I=muayene/ölçüm, T=deney, D=işlev gösterimi. T01–T20 test_plan.md içindedir. «Hedef» test sonucu demek değildir.

| Kimlik | Gereksinim / kabul hedefi | Yöntem / aşama |
|---|---|---|
| SYS-001 | Dört adet ayrı encoder'lı redüktörlü DC motor; sol/sağ skid-steer | I,T08,T09 |
| SYS-002 | CM5 yüksek seviye; STM32G4 gerçek zamanlı kontrol; Linux durması tork güvenliğini engellemez | A,T13,T14 |
| SYS-003 | Tam dış zarf 330×270 mm; nominal kapak üstü zeminden146 mm (140 mm hedeften6 mm sapma, DD21) | I,PH2/4 |
| SYS-004 | Boş kütle≤6 kg, görev kütlesi≤8 kg, faydalı yük≤2 kg | I,T11 |
| SYS-005 | Yüklü CG z≤110 mm, mutlak x≤15 mm, mutlak y≤10 mm; x=0 dingiller ortası | A,I,T11 |
| MOT-001 | İlk sürüm limit0,8 m/s; önce0,2 m/s devreye alma. 1–1,5 m/s isteği motor/termal hesap nedeniyle ertelenmiştir | A,T16 |
| MOT-002 | Sert zeminde0,03 m/s kontrollü hız; 10 s ortalamada±%20,0,1–0,8m/s bölgede±%10 veya±0,02m/s büyük olan | T08,T16 |
| MOT-003 | 8 kg ile15° kuru sert rampada5 dakika; motor akımı/ısısı sınır içinde. Engebeli15° başlangıç kabulü değildir | A,T11,T12,T16 |
| MOT-004 | İvme≤0,5m/s²; yazılım hedef fren ivmesi0,8m/s²; fiziksel E-stop için durma mesafesi deneyle belirlenir | T10,T13 |
| MOT-005 | Sıfır yarıçaplı dönüş düşük hız ve akım limitiyle; yüksek tutunmada sürekli pivot zorunlu değil | A,T09,T16 |
| MEC-001 | Tek baskı parçası bütün yönlerde≤256mm; tasarımda brim için≤240mm tercih | A,I,PH2/10 |
| MEC-002 | Her parça PN/revizyon; M3/M4 esas; motor üreticisi M3 ve mil sabitlemeleri istisna | I,PH4 |
| MEC-003 | Batarya üst/arka kapaktan, kartlar ayrı servis kapaklarından; drivetrain gövdeyi tümden sökmeden değişir | D,PH10/11 |
| MEC-004 | Şasi yük yolu metal; motor ısısı plastik insert üzerinden ana yapıya taşınmaz | A,T11,T12 |
| MEC-005 | Teker nominal120×30mm; iz240mm, dingil arası210mm; minimum statik alt açıklık36mm | I,PH4 |
| MEC-006 | V1'de 50×50mm/40×40mm dört M4 kule arayüzü; çift göz/pan±90°/tilt toplam90° modülü sonraki revizyon | I,D; pan/tilt için gelecek T18 |
| ELE-001 | UGV-PWR-01 ayrı kart; motor/servo enerjisi mantık beslemesinden bağımsız kesilir | A,T01,T13 |
| ELE-002 | Tam hücre aralığında5,1V COMPUTE; kart girişinde4,9–5,2V hedef, açılış/yük adımında reset yok | T02,T17 |
| ELE-003 | 12V yardımcı buck-boost,5V logic,6V servo ayrı; kapasite güç bütçesiyle doğrulanır | A,T02,T12 |
| ELE-004 | Ters polarite, kısa devre sigortası, TVS/EMI, rejenerasyon enerji yolu ve test noktaları | A,T01,T05 |
| ELE-005 | Her motorda akım ölçümü ve donanım akım limiti; anlık kilitlenme MCU kilitlense de sınırlanır | T05,T11 |
| ELE-006 | 4S2P korumalı paket; hücre grubu voltajları/sıcaklığı izlenir; uygun4S CC/CV şarj cihazı | A,T15 |
| COM-001 | CM5–MCU CAN2.0B,500kbit/s,iki uç120Ω; PC tarafında SocketCAN | A,T04 |
| COM-002 | Kamera CAN'den geçmez; görüntü USB/CSI→CM5→ağ, motor komutları ayrı öncelikli kanal | A,T10,T18 |
| SAF-001 | Fiziksel NC E-stop, kablo kopması güvenli duruş; servo dahil hareket enerjisi donanımla kesilir | T13 |
| SAF-002 | Geçerli motor komutu100ms gelmezse sürüş izni düşer; stop sonrası kendiliğinden arm yok | T14 |
| SAF-003 | BOOT/SELF_TEST/IDLE/ARMING/FAULT/E_STOP halinde PWM ve aktüatör izni kapalı; reset/bootloader/crash ve ön şarj testi de kapsanır | T01,T03,T13,T14 |
| SAF-004 | Düşük hücre, aşırı akım/sıcaklık, encoder/IMU arızası, CAN bus-off ve watchdog kayıtlanır | T06,T07,T11–15 |
| SAF-005 | Ağdaki STOP fiziksel güvenlik fonksiyonunun yerine geçmez; tek etkin kontrol sahibi + deadman | T10,T14 |
| SW-001 | STM32 C/C++; timer encoder, sabit süreli PID, watchdog ve state machine | A,T03–09 |
| SW-002 | Ubuntu24.04 arm64 + ROS2 Jazzy aday taban; CM5 boot/kamera/SocketCAN sürücü uyumu sahada doğrulanır | T17,T18 |
| SW-003 | Geometri tek JSON kaynağı; CAD/URDF mm→m dönüşümünü aynı üretici yapar | A,otomatik kontrol,PH2/9 |
| UI-001 | MacBook Safari/Chrome web paneli: kamera,batarya V/%/A,4 hız,araç hızı,IMU,sıcaklıklar,link,fault,E-stop,joystick | T10,T18 |
| UI-002 | Gamepad tak/çıkar,sekme gizlenmesi,focus kaybı/deadman bırakma duruş üretir | T10,T14 |
| LOG-001 | Zaman damgalı telemetri CSV/rosbag2; birim,revizyon,kalibrasyon,brownout/fault nedenleri kaydedilir | T10,T17 |
| ENV-001 | İlk zarf0–40°C kuru ortam; termal test hem25°C hem40°C eşdeğerinde | T12 |
| END-001 | Tanımlı görev profilinde≥60dk; batarya rezervi ve yaşlanma dahil güç hesabıyla sınanır | A,T15 |
| MFG-001 | PH4/7 sonunda STEP/STL/DXF/çizim ve KiCad/Gerber/BOM/PnP/drill ayrı kontrol edilmiş release | I,PH4/7 |
| MOD-001 | V2 algılama,V3 LiDAR+SLAM,V4 Nav2,V5 görev planlama; AI güvenlik MCU'sunu atlayamaz | A,PH14–16 |

## Tamamlanma ölçütü

Her fazın çıkışı teknik tutarlılık, üretim, montaj, test ve servis açısından kayda alınır. Analiz sonucu «geçti» fiziksel testin yerine yazılmaz. PH2 modelinde kart/hücre hacimleri ayırılmış olması şematik veya üretim toleransı onayı değildir. Gereksinim değişikliği design_decisions.md ve config/vehicle.json ile birlikte revize edilir.
