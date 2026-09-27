# A2 AI ve yazılım (alt proje 4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Spec §4'teki denetimli AI kontrolünü (Claude Sonnet 5 planlar, araç üstü yürütücü sınırlar) ve MCU servo/ışık/CAN katmanını, gerçek API'ye para harcamadan mock testlerle doğrulanmış biçimde yazmak.

**Architecture:** Üç katman, her biri tek başına test edilir. (1) `software/ugv_ai/` Python: `tools.py` sabit sıralı katı araç şemaları; `executor.py` her aracı yerel sınırlarla doğrular ve yürütür (AI modu izni, "dur" bayrağı, ToF refleksi, kol pozu–sürüş kilidi); `bridge.py` resmî Anthropic SDK ile manuel araç döngüsü (izin her çağrıdan önce, adım/dolar tavanı, `stop_reason` denetimi); `sim.py` test aracı. SDK yalnız varsayılan istemci oluşturulurken içe aktarılır; testler mock istemciyle ücretsizdir. (2) `firmware/stm32/servo_control.c` rampalı, sınırlı servo hedefleri, ray sıralaması, aşırı akım latch'i, darbe genişliği; `light_bar.c` mod renkleri ve ≤0,5 W güç tavanı; `can_protocol.c`'ye 0x120/0x121 servo/AI çerçeveleri ve AI modunda 200 mm/s MCU hız tavanı. (3) `software/web_ui/` statik panel: sohbet, tr-TR ses tanıma, yerel "dur", AI modu izni (anahtar + görünür/odaklı sayfa + 50 ms lease); izin/dur mantığı saf JS modülünde, `node --test` ile.

**Manuel döngü gerekçesi:** Her API çağrısından önce donanım izni ve dur bayrağı yerelde kontrol edilir, adım/dolar tavanı yanıt `usage` alanından uygulanır ve testte istemci basit bir sahte nesneyle değiştirilir. Beta tool runner'a bağımlılık istenmedi.

**Tech Stack:** Python 3 stdlib (+ araçta `anthropic`), C11 host testleri, Node 24 `node:test`.

**Commit:** Kullanıcı git'i proje sonuna bıraktı; commit yok. **Gerçek API testi yok** (ücretli; kullanıcı onayı ve düşük tavan gerekir).

**Durum (24.09.2026):** Tamamlandı ([DD64](../../design_decisions.md)); sunucu/gateway yapıştırıcısı alt proje 5'e kaldı.

---

### Task 1: Yürütücü ve araç şemaları

**Files:** Create `software/ugv_ai/{__init__,tools,executor,sim}.py`, `tests/check_ai_executor.py`

- [x] Test önce: sınır dışı `drive` (1,5 m, 0,3 m/s), `look` (pan 120°), bilinmeyen araç/fazla anahtar → hata ve araç hareketsiz; izin (anahtar, odak, lease ≤100 ms) düşünce sürüş durur; "dur" bayrağı hareketi 1 tikte keser; ön ToF <0,25 m ileri sürüşü keser ama geri sürüşe izin verir; kol `reach_*` pozundayken sürüş reddedilir; `finish` görevi bitirir. → FAIL (modül yok).
- [x] Uygula; araç listesi: `look, drive, turn, arm, gripper, wait, say, ask_operator, finish`; şemalar `strict: true`, `additionalProperties: false`, sayısal sınırlar açıklamada (strict sayısal kısıt desteklemez) ve yürütücüde. → PASS.

### Task 2: Claude köprüsü

**Files:** Create `software/ugv_ai/bridge.py`, `tests/check_ai_bridge.py`

- [x] Test önce (mock istemci): `tool_use` → araç yürütülür, `tool_result` aynı `tool_use_id` ile döner; `refusal`/`max_tokens` → hiçbir araç yürütülmez, araç durur; adım tavanı ve dolar tavanı aşımı → durur; izin düşünce yeni API çağrısı yapılmaz; istek `model="claude-sonnet-5"`, `thinking={"type":"adaptive"}`, üst düzey `cache_control`, sabit araç sırası; ilk kullanıcı mesajında iki göz görüntüsü + durum JSON'u. → FAIL.
- [x] Uygula; API anahtarı yalnız ortamdan (`ANTHROPIC_API_KEY`, araçta gitignore'lu gizli dosyadan systemd `EnvironmentFile`). → PASS.

### Task 3: MCU servo, ışık ve CAN

**Files:** Create `firmware/stm32/{servo_control,light_bar}.{c,h}`, `tests/servo_light_test.c`; Modify `firmware/stm32/can_protocol.{c,h}`, `tests/can_protocol_test.c`

- [x] Test önce: eklem sınırları (pan ±90°, tilt −60…+30°, omuz −55…180°), rampa hızı, ray açılışında 100 ms bekleme, kapanışta önce PWM, aşırı akım (ort. >3,5 A 200 ms / anlık >5,5 A) latch'i, 500–2500 µs darbe eşlemesi; ışık: FAULT kırmızı, AI mavi, toplam güç ≤0,5 W; CAN 0x120/0x121 yalnız taze lease + doğru session tag ile kabul, AI bayrağı veya 0x121 bayatlığında hız tavanı 200 mm/s. → FAIL.
- [x] Uygula → PASS (`cc -std=c11 -Wall -Wextra -Werror`).

### Task 4: Web panel

**Files:** Create `software/web_ui/{panel.html,panel_logic.mjs,panel_logic.test.mjs}`

- [x] Test önce (`node --test`): "dur", "Dur!", "stop", "DUR lütfen" → yerel STOP; "durum nedir" → STOP değil; AI izni yalnız anahtar açık + sayfa görünür + odaklı iken; lease 50 ms'de bir, 100 ms'de düşer. → FAIL.
- [x] Uygula: saf mantık modülü + mantığı kullanan statik sayfa (sohbet, mikrofon `lang="tr-TR"`, AI anahtarı, STOP, `say` metinleri, gizlilik notu: görüntüler Anthropic API'ye gider). Sunucu/ROS köprüsü alt proje 5'te.

### Task 5: Belgeler

- [x] `docs/ai_control.md` (akış, araçlar, sınırlar, izin, maliyet tahmini, gizlilik, test kapsamı), `software_architecture.md`, `communication_architecture.md` (0x120/0x121), README'ler, `.gitignore` (gizli dosyalar), DD64, faz kaydı, `tests/README.md`; tüm testler → PASS.
