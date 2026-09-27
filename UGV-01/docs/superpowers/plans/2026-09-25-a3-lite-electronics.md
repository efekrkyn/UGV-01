# A3 Lite elektronik (L2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [A3 Lite spec'i](../specs/2026-09-24-a3-lite-budget-design.md) için ESP32-S3 pin haritası, modül seviyesinde KiCad bağlantı şeması, güç bütçesi ve ≤10.000 TL parça listesi; hepsi testli.

**Architecture:** Tek kaynak `config/esp32_pinmap.json`: DevKitC-1 v1.1 J1/J3 başlık tabloları (Espressif kullanıcı kılavuzu), kullanılamayan pinler ve 23 atama. Doğrulayıcı (`tools/esp32_pinmap.py`) pin uygunluğunu, ADC1 kuralını (ADC2 Wi-Fi açıkken kullanılamaz) ve çevre birimi kapasitesini (MCPWM 12, LEDC 8, PCNT 4 birim, RMT 4) denetler. Şema (`tools/build_lite_wiring.py` → `electronics/ugv_lite_01/lite_wiring.kicad_sch`) modülleri bağlantı başlığı sembolleriyle gösterir; test netlist'i pin haritası ve güç yoluyla karşılaştırır. BOM `manufacturing/bom/lite_bom_A3.csv`, testle toplam ≤10.000 TL ve adetler config'le tutarlı.

**Pin kararı (23/23):** TB6612 PWMA/PWMB 3V3'e bağlı, hız IN1/IN2'de MCPWM ile (sür/boşta PWM); sürücü STBY ve servo buck EN tek `ACT_EN` (10 k pulldown, açılışta kapalı); iki ToF tek XSHUT ile sırayla adreslenir.

**Commit:** Yok (kullanıcı kuralı).

**Durum (25.09.2026):** Tamamlandı ([DD67](../../design_decisions.md)). Sapma: `ESTOP_SENSE` ADC1/GPIO2, `ACT_EN` GPIO21 (dijital E-stop okuması tek bölücüyle mümkün değil).

---

### Task 1: Pin haritası
- [x] Test önce (`tests/check_esp32_pinmap.py`): gerekli 23 sinyal; strapping/USB/konsol/PSRAM/RGB LED pinleri reddedilir; ADC sinyali ADC1'de (GPIO1–10); tekrar eden GPIO reddedilir; MCPWM ≤12, LEDC ≤8, PCNT ≤4 birim. → FAIL.
- [x] `config/esp32_pinmap.json` + `tools/esp32_pinmap.py` → PASS.

### Task 2: Bağlantı şeması
- [x] Test önce (`tests/check_lite_wiring.py`): her atama doğru DevKitC başlık pinine bağlı; güç yolu batarya → F1 10 A → ana anahtar → `VBAT_SW` → NC E-stop → `VM_ACT` (iki TB6612 VM + servo buck girişi); mantık buck girişi E-stop'tan önce; servo buck EN ve iki STBY = `ACT_EN` + 10 k pulldown; PWMA/PWMB = 3V3; bölücüler 12,6 V'ta ≤3,14 V; ışık verisi 74AHCT1G125 ile 5 V; ERC hatasız. → FAIL.
- [x] `tools/build_lite_wiring.py` + sayfa ve PDF → PASS.

### Task 3: Parça listesi
- [x] Test önce (`tests/check_lite_bom.py`): toplam ≤10.000 TL; motor/servo/kamera/ToF/hücre adetleri config ve pin haritasıyla tutarlı; her satırda kaynak veya "tahmin" notu. → FAIL.
- [x] `manufacturing/bom/lite_bom_A3.csv` → PASS.

### Task 4: Belgeler
- [x] `docs/lite_electronics_A3.md` (blok şema, güç yolu, güç bütçesi ↔ config görev gücü, pin tablosu, güvenlik, açık işler); A2 elektrik belgelerine A3 yönlendirmesi; README, DD67, faz kaydı, `tests/README.md`; bütün testler → PASS.
