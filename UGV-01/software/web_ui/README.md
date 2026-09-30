# Web kontrol arayüzü

**A3 Lite (güncel):** [panel](panel.html) MacBook'ta çalışır; [`gateway.py`](../ugv_lite/gateway.py) onu yalnız 127.0.0.1'de sunar ve `/ai` WebSocket'ini yalnız bu sayfaya, aynı anda tek bağlantıya açar (DD92/A03). Canlı görüntü, ayrıntılı telemetri ve gamepad yok. Donanımda denenmedi.

Aşağısı A0/A2 kaydıdır. Bu teslim mimari taslaktı; o zaman çalışan panel yoktu. Yerel CM5 sunucusu, tek operatör, gamepad/deadman, kamera ve telemetri sözleşmesi [software_architecture.md](../../docs/software_architecture.md) içinde. Kabul T10/T14/T18. Sahte canlı telemetri veya yazılımsal düğmeyi fiziksel acil durdurma olarak gösteren UI kullanılmaz.

A2 (24.09.2026): [AI paneli](panel.html) (sohbet, tr-TR sesli komut, yerel "dur", AI modu izni ve 50 ms lease; DD80: "Kolu elle park ettim" onayı) ve [saf mantık modülü](panel_logic.mjs) — `node --test software/web_ui/panel_logic.test.mjs`. CM5 sunucu tarafı henüz yok; ayrıntı [ai_control.md](../../docs/ai_control.md).
