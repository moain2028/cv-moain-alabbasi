"""Deterministic typography / layout / ATS measurements for the CV PDFs.

Everything here is measured from the PDF itself (PyMuPDF), not estimated.
Output: audit/metrics.json + a readable summary on stdout.
"""
import json
import pathlib
import re
import statistics as st
import subprocess
import sys
from collections import Counter, defaultdict

import fitz  # PyMuPDF

ROOT = pathlib.Path(__file__).resolve().parent.parent
PT_PER_MM = 72 / 25.4

# Weak openers and filler that recruiters/ATS guides flag.
WEAK = ["responsible for", "worked on", "helped", "various", "etc", "hard-working",
        "team player", "passionate", "synergy", "detail-oriented", "results-driven"]
STRONG_VERBS = {"built", "delivered", "replaced", "modernising", "modernized", "designed", "led",
                "shipped", "migrated", "reduced", "increased", "automated", "launched", "maintain",
                "developed", "implemented", "architected", "created", "integrated"}


def rel_luminance(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(c1, c2=(255, 255, 255)):
    l1, l2 = sorted([rel_luminance(c1), rel_luminance(c2)], reverse=True)
    return round((l1 + 0.05) / (l2 + 0.05), 2)


def int_to_rgb(i):
    return ((i >> 16) & 255, (i >> 8) & 255, i & 255)


def measure(pdf_path: pathlib.Path):
    doc = fitz.open(pdf_path)
    out = {"file": pdf_path.name, "pages": doc.page_count, "page_size_mm": None,
           "fonts": {}, "sizes_pt": {}, "colors": {}, "margins_mm": {}, "pages_detail": []}
    size_chars = Counter()
    font_chars = Counter()
    color_chars = Counter()
    line_gaps = defaultdict(list)          # font size -> baseline gaps (leading)
    line_widths_chars = []
    all_lines = []

    for pno, page in enumerate(doc):
        W, H = page.rect.width, page.rect.height
        out["page_size_mm"] = [round(W / PT_PER_MM, 1), round(H / PT_PER_MM, 1)]
        d = page.get_text("dict")
        xs0, xs1, ys0, ys1 = [], [], [], []
        prev = None
        for b in d["blocks"]:
            if b.get("type") != 0:
                continue
            for ln in b["lines"]:
                spans = [s for s in ln["spans"] if s["text"].strip()]
                if not spans:
                    continue
                text = "".join(s["text"] for s in ln["spans"]).strip()
                x0, y0, x1, y1 = ln["bbox"]
                xs0.append(x0); xs1.append(x1); ys0.append(y0); ys1.append(y1)
                main = max(spans, key=lambda s: len(s["text"]))
                size = round(main["size"], 2)
                origin_y = main["origin"][1]
                for s in spans:
                    n = len(s["text"].strip())
                    size_chars[round(s["size"], 2)] += n
                    font_chars[s["font"]] += n
                    color_chars[s["color"]] += n
                if prev and prev[0] == pno and prev[1] == size and 0 < origin_y - prev[2] < size * 2.2:
                    line_gaps[size].append(round(origin_y - prev[2], 2))
                prev = (pno, size, origin_y)
                all_lines.append({"page": pno + 1, "size": size, "text": text,
                                  "width_pct": round((x1 - x0) / W * 100, 1)})
                line_widths_chars.append(len(text))
        if xs0:
            out["margins_mm"][f"p{pno+1}"] = {
                "left": round(min(xs0) / PT_PER_MM, 1), "right": round((W - max(xs1)) / PT_PER_MM, 1),
                "top": round(min(ys0) / PT_PER_MM, 1), "bottom": round((H - max(ys1)) / PT_PER_MM, 1),
            }
            used = (max(ys1) - min(ys0)) / (H - 2 * min(ys0)) * 100
            out["pages_detail"].append({"page": pno + 1, "vertical_fill_pct": round(used, 1),
                                        "lines": sum(1 for l in all_lines if l["page"] == pno + 1)})

    total = sum(size_chars.values())
    out["fonts"] = {f: f"{c/total*100:.1f}%" for f, c in font_chars.most_common()}
    out["sizes_pt"] = {str(s): f"{c/total*100:.1f}%" for s, c in sorted(size_chars.items())}
    out["colors"] = {"#%02x%02x%02x" % int_to_rgb(c): {"share": f"{n/total*100:.1f}%",
                     "contrast_on_white": contrast(int_to_rgb(c))} for c, n in color_chars.most_common()}
    out["leading"] = {str(s): {"median_pt": st.median(g), "ratio": round(st.median(g) / s, 2), "n": len(g)}
                      for s, g in line_gaps.items() if len(g) >= 3}
    body_lines = [n for n in line_widths_chars if n > 40]
    out["chars_per_full_line"] = {"median": st.median(body_lines) if body_lines else 0,
                                  "max": max(body_lines) if body_lines else 0}
    out["distinct_sizes"] = len(size_chars)
    out["text_chars"] = total
    out["_lines"] = all_lines
    return out


def text_checks(pdf_path: pathlib.Path):
    """What an ATS sees: plain extraction order + content heuristics."""
    raw = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True).stdout
    res = {}
    res["email_found"] = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", raw))
    res["phone_found"] = bool(re.search(r"\+?\d[\d\s]{8,}\d", raw))
    res["broken_words"] = re.findall(r"\b[A-Z] [A-Z]{2,}\b", raw)[:10]  # e.g. "T ECHNICAL"
    res["ligature_or_pua"] = sorted({c for c in raw if 0xE000 <= ord(c) <= 0xF8FF or c in "\ufb00\ufb01\ufb02"})
    res["words"] = len(re.findall(r"\w+", raw))
    lower = raw.lower()
    res["weak_phrases"] = [w for w in WEAK if w in lower]
    bullets = [b.strip() for b in re.split(r"\n(?=[•▪◦\-–])|\n\s*\n", raw) if b.strip()]
    res["first_word_counts"] = Counter(
        b.split()[0].lower().strip("•▪-–") for b in bullets if b.split()).most_common(8)
    res["section_order"] = [l.strip() for l in raw.splitlines() if re.fullmatch(r"[A-Z &]{5,}", l.strip())]
    return res, raw


def main():
    files = sys.argv[1:] or ["cv_en.pdf", "cv_ar.pdf", "services_ar.pdf"]
    report = {}
    for name in files:
        p = ROOT / "output" / name
        m = measure(p)
        tc, raw = text_checks(p)
        m["ats"] = tc
        lines = m.pop("_lines")
        # Widows: last line of a paragraph with <= 2 words (Latin only, meaningful for EN)
        m["short_tail_lines"] = [l["text"] for l in lines if 0 < len(l["text"].split()) <= 2
                                 and l["size"] < 10 and not l["text"].endswith(":") and l["width_pct"] < 12][:15]
        report[name] = m
        (ROOT / "audit" / f"{p.stem}.txt").write_text(raw)
    (ROOT / "audit" / "metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    for name, m in report.items():
        print(f"\n=== {name}  pages={m['pages']}  size={m['page_size_mm']}mm  chars={m['text_chars']}")
        print(" fonts:", m["fonts"])
        print(" sizes:", m["sizes_pt"], "| distinct:", m["distinct_sizes"])
        print(" leading:", m["leading"])
        print(" margins:", m["margins_mm"])
        print(" fill:", m["pages_detail"])
        print(" colors:", m["colors"])
        print(" chars/line:", m["chars_per_full_line"])
        print(" ats:", {k: v for k, v in m["ats"].items() if k != "first_word_counts"})
        print(" first words:", m["ats"]["first_word_counts"])
        print(" short tails:", m["short_tail_lines"])


if __name__ == "__main__":
    main()
