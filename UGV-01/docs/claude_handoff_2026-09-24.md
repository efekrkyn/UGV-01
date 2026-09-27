# Claude için UGV-01 devir promptu

`UGV-01` repository'sinde UGV-01 özgün modüler 4×4 skid-steer kara aracı tasarımına **mevcut dosyaları okuyarak** devam et. Kullanıcı baskıyı bir süre erteledi; fiziksel prototip/test yapılmadı. A1 dış tasarım sıcak sarı paneller ve koyu tamponlarla özgün bir UGV'dir; kameralı çift göz modülü kullanıcının kararıyla sonraki revizyona ertelendi. Mevcut A1'de tek ön RGB kamera zarfı ve düz sensör flanşı var. CAD/PCB üretim onayını kanıtsız ilan etme.

Önce `README.md`, `docs/design_progress.md`, `docs/design_decisions.md`, `docs/phase_reviews.md` ve `docs/superpowers/plans/2026-09-24-pwr-safety-path.md` dosyalarını oku. Yaklaşık %40 tasarım ilerleme tahmini 23.09.2026 tarihlidir; çalışan araç yüzdesi değildir. A1 kavram CAD ve D1/D2A tahrik STEP'leri, sistem belgeleri, kısmi KiCad arayüz sayfaları, host C güvenlik çekirdeği ve CAN protokol testi var. Tam PWR/MCU PCB, tam firmware/ROS/web kodu, üretim dosyaları ve T01–T20 fiziksel kanıt yok.

Son tamamlanan iş: `electronics/ugv_pwr_01/k2_reference.kicad_sch` ve PDF, `tools/build_k2_reference.py`, `tests/check_k2_reference.py`, `docs/k2_reference_schematic.md`. K2 adayında LM74900QRGERQ1 + 2×CSD18540Q5BT ve 1 mΩ dört uçlu Kelvin şönt kullanıldı. 49,9 Ω RSET, 31,6 kΩ ILIM ile OCP yaklaşık18,95 A tipik ve 16,28–21,13 A ön tolerans; ISCP varsayılan 20 mV ile yaklaşık17,68–23,00 A kısa devre aralığı. 68 nF TMR yaklaşık0,99 ms tipik; 100 kΩ paralel direnç latch adayıdır. SLEEP=EN; gerçek güvenli kesme için EN donanımla Low olmalı. U1 thermal pad25 (`RTN`) elektriksel olarak yüzen bakır adaya lehimlenmeli, PGND'ye bağlanmamalı. Sayfa netlist testi geçiyor; ERC 0 hata, 4 uyarı (3 yerel UGV kütüphane çözümleme, 1 haricî PWR_3V3 tek etiket). Bu yalnız **K2 referans devresi**, tam aktüatör/güvenlik kartı değil.

Önce devam eden güç/güvenlik tasarımını tamamla: `docs/precharge_and_separator_diagnostics.md` sırasındaki K1→MID→K2→ACT_BUS, 470 Ω anahtarlı ön şarj, 150 Ω ACT bleed, 1 kΩ çift anahtarlı arıza test enjeksiyonu, üç ray ölçümü ve haricî `SAFE_EN`/NC/watchdog iznini gerçek KiCad sayfalarına geçir. `docs/watchdog_design.md`, `docs/k1_relay_selection.md`, `docs/k2_separator_selection.md` ve `docs/pwr_mcu_interface.md` koşullarını koru. K1'in 16,8 V DC motor yükünü K2 kısa arızasında açabileceği üretici/ölçüm kanıtı hâlâ yok; MPN ve footprint'i onaylama. Şönt MPN/footprint, gate-source koruma, F1 I²t koordinasyonu, TVS/regen clamp, MOSFET SOA ve 120×80 mm kart termali açık. LM74900'un SLEEP iç bypass'ını E-stop olarak kullanma. Ön şarj FET'i kısa kalırsa K1 kapanmadan tanılanmalı; test enjeksiyonunda bir anahtar kısa kalırsa NC/watchdog ikinci anahtar akımı kesebilmeli. PWR_ACT_EN, ARMING süresince Low.

Her tamamlanan KiCad sayfasını gerçek pin/netlist testi ve ERC ile doğrula; beklenen kısmi-sheet uyarılarını açıkça ayır. Tam PWR kartı birleşmeden ERC PASS/PCB release, Gerber veya sürüş onayı verme. Hesap/şema sonucu fiziksel T01/T13 osiloskop izinin yerini tutmaz. Her önemli kararı `docs/design_decisions.md` ve aşama kapısını `docs/phase_reviews.md` içinde güncelle. Kullanıcı yokken bağımsız ilerle; sadece gerçekten vazgeçilmez dış karar/ölçüm için sor.

Bu ortamda son doğrulama komutları:

```sh
cd UGV-01
python3 tools/build_k2_reference.py
python3 tests/check_k2_reference.py
python3 tests/check_board_interface_sheets.py
```
