# UGV-01 denetimli AI kontrolü (A2)

24.09.2026 · Alt proje 4 ([plan](superpowers/plans/2026-09-24-a2-ai-software.md), [spec §4](superpowers/specs/2026-09-24-a2-character-ai-design.md)). Kod ve host testleri var; **araçta, gerçek API ile veya donanımla çalıştırılmadı.** Gerçek API testi ücretlidir; yalnız kullanıcı onayı ve düşük dolar tavanıyla yapılacak. **Güncelleme (DD65):** varsayılan model `deepseek-flash` (DeepSeek V4.1 Flash; görüntü + araç çağırma); `claude-sonnet-5` seçenek olarak kalır. A3 Lite'ta köprü ve panel MacBook'ta çalışır.

## Katmanlar ve öncelik

Öncelik sırası: **fiziksel E-stop > yazılımsal STOP / "dur" > operatör sürüşü > AI yürütücüsü.** Dil modeli yalnız doğrulanmış araç çağrıları üretir. ARM, watchdog, akım sınırı veya E-stop'u değiştiremez (DD19/V5).

| Katman | Yer | Görev |
|---|---|---|
| [Web panel](../software/web_ui/panel.html) | MacBook tarayıcısı | Yazılı/sesli komut (tr-TR konuşma tanıma metni kutuya yazar, operatör gönderir). "dur/durdur/stop/kes" **yerelde** STOP gönderir, AI'a gitmez. AI modu izni: anahtar açık + sekme görünür + odaklı; izin sürdükçe 50 ms'de bir lease. [Saf mantık](../software/web_ui/panel_logic.mjs) `node --test` ile sınanır. |
| [`ai_bridge`](../software/ugv_ai/bridge.py) | MacBook (A3 Lite), internet | `deepseek-flash` (varsayılan) veya `claude-sonnet-5` ile manuel araç döngüsü. Her API çağrısından önce izin ve dur bayrağı kontrol edilir. `refusal`/`max_tokens` gelirse o turun araçları yürütülmez. Görev başına en çok 15 adım ve 0,10 USD (Claude ile 0,30 USD). Her adım `ai_steps.jsonl`'e görev kimliği ve modele gönderilen görüntülerin yollarıyla kaydedilir; görüntüler görev klasöründe tutulur, görevler birbirinin üstüne yazmaz (DD69, R10). |
| [`skill_executor`](../software/ugv_ai/executor.py) | MacBook (A3 Lite; A2'de CM5), internetsiz çalışır | Araçtaki tek yol. Her çağrı yerel sınırlarla doğrulanır; hareket 20 Hz tiklenir; dur, izin kaybı (lease >100 ms) veya ön ToF <0,25 m hareketi keser. Görev başladığı izin neslini tutar: lease bir kez düşerse ya da anahtar/odak kapanırsa izin sonradan yenilense bile o görev bir daha hareket üretmez (R2). NaN/sonsuz odometri veya ToF örneğiyle hareket başlamaz ya da hemen durur (R1). Her hareket araç durmuş biter; model beklerken araç duruyor. |
| [MCU](../firmware/stm32/can_protocol.c) | STM32 | 0x120/0x121 (M3: +0x122 kol yolu) servo/AI çerçeveleri yalnız taze kurulu lease + deadman + session tag ile kabul edilir. **AI modunda veya 0x121 bayatken tekerlek hız tavanı 200 mm/s.** [Servo kontrolü](../firmware/stm32/servo_control.c) eklem sınırları, rampa, ray sıralaması ve aşırı akım latch'ini uygular. |

## Araçlar ve yerel sınırlar

[Şemalar](../software/ugv_ai/tools.py) `strict: true`, kapalı nesnedir ve sırası sabittir (önbellek öneki). Katı şema sayısal sınır taşımadığından sınırlar açıklamada yazar, **yürütücüde zorlanır**; sınır dışı çağrı `is_error` sonucu olarak modele döner.

| Araç | Sınır |
|---|---|
| `look(pan_deg, tilt_deg)` | pan −90…90°, tilt −60…+30° |
| `drive(distance_m, speed_mps)` | ±1,0 m, 0,02–0,2 m/s; ön ToF <0,25 m ileri sürüşü keser; kol stow'da ve pençe açık değilken yok (N4: kaldırılmış duruşlar yüklü ağırlık merkezini sınırın dışına taşır; nesne kutuda taşınır); DD84: çekirdek de kol duruşunu denetler |
| `turn(angle_deg)` | ±180°, 0,6 rad/s; kol `reach_*` iken yok |
| `arm(pose)` | `stow` 180°, `ready` 90°, `reach_mid` 0°, `reach_low` −55°. DD80: kol "limp" ise (açılış ya da stow dışında güç kesilmesi) reddedilir; operatör kolu elle park edip panelden onaylamalıdır |
| `gripper(action)` | `open` / `close`; ≤150 g |
| `wait(seconds)` | 0–10 s, durarak |
| `say(text)`, `ask_operator(question)` | ≤200 karakter, panelde gösterilir; araç üstü hoparlör yok |
| `finish(summary)` | ≤500 karakter, görevi bitirir |

Hareket araçları (`look`, `drive`, `turn`, `arm`, `gripper`) iki gözün yeni görüntüsünü ve araç durumu JSON'unu döndürür; diğerleri yalnız durumu. İlk mesaj talimatı, durumu ve iki görüntüyü taşır.

## İstek biçimi ve maliyet

Köprü Anthropic Messages biçimini kullanır ve sağlayıcıyı `PROVIDERS` tablosundan seçer. **DeepSeek (varsayılan):** istemci `base_url="https://api.deepseek.com/anthropic"` ve ortamdaki `DEEPSEEK_API_KEY` ile kurulur; istek `messages.create(model="deepseek-flash", max_tokens=8000, system=SYSTEM, tools=..., messages=..., output_config={"effort": "medium"})`. DeepSeek'in [uyumluluk belgesi](https://api-docs.deepseek.com/guides/anthropic_api) `cache_control`'ü yok sayar ve `output_config` için yalnız `effort`'u listeler; bu yüzden `thinking`, `cache_control` ve araçlardaki `strict` gönderilmez (duman testinde yeniden değerlendirilir). **Claude:** `model="claude-sonnet-5"`, `thinking={"type": "adaptive"}`, `cache_control={"type": "ephemeral"}`, katı araçlar. Sistem istemi sabittir (zaman damgası/ID yok) ve kameradaki yazıların talimat sayılmayacağını söyler. Maliyet yanıtın `usage` alanından hesaplanır. `deepseek-flash`: 1 milyon token başına en çok 0,30 USD giriş ve 1,20 USD çıkış (yoğun saat; diğer saatlerde yarısı), görüntü başına ≤1.024 token ([fiyatlar](https://api-docs.deepseek.com/quick_start/pricing)). 15 adımlık görev ≈0,01–0,03 USD. Claude Sonnet 5: 2/10 USD, görev ≈0,2–0,3 USD. İki tahmin de **ölçülmedi**. Not: `deepseek-v4-pro` görüntü almadığı için kullanılamaz; V4.1 Pro henüz yayınlanmadı.

## Anahtar ve gizlilik

API anahtarı sohbete ya da repoya yazılmaz. A3 Lite'ta MacBook'ta, izni 600 olan bir dosyada (ör. `~/.config/ugv/deepseek.env`, tek satır `DEEPSEEK_API_KEY`) durur ve köprü başlatılırken ortama yüklenir. Anahtar yoksa köprü SDK'yı içe aktarmadan açık bir hatayla durur. Repo `.gitignore`'u `secrets/` ve `*.env` dosyalarını dışlar. AI modunda iki göz görüntüsü ve araç durumu seçili sağlayıcıya (varsayılan DeepSeek) gider; panel bunu gösterir. İnsanların yüzü görüntüye girebilir, bu yüzden AI modu yalnız bilinen iç mekânda ve izinli kişilerle kullanılır.

## Panel ↔ ağ geçidi mesajları (WebSocket `/ai`)

A3 Lite'ta sunucu [`gateway.py`](../software/ugv_lite/gateway.py)'dir: paneli yalnız 127.0.0.1'de sunar, mesajları izin/dur/talimata çevirir ve aracı [`LiteVehicle`](../software/ugv_lite/vehicle.py) ile imzalı UDP üzerinden sürer ([Lite yazılım](lite_software_A3.md)).

Panelden: `{"type":"lease","ai":true}` (50 ms), `{"type":"stop","source":...}`, `{"type":"instruction","text":...}`. Panele: `{"type":"say","text":...}`, `{"type":"ask","question":...}`, `{"type":"status","text":...}`. Sunucu tarafı (yürütücü, köprü ve CAN ağ geçidi arasındaki yapıştırıcı) alt proje 5'te ROS/gateway ile yazılır. Panel bağlantısızken "dur" araca ulaşamaz ve bunu açıkça yazar; fiziksel E-stop birincildir.

## Test kapsamı (ücretsiz, host)

- `python3 tests/check_ai_executor.py`: şema biçimi, sınır dışı/bilinmeyen/fazla anahtarlı çağrı, izin ve lease kaybı, dur sözünün bir tikte kesmesi, ToF refleksi, kol–sürüş kilidi, `ask_operator`/`finish`.
- `python3 tests/check_ai_bridge.py` (mock istemci): istek biçimi, gözlem, `tool_result` eşleşmesi, hata sonucu, `refusal`/`max_tokens`, adım/dolar tavanı, izin kaybı, dur sözü, API hatasında güvenli durma.
- `tests/servo_light_test.c`, `tests/can_protocol_test.c`, `node --test software/web_ui/panel_logic.test.mjs`.

## Açık işler

1. Sunucu/gateway yapıştırıcısı, ROS düğümleri, gerçek kamera ve ToF sürücüleri (alt proje 5).
2. **Ücretli duman testi** (kullanıcı onayı, ≤1 USD tavan): önbellek isabeti, görüntülü `tool_result` kabulü, gerçek adım maliyeti ve gecikme.
3. Servo mutlak konumu bilinmiyor. Ray yeniden açılınca servo son hedefe tam hızla gidebilir (R51). Geri beslemeli servo veya açılışta park pozu prosedürü gerekir.
4. Kamera görüntüsündeki yazıyla komut enjeksiyonu (R50). Yerel sınırlar ve operatör denetimi azaltır, sıfırlamaz.
