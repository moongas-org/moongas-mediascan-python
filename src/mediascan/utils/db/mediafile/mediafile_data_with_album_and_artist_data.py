from dataclasses import dataclass
from typing import Protocol

from mediascan.utils.db._dataframe_row import (
    optional_float as _optional_float,
    optional_integer as _optional_integer,
    optional_text as _optional_text,
)


class _JoinedRow(Protocol):
    def __getitem__(self, key: str, /) -> object: ...


@dataclass
class MediaFileDataWithAlbumAndArtistData:
    """Media-file metadata from a dataframe joined with track, album, and artist."""

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
    artistid: int | None = None
    albumid: int | None = None
    trackid: int | None = None
    size: int | None = None
    format: str | None = None
    duration: float | None = None
    countryCode: str | None = None
    regionCode: str | None = None
    city: str | None = None
    languageCode: str | None = None


def row_to_mediafile_data_with_album_and_artist_data(
    row: _JoinedRow,
) -> MediaFileDataWithAlbumAndArtistData:
    """Convert an iterrows() row or record mapping using the joined dataframe aliases."""
    path = _optional_text(row["mediafile_path"])
    if path is None:
        raise ValueError("mediafile_path must not be missing")
    mediafile_id = _optional_integer(row["mediafile_id"])
    if mediafile_id is None:
        raise ValueError("mediafile_id must not be missing")
    return MediaFileDataWithAlbumAndArtistData(
        id=mediafile_id,
        path=path,
        album_path=_optional_text(row["album_path"]),
        artist_path=_optional_text(row["artist_path"]),
        title=_optional_text(row["mediafile_title"]),
        artist=_optional_text(row["mediafile_artist"]),
        albumartist=_optional_text(row["mediafile_albumartist"]),
        album=_optional_text(row["mediafile_album"]),
        genre=_optional_text(row["mediafile_genre"]),
        year=_optional_integer(row["mediafile_year"]),
        artistid=_optional_integer(row["mediafile_artistid"]),
        albumid=_optional_integer(row["mediafile_albumid"]),
        trackid=_optional_integer(row["trackid"]),
        size=_optional_integer(row["size"]),
        format=_optional_text(row["format"]),
        duration=_optional_float(row["duration"]),
        countryCode=_optional_text(row["countrycode"]),
        regionCode=_optional_text(row["regioncode"]),
        city=_optional_text(row["city"]),
        languageCode=_optional_text(row["languagecode"]),
    )
