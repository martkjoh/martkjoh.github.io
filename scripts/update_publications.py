"""Fill publications.html with the works listed on ORCID.

Run from the repo folder:  python scripts/update_publications.py

Only the part of publications.html between the ORCID START and ORCID END
comments is replaced; everything else on the page is left alone.
"""

import html
import json
import re
import urllib.request
from pathlib import Path

ORCID_ID = "0000-0001-8460-7149"
MY_NAME = "Martin Kjøllesdal Johnsrud"  # shown in bold in author lists
PAGE = Path(__file__).resolve().parent.parent / "pages" / "publications.html"
API = f"https://pub.orcid.org/v3.0/{ORCID_ID}"


def get(path):
    req = urllib.request.Request(API + path, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as res:
        return json.load(res)


def text(obj, *keys):
    """Safely read nested ORCID fields like obj['title']['title']['value']."""
    for k in keys:
        if not isinstance(obj, dict) or obj.get(k) is None:
            return ""
        obj = obj[k]
    return obj


def fetch_works():
    put_codes = [str(g["work-summary"][0]["put-code"]) for g in get("/works")["group"]]
    works = []
    for i in range(0, len(put_codes), 100):  # ORCID allows up to 100 per request
        for item in get("/works/" + ",".join(put_codes[i:i + 100]))["bulk"]:
            w = item["work"]
            doi = next((e["external-id-value"] for e in text(w, "external-ids", "external-id") or []
                        if e["external-id-type"] == "doi"), "")
            works.append({
                "title": text(w, "title", "title", "value"),
                "type": w.get("type", ""),
                "journal": text(w, "journal-title", "value"),
                "year": text(w, "publication-date", "year", "value"),
                # Full date as "YYYY-MM-DD" (missing parts become 00), used for sorting
                "date": "-".join(text(w, "publication-date", part, "value") or "00"
                                 for part in ("year", "month", "day")),
                "url": text(w, "url", "value") or (f"https://doi.org/{doi}" if doi else ""),
                "authors": [text(c, "credit-name", "value")
                            for c in text(w, "contributors", "contributor") or []],
            })
    return works


def norm(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())


def render(work):
    authors = ", ".join(
        f"<b>{html.escape(a)}</b>" if a == MY_NAME else html.escape(a)
        for a in work["authors"] if a
    )
    title = html.escape(work["title"])
    if work["url"]:
        title = f'<a href="{html.escape(work["url"])}">{title}</a>'
    venue = html.escape(work["journal"] or ("arXiv" if "arxiv" in work["url"] else "Preprint"))
    year = f" ({work['year']})" if work["year"] else ""
    lines = [title] + ([authors] if authors else []) + [f"<em>{venue}</em>{year}"]
    return "        <li>\n            " + "<br>\n            ".join(lines) + "\n        </li>"


def main():
    works = sorted(fetch_works(), key=lambda w: w["date"], reverse=True)
    articles = [w for w in works if w["type"] == "journal-article"]
    published = {norm(w["title"]) for w in articles}
    # Hide preprints that have since been published under the same title
    preprints = [w for w in works if w["type"] != "journal-article" and norm(w["title"]) not in published]

    parts = []
    for heading, items in [("Journal articles", articles), ("Preprints", preprints)]:
        if items:
            parts.append(f"    <h3>{heading}</h3>\n    <ol class=\"publications\" reversed>\n"
                         + "\n".join(render(w) for w in items) + "\n    </ol>")
    block = "\n\n".join(parts)

    page = PAGE.read_text(encoding="utf-8")
    new, n = re.subn(r"(<!-- ORCID START.*?-->\n).*?([ \t]*<!-- ORCID END -->)",
                     lambda m: m.group(1) + block + "\n" + m.group(2), page, flags=re.S)
    if n != 1:
        raise SystemExit("Could not find the ORCID START / ORCID END comments in publications.html")
    PAGE.write_text(new, encoding="utf-8", newline="\n")
    print(f"Wrote {len(articles)} articles and {len(preprints)} preprints to {PAGE.name}")


if __name__ == "__main__":
    main()
