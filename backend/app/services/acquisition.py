"""
Orchestrates the Acquisition -> Parsing -> Correlation -> Indexing ->
Timeline pipeline described in the roadmap's Architecture and Data Flow
section.

Two additions beyond the original Phase 1 scope, pulled forward from the
ForensioGraph plan because they need no new infrastructure (no Neo4j, no
LLM) to deliver real value now:

  - `_flag_anomalies`: simple timestamp-contradiction / masquerade
    heuristics (per Studiawan et al.'s timeline-contradiction concept),
    populating the `flagged_score`/`flagged_reason` fields that already
    existed on Artifact but were never written to.
  - `_correlate_artifacts`: a lightweight cross-artifact correlation
    pass (per Iyengar et al. / DF-Graph) that links a browser-history
    download to the matching file artifact on disk, populating
    `source_refs_json` on both sides. This is the knowledge-graph
    "edges" concept implemented as plain foreign-key-style references
    instead of a graph database -- the same information, without
    standing up Neo4j for two artifact types.
"""
import os
import json
import zipfile
import datetime as dt
from urllib.parse import urlparse
from sqlalchemy.orm import Session

from .. import models
from ..database import get_raw_connection
from ..plugins import PLUGIN_REGISTRY


def _resolve_parse_target(stored_path: str) -> str:
    """If the acquired evidence is a zip bundle, extract it once into a
    sibling read-only directory and parse *that* instead of the zip
    itself. Some plugins (browser_history_parser) only recognize a
    mounted directory tree, matching how a real triage bundle or live
    endpoint collection would be laid out on disk -- a zip file alone
    can't be walked for a `History` or `places.sqlite` file. The
    original zip is left untouched; the extracted copy is the only
    thing ever opened for parsing."""
    if not zipfile.is_zipfile(stored_path):
        return stored_path
    extract_dir = stored_path + "_extracted"
    if not os.path.isdir(extract_dir):
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(stored_path) as zf:
            zf.extractall(extract_dir)
    return extract_dir


def run_parsers_on_evidence(db: Session, evidence: models.Evidence) -> int:
    target_path = _resolve_parse_target(evidence.stored_path)
    handled_by_plugin = False
    new_artifacts = []

    for plugin in PLUGIN_REGISTRY:
        if not plugin.can_handle(target_path):
            continue
        handled_by_plugin = True
        try:
            records = plugin.parse(target_path)
        except NotImplementedError:
            continue
        for rec in records:
            new_artifacts.append(_build_artifact(evidence, plugin.name, rec))

    if not handled_by_plugin:
        new_artifacts.append(
            _build_artifact(
                evidence,
                "raw_fallback",
                {
                    "artifact_type": "file",
                    "name": evidence.original_filename,
                    "path": evidence.original_filename,
                    "size_bytes": evidence.size_bytes,
                    "sha256": evidence.sha256,
                    "created_ts": evidence.acquired_at,
                    "modified_ts": evidence.acquired_at,
                    "accessed_ts": None,
                    "extra": {},
                },
            )
        )

    for artifact in new_artifacts:
        _flag_anomalies(artifact)

    for artifact in new_artifacts:
        db.add(artifact)
    db.flush()  # populate artifact.id for every pending row

    _correlate_artifacts(db, evidence.case_id, new_artifacts)

    for artifact in new_artifacts:
        _add_timeline_events(db, artifact)

    db.commit()
    for artifact in new_artifacts:
        db.refresh(artifact)

    _index_artifacts(new_artifacts)
    return len(new_artifacts)


def _build_artifact(evidence, plugin_name, rec):
    return models.Artifact(
        evidence_id=evidence.id,
        case_id=evidence.case_id,
        artifact_type=rec.get("artifact_type", "unknown"),
        operation=rec.get("operation", ""),
        name=rec.get("name", ""),
        path=rec.get("path", ""),
        size_bytes=rec.get("size_bytes", 0) or 0,
        sha256=rec.get("sha256", "") or "",
        created_ts=rec.get("created_ts"),
        modified_ts=rec.get("modified_ts"),
        accessed_ts=rec.get("accessed_ts"),
        user=rec.get("user", "") or "",
        process=rec.get("process", "") or "",
        extra_json=json.dumps(rec.get("extra", {}), default=str),
        parser_plugin=plugin_name,
        confidence=1.0,
        labels_json="[]",
        source_refs_json="[]",
    )


# ---------------------------------------------------------------------
# Anomaly / timeline-contradiction flagging
# ---------------------------------------------------------------------

def _flag_anomalies(artifact: models.Artifact):
    reasons = []

    if artifact.accessed_ts and artifact.created_ts and artifact.accessed_ts < artifact.created_ts:
        reasons.append("accessed timestamp precedes creation timestamp (possible timestomping)")

    if artifact.modified_ts and artifact.created_ts and artifact.modified_ts < artifact.created_ts:
        reasons.append("modified timestamp precedes creation timestamp (possible timestomping)")

    if artifact.artifact_type == "file" and artifact.name:
        ext = os.path.splitext(artifact.name)[1].lower().lstrip(".")
        carved = json.loads(artifact.extra_json or "{}").get("carved_type", "unknown")
        mismatch_pairs = {
            ("txt", "pdf"), ("txt", "jpg"), ("txt", "png"), ("txt", "zip_or_docx"),
            ("jpg", "pdf"), ("png", "pdf"), ("doc", "jpg"), ("pdf", "jpg"), ("pdf", "png"),
        }
        if ext and carved != "unknown" and (ext, carved) in mismatch_pairs:
            reasons.append(f"file extension '.{ext}' does not match detected content type '{carved}' (possible masquerading)")

    if reasons:
        artifact.flagged_score = min(1.0, 0.4 * len(reasons))
        artifact.flagged_reason = "; ".join(reasons)
        labels = json.loads(artifact.labels_json or "[]")
        if "flagged" not in labels:
            labels.append("flagged")
        artifact.labels_json = json.dumps(labels)


# ---------------------------------------------------------------------
# Cross-artifact correlation (lightweight knowledge-graph edges)
# ---------------------------------------------------------------------

def _correlate_artifacts(db: Session, case_id: str, new_artifacts):
    new_downloads = [a for a in new_artifacts if a.artifact_type == "browser_history"]
    if not new_downloads:
        # Still worth checking: a newly-added file might match an
        # already-recorded browser_history entry from earlier evidence.
        new_downloads = (
            db.query(models.Artifact)
            .filter(models.Artifact.case_id == case_id, models.Artifact.artifact_type == "browser_history")
            .all()
        )
    new_files = [a for a in new_artifacts if a.artifact_type == "file"]
    if not new_files:
        return

    file_by_name = {f.name.lower(): f for f in new_files if f.name}

    for hist in new_downloads:
        url = json.loads(hist.extra_json or "{}").get("url", "")
        if not url:
            continue
        basename = os.path.basename(urlparse(url).path).lower()
        if not basename or basename not in file_by_name:
            continue
        file_artifact = file_by_name[basename]

        hist_refs = json.loads(hist.source_refs_json or "[]")
        hist_refs.append({"type": "File", "artifact_id": file_artifact.id, "path": file_artifact.path})
        hist.source_refs_json = json.dumps(hist_refs)

        file_refs = json.loads(file_artifact.source_refs_json or "[]")
        file_refs.append({"type": "BrowserHistory", "artifact_id": hist.id, "value": url})
        file_artifact.source_refs_json = json.dumps(file_refs)

        file_labels = json.loads(file_artifact.labels_json or "[]")
        if "corroborated-download" not in file_labels:
            file_labels.append("corroborated-download")
        file_artifact.labels_json = json.dumps(file_labels)


def _index_artifacts(artifacts):
    if not artifacts:
        return
    conn = get_raw_connection()
    conn.executemany(
        "INSERT INTO artifact_index (artifact_id, case_id, artifact_type, name, content, path) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [
            (a.id, a.case_id, a.artifact_type, a.name, f"{a.name} {a.path}", a.path)
            for a in artifacts
        ],
    )
    conn.commit()
    conn.close()


def _add_timeline_events(db: Session, artifact: models.Artifact):
    ts_fields = [
        ("created", artifact.created_ts),
        ("modified", artifact.modified_ts),
        ("accessed", artifact.accessed_ts),
    ]
    for event_type, ts in ts_fields:
        if ts is None:
            continue
        db.add(
            models.TimelineEvent(
                case_id=artifact.case_id,
                artifact_id=artifact.id,
                event_ts=ts,
                event_type=event_type,
                summary=f"{artifact.artifact_type}:{artifact.name} ({event_type})",
                source_type=artifact.parser_plugin,
            )
        )
