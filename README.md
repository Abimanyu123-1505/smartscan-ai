# DFIOP — Digital Forensics Investigation Operating Platform

A working Phase 1 (MVP) implementation of the DFIOP roadmap: a unified
case-management + evidence-acquisition + timeline/search platform for
digital forensics investigations, built as the foundation for the
Phase 2/3 modules described in `docs/ROADMAP.md`.

## What's actually implemented (Phase 1)

- **Case management** — create/list cases, each an isolated evidence store.
- **Acquisition & integrity** — upload evidence (a directory-zip, a single
  file, or a raw SQLite export like a browser history file). Every item is
  hashed on acquisition (SHA-256, SHA-1, MD5), stored read-only, and can be
  re-verified on demand to detect tampering.
- **Chain of custody** — every action (case created, evidence acquired,
  parsed, re-verified, report exported) is written to an append-only audit
  log, per case.
- **Parsing** — a real filesystem parser (walks directories/zips, records
  MAC timestamps + SHA-256 per file, flags magic-byte file types) and a real
  Chrome/Firefox browser-history parser (reads `History` / `places.sqlite`
  directly with `sqlite3`, no third-party dependency).
- **Timeline** — every artifact's created/modified/accessed timestamps are
  denormalized into a queryable timeline.
- **Search** — full-text search over all extracted artifact names/paths via
  SQLite FTS5.
- **Reporting** — one-click PDF case report: summary, evidence + hash list,
  timeline, and chain-of-custody log.
- **Plugin architecture** — parsers implement one interface
  (`app/plugins/base.py::ParserPlugin`). Phase 2/3 modules (memory
  forensics via Volatility3, PCAP parsing, Windows registry hives, cloud
  audit logs) are stubbed in `app/plugins/__init__.py` with the exact
  interface they'll implement, so adding them later doesn't change any
  other part of the system.

### Additions from the ForensioGraph plan

A second planning document ("ForensioGraph") proposed the same platform
with a heavier knowledge-graph/AI emphasis. Four of its ideas were pulled
into Phase 1 because they needed no new infrastructure (no Neo4j, no LLM)
to deliver real value now — see `app/services/acquisition.py` and
`app/services/audit.py`:

- **Unified artifact/event schema** — every `Artifact` now carries
  `operation`, `user`, `process`, `labels`, `confidence`, and
  `source_refs`, matching the JSON event schema from the ForensioGraph
  doc. This is the same information a graph database would store as node
  properties and edges — implemented as plain columns so a future Neo4j
  layer can be built on top without a schema rewrite.
- **Cross-artifact correlation** — a lightweight pass links a browser
  download to the matching file on disk (by filename), populating
  `source_refs` on both sides and tagging the file `corroborated-download`.
  This is the "knowledge graph edges" concept for two artifact types,
  without standing up a graph database.
- **Timeline-contradiction / anomaly flagging** — heuristics catch
  timestomping-style timestamp ordering (accessed before created) and
  file-extension-vs-content-type mismatches (e.g. a `.txt` file that's
  actually a PDF), populating `flagged_score`/`flagged_reason`.
- **Hash-chained, tamper-evident audit log** — each `AuditLog` entry now
  stores a SHA-256 hash chained to the previous entry
  (`prev_hash`/`entry_hash`). `GET /api/cases/{id}/audit-log/verify`
  recomputes the chain and reports exactly where it breaks if any entry
  was altered after the fact.
- **Human-in-the-loop verification** — `POST /api/artifacts/{id}/label`
  lets an analyst confirm or dismiss a flagged/correlated artifact
  (`{"label": "verified"}`), per both documents' "AI/heuristics suggest,
  analyst confirms" principle.

Fixed along the way: zip-uploaded evidence is now extracted to a
directory before parsing, so directory-based plugins (like the browser
history parser) can actually run — previously `stored_path` was always a
single zip/file, so `browser_history_parser.can_handle()` could never
return `True` via the upload API.

## What's intentionally *not* built yet

Everything in the roadmap's Phase 2/3 tables that needs a native forensic
library or live system access — SleuthKit/E01 image mounting, Volatility3
memory analysis, PCAP flow parsing, mobile backups, cloud/container
forensics, the AI/LLM triage layer, and the Neo4j knowledge graph. These
need dependencies (`pytsk3`, `volatility3`, `scapy`, GPU-backed models)
that don't belong in a first working scaffold. The stub classes in
`app/plugins/__init__.py` and the architecture notes in `docs/ARCHITECTURE.md`
show exactly where each one plugs in.

## Running it

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8123
```
API docs at `http://127.0.0.1:8123/docs`. SQLite database and uploaded
evidence are stored under `backend/storage/` (gitignored).

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Opens at `http://127.0.0.1:5173`, proxying `/api` to the backend on `:8123`
(see `vite.config.js`).

## Project layout

```
backend/
  app/
    main.py              FastAPI app, CORS, router registration
    models.py             Case, Evidence, Artifact, TimelineEvent, AuditLog
    schemas.py            Pydantic request/response models
    database.py            SQLite engine + FTS5 index setup
    routers/               cases, evidence, artifacts, search, reports
    services/
      hashing.py            SHA-256/SHA-1/MD5
      acquisition.py         parser orchestration -> artifacts -> timeline -> index
      audit.py                chain-of-custody logging
      reporting.py            PDF report builder (reportlab)
    plugins/
      base.py                 ParserPlugin interface (the Plugin/SDK seam)
      filesystem_parser.py    real: walks dirs/zips, hashes + MAC times
      browser_history_parser.py  real: Chrome + Firefox history
      __init__.py             registry + Phase 2/3 stubs (memory, pcap, registry, cloud)
frontend/
  src/
    api.js                 thin fetch wrapper over the REST API
    App.jsx                 shell, routing
    pages/CaseList.jsx       docket view, case creation
    pages/CaseDetail.jsx     evidence upload, artifact table, timeline, search, audit log
    styles/global.css        design tokens
docs/
  ROADMAP.md               phase-by-phase plan (source document)
  ARCHITECTURE.md          how this scaffold maps to the roadmap's architecture
```

## Design notes

Visual identity is an "evidence locker" palette rather than a generic
dashboard theme — deep charcoal-navy background, a manila-folder amber for
case/evidence tags, a verified-teal for integrity-confirmed states, and
alert red reserved only for flagged or hash-mismatched evidence. Hashes and
timestamps are set in monospace (IBM Plex Mono) throughout so they read as
literal, checkable data rather than UI chrome.
