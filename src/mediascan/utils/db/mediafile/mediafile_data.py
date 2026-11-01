from dataclasses import dataclass
from typing import Protocol

from mediascan.utils.db._dataframe_row import (
    optional_integer as _optional_integer,
    optional_text as _optional_text,
)


class _MediaFileRow(Protocol):
    def __getitem__(self, key: str, /) -> object: ...


@dataclass
class MediaFileData:
    """Media-file metadata from the mediafile table."""

    id: int
    path: str
    album_path: str | None
    artist_path: str | None
    title: str | None
    artist: str | None
    albumartist: str | None
    album: str | None
    genre: str | None
    year: int | None
    size: int | None = None
    format: str | None = None
    duration: float | None = None


def row_to_mediafile_data(row: _MediaFileRow) -> MediaFileData:
    """Convert a mediafile dataframe row or record mapping."""
    path = _optional_text(row["path"])
    if path is None:
        raise ValueError("path must not be missing")
    mediafile_id = _optional_integer(row["id"])
    if mediafile_id is None:
        raise ValueError("id must not be missing")
    return MediaFileData(
        id=mediafile_id,
        path=path,
        album_path=_optional_text(row["albumpath"]),
        artist_path=_optional_text(row["artistpath"]),
        title=_optional_text(row["title"]),
        artist=_optional_text(row["artist"]),
        albumartist=_optional_text(row["albumartist"]),
        album=_optional_text(row["album"]),
        genre=_optional_text(row["genre"]),
        year=_optional_integer(row["year"]),
    )
