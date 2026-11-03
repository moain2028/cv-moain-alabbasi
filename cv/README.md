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
python cv/audit/fidelity.py    # every source word survives extraction, and no split/mirrored tokens appear
```

`audit/standards.py` checks body size 10-12 pt, bottom edge >= 8 mm (printable), margins >= 0.5 in, <= 5 type sizes, headings >= 1.15x body,
line height >= 1.4, <= 100 chars/line, WCAG contrast >= 4.5:1, page count, embedded fonts, tagged PDF, /Lang and title.

## Review process

- `audit/facts.md` is the ground truth. Every claim in the CVs must be traceable to a repo README or to the candidate.
- `audit/reviewers.py <round>` runs eight parallel reviewers (claude-opus-5-5, claude-fable-5-1, gpt-6-astra) on the
  rendered pages; results are kept in `audit/rev_<round>_*.json`. Rounds r1 -> r3 raised every score from 5-6 to 7/10.
- Needs `OPENAI_API_KEY` and `OPENAI_BASE_URL` in the environment; the key is never written to disk.

Not committed on purpose (see `/.gitignore`): tokens, the WhatsApp export, repo-migration work files, scratch builds.
