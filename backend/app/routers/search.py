from typing import List
from fastapi import APIRouter, Query
from ..database import get_raw_connection
from .. import schemas

router = APIRouter(prefix="/api/cases", tags=["search"])


@router.get("/{case_id}/search", response_model=List[schemas.SearchResult])
def search_artifacts(case_id: str, q: str = Query(..., min_length=1)):
    """Timeline & Search deliverable: keyword search over all extracted
    metadata via SQLite FTS5, matching Phase 1's search scope (later
    swapped for Elasticsearch/OpenSearch in Phase 3 behind this same
    endpoint contract)."""
    conn = get_raw_connection()
    # FTS5 query syntax: wrap the term so punctuation in filenames/URLs
    # doesn't break the query parser.
    fts_query = f'"{q}"*' if " " not in q else q
    rows = conn.execute(
        """
        SELECT artifact_id, case_id, artifact_type, name, path,
               snippet(artifact_index, 4, '[', ']', '…', 8) as snip
        FROM artifact_index
        WHERE artifact_index MATCH ? AND case_id = ?
        LIMIT 200
        """,
        (fts_query, case_id),
    ).fetchall()
    conn.close()
    return [
        schemas.SearchResult(
            artifact_id=r["artifact_id"],
            case_id=r["case_id"],
            artifact_type=r["artifact_type"],
            name=r["name"],
            path=r["path"],
            snippet=r["snip"],
        )
        for r in rows
    ]
