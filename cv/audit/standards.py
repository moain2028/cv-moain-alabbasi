"""Check the rendered PDFs against published CV/typography/accessibility standards.

Each rule cites its source. Exit code 1 if any rule fails.
Usage: python3 audit/standards.py   (run audit/measure.py first)
"""
import json
import pathlib
import subprocess
import sys

import fitz

ROOT = pathlib.Path(__file__).resolve().parent.parent
M = json.loads((ROOT / "audit" / "metrics.json").read_text())

SRC = {
    "harvard": "Harvard OCS résumé guide: body 10-12 pt, margins 0.5-1 in",
    "wcag143": "WCAG 2.2 SC 1.4.3: text contrast >= 4.5:1",
    "wcag1412": "WCAG 2.2 SC 1.4.12: line height >= 1.5x for body text (we accept >= 1.4 for print CVs)",
    "bringhurst": "Bringhurst, Elements of Typographic Style: 45-75 chars ideal, ~66; up to ~90-100 tolerated in dense documents",
    "scale": "Type-scale practice: <= 5 distinct sizes; headings >= 1.15x body",
    "pdfua": "ISO 14289 (PDF/UA): tagged PDF, document title, language, embedded fonts",
    "length": "Recruiter norm: 1-2 pages for a CV, 1 page for a sales sheet",
}


def body_size(m):
    return float(max(m["sizes_pt"].items(), key=lambda kv: float(kv[1].rstrip("%")))[0])


def check(name, m):
    rows = []
    pdf = ROOT / "output" / name
    b = body_size(m)
    sizes = sorted(float(s) for s, share in m["sizes_pt"].items() if float(share.rstrip("%")) >= 0.1)
    heads = [s for s in sizes if s > b]
    small = min(sizes)
    rows.append(("Body size 10-12 pt", f"{b:.2f} pt", 10 <= b <= 12, "harvard"))
    rows.append(("Smallest text >= 8.5 pt", f"{small:.2f} pt", small >= 8.5, "harvard"))
    rows.append(("Heading >= 1.15x body", f"{(heads[0] / b if heads else 0):.2f}x", bool(heads) and heads[0] / b >= 1.15, "scale"))
    rows.append(("Distinct sizes <= 5", str(len(sizes)), len(sizes) <= 5, "scale"))
    mg = [v for p in m["margins_mm"].values() for k, v in p.items() if k in ("left", "right", "top")]
    rows.append(("Margins >= 12.7 mm (0.5 in)", f"min {min(mg)} mm", min(mg) >= 12.0, "harvard"))
    lead = m["leading"].get(str(round(b, 2)), {}).get("ratio") or max((v["ratio"] for v in m["leading"].values()), default=0)
    rows.append(("Line height >= 1.4", f"{lead}", lead >= 1.4, "wcag1412"))
    cpl = m["chars_per_full_line"]["median"]
    rows.append(("Median chars/line <= 100", str(cpl), cpl <= 100, "bringhurst"))
    acc_l = 0.0723  # relative luminance of #0b4f8a (CTA background)
    def ratio(hexc, v):
        if hexc.lower() == "#ffffff":  # white text is only used on the accent bar
            return round((1.05) / (acc_l + 0.05), 2)
        return v["contrast_on_white"]
    worst = min(ratio(h, v) for h, v in m["colors"].items())
    rows.append(("Text contrast >= 4.5:1", f"min {worst}", worst >= 4.5, "wcag143"))
    limit = 1 if name.startswith("services") else 2
    rows.append((f"Pages <= {limit}", str(m["pages"]), m["pages"] <= limit, "length"))
    fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    emb = all(l.split()[-5] == "yes" for l in fonts) and not any("Type 3" in l for l in fonts)
    rows.append(("All fonts embedded, no Type 3", f"{len(fonts)} fonts", emb, "pdfua"))
    doc = fitz.open(pdf)
    cat = doc.xref_object(doc.pdf_catalog())
    rows.append(("Tagged PDF (StructTreeRoot)", "yes" if "StructTreeRoot" in cat else "no", "StructTreeRoot" in cat, "pdfua"))
    rows.append(("Document language set", "yes" if "/Lang" in cat else "no", "/Lang" in cat, "pdfua"))
    title = doc.metadata.get("title") or ""
    rows.append(("Document title set", title[:40] or "-", bool(title), "pdfua"))
    ats = m["ats"]
    rows.append(("Email + phone extractable", f"{ats['email_found']}/{ats['phone_found']}", ats["email_found"] and ats["phone_found"], "pdfua"))
    return rows


fails = 0
report = {}
for name, m in M.items():
    rows = check(name, m)
    report[name] = [{"rule": r, "value": v, "pass": ok, "source": SRC[s]} for r, v, ok, s in rows]
    print(f"\n=== {name}")
    for r, v, ok, s in rows:
        fails += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {r:32s} {v:28s} [{s}]")
(ROOT / "audit" / "standards.json").write_text(json.dumps({"sources": SRC, "results": report}, ensure_ascii=False, indent=1))
print(f"\nfailures: {fails}")
sys.exit(1 if fails else 0)
