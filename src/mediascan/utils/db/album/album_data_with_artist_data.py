from dataclasses import dataclass
from typing import Protocol

from mediascan.utils.db._dataframe_row import (
    optional_boolean as _optional_boolean,
    optional_integer as _optional_integer,
    optional_text as _optional_text,
)


class _JoinedAlbumRow(Protocol):
    def __getitem__(self, key: str, /) -> object: ...


@dataclass
class AlbumDataWithArtistData:
    """Album metadata joined with artist metadata."""

    id: int
    path: str
    name: str | None
    year: int | None
    explicitcover: bool | None
    artistid: int | None
    genre: str | None
    artist_path: str | None
    artist_name: str | None
    city: str | None
    countryCode: str | None
    regionCode: str | None
    languageCode: str | None


def row_to_album_data_with_artist_data(
    row: _JoinedAlbumRow,
) -> AlbumDataWithArtistData:
    """Convert a row from get_df_album_artist_joined using its column aliases."""
    path = _optional_text(row["album_path"])
    if path is None:
        raise ValueError("album_path must not be missing")
    album_id = _optional_integer(row["album_id"])
    if album_id is None:
        raise ValueError("album_id must not be missing")
    return AlbumDataWithArtistData(
        id=album_id,
        path=path,
        name=_optional_text(row["album_name"]),
        year=_optional_integer(row["year"]),
        explicitcover=_optional_boolean(row["explicitcover"]),
        artistid=_optional_integer(row["artistid"]),
        genre=_optional_text(row["genre"]),
        artist_path=_optional_text(row["artist_path"]),
        artist_name=_optional_text(row["artist_name"]),
        city=_optional_text(row["city"]),
        countryCode=_optional_text(row["countrycode"]),
        regionCode=_optional_text(row["regioncode"]),
        languageCode=_optional_text(row["languagecode"]),
    )
