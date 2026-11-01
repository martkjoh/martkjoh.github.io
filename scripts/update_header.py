"""Copy the shared head and header into every page.

Edit scripts/head.html or scripts/header.html, then run:  python scripts/update_header.py
Only the parts between the HEAD START/END and HEADER START/END comments are
replaced. The menu link to the page itself gets class="active".
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PAGES = ["index.html", "pages/research.html", "pages/publications.html", "pages/teaching.html"]


def fill(page, name, block, path):
    """Replace whatever is between <!-- NAME START ... --> and <!-- NAME END --> with block."""
    pattern = rf"(<!-- {name} START.*?-->\n).*?([ \t]*<!-- {name} END -->)"
    new, n = re.subn(pattern, lambda m: m.group(1) + block + m.group(2), page, flags=re.S)
    if n != 1:
        raise SystemExit(f"Could not find the {name} START / {name} END comments in {path.name}")
    return new


head = (HERE / "head.html").read_text(encoding="utf-8")
header = (HERE / "header.html").read_text(encoding="utf-8")

for name in PAGES:
    path = ROOT / name
    page = path.read_text(encoding="utf-8")
    link = "/" if name == "index.html" else "/" + name
    this_header = header.replace(f'<a href="{link}">', f'<a href="{link}" class="active">')
    page = fill(page, "HEAD", head, path)
    page = fill(page, "HEADER", this_header, path)
    path.write_text(page, encoding="utf-8", newline="\n")
    print("Updated", name)
