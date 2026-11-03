# Verified facts (ground truth for reviewers)

Source: the candidate's public GitHub repositories (MoTechSys, moain2028), live websites, and statements by the candidate.
Anything in the CV that is NOT in this list must be flagged as "unverified".

## Identity & contact (confirmed by candidate)
- Name: Moain Al-Abbasi (م. معين العباسي). Based in Sana'a, Yemen. Works remotely only.
- Email: moain.learn@gmail.com (candidate confirmed; old info@alabbasi.tech does NOT work).
- WhatsApp: +967 770 941 666. GitHub: github.com/MoTechSys (main). Company site: alabbasi.uk.
- Education details (university, degree, year) are UNKNOWN. Only a team graduation project (SOC) is documented.
- CONFIRMED BY CANDIDATE (2026-11-03): email moain.learn@gmail.com is correct; he founded and works as Alabbasi Tech in 2026 and has real market experience through that work. 'Founder & Software Engineer · Alabbasi Tech · 2026 – Present' is confirmed.
- Candidate said website traffic numbers previously shown (CTR 0.4%->2.1%, 556 impressions) are OUTDATED; they were removed. No current numbers are available.

## Verified from repository READMEs
- Basira (basirapp.site, public repo MoTechSys/Project-Basira): Quran/Hadith quotation verification; 71,987 records; 150/150 evaluation; 0/500 false alarms; 78.54% IslamicEval 2025 subtask 1B (dev); tests 345 backend + 110 bot + 32 frontend = 487; REST API, MCP server, Telegram bot @BasiraCheckBot; entry to "AI in Service of Islamic Content Challenge 2026", Track 4.
- Mansur AI (repo moain2028/mansur-ai, private): 38 tools, 13 agents, 82 passing tests; LangGraph planner/executor/verifier/learner; model router with fallback and cost tracking; hierarchical memory; FastAPI + WebSocket Arabic UI.
- Ai_Alabbasi: swappable-brain coding agent; CodeAct sandboxed Python; hybrid search FTS5 + vectors with RRF.
- Moain Promoter AI: 7 specialised agents + orchestrator; 6 platforms; Next.js dashboard; Celery + Redis; Playwright.
- Diafa Studio: Arabic PDF generator with an MCP server exposing 18 tools.
- Bina agents: site-audit agent (205 checks), site-rebuild agent, content agent.
- telegram-mcp-2: Telegram MCP server.
- Nexus Notify: multi-tenant multi-channel notifications; NestJS + PostgreSQL 17 + Prisma + Redis/BullMQ; Angular 22 dashboard; Kotlin + Compose Android SMS gateway (dual SIM).
- POS/ERP replacing YemenSoft Onyx Pro: NestJS 10, React 19, Oracle PL/SQL; printed on Bixolon SPP-R310 over Bluetooth SPP (Web Serial); USB on Xprinter failed due to Windows driver (documented).
- Attendance system: Go 1.26, PostgreSQL; pulls from ZKTeco iFace950; daily/monthly reports HTML/CSV.
- Zero-Trust remote access: Go, SSH, NetBird mesh, signed agents, per-user policies, session audit; motech-cli cross-platform.
- Event & hospitality PWA: Angular 22.1, IndexedDB, offline.
- Legacy PHP accounting modernisation: in progress (modern layer under construction).
- Google Ads platform: phase 1 complete (Next.js 15, Prisma, PostgreSQL 16, 12 tables, live Google Ads API data).
- keif-publisher: AI content generation, human approval gate, scheduled publishing, kill switch, dry-run default.
- Idhaat: live tutoring; 4 Zoom rooms auto-allocated; Jitsi fallback with JWT; recordings to Cloudflare R2 during class; 48-hour retention; moving watermark; homework; messaging; finances; ~25 SAR/month running cost.
- Grocery Ledger (MoTechSys/mohanad-web-app-2): Flutter Android, offline, v2.2.1, 157 tests.
- Sijil (MoTechSys/Sijilati): Flutter offline debt ledger, 93 tests.
- S-ACM: React 19, TypeScript, Tailwind 4; AI summarisation & question generation.
- Ghaida: domestic-worker household book, AI voice per sentence, offline PWA, admin panel; API 27/27.
- SOC graduation project (MoTechSys/my-bro): Wazuh 4.14.7, Suricata, YARA, VirusTotal, auditd, MikroTik syslog, AI analyst with human approval; 14 use cases verified on a lab (2026-09-28).
- Digital forensics lab: Autopsy, FTK Imager, registry, event logs, browser forensics.
- Live sites (HTTP 200 checked): keifaldiafa.com, asoulaldiafa.com, qahwajeen.com, basirapp.site, alabbasi.uk.

## Target audience
1. Saudi companies hiring or outsourcing software work to a remote engineer (Arabic CV + services profile).
2. International tech companies / remote platforms (English CV).

## Round-2 additions verified directly from repo READMEs (2026-11-03)
- motech-attendance: central Go service + branch collectors (pyzk, TCP/4370), multi-tenant, idempotent ingest; tested on live iFace950 (11 users, 3,118 punches); shifts, leave balances, CSV/Excel; WPS export for KSA (MHRSD/SAMA) and UAE (SIF). Replaces ZKTeco desktop software.
- motech-pos: works on existing Oracle YSPOS23 schema; built modules auth, bills, catalog, customers, reports, returns, shifts. Print field test: Bixolon SPP-R310 over Bluetooth via Web Serial succeeded; Xprinter USB on Windows failed (documented).
- ads-agency-platform: multi-tenant SaaS for Google Ads across clients; phase 1 done (Next.js 15, Prisma, PostgreSQL 16, 12 tables, live API data, dashboard).
- keif-aldiafa-ads-platform: Hono + Cloudflare D1, OAuth to Google Ads + Search Console, free GAQL, Arabic dashboard (phase 0 done).
- Idhaat: Hono on Cloudflare Pages, D1, R2, Vitest; moving watermark with student name and number.
- Grocery Ledger: barcode via camera (ML Kit) or USB/Bluetooth HID scanner; append-only ledgers.
- Sijil: designed for owner and worker "even illiterate"; banknote entry, spoken confirmation, 8-second undo.
- S-ACM: README stack React 19, TypeScript 5, Tailwind 4 (no Hono/Drizzle).
- motech-cli: cosign keyless-signed releases; joins NetBird mesh.

## Round-3 additions verified directly from repo READMEs (2026-11-03)
- Basira README: matches quotations "byte-exactly against licensed source corpora"; optional model only *proposes* spans and reads images (OCR), never decides; backend FastAPI; frontend React 19 + TypeScript + Vite; tests 345 + 110 + 32 (vitest).
- Mansur AI README: ReAct executor; hierarchical SQLite memory (working, episodic, procedural, semantic); "saves its experience as skills after success"; sandboxed shell; HTTP tools with SSRF protection; FastAPI + WebSocket UI.
- Ai_Alabbasi README: brain swapped "with one line" (Claude / GPT-5 / DeepSeek / local model); planner + todo list; CodeAct; hybrid FTS5 + vectors with RRF; RAG; sandbox local/Daytona/E2B.
- keif-publisher README: content from the media archive; 9:16 conversion; human approval gate (FastAPI + Jinja2 UI); APScheduler; dry-run default and kill switch enabled by default.
- keif-aldiafa-ads-platform README: client = Keif Al-Diafa, Jeddah; "permanent" OAuth connection to Google Ads + Search Console; free GAQL; Arabic dashboard; phase 0 done.
- motech_V2 README (remote access): Authenticode-signed Windows agent running as a service, 20 s heartbeat, NetBird mesh, SSH key rotation, AES-256-GCM encrypted private keys, full activity log. NOT stated: "Zero-Trust", "per-user policies", "session audit" -> do not use.
- motech-pos: built modules auth, bills, catalog, customers, reports, returns, shifts; OpenAPI; Arabic raster printing proven on Bixolon. BullMQ is only in the planned stack -> do not list.
- Nexus Notify README: one unified API; Android gateway is a foreground service with dual SIM.
- my-bro README: UC-11 "SSH brute force + automatic blocking" verified live in the lab. VirusTotal is an external service (not open source).
- Websites: MoTechSys/keif-aldiafa-web (keifaldiafa.com, Next.js 14, Jeddah) and MoTechSys/osoul-aldiafa-v2 (asoulaldiafa.com, Next.js 14) are in the candidate's org. qahwajeen.com: live, but no repo found.
- MoTechSys/diafa-apps + keif_blins: Android apps "Keif Al-Diafa" and "Asoul Al-Diafa" v2.6.0 (Flutter/Dart + Kotlin), signed APK releases with remote lock.
- All project links in the CV return HTTP 200 (public repos).

## Round-4 additions (verified in READMEs; reviewers flagged them only because they were missing here)
- Basira: pytest (345), vitest (32), GitHub Actions CI (actions/workflows/ci.yml), ruff, mypy strict.
- Idhaat: Jitsi Meet self-hosted in Docker on a VPS; JWT token per lesson; moving watermark with student name and number.
- Moain Promoter AI: bilingual Arabic + English posts; providers OpenAI, Anthropic, Gemini, Groq.
- Ai_Alabbasi: brain "swappable from one file"; private repository (GitHub API private=true).
- Grocery Ledger: PdfExporter and ExcelExporter in the code layout.
- motech-attendance: systemd units for scheduled sync.
- motech_V2 (remote access): languages Go + PLpgSQL (PostgreSQL).
- Printing: Arabic raster printing over Bluetooth SPP / Web Serial (not "ESC/POS" as a skill claim).
- qahwajeen.com: live, but NO repo or other evidence of authorship -> removed until the candidate confirms.
- Basira has no client-service bot; the only bot verifies quotations (@BasiraCheckBot).
