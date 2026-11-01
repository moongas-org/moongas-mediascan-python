from dataclasses import dataclass
from typing import Any


@dataclass
class TrackDataWithAlbumAndArtistData:
    """Track data from a tracks dataframe joined with both album and artist tables."""

    id: int
    path: str
    album_path: str
    artist_path: str
    size: int
    format: str
    title: str
    artist: str
    albumartist: str
    album: str
    genre: str
    year: int
    duration: int
    countryCode: str = ""
    regionCode: str = ""
    city: str = ""
    languageCode: str = ""


def row_to_track_data_with_album_and_artist_data(
    row: Any,
) -> TrackDataWithAlbumAndArtistData:
    return TrackDataWithAlbumAndArtistData(
        id=int(str(row.id)),
        path=str(row.path),
        album_path=str(row.album_path),
        artist_path=str(row.artist_path),
        size=0,
        format="mp3",
        title=str(row.title),
        artist=str(row.artist),
        albumartist=str(row.albumartist),
        album=str(row.album),
        genre=str(row.genre),
        year=int(str(row.year)),
        duration=0,
        countryCode=str(row.countrycode),
        regionCode=str(row.regioncode),
        city=str(row.city),
        languageCode=str(row.languagecode),
    )
