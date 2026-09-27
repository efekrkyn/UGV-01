# UGV-01 A3 Lite yazılım

25.09.2026 · L3 ([plan](superpowers/plans/2026-09-25-a3-lite-software.md), [DD70/DD71](design_decisions.md)); M3 kol (DD73/DD75); M3 inceleme düzeltmeleri N1/N2 (DD76). Masaüstünde test edilebilen katman tamam: robot çekirdeği (C), imzalı Wi-Fi bağlantısı ve MacBook ağ geçidi. 26.09.2026: L4a ([plan](superpowers/plans/2026-09-26-l4a-esp32-board-layer.md), DD86) ESP32-S3 kart katmanını, DD87 ön ToF sürücüsünü, DD88 göz firmware'ini yazdı ve ESP-IDF 5.3.2 ile derledi; **donanımda çalışmadı (L4b);** sürüş onayı değildir. Bütün sonuçlar model ve host testleridir.

## Akış

```text
Panel (tarayıcı, 127.0.0.1:8765)  --WebSocket /ai-->  gateway.py (MacBook)
   lease 50 ms / stop / instruction                    Permit + SkillExecutor + AiBridge (DeepSeek)
                                                          |
                                               LiteVehicle.pump() 50 Hz
                                                          |  UDP, 21 bayt, HMAC-SHA256/8
                                                          v
                                  ESP32-S3: lite_core (20 ms) -> MCPWM, ACT_EN, PCA9685 (I2C, /OE), RMT
                                       <- 20 Hz telemetri: durum, batarya/ToF, odometri
ESP32-CAM × 2 (/capture JPEG) ------HTTP------> LiteVehicle.images()
```

| Parça | Dosya | Görev |
|---|---|---|
| Bağlantı | [`lite_link.c`](../firmware/lite/lite_link.c), [`hmac_sha256.c`](../firmware/lite/hmac_sha256.c), [`frames.py`](../software/ugv_lite/frames.py) | `'U'` + yön (`C`/`T`) + sürüm + id16 + 8 bayt yük + HMAC'in ilk 8 baytı. Yön etikete dahil: telemetri komut diye geri yansıtılamaz. Telemetri etiketi ayrıca çekirdeğin son kabul ettiği lease'e bağlıdır (oturum32 + 32 bite genişletilmiş lease sırası; DD80): MacBook onu yalnız son 0,2 s'te kendi gönderdiği bir lease'le doğrular ve yaşını o lease'ten sayar, bu yüzden kaydedilip yeniden gönderilen, geciken ya da başka oturumdan gelen telemetri düşer. Python ve C bayt bayt aynı |
| Oturum | [`can_protocol.c`](../firmware/stm32/can_protocol.c) | A2 çerçeve anlamları: 0x110 lease (oturum, sıra, mod, deadman), 0x100 sürüş, 0x120 baş, 0x121 kol (omuz, pençe, AI bayrağı), 0x080 STOP. M3/N1: 0x121'in omuz alanı yok sayılır; 0x122 = kol yolu (kaynak duruş, hedef duruş, hedef kesir), kendi ileri sırasıyla; 0x123 = kol elle park edildi onayı (DD80: yalnız aktüatörler kapalıyken, oturum etiketi ve ileri sırayla). Tazelik ile sıra geçmişi ayrı; mod değişimi eski imzalı komutu kabul ettirmez (R3) |
| Robot çekirdeği | [`lite_core.c`](../firmware/lite/lite_core.c) | IDLE → ARMED → DRIVING, ESTOP, FAULT; motor başına PI hız döngüsü (N2), servo ve ışık çıktıları. DD84: kol bir sürüş duruşunda (config `drive_poses`, `arm_graph.h` maskesi) oturmuş değilse ya da gevşekse tekerler sıfıra rampalanır, 0x1A0 bit3 kalkar |
| Kol yolu | [`arm_path.c`](../firmware/lite/arm_path.c), [`arm_graph.h`](../firmware/lite/arm_graph.h) | N1: config'ten üretilen duruş grafiği; yalnız kenar komutları; beş eklem tek noktadan, CAD'in süpürdüğü doğru üzerinde, 45°/s; aktüatör kapanınca hareket iptal. DD80: servo rayı ACT_EN'i izlediği için kol ACT_EN düşünce gevşer; stow'da oturmuş değilse (ve açılışta) kol "gevşek" kilitlenir: kol servolarına darbe yok, 0x122 reddedilir, ta ki operatör kolu elle park edip panelden onaylayana (0x123) dek |
| Araç arayüzü | [`vehicle.py`](../software/ugv_lite/vehicle.py) | Yürütücünün beklediği arayüz; 50 Hz lease/sürüş, 25 Hz pençe ve kol yolu çerçeveleri, telemetriden odometri, ToF ve kol durumu. N1: rotayı duruş grafiğinde planlar, bir sonraki kenarı yalnız 0x1A2 "yerleşti" deyince gönderir; kenar ortasında tutulan kol yeni hedefte önce aynı kenardan geri döner. DD80: telemetriyi lease bağıyla doğrular; gevşek kolu "limp" bildirir, `confirm_arm_parked()` 0x123 gönderir. N3: geç ya da sırası bozuk örneği atar; hedef ve hold yalnız kendi 0x122'sini yankılayan örnekle biter |
| Ağ geçidi | [`gateway.py`](../software/ugv_lite/gateway.py) | Panel mesajları → izin, "dur", AI görevi; paneli yalnız yerelde sunar |
| AI | [`bridge.py`](../software/ugv_ai/bridge.py), [`executor.py`](../software/ugv_ai/executor.py) | [AI kontrolü](ai_control.md) |

Telemetri (20 Hz): 0x190 durum (state, arıza bitleri, sıra, ms), 0x1A0 (batarya mV, bayraklar, ToF sol/sağ), 0x1A1 (sol/sağ enkoder kenarları, komut yönüyle işaretli), 0x1A2 (kol yolu: kaynak, hedef, kesir, hedef kesir, bayrak: bit0 yerleşti, bit1 gevşek; N1, DD80; bayt 7: çekirdeğin aldığı son 0x122 sırasının düşük baytı, N3). Hepsi lease'e bağlı etiketle; her çerçeve kimliği için yalnız daha yeni bir lease'e bağlı örnek kabul edilir (N3). Arıza bitleri: 1 düşük batarya, 2 sürücü ısısı, 16/32/64/128 FL/FR/RL/RR sıkışması.

## Güvenlik katmanları

Öncelik: fiziksel E-stop > STOP/"dur" > operatör > AI.

1. **E-stop:** NC güç kontağı motor ve servo enerjisini doğrudan keser. İkinci kontak GPIO2'de kenarla kilitlenir; kesme `ACT_EN`'i ≤2 ms'de düşürür. Bırakmak robotu harekete geçirmez: IDLE el sıkışması + 500 ms nötr ARM gerekir.
2. **Lease:** 100 ms'den eski lease/komut → IDLE, `ACT_EN` Low. MacBook, izin (panel anahtarı + görünür/odaklı sayfa + 100 ms lease) düşünce deadman'ı bırakır. Yeniden kurulum yalnız açık istekle olur; yürütücüdeki izin nesli eski görevi geçersiz kılar (R2).
3. **Hareket:** elle 300, AI'da 200 mm/s; 0,5 m/s² rampa; ön ToF <250 mm ya da geçersiz okuma ileri hareketi hemen keser. Sürüş ve dönüş yalnız kol parkta (stow) otururken serbest (N4: kaldır, yukarı ve hazır duruşlarında yüklü ağırlık merkezi x/z sınırlarını aşar); kol hareket halinde ya da kenar ortasındaysa yasak. Yürütücü ayrıca pençenin açık olmasını ister: tutulan nesne önce kargo kutusuna bırakılır.
4. **Kol (M3, N1):** kolun hareketini çekirdek kendisi yürütür; yalnız duruş grafiğinin kenarlarında ilerler, kenar dışı ve süreksiz komutları reddeder. Paket kaybı yalnız gecikme yaratır. Yürütücü, telemetri hedef duruşta "yerleşti" diyene kadar bekler; "dur", izin kaybı ya da 20 s zaman aşımında kol olduğu yerde tutulur. Aktüatörler kapanınca hareket iptal olur, yeniden ARM onu sürdürmez. Eklem sınırları ve hızları servo modülünde ayrıca uygulanır.
5. **Sürücü ve motor (R4, F1):**
   - motor başına PI hız döngüsü (N2); çıkış paket gerilimine kadar, sabit gerilim tavanı yok (DD76);
   - teker başına 300 ms stall kesmesi;
   - TB6612 başına 0,5 W + 2 J ısı bütçesi;
   - ters yönde bir tur boşa alma ve geri-EMK sınırlayıcı (tahmin ≤0,9 A); dönmeyen teker 300 ms'de, akım sınırında yavaş dönen çift ≈3 s'de keser.
   Ayrıntı: [Lite elektronik](lite_electronics_A3.md), [hesap](calculation_results.md).
6. **Sensör verisi:** bayat (>200 ms) ya da geçersiz telemetri `NaN` okunur; yürütücü NaN/sonsuz örnekle hareket başlatmaz, hareket ortasında durur (R1).
7. **Arıza sonrası:** FAULT, arıza nedeni kalkınca, 10 s soğuma (stall/ısı) ve IDLE el sıkışmasıyla temizlenir.

Bilinen sınırlar:
- Tek kanallı enkoder dıştan geri sürülmeyi göremez.
- Yerinde dönüş zeminle sınırlıdır: M3'te 5,1 kg brüt kütleyle yürütücü 0,45 rad/s döner, boş pakette µ≤0,30.
- Servolarda konum geri bildirimi yok: servo rayı kesilip yeniden açılınca düşmüş kol son komut açısına tam hızla gider.
- Kameralar ağda kimlik doğrulamasızdır (aşağıya bakın).

## Bağlantı anahtarı

Anahtar repoya, sohbete ya da ekran görüntüsüne girmez. MacBook'ta bir kez üretilir:

```sh
mkdir -p ~/.config/ugv && python3 -c "import secrets; print('UGV_LINK_KEY=' + secrets.token_hex(32))" > ~/.config/ugv/link.env && chmod 600 ~/.config/ugv/link.env
```

Aynı 32 bayt ESP32-S3'ün NVS'sine yazılır (bring-up; `tools/make_nvs.py`, aşağıda "NVS ayarları"). Anahtar değişirse iki taraf birlikte değişir. `.gitignore` `*.env` ve `secrets/` dışlar.

## Ağ ve kameralar

Varsayılan: MacBook, ESP32-S3 ve iki ESP32-CAM aynı 2,4 GHz Wi-Fi ağında, yönlendiricide sabit DHCP kiralarıyla. MacBook internete de bu ağdan çıkar (DeepSeek). Kontrol bağlantısı imzalıdır.

ESP32-CAM'ler 80. portta `/capture` ile en yeni JPEG karesini sunar ([`firmware/lite/eye/`](../firmware/lite/eye/main/eye_main.c), DD88). Ayar: VGA 640×480, JPEG kalite 12, PSRAM'de iki tampon, "en yeni kare" kipi; beyaz flaş LED'i kapalı. Pozlama, kazanç ve beyaz dengesi stereo kalibrasyonuna kadar otomatiktir; kalibrasyon iki göze aynı sabit değerleri NVS'e yazar (`aec`, `agc`, `wb_mode`). Bu uç **kimlik doğrulamasızdır**, aynı ağdaki herkes görüntüyü çekebilir. Bu yüzden ev ağı yerine ayrı bir SSID ya da misafir ağı önerilir; kalibrasyon ve gecikme L4'te ölçülür.

## Çalıştırma (L4 sonrası)

```sh
set -a; . ~/.config/ugv/link.env; . ~/.config/ugv/deepseek.env; set +a
UGV_ESP32_ADDR=192.168.1.50:4210 UGV_EYE_URLS=http://192.168.1.51/capture,http://192.168.1.52/capture \
  python3 software/ugv_lite/gateway.py
```

Sonra tarayıcıda `http://127.0.0.1:8765/`. Panel yalnız bu makineden açılır. IP ve port değerleri örnektir; ESP32 tarafı L4'te belirlenir. Ücretli API ile ilk çalıştırma kullanıcı onayı ve düşük dolar tavanıyla yapılır.

## Testler

`tests/lite_link_test.c`, `tests/lite_core_test.c` (motor modeliyle), `tests/check_lite_gateway.py` (C çekirdeği ctypes ile; Python↔C paket eşliği, firmware servo tablosu ↔ config, kurulum, 0,2 m sürüş, 30° dönüş, kolun grafik yolu ve çekirdek darbeleri, izin kaybında kolu tutma, ToF, bağlantı/izin kaybı, bayat telemetri, ağ geçidi), `tests/check_ai_executor.py`, `tests/check_ai_bridge.py`. `tests/board_math_test.c` (L4a kart hesabı), `tests/vl53l0x_test.c` (ToF çifti, kayıt modeli). İki ESP-IDF projesi Docker'da uyarısız derlenir: `firmware/lite/esp32` ve `firmware/lite/eye`. Canlı sunucu yerelde bir kez denendi (panel HTTP + `/ai` WebSocket). Komutlar: [tests/README.md](../tests/README.md).

## L4a: ESP32-S3 kart katmanı (derlendi, donanımda çalışmadı)

- `firmware/lite/board_math.{h,c}` (host testli, `tests/board_math_test.c`):
  - PCA9685 ön bölücü ve µs → sayım; osilatör frekansı NVS'ten kalibre edilir, 0 µs = tam kapalı;
  - TB6612 IN1/IN2 (sür–serbest, motor başına kutup);
  - batarya bölücüsü 100k/22k × kalibrasyon.
- `tools/gen_pins.py` → `firmware/lite/esp32/main/pins.h`, `config/esp32_pinmap.json`'dan üretilir; `check_esp32_pinmap.py` eşliği denetler.
- `firmware/lite/esp32/` (ESP-IDF ≥ 5.3, hedef esp32s3): `main/app_main.c` çekirdeği gerçek çevre birimlerine bağlar:
  - NVS `ugv` alanı: `link_key` (32 bayt), `ssid`, `pass`, `port` (varsayılan 4210), `vbat_cal`, `pca_osc_hz`, `motor_pol`;
  - E-stop kesmesi (IRAM): `ACT_EN` Low ve /OE High, çekirdeğin sonraki adımını beklemeden;
  - MCPWM 20 kHz (%0'da çıkış Low'a zorlanır), PCNT (A kanalı, iki kenar, taşma birikimi), PCA9685 (I²C0, yalnız değişen kanal yazılır), ADC1 (eğri kalibrasyonu), RMT ile WS2812;
  - Wi-Fi STA (güç tasarrufu kapalı), engellemesiz UDP; telemetri yalnız imzası doğrulanmış gönderene gider;
  - 1. çekirdekte 20 ms görev, görev watchdog'u 1 s (panik);
  - sıra: kapatırken önce `ACT_EN`/`/OE`, açarken çıkışlar yazıldıktan sonra; `/OE` yalnız `ACT_EN` High ve E-stop bırakılmışken Low.
  - Ön VL53L0X çifti (L4b, DD87, `firmware/lite/vl53l0x.{h,c}`, host testli): sol sensör XSHUT ile resette tutulurken sağdaki 0x29 → 0x30 taşınır, sonra ikisi ST sırasıyla kurulur ve arka arkaya ölçer. Her adımda engellemeden okunur; 100 ms yeni ölçüm yoksa 0 verilir, çekirdek bunu "ileri engelli" sayar.
- Derleme (Docker, `espressif/idf:v5.3.2`; repo salt okunur bağlanır, çıktı konteynerde kalır). Xtensa GCC 13.2 ile `-Wall -Wextra -Werror` altında uyarısız; uygulama 0xCCA40 bayt, 1 MB bölümün %20'si boş:

```bash
docker run --rm -v "$PWD/firmware":/fw:ro -e IDF_COMPONENT_MANAGER=0 espressif/idf:v5.3.2 bash -c 'cd /fw/lite/esp32 && idf.py -B /tmp/build -DSDKCONFIG=/tmp/build/sdkconfig -DIDF_TARGET=esp32s3 build'
```

## NVS ayarları (bring-up)

İki kart da ayarlarını NVS'in `ugv` alanından okur; değerler repoda durmaz. [`tools/make_nvs.py`](../tools/make_nvs.py) (DD89) CSV'yi `~/.config/ugv/link.env` ve `wifi.env`'den üretir, `~/.config/ugv/nvs/` altına yalnız sahibinin okuyacağı izinle yazar. Değerleri denetler: anahtar 32 bayt hex, SSID ≤32 bayt, WPA2 parolası 8–63, kutuplar ±1, kalibrasyonlar makul aralıkta. Sonra bastığı iki komutla bölüm görüntüsü üretilip 0x9000'e yazılır. Espressif'in üretici ve okuyucusuyla uydurma bir anahtar üzerinde sınandı.

```sh
# wifi.env'i bir düzenleyiciyle oluştur (parola kabuk geçmişine girmesin): UGV_WIFI_SSID=... ve UGV_WIFI_PASS=... satırları
chmod 600 ~/.config/ugv/wifi.env
python3 tools/make_nvs.py s3 --motor-pol 1,1,1,1      # kutuplar bring-up'ta ölçülür
python3 tools/make_nvs.py eye                          # kalibrasyondan sonra: --aec --agc --wb-mode
```

Kartlara yükleme macOS'ta yapılır, çünkü Docker macOS'ta USB seri porta erişemez. Derleme çıktısı konteynerden `~/ugv-build`'e alınır ve `esptool` ile yazılır (`python3 -m pip install --user esptool`; henüz denenmedi):

```sh
docker run --rm -v "$PWD/firmware":/fw:ro -v ~/ugv-build:/out -e IDF_COMPONENT_MANAGER=0 espressif/idf:v5.3.2 bash -c 'cd /fw/lite/esp32 && idf.py -B /out/s3 -DSDKCONFIG=/out/s3/sdkconfig -DIDF_TARGET=esp32s3 build'
cd ~/ugv-build/s3 && python3 -m esptool --chip esp32s3 -b 460800 write_flash @flash_args
```

| Kart | Anahtarlar |
|---|---|
| ESP32-S3 | `link_key` (32 bayt, `~/.config/ugv/link.env` ile aynı), `ssid`, `pass`, `port`, `vbat_cal`, `pca_osc_hz`, `motor_pol` |
| ESP32-CAM × 2 | `ssid`, `pass`; kalibrasyondan sonra `aec`, `agc`, `wb_mode` |

## L4b'ye kalanlar (parçalar gelince)

1. İki ESP32-CAM'i ESP32-CAM-MB ile yüklemek, yönlendiricide sabit DHCP kiraları, görüntü gecikmesi ve stereo kalibrasyonu (sabit `aec`/`agc`/`wb_mode`).
2. Bring-up ve TL1–TL5 / T-testleri: `make_nvs.py` ile anahtar ve kalibrasyonları NVS'e yazmak, motor kutupları, PCA9685 osilatörü (darbe ölçümü), sargı direnci, 1:78/PPR, iki ToF'un gerçek menzil ve adresleme denemesi, ısı bütçesi sabitleri, gerçek µ, E-stop süresi, kol duruşları ve servo kalibrasyonu, kargo düşüşü.
3. İlk ücretli DeepSeek denemesi (onaylı, ≤0,10 USD).
