"""Parallel expert review of the CV PDFs by several frontier models.

Each reviewer gets: rendered page images, the exact text an ATS extracts,
deterministic layout metrics, and the verified-facts sheet. Each must return
strict JSON so findings can be merged and adjudicated.

Usage: python audit/reviewers.py [round_name]
Key/base URL come from the environment (OPENAI_API_KEY / OPENAI_BASE_URL).
"""
import base64
import concurrent.futures as cf
import json
import os
import pathlib
import re
import sys
import time

from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parent.parent
AUD = ROOT / "audit"
ROUND = sys.argv[1] if len(sys.argv) > 1 else "r1"
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.environ["OPENAI_BASE_URL"], timeout=480, max_retries=0)

FACTS = (AUD / "facts.md").read_text()
METRICS = json.loads((AUD / "metrics.json").read_text())

SCHEMA = """Return ONLY a JSON object, no prose, in this exact shape:
{"verdict": "one sentence overall judgement",
 "score_10": <integer 1-10>,
 "issues": [
   {"file": "cv_en|cv_ar|services_ar",
    "where": "section or quoted text so it can be found",
    "severity": "critical|major|minor",
    "category": "content|fact|language|ats|layout|typography|strategy",
    "problem": "what is wrong and why it matters to the reader",
    "fix": "exact replacement text or exact CSS/layout change"}
 ]}
Rules: be specific and quote the text. No generic advice. Never propose adding a fact, number,
employer, degree or date that is not in the VERIFIED FACTS sheet. If something is unverifiable, say so.
Max 18 issues, most important first."""


def img(path):
    return {"type": "image_url",
            "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()}}


def pages(stem):
    return sorted((AUD / "pages").glob(f"{stem}-*.jpg"))


def text(stem):
    return (AUD / f"{stem}.txt").read_text()


REVIEWERS = [
    {"id": "recruiter_intl", "model": "claude-opus-5-5", "files": ["cv_en"],
     "role": "You are a senior technical recruiter who has screened 20,000+ software-engineer CVs for "
             "remote roles at international product companies and agencies. You know how Greenhouse, Lever, "
             "Workday and Taleo parse PDFs and how a recruiter reads a CV in 7 seconds.",
     "task": "Review the English CV for a remote Software Engineer / AI Engineer role. Judge the 7-second "
             "scan, title and summary, bullet impact (action + scope + result), keyword coverage for "
             "full-stack + AI-agent + security roles, credibility risks (anything that sounds inflated or "
             "vague), section order, length, and what would make a hiring manager reject it."},
    {"id": "hr_saudi", "model": "gpt-6-astra", "files": ["cv_ar", "services_ar"],
     "role": "You are an HR manager and procurement lead at a mid-size Saudi company (Jeddah/Riyadh) who "
             "hires and outsources software work. You read Arabic CVs and vendor profiles daily.",
     "task": "Review the Arabic CV and the Arabic services profile as a Saudi decision-maker deciding whether "
             "to hire this remote engineer from Yemen or give him a project. Judge trust signals, clarity, "
             "professional tone in Arabic, what is missing for you to say yes, anything that raises a red "
             "flag, and whether the services profile reads like a credible vendor."},
    {"id": "typographer", "model": "claude-fable-5-1", "files": ["cv_en", "cv_ar", "services_ar"],
     "role": "You are a senior editorial designer and typographer specialised in bilingual Latin/Arabic "
             "documents and résumé design. You judge hierarchy, rhythm, whitespace, alignment, measure "
             "(characters per line), leading, contrast, and RTL/LTR mixing.",
     "task": "Review all pages pixel by pixel using the images AND the measured metrics. Comment on: font "
             "choice and pairing (Latin IBM Plex Sans + Arabic Noto Naskh Arabic), type scale, leading, "
             "line length, margins, vertical rhythm, page balance (page 2 fill), header design, separators, "
             "bullet alignment, RTL punctuation and mixed-direction runs, widows/orphans, colour use. Give "
             "exact CSS values to change. Note: the Arabic font was chosen because it is the only tested font "
             "whose text layer extracts 100% correctly; propose an alternative only if you also explain how "
             "text extraction would stay correct."},
    {"id": "fact_checker", "model": "claude-opus-5-5", "files": ["cv_en", "cv_ar", "services_ar"],
     "role": "You are a meticulous fact-checker and due-diligence analyst.",
     "task": "Compare EVERY claim, number, technology, date, project name and link in all three documents "
             "against the VERIFIED FACTS sheet. Flag: claims not supported, numbers that differ, wording that "
             "overstates what the facts say (e.g. 'delivered' vs 'in progress'), inconsistencies between the "
             "English and Arabic versions, and anything an interviewer could catch as exaggeration."},
    {"id": "arabic_editor", "model": "claude-fable-5-1", "files": ["cv_ar", "services_ar"],
     "role": "You are a senior Arabic copy editor (Modern Standard Arabic, business and technical register) "
             "who edits professional CVs for the Gulf market.",
     "task": "Edit the Arabic text line by line: grammar, agreement, prepositions, punctuation (Arabic comma, "
             "spacing around Latin terms), word choice, colloquialisms, awkward literal translations, "
             "consistency of terminology (e.g. one term for 'system', 'agent', 'tests'), and tone. Diacritics "
             "were deliberately removed for PDF text extraction; do not ask to add them back. Give the exact "
             "corrected sentence for each issue."},
    {"id": "eng_lead", "model": "gpt-6-astra", "files": ["cv_en"],
     "role": "You are a principal engineer and hiring manager who interviews senior full-stack and AI "
             "engineers. You know what real NestJS/Go/LangGraph/MCP/Wazuh work looks like.",
     "task": "Review the English CV for technical credibility and depth. Which bullets would impress you, "
             "which sound like buzzwords, which claims you would probe in an interview, what technical "
             "signal is missing (architecture, scale, trade-offs, testing, security), and whether the skills "
             "list is credible or too broad. Suggest sharper, honest rewrites using only verified facts."},
]


def _split(revs):
    out = []
    for r in revs:
        if r["id"] == "typographer":
            for f in r["files"]:
                out.append({**r, "id": f"typographer_{f}", "files": [f]})
        else:
            out.append(r)
    return out


REVIEWERS = _split(REVIEWERS)


def run(rv):
    print(f"[{rv['id']}] start -> {rv['model']}", flush=True)
    content = [{"type": "text", "text":
                f"{rv['role']}\n\nTASK: {rv['task']}\n\nVERIFIED FACTS SHEET:\n{FACTS}\n\n{SCHEMA}"}]
    for stem in rv["files"]:
        m = {k: v for k, v in METRICS[f"{stem}.pdf"].items() if k not in ("ats",)}
        content.append({"type": "text", "text":
                        f"\n===== FILE {stem} =====\nMEASURED METRICS: {json.dumps(m, ensure_ascii=False)}\n"
                        f"TEXT AS EXTRACTED BY AN ATS (pdftotext):\n{text(stem)}\nPAGE IMAGES FOLLOW:"})
        content += [img(p) for p in pages(stem)]
    t0 = time.time()
    err = ""
    for attempt in range(2):
        try:
            # streaming keeps bytes flowing so the edge proxy does not cut the request (524)
            stream = client.chat.completions.create(model=rv["model"], max_completion_tokens=9000, stream=True,
                                                    messages=[{"role": "user", "content": content}])
            parts, model_used = [], rv["model"]
            for ch in stream:
                model_used = getattr(ch, "model", None) or model_used
                if ch.choices and ch.choices[0].delta and ch.choices[0].delta.content:
                    parts.append(ch.choices[0].delta.content)
            raw = "".join(parts)
            m = re.search(r"\{.*\}", raw, re.S)
            data = json.loads(m.group(0)) if m else {"verdict": "unparseable", "issues": [], "raw": raw[:3000]}
            data.update({"reviewer": rv["id"], "model": model_used, "seconds": round(time.time() - t0, 1)})
            (AUD / f"rev_{ROUND}_{rv['id']}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
            return data
        except Exception as e:  # retry transient errors
            err = str(e).replace(os.environ["OPENAI_API_KEY"], "***")[:300]
            print(f"[{rv['id']}] attempt {attempt+1} failed after {time.time()-t0:.0f}s: {err[:120]}", flush=True)
            time.sleep(5)
    data = {"reviewer": rv["id"], "model": rv["model"], "error": err, "issues": []}
    (AUD / f"rev_{ROUND}_{rv['id']}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    return data


def main():
    with cf.ThreadPoolExecutor(max_workers=len(REVIEWERS)) as ex:
        only = os.environ.get("ONLY")
        todo = [r for r in REVIEWERS if not only or any(r["id"].startswith(o) for o in only.split(","))]
        results = list(ex.map(run, todo))
    out = AUD / f"reviews_{ROUND}.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1))
    for r in results:
        sev = {}
        for i in r.get("issues", []):
            sev[i.get("severity")] = sev.get(i.get("severity"), 0) + 1
        print(f"{r['reviewer']:15s} {r.get('model',''):18s} score={r.get('score_10','-')!s:>2} "
              f"t={r.get('seconds','-')}s issues={sev} {r.get('error','')}")
        print(f"   verdict: {r.get('verdict','')[:220]}")
    print("saved", out)


if __name__ == "__main__":
    main()
