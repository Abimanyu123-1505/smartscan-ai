# Roadmap Summary (source: DFIOP Implementation Roadmap)

Full detail lives in the original planning document. This is a condensed
reference for contributors so the phase boundaries are visible without
re-reading the whole roadmap.

## Phase 1 — Prototype / MVP (Months 1–6) — **this repo**
Acquisition engine (hash + chain of custody), filesystem parsing
(SleuthKit-equivalent metadata/carving), basic artifact extraction
(browser history, USB logs, prefetch, registry, event logs), timeline &
full-text search, case management, exportable PDF/HTML reports, read-only
evidence handling.

## Phase 2 — Intermediate (Months 7–18)
Memory forensics (Volatility3/Rekall), network analysis (PCAP/NetFlow,
protocol-level insights), web/app forensics (HTTP log ingestion, Burp
import), deeper OS artifacts (Shellbags, ShimCache, WMI logs), AI-assisted
triage (summarization, clustering, anomaly scoring, explainable), plugin
SDK, RBAC + multi-user, encrypted storage, CI validation suite.

## Phase 3 — Advanced / Production (Months 19–30+)
Mobile & IoT forensics, cloud & container forensics (CloudTrail, K8s
audit logs), investigation knowledge graph (Neo4j), LLM-based case
summaries and natural-language querying with cited provenance, MITRE
ATT&CK mapping, enterprise RBAC/LDAP/compliance (CJIS, FIPS, ISO 27037),
plugin marketplace.

## Feature-to-phase mapping (abridged)

| Feature | Phase | Status in this repo |
|---|---|---|
| Disk/USB acquisition + hashing | 1 | done (zip/dir/file upload) |
| Filesystem parsing | 1 | done |
| Deleted file recovery / carving | 1 | signature-based type detection only; no unallocated-space carving |
| Registry/Prefetch/Event logs | 2 | stubbed interface, not implemented |
| Browser history | 1 | done (Chrome + Firefox) |
| Memory forensics | 2 | stubbed interface, not implemented |
| Network (PCAP) | 2 | stubbed interface, not implemented |
| Web/app (HTTP logs) | 2 | not started |
| Mobile/IoT | 3 | not started |
| Cloud forensics | 2–3 | stubbed interface, not implemented |
| Container forensics | 3 | not started |
| Timeline engine | 1 | done |
| Case management & collaboration | 1 (RBAC in 2) | single-user case management done; no RBAC yet |
| Search & triage | 1 (AI in 2) | FTS5 keyword search done; AI scoring not started |
| Reporting & export | 1 | PDF done; HTML/CSV not yet |
| Plugin/SDK framework | 1 | interface + registry done |

See `docs/ARCHITECTURE.md` for how the current code maps to the roadmap's
architecture diagram and why the graph DB / AI layer are deferred to
Phase 2.
