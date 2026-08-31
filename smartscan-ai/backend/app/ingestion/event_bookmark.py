"""
smartscan.backend.app.ingestion.event_bookmark
===============================================
User event bookmarking and annotation manager for RF spectrogram features.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class EventBookmark:
    bookmark_id: str
    dataset_id: str
    recording_id: str
    start_slot: int
    end_slot: int
    freq_bin: int
    label: str
    notes: str
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bookmark_id": self.bookmark_id,
            "dataset_id": self.dataset_id,
            "recording_id": self.recording_id,
            "start_slot": self.start_slot,
            "end_slot": self.end_slot,
            "freq_bin": self.freq_bin,
            "label": self.label,
            "notes": self.notes,
            "created_at": self.created_at,
        }


class BookmarkStore:
    def __init__(self):
        self.bookmarks: List[EventBookmark] = []

    def add_bookmark(self, dataset_id: str, recording_id: str, start_slot: int, end_slot: int, freq_bin: int, label: str, notes: str = "") -> EventBookmark:
        bm_id = f"bm_{len(self.bookmarks) + 1:04d}"
        bm = EventBookmark(
            bookmark_id=bm_id,
            dataset_id=dataset_id,
            recording_id=recording_id,
            start_slot=start_slot,
            end_slot=end_slot,
            freq_bin=freq_bin,
            label=label,
            notes=notes
        )
        self.bookmarks.append(bm)
        return bm

    def list_bookmarks(self) -> List[Dict[str, Any]]:
        return [bm.to_dict() for bm in self.bookmarks]
