from dataclasses import dataclass
from math import isnan
from numbers import Integral, Real
from typing import Protocol

import pandas as pd


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
    size: int | None = None
    format: str | None = None
    duration: float | None = None
    countryCode: str | None = None
    regionCode: str | None = None
    city: str | None = None
    languageCode: str | None = None


def _optional_text(value: object) -> str | None:
    if value is None or value is pd.NA or (isinstance(value, float) and isnan(value)):
        return None
    if not isinstance(value, str):
        raise TypeError(f"Expected a string or missing value, got {value!r}")
    return value


def _optional_integer(value: object) -> int | None:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"Expected an integer or missing value, got {value!r}")
    if isinstance(value, Integral):
        return int(value)
    if isnan(value):
        return None
    result = int(float(value))
    if result != value:
        raise ValueError(f"Expected an integer, got {value!r}")
    return result


def row_to_media_file_data_with_album_and_artist_data(
    row: _JoinedRow,
) -> MediaFileDataWithAlbumAndArtistData:
    """Convert an iterrows() row or record mapping using the joined dataframe aliases.

    Size, format, and duration are not stored in the current mediafile table.
    """
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
        countryCode=_optional_text(row["countrycode"]),
        regionCode=_optional_text(row["regioncode"]),
        city=_optional_text(row["city"]),
        languageCode=_optional_text(row["languagecode"]),
    )
