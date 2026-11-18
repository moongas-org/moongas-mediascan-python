from dataclasses import dataclass
from typing import Protocol

from mediascan.utils.db._dataframe_row import (
    optional_boolean as _optional_boolean,
    optional_integer as _optional_integer,
    optional_text as _optional_text,
)


class _AlbumRow(Protocol):
    def __getitem__(self, key: str, /) -> object: ...


@dataclass
class AlbumData:
    """Album metadata from the album table."""

    id: int
    path: str
    name: str | None
    year: int | None
    explicitcover: bool | None
    artistid: int | None
    genre: str | None
    hasalbumyaml: bool


def row_to_album_data(row: _AlbumRow) -> AlbumData:
    """Convert an album dataframe row or record mapping."""
    path = _optional_text(row["path"])
    if path is None:
        raise ValueError("path must not be missing")
    album_id = _optional_integer(row["id"])
    if album_id is None:
        raise ValueError("id must not be missing")
    has_album_yaml = _optional_boolean(row["hasalbumyaml"])
    if has_album_yaml is None:
        raise ValueError("hasalbumyaml must not be missing")
    return AlbumData(
        id=album_id,
        path=path,
        name=_optional_text(row["name"]),
        year=_optional_integer(row["year"]),
        explicitcover=_optional_boolean(row["explicitcover"]),
        artistid=_optional_integer(row["artistid"]),
        genre=_optional_text(row["genre"]),
        hasalbumyaml=has_album_yaml,
    )
