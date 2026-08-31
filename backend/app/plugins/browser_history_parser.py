"""
Browser History Extraction (Phase 1 deliverable: "Basic Artifact
Extraction" -- browser history/downloads/cookies).

Runs against a mounted directory tree looking for Chrome/Chromium
'History' SQLite files or Firefox 'places.sqlite' files, and parses
visits directly with sqlite3 -- no third-party dependency needed since
both browsers use plain SQLite for history storage.
"""
import os
import sqlite3
import shutil
import tempfile
import datetime as dt
from typing import List, Dict, Any

from .base import ParserPlugin

CHROME_EPOCH = dt.datetime(1601, 1, 1)


def _chrome_time_to_dt(webkit_ts: int):
    if not webkit_ts:
        return None
    try:
        return CHROME_EPOCH + dt.timedelta(microseconds=webkit_ts)
    except (OverflowError, OSError):
        return None


def _firefox_time_to_dt(usec: int):
    if not usec:
        return None
    try:
        return dt.datetime.utcfromtimestamp(usec / 1_000_000)
    except (OverflowError, OSError, ValueError):
        return None


class BrowserHistoryParser(ParserPlugin):
    name = "browser_history_parser"
    description = "Parses Chrome/Chromium 'History' and Firefox 'places.sqlite' files."

    def can_handle(self, path: str) -> bool:
        if not os.path.isdir(path):
            return False
        for _dirpath, _dirnames, filenames in os.walk(path):
            if "History" in filenames or "places.sqlite" in filenames:
                return True
        return False

    def parse(self, path: str) -> List[Dict[str, Any]]:
        artifacts = []
        for dirpath, _dirnames, filenames in os.walk(path):
            if "History" in filenames:
                artifacts += self._parse_chrome(os.path.join(dirpath, "History"))
            if "places.sqlite" in filenames:
                artifacts += self._parse_firefox(os.path.join(dirpath, "places.sqlite"))
        return artifacts

    def _copy_readonly(self, src: str) -> str:
        # SQLite files may be locked by the source browser; work on a copy
        # so the original evidence file is never opened for writing.
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite")
        tmp.close()
        shutil.copy2(src, tmp.name)
        return tmp.name

    def _parse_chrome(self, history_path: str) -> List[Dict[str, Any]]:
        artifacts = []
        try:
            tmp = self._copy_readonly(history_path)
            conn = sqlite3.connect(tmp)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT url, title, visit_count, last_visit_time FROM urls "
                "ORDER BY last_visit_time DESC LIMIT 5000"
            ).fetchall()
            conn.close()
            os.unlink(tmp)
        except Exception:
            return artifacts

        for row in rows:
            visited = _chrome_time_to_dt(row["last_visit_time"])
            artifacts.append(
                {
                    "artifact_type": "browser_history",
                    "operation": "visited",
                    "name": row["title"] or row["url"],
                    "path": row["url"],
                    "size_bytes": 0,
                    "sha256": "",
                    "created_ts": visited,
                    "modified_ts": visited,
                    "accessed_ts": visited,
                    "extra": {
                        "browser": "chrome",
                        "visit_count": row["visit_count"],
                        "url": row["url"],
                    },
                }
            )
        return artifacts

    def _parse_firefox(self, places_path: str) -> List[Dict[str, Any]]:
        artifacts = []
        try:
            tmp = self._copy_readonly(places_path)
            conn = sqlite3.connect(tmp)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT p.url as url, p.title as title, p.visit_count as visit_count, "
                "MAX(h.visit_date) as last_visit "
                "FROM moz_places p JOIN moz_historyvisits h ON h.place_id = p.id "
                "GROUP BY p.id ORDER BY last_visit DESC LIMIT 5000"
            ).fetchall()
            conn.close()
            os.unlink(tmp)
        except Exception:
            return artifacts

        for row in rows:
            visited = _firefox_time_to_dt(row["last_visit"])
            artifacts.append(
                {
                    "artifact_type": "browser_history",
                    "operation": "visited",
                    "name": row["title"] or row["url"],
                    "path": row["url"],
                    "size_bytes": 0,
                    "sha256": "",
                    "created_ts": visited,
                    "modified_ts": visited,
                    "accessed_ts": visited,
                    "extra": {
                        "browser": "firefox",
                        "visit_count": row["visit_count"],
                        "url": row["url"],
                    },
                }
            )
        return artifacts
