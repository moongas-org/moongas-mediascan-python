from dataclasses import dataclass
from typing import Any

from mediascan.utils.db._dataframe_row import (
    optional_boolean,
    optional_integer,
    optional_text,
)


@dataclass
class TrackDataWithAlbumAndArtistData:
    """Track data from a tracks dataframe joined with both album and artist tables."""

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
    hasspotify: bool | None
    hasmedia: bool | None
    haslyricstxt: bool | None
    haslyricslrc: bool | None
    artistid: int | None = None
    albumid: int | None = None
    countryCode: str | None = None
    regionCode: str | None = None
    city: str | None = None
    languageCode: str | None = None


def row_to_track_data_with_album_and_artist_data(
    row: Any,
) -> TrackDataWithAlbumAndArtistData:
    """Convert a row from get_df_track_album_artist_joined using its column aliases."""
    track_id = optional_integer(row.track_id)
    if track_id is None:
        raise ValueError("track_id must not be missing")
    path = optional_text(row.track_path)
    if path is None:
        raise ValueError("track_path must not be missing")
    return TrackDataWithAlbumAndArtistData(
        id=track_id,
        path=path,
        album_path=optional_text(row.album_path),
        artist_path=optional_text(row.artist_path),
        title=optional_text(row.title),
        artist=optional_text(row.artist),
        albumartist=optional_text(row.albumartist),
        album=optional_text(row.album),
        genre=optional_text(row.track_genre if hasattr(row, "track_genre") else row.genre),
        year=optional_integer(row.track_year),
        hasspotify=optional_boolean(row.hasspotify),
        hasmedia=optional_boolean(row.hasmedia),
        haslyricstxt=optional_boolean(row.haslyricstxt),
        haslyricslrc=optional_boolean(row.haslyricslrc),
        artistid=optional_integer(
            row.track_artistid if hasattr(row, "track_artistid") else row.artistid
        ),
        albumid=optional_integer(row.albumid),
        countryCode=optional_text(row.countrycode),
        regionCode=optional_text(row.regioncode),
        city=optional_text(row.city),
        languageCode=optional_text(row.languagecode),
    )
