# Haricî watchdog zamanlama ve güvenli varsayılan — PH6 şematik girdisi

23.09.2026 · **Kart şematiği/ölçüm onayı değildir.** Hareket izin hedefi, son sağlıklı `MCU_WDI` darbesinden donanım trip'ine toleranslar dahil ≤100 ms, trip sonrası K1/K2 enerji ayırmasına ≤50 ms'dir. [TI TPS3431 veri sayfasındaki](https://www.ti.com/lit/ds/symlink/tps3431.pdf) fabrika ayarı (`CWD=10 kΩ→VDD`) **170–230 ms** watchdog süresi verir; bu ayar hedefi karşılamaz. Önceki genel “TPS3431 adayı” ifadesi yalnız aşağıdaki CWD seçimiyle geçerli olur.

## Ön seçim ve zaman bütçesi

| Öğe | Ön tasarım | Hesap / kapanış |
|---|---|---|
| IC | [TPS3431SDRBR](https://www.ti.com/product/TPS3431/part-details/TPS3431SDRBRG4) adayı, 3,3 V `VDD` | Exact sipariş/footprint ve sıcaklık aralığı PH6'da kontrol |
| `CWD` | 100 pF C0G/NP0, ±5%, doğrudan GND; kısa iz/guard | TI: `tWD = 55 + 77,4×C[nF] ms`; nominal **62,74 ms**. Veri sayfasında ideal100 pF için **56,77–68,70 ms**; +%5 C ile üst yaklaşık69,12 ms. PCB paraziti/kaçak/gerçek sıcaklık ölçülür. |
| Besleme gözetimi | 3,3 V power-good, `WDO`/`ENOUT` açık-drenaj Low izin keser | `VDD<VPOR` için `WDO` tanımsız olabilir; yalnız WDO pull-up'ına güvenilmez. PGOOD Low ise tüm K1/K2, ön şarj ve test gate izinleri fiziksel Low. |
| `EN`, `SET1` | Sabit High'a bağlanır; yazılım bunları süremez | `EN=Low` WDO'yu Hi-Z/High yapabildiği, `SET1=Low` watchdog'u kapattığı için MCU kontrolüne verilmez. `ENOUT` da Low'a çeken izin zincirinde yer alır. |
| `WDI` | J-SIG pin2, PWR'de varsayılan Low bias ve giriş koruması | 20 ms aralıkla yalnız doğrulanmış ana güvenlik turu sonrası kenar; salt timer/DMA pet'i yok. Kablo açık ve MCU reset'te kenar yok. |

Tasarım hesabında 100 pF +%5, en kötü IC faktörü ×1,095 için `tWD,max≈(55+77,4×0,105)×1,095=69,12 ms`; ek +5 pF PCB paraziti varsayılsa yaklaşık69,55 ms olur. Bu, 100 ms trip hedefine yaklaşık30,45 ms kâğıt üstü pay bırakır; giriş filtre, jitter ve fiziksel ölçüm eklenmeden kesin değer değildir. TI'nin açılış `tRST` süresi **170–230 ms** olabilir: ARM isteği bu sırada reddedilir; E-stop ve rail fault kesmesi watchdog boot'unu beklemez. Bağımsız kesici bırakma süresi≤50 ms ayrıca K1 bobin kelepçesiyle birlikte test edilir.

## Donanım izin denklemi

`SAFE_GATE = NC_A_OK ∧ NC_B_OK ∧ LATCH_RESET ∧ PGOOD_3V3 ∧ WD_OK ∧ UV_OK ∧ OV_OK` taslak denklemdir. `WD_OK`, TPS3431 `WDO` ve `ENOUT` her ikisi açık-drenaj serbestken ve PGOOD sağlıklıyken oluşur. Bu sinyal varsayılan Low sürücü katıyla K1 bobini, K2 gate sürücüsü, ön şarj ve test **izin anahtarını** bastırır; `MCU_RUN_REQ` sadece ayrıca gerekli bir talep sinyalidir. Test komut FET'i kısa kalırsa seri izin FET'i açabilmelidir. Motor nSLEEP ve servo gücü aynı güvenlik sonucuyla ayrı bastırılır. MCU GPIO, I²C expander veya yazılım latçli çıkış High kalmış olsa bile `SAFE_GATE=0` aktüatör kaynak yolunu açar. Bu denklem PCB devresi, NC kanal çapraz-kısa tanısı veya fonksiyonel güvenlik sertifikası yerine geçmez.

**PH6/T03/T13 kabul kapısı:** CWD kapasite/tolerans/paraziti, TPS3431 güç dizisi ve WDO/ENOUT mantığı osiloskopla; MCU ana-loop, ISR, CAN ve ADC hang ayrı; `EN`/`SET1` zorla Low hata enjeksiyonunda izin çıkmaması; 3,3 V brownout'ta WDO belirsiz kalsa da PGOOD'un kapatması; son geçerli WDI→gate Low≤100 ms; son WDI→K1/K2 enerji ayrımı≤150 ms. Her ölçüm 12,4–16,8 V ve sıcaklık zarfında tekrarlanır. Sonuç alınmadan BOM adayı güvenlik yeterliliği sayılmaz.

## 24.09.2026 şema karşılığı

[Güvenlik kapısı sayfasında](../electronics/ugv_pwr_01/safety_gate.kicad_sch) TPS3431 DRB pinleri TI Tablo 5-1'e göre çizildi (1 VDD, 2 CWD, 3 EN, 4 GND, 5 SET1, 6 WDI, 7 WDO, 8 ENOUT, pad GND). `CWD` 100 pF C0G (C305); `SET1=PWR_3V3`; `WDI` MCU'dan 1 kΩ seri ve 100 kΩ pulldown ile gelir. **Değişiklik:** `EN` sabit High yerine TPS3808G33 `RAIL_OK` açık-drenaj çıkışıyla sürülür ve MCU'ya bağlı değildir. 3,3 V ray 3,07 V eşiğin altına düşünce `EN` Low olur, `ENOUT` 200 ns içinde Low'a iner; `WD_OK = WDO ∧ ENOUT` açık-drenaj bağlantısı böylece ayrı PGOOD şartını da taşır. `WD_OK`, `CHAIN_OK`'a ve reset latch'inin `/CLR` girişine gider; WDO darbesi bitince izin kendiliğinden dönmez. `SET1` Low kısa arızası watchdog'u sessizce kapatacağından SELF_TEST'te bilerek WDI durdurma kanıt testi PH8 gereksinimidir. [Ayrıntı](pwr_safety_path.md), [DD54](design_decisions.md). Osiloskop ve sıcaklık kanıtı hâlâ yok.
