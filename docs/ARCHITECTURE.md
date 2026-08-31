# Architecture

This scaffold implements the roadmap's Architecture and Data Flow section
at Phase 1 scope. Layers, and their current vs. planned state:

| Layer | Roadmap plan | This scaffold |
|---|---|---|
| Acquisition | disk/memory/USB/cloud ingestion, hash + mount into Case DB | file upload (zip/dir/single file) with SHA-256/SHA-1/MD5 hashing, read-only storage |
| Parsing/Extraction | plugin-based parsers -> JSON events | `ParserPlugin` interface; filesystem + browser-history parsers implemented; memory/pcap/registry/cloud stubbed |
| Indexing | full-text index (SQLite FTS -> Elasticsearch later) + graph DB (Neo4j) | SQLite FTS5 implemented; graph DB not yet built (see below) |
| Analysis | Timeline Engine, Correlation/Graph Engine, AI/Analytics | Timeline Engine implemented (denormalized `TimelineEvent` table); graph correlation and AI modules not built |
| UI/Dashboard | React case dashboard, natural-language query | React dashboard implemented (case list, evidence upload, artifact table, timeline, keyword search, audit log); natural-language query not built |
| Reporting | PDF/HTML/CSV export, links back to evidence | PDF export implemented (summary, hash list, timeline, chain-of-custody) |

## Why no graph database yet

The roadmap's Investigation Knowledge Graph (Neo4j/ArangoDB) earns its
keep once there are multiple *correlated* artifact types to link — a
process from memory forensics connected to a network flow connected to a
file on disk. With only filesystem and browser-history artifacts in Phase
1, every "relationship" is really just "belongs to this case," which the
existing `case_id` foreign keys already express. Adding Neo4j now would be
infrastructure with nothing meaningful to query. The natural point to
introduce it is alongside the Phase 2 memory-forensics and network-parsing
plugins, when cross-artifact correlation (`file downloaded` -> `process
executed` -> `network connection opened`) becomes real data instead of a
single table.

## Extension point: adding a Phase 2 parser

1. Implement `ParserPlugin.can_handle()` / `.parse()` in a new file under
   `backend/app/plugins/`.
2. Have `.parse()` return a list of dicts shaped like:
   ```python
   {
     "artifact_type": "process",       # or network_flow, registry_key, ...
     "name": "...", "path": "...",
     "size_bytes": 0, "sha256": "",
     "created_ts": dt, "modified_ts": dt, "accessed_ts": dt,
     "extra": {...},                    # anything plugin-specific
   }
   ```
3. Add an instance to `PLUGIN_REGISTRY` in `app/plugins/__init__.py`.

`run_parsers_on_evidence()` in `app/services/acquisition.py` handles the
rest: persisting artifacts, building timeline events, and updating the
search index. No other file changes.

## Why AI/LLM triage isn't wired in

The roadmap treats AI strictly as an *explainable* decision-support layer
that always cites the artifacts behind a suggestion — never an opaque
black box. Bolting on an LLM call now, before there's a knowledge graph or
enough artifact variety to reason over, would produce exactly the kind of
unexplainable, ungrounded output the roadmap explicitly warns against
(see the Yin et al. and Brandao references in `ROADMAP.md`). The right
place for it is Phase 2, reading from the FTS index and (once it exists)
the graph DB, with every output required to link back to source artifact
IDs — the same provenance discipline already used by `TimelineEvent` and
`AuditLog`.
