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

Fonts: IBM Plex Sans Arabic + Inter (SIL Open Font License), bundled in `fonts/`.
