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
        fenced = False
        for number, line in enumerate(md.read_text(errors="replace").splitlines(), 1):
            if line.lstrip().startswith("```"):
                fenced = not fenced
            if fenced:
                continue
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
    (base / "b.md").write_text("[up](a.md)\n```md\n[example](inside_fence.md)\n```\n")
    assert broken_links(base) == ["a.md:1: missing.md#x"], broken_links(base)

bad = broken_links(ROOT)
assert not bad, "\n".join(bad)
print("PASS: every relative Markdown link resolves")
