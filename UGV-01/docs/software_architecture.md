# Firmware, ROS 2 ve kontrol arayüzü

A0 mimari sözleşme; [host üzerinde derlenebilen güvenlik durum makinesi çekirdeği](../firmware/stm32/safety_core.c), [CAN komut çözücüsü](../firmware/stm32/can_protocol.c) ve bunların senaryo testleri var. STM32 karta yüklenebilir firmware, ROS paketi veya web uygulaması henüz teslim edilmiş değildir. PH8/9/12 uygulama işleri aşağıdaki sınırları korur.

## STM32

C/C++, timer tabanlı 20 kHz PWM ve 1 kHz hız/safety çevrimi. Encoder timerları kesme başına yazılım sayacı değildir; overflow modulo fark hesabıyla çözülür. 0,03 m/s'de yalnız 1 ms sayım yaklaşık0,36 count olduğundan düşük hızda periyot ve20 ms pencere hibriti gerekir. PID; dört ayrı kazanç, anti-windup, ivme limiti, encoder işaret kontrolü, arıza/reset sırasında integral sıfırlama içerir. Kazanç ve teker etkin yarıçapı kalibrasyon parametresidir.

| Modül | Sorumluluk / bağımlılık |
|---|---|
| motor_control | DRV8874 PWM modunda motor başına IN1/IN2; `00` coast, yön değişiminde iki giriş nötr geçişi, Vbus bazlı duty sınırı |
| encoder | Timer capture/overflow, counts→rad/s, kaynak yaş bilgisi |
| pid | Sabit dt, doygunluk ve anti-windup |
| imu | SPI örnekleri, data-ready zamanı, eksen/bias kalibrasyonu |
| battery | BMS hücre telemetrisi, UV/OV, INA228 kapasite hesabı |
| current_monitor | PWM senkron ADC, RMS/I²t, IPROPI ölçüm kısıtları |
| temperature | Motor, kart, hücre ve MCU; açık/kısa sensör tespiti |
| can | Byte packing, seq/session, timeout, bus-off; queue depth1 komut |
| safety | State machine, öncelikli fault, arm ve izin kararı |
| watchdog | Yalnız sağlıklı ana çevrim sonrası harici WDI ve IWDG |
| diagnostics | Reset/fault ring buffer, kalibrasyon revizyonu, hata sayaçları |

Paket ölçümü PA8/PA9 yerel I²C2 üzerinden, kabloda iki PCA9615 arasında dört diferansiyel damar üzerinden gelir. `battery` okuması zaman aşımı, SDA takılması ve güç sırası arızasında en çok dokuz SCL darbesiyle sınırlı bus-recovery denemesi yapar; ölçüm tazeliği geri gelmezse FAULT ve haricî izin düşer. Kurtarma döngüsü kontrol/safety çevrimini bloklayamaz. TIM1/TIM8 eşzamanı ve preload/update davranışı CubeMX/logic analyzer ile kanıtlanır; yön değişimi önce her iki kanalı `00` yapıp bir tam PWM periyodu bekler. İki timerı eşzamanlı başlatmak tek başına atomik çıkış güncellemesi kanıtı değildir.

Durum/iyileşme sözleşmesinin tek kaynağı [safety_architecture.md](safety_architecture.md). `safety_core` bu sözleşmenin **yalnız üst seviye sıralama taslağıdır**: `ARMING` içinde BLEED→TEST→K1→PRECHARGE→K2; E-stop/WD/komut kaybında bütün istekler Low. Girişlerin gerçek ADC/encoder/CAN tazeliği ve fiziksel NC/PGOOD kaynakları henüz bağlı değildir; çıktıların hardware gate'i geçmeden aktüatör izni olamaz. Haberleşme alanları [communication_architecture.md](communication_architecture.md). Firmware internet/UI işini üstlenmez; CM5 durduğunda da motor sınırları sürer.

## CM5 ve ROS 2

Ubuntu24.04 arm64 ve ROS2 Jazzy aday tabandır; resmi ROS hedef platformu Noble arm64'tür. Gerçek CM5 imajında kamera ve USB–CAN sürücü testi ayrıca yapılır. [ROS Jazzy kurulum belgesi](https://docs.ros.org/en/jazzy/Installation/Alternatives/Ubuntu-Install-Binary.html), [REP2000](https://www.ros.org/reps/rep-2000.html).

| Paket | Girdi → çıktı / sorumluluk |
|---|---|
| ugv_description | Ortak JSON→Xacro/URDF; robot_state_publisher; CAD eşlemesi |
| ugv_driver | SocketCAN↔teker hedefleri/ölçümleri; command arbiter, joint_states, raw odom, diagnostics |
| ugv_bringup | Konfigürasyon/lifecycle başlatma; varsayılan disarmed; gerçek/sim ayrımı |
| ugv_camera | A2: iki CSI göz kamerası (CAM0/CAM1); image_raw,camera_info; stereo intrinsics/extrinsics, pan/tilt eklem dönüşümleri |
| ugv_telemetry | BatteryState,temperatures,motor currents,fault; CSV/rosbag2, veri yaşı |
| ugv_localization | Encoder+IMU EKF; odom→base_link'in tek sahibi; covariance |
| ugv_navigation | Nav2, map/costmap, goal/cancel; güvenlik arbiter'ından geçen cmd_vel |
| ugv_slam | LiDAR SLAM, map ve loop closure; map→odom'un tek sahibi |
| ugv_web_ui | Yerel HTTPS/WSS gateway; yetkili tek operatör, telemetri/video/joystick |

TF: map→odom→base_link→chassis/wheels/sensor_mast_mount/camera; A1 kamera ön yüzde, `sensor_mast_mount` yalnız düz genişleme flanşıdır. Kamera optical frame ROS optik yönlerine ayrı sabit dönüşümle bağlanır. Mevcut `simulation/ugv_geometry.urdf` yalnız geometri görselleştirmesi; inertial, contact/collision, ros2_control ve optik kalibrasyon içermediğinden dinamik simülasyon kabulü değildir. Xacro ve paket build dosyaları PH9'da hazırlanır.

Skid kinematiği ilk yaklaşım: vL=vx−ωb_eff/2, vR=vx+ωb_eff/2. b_eff gerçek240mm izden farklı olabilir; zeminde dönüş kaymasıyla kalibre edilir. Dört teker encoder'ı gözlenir; her yandaki hızlar güven kontrolü sonrası birleştirilir. Odometri kaymayı fiziksel hareket olarak varsayar, IMU/SLAM doğrulaması gerekir. `odom→base_link` sürücünün ve EKF'nin ikisi tarafından aynı anda yayımlanmaz.

Motor kontrol 50Hz komut; sensör telemetri alanına göre10–50Hz. Reliable komut kuyruğu eski komutları biriktirmez: depth1, deadline/lifespan + gateway timestamp. Safety zaman aşımı ROS zamanından değil MCU monotonic saatinden işler. DDS yalnız araç içi/izinli ağda; browser doğrudan ROS topic yazmaz.

## Web panel

MacBook tarayıcısı CM5 üzerindeki yerel sunucuya bağlanır. İlk tasarım iki sütun: solda zaman damgalı kamera ve sürüş joystick'i; sağda batarya yüzde/V/A, dört motor hedef/ölçülen hız, araç hızı, roll/pitch/yaw, IMU ivme/gyro, CPU/STM32 sıcaklığı, CAN/ağ durumu ve fault geçmişi. Alt sabit şerit fiziksel E-stop geri bildirimi, ayrı **Yazılımsal STOP**, arm ve deadman durumunu gösterir. Devreden kopmuş durumda son veri gri/yaşıyla gösterilir; başarılı stop ACK alınmadan «durdu» yazılmaz.

Gamepad API; ayrı basılı tutulan deadman düğmesi, dead-zone ve hız ölçeği. Sekme gizlenmesi, focus kaybı, gamepad çıkarma, session değişimi veya bağlantı kaybı izin düşürür. Klavye/joystick komutları aynı arbitrajdan geçer. Arm için nötr ve açık operatör eylemi şarttır. Kamera donması fiziksel görüş olmayan modda sürüşü keser. Hareketi başlatan kontrol yalnız renk veya hover ile verilmez; klavye odağı, okunur etiket ve dokunma hedefleri korunur.

V1 için720p20fps ve p95≤250ms video gecikme hedefi. UVC görüntü ağda ayrı kanal; sürüş komutu video kuyruğunda beklemez. WebRTC değerlendirilebilir; codec desteği ve gecikme ölçülmeden seçilmiş sayılmaz. Telemetri daha sonra analiz için SI birimli CSV ve rosbag2: monotonic+UTC eşlemesi,firmware/CAD revizyonu,kalibrasyon,session,seq,fault,raw kaynak yaşları. Disk dolması kayıt uyarısı üretir, MCU hız çevrimini durdurmaz.

V2 algılama/V3 SLAM/V4 Nav2/V5 doğal dil görevleri ayrı node ve kaynak bütçeleridir. Dil modeli yalnız doğrulanan görev şemasını üretir; ARM, watchdog veya akım limitlerini değiştiremez.

**A2 denetimli AI (24.09.2026):** V5 doğal dil görevleri, bulutta Claude (`claude-sonnet-5`) planlayıcısı ve araç üstünde internetsiz `skill_executor` olarak öne alındı. Model yalnız doğrulanmış araç çağrıları üretir; sınırlar, dur sözü, AI modu izni ve ToF refleksi yerelde, 200 mm/s tavan ve servo sınırları MCU'da. Ayrıntı: [ai_control.md](ai_control.md). Kod: `software/ugv_ai/`, [panel](../software/web_ui/panel.html), [servo](../firmware/stm32/servo_control.c) ve [ışık](../firmware/stm32/light_bar.c) modülleri.
