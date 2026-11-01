from dataclasses import dataclass
from typing import Protocol

from mediascan.utils.db._dataframe_row import (
    optional_integer as _optional_integer,
    optional_text as _optional_text,
)


class _ArtistRow(Protocol):
    def __getitem__(self, key: str, /) -> object: ...


@dataclass
class ArtistData:
    """Artist metadata from the artist table."""

    id: int
    path: str
    name: str | None
    city: str | None
    countryCode: str | None
    regionCode: str | None
    languageCode: str | None


def row_to_artist_data(row: _ArtistRow) -> ArtistData:
    """Convert an artist dataframe row or record mapping."""
    path = _optional_text(row["path"])
    if path is None:
        raise ValueError("path must not be missing")
    artist_id = _optional_integer(row["id"])
    if artist_id is None:
        raise ValueError("id must not be missing")
    return ArtistData(
        id=artist_id,
        path=path,
        name=_optional_text(row["name"]),
        city=_optional_text(row["city"]),
        countryCode=_optional_text(row["countrycode"]),
        regionCode=_optional_text(row["regioncode"]),
        languageCode=_optional_text(row["languagecode"]),
    )
