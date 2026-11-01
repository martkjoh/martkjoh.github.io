# martkjoh.github.io

Personal page - [mkjohnsrud.com](https://mkjohnsrud.com)

Plain HTML and CSS on GitHub Pages, with no build step: push to `main` and the site updates.

- **Shared head and header:** edit `scripts/head.html` or `scripts/header.html`, then run `python scripts/update_header.py` to copy them into every page.
- **Publications:** run `python scripts/update_publications.py` to fetch the list from ORCID.
- **Research directions:** one file each in `research/`, loaded into the Research page by `include.js`.
- **Maths:** LaTeX works on every page via KaTeX: `$...$` inline, `$$...$$` displayed.
