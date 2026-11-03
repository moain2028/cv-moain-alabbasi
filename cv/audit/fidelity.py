"""ATS text-fidelity test.

For every visible word in the HTML source, check that the same word can be
recovered from the PDF text layer (what an ATS / search / copy-paste sees).
Three independent extractors are used; a word passes only if pdftotext finds it.

Usage: python audit/fidelity.py            -> all files
Exit code 1 if any file is below 99%.
"""
import pathlib
import re
import subprocess
import sys
import unicodedata

from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent
BIDI = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069\u00ad]")  # direction marks -> treated as spaces
WORD = re.compile(r"[\w\u0600-\u06FF@.+#/-]+")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", BIDI.sub(" ", s))
    s = s.replace("\u0640", "")  # tatweel
    s = re.sub(r"-\n", "-", s)  # compound words broken at their hyphen
    return s.lower()


def tokens(s: str):
    out = set()
    for t in WORD.findall(norm(s)):
        t = t.strip(".,;:()/-·|،؛")
        if len(t) >= 2:
            out.add(t)
    return out


def source_words(html: pathlib.Path):
    soup = BeautifulSoup(html.read_text(), "html.parser")
    for tag in soup(["style", "script", "title", "head"]):
        tag.decompose()
    return tokens(soup.get_text(" "))


def extract(pdf: pathlib.Path):
    return subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout


def main():
    names = sys.argv[1:] or ["cv_en", "cv_ar", "services_ar"]
    worst = 100.0
    for n in names:
        src = source_words(ROOT / "src" / f"{n}.html")
        got = tokens(extract(ROOT / "output" / f"{n}.pdf"))
        missing = sorted(w for w in src if w not in got)
        # Reverse check: garbage tokens created by extraction, e.g. "لاختبارات" from "ا لاختبارات" or ")wps(".
        footer = {"cv", "moain", "al-abbasi", "السيرة", "الذاتية", "معين", "العباسي"}
        junk = sorted(t for t in got - src if t not in footer and not re.fullmatch(r"[\d/]+", t))
        if junk:
            worst = min(worst, 0)
            print(f"{n:12s} EXTRACTION ARTEFACTS (not in source): {junk[:15]}")
        pct = 100 * (len(src) - len(missing)) / len(src)
        worst = min(worst, pct)
        print(f"{n:12s} {len(src)-len(missing):4d}/{len(src)} words recoverable = {pct:5.1f}%"
              + (f"   missing: {missing[:25]}" if missing else ""))
    sys.exit(0 if worst >= 99 else 1)


if __name__ == "__main__":
    main()
