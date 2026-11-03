# CV & Services Profile — Moain Al-Abbasi

| File | Purpose |
|---|---|
| `output/cv_en.pdf` | English CV (2 pages, A4, ATS-friendly single column) |
| `output/cv_ar.pdf` | Arabic CV (2 pages, RTL) |
| `output/services_ar.pdf` | One-page Arabic services profile for client outreach |

Sources are plain HTML/CSS in `src/`. Rebuild PDFs:

```bash
pip install playwright && python -m playwright install chromium
python cv/render.py            # all files
python cv/render.py cv_en.html # one file
```

Fonts: IBM Plex Sans (Latin) + Noto Naskh Arabic (Arabic), static files under the SIL Open Font License in `fonts/`.
Both embed as CID TrueType, so ATS parsers read real text.

## Quality gates (run after every change)

```bash
python cv/render.py && python cv/audit/measure.py
python cv/audit/standards.py   # 14 published rules x 3 files; exits 1 on any failure
python cv/audit/fidelity.py    # every source word must survive PDF text extraction
```

`audit/standards.py` checks body size 10-12 pt, margins >= 0.5 in, <= 5 type sizes, headings >= 1.15x body,
line height >= 1.4, <= 100 chars/line, WCAG contrast >= 4.5:1, page count, embedded fonts, tagged PDF, /Lang and title.
