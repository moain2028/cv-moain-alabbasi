"""Root-cause check for broken Arabic text extraction.

Chromium/Skia writes ONE Unicode value per glyph into the PDF ToUnicode map.
If a font reuses the same glyph for different letters (e.g. a dotless base
shared by ب ت ث ن ي, with the dots as separate mark glyphs), every later
letter that reuses that glyph is extracted as the first letter seen.

This script shapes the real CV text with HarfBuzz and counts glyphs that
stand for more than one character sequence. Zero means extraction can be exact.
"""
import re, sys, pathlib
from collections import defaultdict
import uharfbuzz as hb
from bs4 import BeautifulSoup

def ambiguity(font_path, text, features=None):
    blob = hb.Blob.from_file_path(font_path); face = hb.Face(blob); font = hb.Font(face)
    g2s = defaultdict(set)
    for run in re.findall(r"[\u0600-\u06FF\u0660-\u0669\u064B-\u065F]+(?:\s+[\u0600-\u06FF\u0660-\u0669]+)*", text):
        buf = hb.Buffer(); buf.add_str(run); buf.guess_segment_properties()
        hb.shape(font, buf, features or {})
        infos = buf.glyph_infos
        clusters = sorted({i.cluster for i in infos}) + [len(run)]
        nxt = {c: clusters[k + 1] for k, c in enumerate(clusters[:-1])}
        per_cluster = defaultdict(list)
        for i in infos: per_cluster[i.cluster].append(i.codepoint)
        for c, gids in per_cluster.items():
            chars = run[c:nxt[c]]
            if len(gids) == 1:
                g2s[gids[0]].add(chars)
            else:  # base + marks inside one cluster: each glyph only knows the cluster
                for g in gids: g2s[g].add("<cl>" + chars)
    amb = {g: s for g, s in g2s.items() if len({x.replace("<cl>", "") for x in s}) > 1}
    return len(g2s), amb

if __name__ == "__main__":
    html = pathlib.Path(sys.argv[1]).read_text()
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["style", "head"]): t.decompose()
    text = soup.get_text(" ")
    for fp in sys.argv[2:]:
        n, amb = ambiguity(fp, text)
        ex = list(amb.items())[:3]
        print(f"{pathlib.Path(fp).name:34s} glyphs={n:4d} ambiguous={len(amb):3d}  e.g. {[sorted(v)[:4] for k,v in ex]}")
