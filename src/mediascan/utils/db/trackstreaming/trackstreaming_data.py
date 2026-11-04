from dataclasses import dataclass
from typing import Protocol

from mediascan.utils.db._dataframe_row import (
    optional_integer as _optional_integer,
    optional_text as _optional_text,
)


class _TrackStreamingRow(Protocol):
    def __getitem__(self, key: str, /) -> object: ...
    def __contains__(self, key: object, /) -> bool: ...


@dataclass
class TrackStreamingData:
    """Track streaming identifiers from the trackstreaming table."""

    track_id: int
    streaming_service: str
    streaming_track_id: str
    streaming_track_url: str | None


def row_to_trackstreaming_data(row: _TrackStreamingRow) -> TrackStreamingData:
    """Convert a trackstreaming dataframe row or record mapping."""
    track_id = _optional_integer(row["trackid"])
    if track_id is None:
        raise ValueError("trackid must not be missing")
    streaming_service = _optional_text(row["streamingservice"])
    if streaming_service is None:
        raise ValueError("streamingservice must not be missing")
    streaming_track_id = _optional_text(row["streamingtrackid"])
    if streaming_track_id is None:
        raise ValueError("streamingtrackid must not be missing")
    streaming_track_url = _optional_text(
        row["streamingtrackurl"] if "streamingtrackurl" in row else None
    )
    return TrackStreamingData(
        track_id=track_id,
        streaming_service=streaming_service,
        streaming_track_id=streaming_track_id,
        streaming_track_url=streaming_track_url,
    )
