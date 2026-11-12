from dataclasses import dataclass
from typing import Protocol

from mediascan.utils.db._dataframe_row import (
    optional_boolean as _optional_boolean,
    optional_integer as _optional_integer,
    optional_text as _optional_text,
)


class _TrackRow(Protocol):
    def __getitem__(self, key: str, /) -> object: ...


@dataclass
class TrackData:
    """Track metadata from the track table."""

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
    artistid: int | None
    albumid: int | None
    hasspotify: bool
    hasmedia: bool
    haslyricstxt: bool
    haslyricslrc: bool


def row_to_track_data(row: _TrackRow) -> TrackData:
    """Convert a track dataframe row or record mapping."""
    path = _optional_text(row["path"])
    if path is None:
        raise ValueError("path must not be missing")
    track_id = _optional_integer(row["id"])
    if track_id is None:
        raise ValueError("id must not be missing")
    has_spotify = _optional_boolean(row["hasspotify"])
    if has_spotify is None:
        raise ValueError("hasspotify must not be missing")
    has_media = _optional_boolean(row["hasmedia"])
    if has_media is None:
        raise ValueError("hasmedia must not be missing")
    has_lyrics_txt = _optional_boolean(row["haslyricstxt"])
    if has_lyrics_txt is None:
        raise ValueError("haslyricstxt must not be missing")
    has_lyrics_lrc = _optional_boolean(row["haslyricslrc"])
    if has_lyrics_lrc is None:
        raise ValueError("haslyricslrc must not be missing")
    return TrackData(
        id=track_id,
        path=path,
        album_path=_optional_text(row["albumpath"]),
        artist_path=_optional_text(row["artistpath"]),
        title=_optional_text(row["title"]),
        artist=_optional_text(row["artist"]),
        albumartist=_optional_text(row["albumartist"]),
        album=_optional_text(row["album"]),
        genre=_optional_text(row["genre"]),
        year=_optional_integer(row["year"]),
        artistid=_optional_integer(row["artistid"]),
        albumid=_optional_integer(row["albumid"]),
        hasspotify=has_spotify,
        hasmedia=has_media,
        haslyricstxt=has_lyrics_txt,
        haslyricslrc=has_lyrics_lrc,
    )
