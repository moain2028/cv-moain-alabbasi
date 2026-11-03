"""Render the HTML sources in cv/src to PDF (A4) with headless Chromium."""
import pathlib
import sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "output"
OUT.mkdir(exist_ok=True)

# Wrap every hyphenated token (multi-tenant, offline-first, mohanad-web-app-2) in a nowrap span.
# pdftotext drops a hyphen that falls at a line end, so "multi-tenant" became "multitenant".
NO_HYPHEN_BREAK = r"""() => {
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = []; while (w.nextNode()) nodes.push(w.currentNode);
  for (const n of nodes) {
    if (!/\S-\S/.test(n.data) || n.parentElement.closest('.nowrap,style,script')) continue;
    const frag = document.createDocumentFragment();
    for (const part of n.data.split(/(\S+-\S+)/)) {
      if (!part) continue;
      if (/\S-\S/.test(part)) { const s = document.createElement('span'); s.className = 'nowrap'; s.textContent = part; frag.appendChild(s); }
      else frag.appendChild(document.createTextNode(part));
    }
    n.replaceWith(frag);
  }
}"""

files = sys.argv[1:] or [p.name for p in SRC.glob("*.html")]
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    for name in files:
        src = SRC / name
        page.goto(src.as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        page.evaluate(NO_HYPHEN_BREAK)
        pdf = OUT / (src.stem + ".pdf")
        page.pdf(path=str(pdf), format="A4", print_background=True, prefer_css_page_size=True,
                 tagged=True, outline=True)  # tagged = PDF/UA structure + /Lang from <html lang>
        print("wrote", pdf)
    browser.close()
