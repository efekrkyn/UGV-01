"""Builds media/film/out/film.html: the real CAD meshes (tools/build_viewer.py export), timeline.json and the check
list from tests/README.md, filled into film_template.html. Run with the CAD venv: ../../.venv/bin/python build_film.py"""
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_viewer import build  # noqa: E402

page, meta = build(HERE / 'film_template.html')
readme = (ROOT / 'tests/README.md').read_text()
checks = list(dict.fromkeys(Path(m).name for m in re.findall(r'((?:tests|software/web_ui)/[\w./-]+?\.(?:py|c|mjs))\b', readme)))
checks += [name for key, name in (('lite/esp32 && idf.py', 'ESP32-S3 firmware build'), ('lite/eye', 'ESP32-CAM eye build'))
           if key in readme]
page = page.replace('__TIMELINE__', (HERE / 'timeline.json').read_text()).replace('__CHECKS__', json.dumps(checks))
out = HERE / 'out'
out.mkdir(exist_ok=True)
(out / 'film.html').write_text(page)
print(f'{out / "film.html"}: {len(meta["parts"])} parts, {len(checks)} checks')
