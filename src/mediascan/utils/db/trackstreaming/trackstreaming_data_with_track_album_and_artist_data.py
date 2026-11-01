from dataclasses import dataclass
from typing import Protocol

from mediascan.utils.db._dataframe_row import (
    optional_integer as _optional_integer,
    optional_text as _optional_text,
)


class _JoinedTrackStreamingRow(Protocol):
    def __getitem__(self, key: str, /) -> object: ...
    def __contains__(self, key: object, /) -> bool: ...


@dataclass
class TrackStreamingDataWithTrackAlbumAndArtistData:
    """Streaming identifiers with track, album, and artist metadata."""

    track_id: int
    streaming_service: str
    streaming_track_id: str
    path: str | None
    album_path: str | None
    artist_path: str | None
    title: str | None
    artist: str | None
    albumartist: str | None
    album: str | None
    genre: str | None
    year: int | None
    countryCode: str | None
    regionCode: str | None
    city: str | None
    languageCode: str | None


def row_to_trackstreaming_data_with_track_album_and_artist_data(
    row: _JoinedTrackStreamingRow,
) -> TrackStreamingDataWithTrackAlbumAndArtistData:
    """Convert a row from get_df_trackstreaming_track_album_artist_joined."""
    track_id = _optional_integer(row["trackid"])
    if track_id is None:
        raise ValueError("trackid must not be missing")
    streaming_service = _optional_text(row["streamingservice"])
    if streaming_service is None:
        raise ValueError("streamingservice must not be missing")
    streaming_track_id = _optional_text(row["streamingtrackid"])
    if streaming_track_id is None:
        raise ValueError("streamingtrackid must not be missing")
    return TrackStreamingDataWithTrackAlbumAndArtistData(
        track_id=track_id,
        streaming_service=streaming_service,
        streaming_track_id=streaming_track_id,
        path=_optional_text(row["track_path"]),
        album_path=_optional_text(row["album_path"]),
        artist_path=_optional_text(row["artist_path"]),
        title=_optional_text(row["title"]),
        artist=_optional_text(row["artist"]),
        albumartist=_optional_text(row["albumartist"]),
        album=_optional_text(row["album"]),
        genre=_optional_text(
            row["track_genre"] if "track_genre" in row else row["genre"]
        ),
        year=_optional_integer(
            row["track_year"] if "track_year" in row else row["year"]
        ),
        countryCode=_optional_text(row["countrycode"]),
        regionCode=_optional_text(row["regioncode"]),
        city=_optional_text(row["city"]),
        languageCode=_optional_text(row["languagecode"]),
    )
