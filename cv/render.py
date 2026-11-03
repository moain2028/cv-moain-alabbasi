"""Render the HTML sources in cv/src to PDF (A4) with headless Chromium."""
import pathlib
import sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "output"
OUT.mkdir(exist_ok=True)

files = sys.argv[1:] or [p.name for p in SRC.glob("*.html")]
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    for name in files:
        src = SRC / name
        page.goto(src.as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        pdf = OUT / (src.stem + ".pdf")
        page.pdf(path=str(pdf), format="A4", print_background=True, prefer_css_page_size=True,
                 tagged=True, outline=True)  # tagged = PDF/UA structure + /Lang from <html lang>
        print("wrote", pdf)
    browser.close()
