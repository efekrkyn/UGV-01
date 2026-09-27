# UGV-01 Genel Tasarım Denetimi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** UGV-01 belgeleri, konfigürasyonu, KiCad sayfaları ve BOM arasındaki tasarım hatalarını kanıtlı biçimde bulup düzeltmek; bulguları tek raporda toplamak.

**Architecture:** Bir Markdown bağlantı denetleyicisi test olarak eklenir. Diğer denetimler belirli kaynak çiftlerinin (config ↔ belge ↔ hesap ↔ KiCad ↔ BOM) komutla karşılaştırılmasıdır. Her bulgu `docs/design_review_2026-09-24.md` tablosuna kaynak, hata, düzeltme ve kanıtla yazılır. A2'nin değiştireceği öğeler yalnız işaretlenir ([spec](../specs/2026-09-24-a2-character-ai-design.md) §1).

**Tech Stack:** Python 3 stdlib, mevcut `tools/`/`tests/` betikleri, KiCad 10 `kicad-cli`, `.venv` CadQuery.

**Commit:** Kullanıcı depo/paylaşımı proje sonuna bıraktı ve git kökü üst klasör `ika`. Bu plan commit **yapmaz**; commit adımları yerine test kanıtı kaydedilir.

---

## Dosya yapısı

- Create `tests/check_markdown_links.py` — kendi kendini sınayan göreli bağlantı denetleyicisi; repo `.md` dosyalarında kırık bağlantı kalmadığını doğrular.
- Create `docs/design_review_2026-09-24.md` — bulgu tablosu (ID, kaynak dosya:satır, hata, düzeltme, kanıt, durum: DÜZELTİLDİ / A2'DE DEĞİŞİYOR / KARAR GEREKİR).
- Modify — yalnız bulgulara göre: ilgili `docs/*.md`, `README.md`, `config/*.json`, `manufacturing/bom/*`, `tests/README.md`.
- Modify `docs/design_decisions.md`, `docs/phase_reviews.md` — karar ve faz sonucu.

### Task 1: Markdown bağlantı denetleyicisi

**Files:**
- Create: `tests/check_markdown_links.py`
- Modify: `tests/README.md` (komut listesine ekle)

- [x] **Step 1: Testi yaz (önce kendi negatif örneğini doğrulasın)**

```python
"""Relative Markdown links in the repo must point at existing files."""
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SKIP = (".venv", "__pycache__", ".git")


def broken_links(root):
    bad = []
    for md in sorted(root.rglob("*.md")):
        if any(part in SKIP for part in md.parts):
            continue
        for number, line in enumerate(md.read_text(errors="replace").splitlines(), 1):
            for target in LINK.findall(line):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path = target.split("#")[0]
                if path and not (md.parent / path).exists():
                    bad.append(f"{md.relative_to(root)}:{number}: {target}")
    return bad


with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    (base / "a.md").write_text("[ok](b.md) [web](https://x.y) [anchor](#top) [bad](missing.md#x)\n")
    (base / "b.md").write_text("[up](a.md)\n")
    assert broken_links(base) == ["a.md:1: missing.md#x"], broken_links(base)

bad = broken_links(ROOT)
assert not bad, "\n".join(bad)
print("PASS: every relative Markdown link resolves")
```

- [x] **Step 2: Çalıştır; kırık bağlantıları listele**

Run: `python3 tests/check_markdown_links.py`
Expected: öz-sınama geçer; repo kırık bağlantı içeriyorsa `AssertionError` ile liste basar. Liste rapora bulgu olarak girer (Task 4).

- [x] **Step 3: Kırık bağlantıları düzelt**

Her satır için hedef dosyayı `ls`/`find` ile bul; doğru göreli yolu yaz. Hedef gerçekten yoksa bağlantıyı metne çevir ve rapora "hedef dosya yok" bulgusu ekle.

- [x] **Step 4: Tekrar çalıştır**

Run: `python3 tests/check_markdown_links.py`
Expected: `PASS: every relative Markdown link resolves`

- [x] **Step 5: `tests/README.md` komut bloğuna `python3 tests/check_markdown_links.py` satırını ekle**

### Task 2: Taban çizgisi — bütün testler ve hesaplar

**Files:** değişiklik yok; çıktı raporun "taban" bölümüne.

- [x] **Step 1: Hesapları yeniden üret ve fark var mı bak**

Run: önce `docs/calculation_results.md` ve `.json` dosyalarını scratchpad'e kopyala, sonra `python3 tools/calculations.py`, ardından `cmp` ile karşılaştır.
Expected: fark yoksa hesap belgeleri kaynakla tutarlı; fark varsa bulgu (belge elle düzenlenmiş/eskimiş).

- [x] **Step 2: Tüm test listesini çalıştır**

Run (her satır `tests/README.md`'deki komut): `python3 tests/check_design.py`, `.venv/bin/python tests/check_cad.py`, `.venv/bin/python tests/check_body_mass.py`, `.venv/bin/python tests/check_drivetrain.py`, `.venv/bin/python tests/check_lightweight.py`, tüm `python3 tests/check_*.py` KiCad testleri, iki C testi.
Expected: hepsi PASS. FAIL olan her test bulgu olur ve kök nedeni düzeltilir.

### Task 3: Kaynaklar arası sayısal tutarlılık

Her adım bir kaynak çiftini karşılaştırır; uyuşmazlık = bulgu. Düzeltme her zaman **kaynak** tarafta yapılır (config/hesap/netlist), belge ona göre güncellenir.

- [x] **Step 1: Araç ölçüleri** — `config/vehicle.json` değerleri (dış zarf, teker Ø, iz, dingil, gövde üstü) ile `README.md`, `docs/mechanical_architecture.md`, `docs/system_requirements.md`, `cad/assembly/manifest.json`.
Run: `python3 -c "import json;print(json.dumps(json.load(open('config/vehicle.json')),indent=1))" | head -80` ve `grep -n -E "330|270|Ø120|240|210|146" README.md docs/mechanical_architecture.md docs/system_requirements.md`

- [x] **Step 2: Kütle ve CG** — `docs/mass_budget.md`, `docs/drivetrain_trade_D2.md` (5,933 kg), `docs/body_mass_screen_A1.md` (738,6 g), `README.md`, `docs/design_decisions.md` DD01/DD26/DD28/DD50.
Run: `grep -n -E "5[,.]9|6[,.]0|kg|rezerv|738|700 g" docs/mass_budget.md docs/drivetrain_trade_D2.md docs/body_mass_screen_A1.md README.md | head -60`

- [x] **Step 3: Güç bütçesi** — `docs/electrical_architecture.md` §6 toplamları (62,07/105,32 W, 63,2/107,4 W, 227,2 W, 18,3 A) ile `docs/calculation_results.md` ve `tools/calculations.py` girdileri.
Run: `grep -n -E "W|A\b" docs/calculation_results.md | head -40`

- [x] **Step 4: Pin ve arayüz** — `config/mcu_pinmap.json` (53 atama) ↔ `docs/mcu_pinmap_review.md` ↔ `docs/pwr_mcu_interface.md` J-SIG tablosu ↔ `config/pwr_mcu_connector.json` ↔ KiCad arayüz sayfaları (`tests/check_board_interface_sheets.py` zaten netleri denetler; burada belge tablosunun JSON'la aynı olduğu kontrol edilir).
Run: `python3 -c "import json;d=json.load(open('config/mcu_pinmap.json'));print(len(d['assignments']))"` ve J-SIG satırlarını JSON ile satır satır karşılaştır.

- [x] **Step 5: BOM** — `manufacturing/bom/initial_bom.csv` V1 satır toplamı ile `docs/initial_bom.md` (1999 USD, %30 pay 2599), README "≈1.999 USD" ve BOM satır sayısı ("36 satır").
Run:
```bash
python3 - <<'EOF'
import csv
rows = list(csv.DictReader(open("manufacturing/bom/initial_bom.csv")))
v1 = sum(float(r["quantity"]) * float(r["estimated_unit_usd"]) for r in rows if r["cost_scope"] == "V1")
print(len(rows), "rows; V1 total", v1)
EOF
```

- [x] **Step 6: Durum ifadeleri** — PWR/K1/K2/test sayıları ve “yok/çizilmedi” ifadelerinin 24.09 PWR sayfalarıyla çelişmediği.
Run: `grep -rn -i -E "henüz çizilmedi|şematiği yok|0 hata|ERC" README.md docs/*.md electronics/*/README.md | grep -v design_review_2026`
Her eşleşmeyi [pwr_safety_path.md](../../pwr_safety_path.md) durumuyla karşılaştır.

- [x] **Step 7: A2 işaretleri** — A1 ön kamera podu, tek RGB kamera, 2 servo BOM satırı (B15), “çift göz ertelendi” ifadeleri: düzeltme yapma, rapora `A2'DE DEĞİŞİYOR` yaz.
Run: `grep -rn -i -E "ön kamera|front camera|çift göz|B15|sonraki revizyon" README.md docs/*.md manufacturing/bom/initial_bom.csv | head -40`

### Task 4: Rapor, karar ve faz kaydı

**Files:**
- Create: `docs/design_review_2026-09-24.md`
- Modify: `docs/design_decisions.md`, `docs/phase_reviews.md`, `README.md` (rapor bağlantısı)

- [x] **Step 1: Raporu yaz** — başlık, kapsam, taban (Task 2 sonuçları), bulgu tablosu:

```markdown
| ID | Kaynak | Hata | Düzeltme | Kanıt | Durum |
|---|---|---|---|---|---|
| R01 | docs/x.md:12 | örnek biçim satırı | örnek | komut/test çıktısı | DÜZELTİLDİ |
```

- [x] **Step 2: Karar gerektiren her bulgu için `design_decisions.md` sonuna DD maddesi ekle; `phase_reviews.md` sonuna “Genel tasarım denetimi — 24.09.2026” bölümü (bulgu sayısı, düzeltilen, A2'ye devreden, açık kalan; T01–T20 NOT_RUN).**

- [x] **Step 3: Doğrulama** — Task 2 Step 2 test listesini ve `python3 tests/check_markdown_links.py`'yi tekrar çalıştır.
Expected: hepsi PASS.
