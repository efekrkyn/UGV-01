# Tekrar üretilebilir ön hesap raporu — A3

Kaynak: config/vehicle.json; güç profilleri docs/electrical_architecture.md §6. Üretim/deney onayı değildir.

| Metrik (birim isimde) | Değer |
|---|---:|
| battery_wh | 32.400000 |
| battery_min_wh | 30.780000 |
| aged_usable_min_wh | 20.930400 |
| runtime_typical_h | 1.308150 |
| runtime_heavy_h | 0.455009 |
| curb_mass_kg | 4.580000 |
| curb_cg_x_mm | 10.205240 |
| curb_cg_z_mm | 118.135371 |
| loaded_cg_z_mm | 131.114173 |
| flat_rolling_force_n | 1.500417 |
| grade_force_n | 5.853708 |
| grade_motor_torque_nm | 0.138640 |
| grade_motor_current_a | 0.391812 |
| accel_grade_motor_torque_nm | 0.199035 |
| accel_grade_motor_current_a | 0.532000 |
| pivot_scrub_moment_nm | 3.150877 |
| pivot_motor_torque_nm | 0.357919 |
| pivot_rolling_torque_nm | 0.023691 |
| pivot_motor_current_a | 0.955790 |
| stall_current_full_pack_a | 0.889412 |
| stall_current_empty_pack_a | 0.645740 |
| pivot_friction_limit_empty_pack | 0.376083 |
| pivot_turn_wheel_rpm | 9.955142 |
| pivot_friction_limit_turning_empty | 0.303647 |
| pivot_friction_limit_turning_nominal | 0.361941 |
| pivot_friction_limit_turning_full | 0.449382 |
| tb6612_allowance_w | 0.592800 |
| pivot_current_cap_a | 0.824832 |
| tb6612_limited_stall_w | 1.134000 |
| tb6612_ceiling_motor_w | 0.504000 |
| tb6612_fault_full_duty_stall_w | 1.221346 |
| no_load_speed_m_s | 0.483805 |
| flat_speed_empty_pack_m_s | 0.307609 |
| grade_speed_empty_pack_m_s | 0.158358 |
| encoder_counts_output_rev | 1716.000000 |
| minimum_speed_counts_per_ms | 0.136555 |
| kinetic_energy_j | 0.229500 |
| static_pitch_tip_deg | 33.690068 |
| plate_gross_mass_kg | 0.441960 |

Model: F=mg(sinθ+Crr cosθ); T=Fr·k/(4η); I=I0+(Is−I0)T/Tstall.
η yalnız dış kaplin/yatak kaybıdır; üretici gearbox çıkış torkuna ikinci dişli verimi uygulanmaz.
Akım/hız doğrusal taramadır; PWM RMS, sıcak sargı ve lastik kaymasını çözmez.
Çalışma süreleri minimum kapasite ×0,80 kullanım ×0,85 yaşlanma / ölçülmemiş görev gücü ile hesaplanır.
16.0 W tipik profilde 60 dakika hedefi ön hesapla desteklenir; 46.0 W ağır profilde desteklenmez.
Statik devrilme açısı dinamik saha eğimi veya fren garantisi değildir.

## Yük paylaşımı ve zemin duyarlılığı

| Zemin / katsayı | En yüklü motor torku N·m | Tarama akımı A | 0.6 A tavan |
|---|---:|---:|---|
| Sert 5° / 1.5 | 0.139 | 0.392 | KOŞULLU |
| Sert 5° / 1.6 | 0.148 | 0.413 | KOŞULLU |
| Pürüzlü 5° / 1.5 | 0.198 | 0.529 | KOŞULLU |
| Pürüzlü 5° / 1.6 | 0.211 | 0.559 | KOŞULLU |

## Balast, ivme ve yerinde dönüş (R4/R7, yeniden kontrol F2)

Her motorun önünde 7.5 Ω seri direnç var: tam dolu pakette sıkışma akımı 0.889 A ≤ TB6612 önerilen 1 A. Bu akım sınırı tek başına süresiz ısıl uygunluk kanıtı değildir (iki kanal aynı çipte; bkz. Lite çekirdeği ısı bütçesi). 5° rampada 0,5 m/s² ivme 0.532 A ister.
Yerinde dönüş kaba, muhafazakâr kayma modeliyle: M=µmgL/2, motor başına T=Mr/(2Bη), artı teker başına yuvarlanma mgCrr·r/(4η); gerilim yolu sargı + balast + TB6612 köprüsü (en çok 0,7 Ω, 1 A'de 0,7 V). N2: çekirdeğin PI hız döngüsü paket gerilimine kadar çıkabilir; akım geri-EMK sınırlayıcıyla 0.825 A ile kırpılır (sabit gerilim tavanı yok). Kopma (0 hız) ile 0.45 rad/s dönüş (10.0 dev/dk teker, geri EMK payı) ayrıdır. Satırlar model duyarlılığıdır; ölçüm değildir.

| Zemin µ | Motor torku N·m | Akım A | Kopma, boş 9,6 V | Dönüş, boş 9,6 V | Dönüş, nominal 10,8 V | Dönüş, dolu 12,6 V |
|---:|---:|---:|---|---|---|---|
| 0.3 | 0.203 | 0.540 | döner | döner | döner | döner |
| 0.4 | 0.262 | 0.679 | durur | durur | durur | döner |
| 0.45 | 0.292 | 0.748 | durur | durur | durur | durur |
| 0.6 | 0.382 | 0.956 | durur | durur | durur | durur |

Sınır µ: kopma boş pakette 0.376; 0.45 rad/s dönüşte boş 0.304, nominal 0.362, dolu 0.449. Üstünde teker sınırlı akımda durur, Lite çekirdeğinin stall/ısı korumaları keser ve yürütücü hata döndürür. Pivot akımı, ısınma ve gerçek µ fiziksel testte ölçülür (NOT_RUN).

## TB6612 ısıl sınır (yeniden kontrol F1)

İki kanal aynı çipte: kayıp 2·I²·0.7 Ω. Çip tek başına 0.78 W (25 °C, Tj 150 °C), gövde içi 55 °C varsayımıyla 0.593 W. Akımlar muhafazakâr yoldan (sargı −%10, balast −%5, köprü tipik).

| Durum | Çip kaybı W | Süre |
|---|---:|---|
| İki motor 0,6 A sürekli tavanda | 0.504 | sınırda: 0,5 W payının hemen üstü, bütçe ≈8 dakikada dolar |
| Hız döngüsü: iki teker akım sınırlayıcıda duruk ya da çok yavaş (tahmin 0.9 A) | 1.134 | 300 ms stall kesmesi; dönüyorsa ısı bütçesi 2 J → ≈3 s |
| Firmware arızası: tam görev, iki kanal sıkışık, dolu paket | 1.221 | 0.89 W kart değerini aşar: 300 ms stall kesmesi + çip ısıl kapanması + watchdog |

Kanal akımının 1 A altında olması süresiz ısıl uygunluk kanıtı değildir. Isı bütçesi sabitleri `firmware/lite/lite_core.h`'dedir ve `tests/check_design.py` bu tabloyla karşılaştırır. Gerçek ısınma TL1'de ölçülür (NOT_RUN).
