# UGV-MCU-01 pin kaynak incelemesi — P0

> **A2 kaydı.** A3 Lite (≤10.000 TL, DD65–DD67) bu kartları ve pinleri kullanmaz; güncel elektronik: [Lite elektronik](lite_electronics_A3.md).

23.09.2026 · PHASE 5 masaüstü ön kontrolü. Baskı ve elektronik prototip beklenirken yapılan **pin kaynak seçimi**; şematik, ERC, PCB veya donanım onayı değildir.

Kaynak: ST [DS12288 Rev 6, LQFP100 pinout ve Tablo 13](https://www.st.com/resource/en/datasheet/stm32g474ve.pdf), TI [DRV8874 Rev A veri sayfası, Tablo 2–4](https://www.ti.com/lit/ds/symlink/drv8874.pdf) ve yerel KiCad 10.0.6 `MCU_ST_STM32G4:STM32G474VETx` sembolünün temel `STM32G474V_B-C-E_Tx` pin tanımı. Tek düzenlenebilir atama listesi [`config/mcu_pinmap.json`](../config/mcu_pinmap.json); test [`tools/check_mcu_pinmap.py`](../tools/check_mcu_pinmap.py) üzerinden fiziksel pin numarası, alternatif işlev, yinelenen kullanım ve kritik sinyal eksikliği denetlenir. Test sonucu: **53/53 pin ataması geçti**. KiCad sembolü elektriksel davranış ve AF numarasını kanıtlamaz; AF değerleri ayrıca ST Tablo 13'ten okunmuştur.

| Kaynak | Sinyaller | Portlar / paket pinleri | ST AF |
|---|---|---|---|
| Encoder FL | TIM2 CH1/2 | PA15/78, PB3/90 | AF1 |
| Encoder FR | TIM3 CH1/2 | PB4/91, PB5/92 | AF2 |
| Encoder RL | TIM4 CH1/2 | PB6/93, PB7/94 | AF2 |
| Encoder RR | TIM5 CH1/2 | PA0/20, PA1/21 | AF2 |
| Motor `IN1` PWM | TIM8 CH1/2/3/4 | PC6/65, PC7/66, PC8/67, PC9/68 | AF4 |
| Motor `IN2` PWM | TIM1 CH1/2/3/4 | PE9/40, PE11/42, PE13/44, PE14/45 | AF2 |
| CAN | FDCAN1 RX/TX | PD0/82, PD1/83 | AF9 |
| Timer break girişleri | TIM8 BKIN / TIM1 BKIN | PD2/84, PE15/46 | AF4 / AF2 |
| IMU SPI1 | SCK/MISO/MOSI | PA5/27, PA6/28, PA7/29 | AF5 |
| Servolar pan/tilt | TIM15 CH1/2 | PA2/22, PA3/25 | AF9 |
| A2 omuz / pençe servo | TIM17 CH1 / TIM20 CH2 | PB9/96, PE3/2 | CubeMX teyidi |
| A2 servo rayı istek / akım | GPIO / ADC2_IN5 | PE8/39, PC4/30 | GPIO / analog |
| A2 ışık şeridi verisi | SPI2 MOSI (TX-only) | PB15/54 | CubeMX teyidi |
| Yerel ölçüm | I²C2 SDA/SCL | **PA8/69, PA9/70** | **AF4** |
| PWR↔MCU güvenlik/tanı | RUN_REQ, WDI, ACT_EN readback, K1/K2, E-stop A/B, WD_OK | PD8–PD15 / pin55–62 | GPIO |
| Debug | USART3 TX/RX | PC10/79, PC11/80 | AF7 |
| USB servis | DM/DP | PA11/72, PA12/73 | dedicated |
| SWD | SWDIO/SWCLK | PA13/76, PA14/77 | AF0 |
| 4 motor akımı | ADC1 IN6/7/8/9 | PC0/15, PC1/16, PC2/17, PC3/18 | analog |
| GPIO rezervleri | IMU CS/DRDY, motor nFAULT | PA4, PE0–2, PE4–7 | GPIO |

PWR bağlantısının voltaj, yön, pin sırası, kopuk kablo ve ortak yüksek akım dönüşü koşulları [arayüz sözleşmesinde](pwr_mcu_interface.md) tanımlıdır. Bu tablo, iki gerçek konnektörün şematikte yerleştirildiği anlamına gelmez.

**Düzeltme:** Ön mimarideki PB10/PB11 I²C2 adayı geçersizdi: LQFP100 paketinde pinler vardır ancak Tablo 13'te I²C2 SDA/SCL işlevi yoktur. PA8/PA9 hem paket hem AF4 açısından uygundur ve mevcut tahsise çarpmaz. PB8-BOOT0 üzerindeki I²C1 SCL seçeneği, normal boot durumunu haricî pull-up ile etkileyebileceğinden tercih edilmedi. Bu seçim 3.3 V open-drain I²C elektrik tasarımı, pull-up değeri ve kapasitans hesabı yapılmış demek değildir.

**Sürüş modu düzeltmesi:** DRV8874 PH/EN modunda `EN=0` **brake** verir; güvenlik mimarisinin nötr/coast şartıyla çelişiyordu. PMODE=High PWM modu seçildi: `IN1/IN2=00` coast, `10` ileri, `01` geri, `11` brake. Dört `DIR_*` GPIO tahsisi çıkarıldı, dört TIM1 kanalı eklendi; TIM1 BKIN PE15'in aynı güvenlik olayına bağlanması planlanır. 20 kHz çift timer PWM, sıfır geçiş ve yön değişiminde 1 periyot coast aralığı, iki break girişinin aktif seviyesi ve haricî nSLEEP hattı şematik/firmware test konusudur. PMODE sabit mantık High seviyesinde tutulur; nSLEEP bırakılmadan önce geçerli seviye ölçülür.

## Şematik öncesi kapanış

1. CubeMX/STM32CubeIDE `.ioc` ile 58 atamanın (A2 servo zamanlayıcıları TIM15/17/20 yalnız 50 Hz; PB8 BOOT0 yasak — doğrulayıcı kuralı) pin, AF, TIM1/TIM8 timer eşzamanlılığı ve break polaritesi, ADC tetikleme/DMA ve EXTI paylaşımı bağımsız teyit edilecek. Sembol kontrolü DMA kanal/IRQ çakışmasını görmez.
2. Tüm VDD/VSS, VDDA/VSSA, VREF+, VBAT, NRST, BOOT0 ve saat pinlerinin bağlantısı; bypass kondansatörleri ve güç sıralaması şematikte netleşecek. PB3 SWO ve PA15 JTAG kullanılamaz; SWD açık kalacak.
3. DRV8874 PMODE, IN1/IN2, nSLEEP, nFAULT, IPROPI ve VREF bağlantısı/logic seviyeleri gerçek veri sayfası devresine bağlanacak. Dört akım kanalının ADC örnekleme penceresi PWM gürültüsünden ayrılacak.
4. Fiziksel E-stop ve haricî watchdog, `TIM1_BKIN`/`TIM8_BKIN` girişlerinden **bağımsız** olarak sürücü nSLEEP ve güç kesicilerine müdahale edecek. MCU reset/boot sırasında aktüatörler pasif durumda kalacak. Timer break tek güvenlik katmanı değildir.
5. PWR↔MCU ve motor/encoder/CAN/servis konnektörleri için tam pinout, voltaj, akım, eş konektör ve keyed orientation tablosu hazırlanacak. `GPIO` tahsisi bir kablo demeti veya PCB netlisti değildir.
6. KiCad şematik, ERC ve bağımsız pin/polarite incelemesi bitmeden PHASE 5 geçilmez; Gerber/üretim kararı alınmaz.

Çalıştırma (KiCad 10 macOS kurulumunda):

```bash
python3 tools/check_mcu_pinmap.py --library /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/MCU_ST_STM32G4.kicad_sym
python3 tests/check_mcu_pinmap_integration.py
```
