from dataclasses import asdict

import pandas as pd
import pytest
import sqlalchemy

from mediascan.utils.db.mediascan_db_loader import (
    get_df_trackstreaming_track_album_artist_joined,
)
from mediascan.utils.db.trackstreaming.trackstreaming_data_with_track_album_and_artist_data import (
    TrackStreamingDataWithTrackAlbumAndArtistData,
    row_to_trackstreaming_data_with_track_album_and_artist_data,
)


@pytest.fixture
def joined_trackstreaming() -> pd.DataFrame:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            for statement in (
                "CREATE TABLE artist (id INTEGER PRIMARY KEY, path TEXT, name TEXT, city TEXT, countrycode TEXT, regioncode TEXT, languagecode TEXT)",
                "CREATE TABLE album (id INTEGER PRIMARY KEY, path TEXT, name TEXT, year INTEGER, genre TEXT)",
                "CREATE TABLE track (id INTEGER PRIMARY KEY, path TEXT, albumpath TEXT, artistpath TEXT, title TEXT, artist TEXT, albumartist TEXT, album TEXT, genre TEXT, year INTEGER, artistid INTEGER, albumid INTEGER)",
                "CREATE TABLE trackstreaming (trackid INTEGER NOT NULL, streamingservice TEXT NOT NULL, streamingtrackid TEXT NOT NULL)",
                "INSERT INTO artist VALUES (10, '/music/Artist', 'Artist', 'City', 'US', 'CA', 'en')",
                "INSERT INTO album VALUES (20, '/music/Artist/Album', 'Album', 2000, 'Album genre')",
                "INSERT INTO track VALUES (4, '/music/Artist/Album/track.yml', '/music/Artist/Album', '/music/Artist', 'Title', 'Artist', 'Album artist', 'Album', 'Track genre', 2001, 10, 20)",
                "INSERT INTO trackstreaming VALUES (4, 'spotify', 'spotify-id')",
                "INSERT INTO trackstreaming VALUES (99, 'apple-music', 'apple-id')",
            ):
                conn.exec_driver_sql(statement)
        return get_df_trackstreaming_track_album_artist_joined(engine)
    finally:
        engine.dispose()


def test_convert_joined_trackstreaming_row(
    joined_trackstreaming: pd.DataFrame,
) -> None:
    row = joined_trackstreaming.iloc[0]
    streaming = row_to_trackstreaming_data_with_track_album_and_artist_data(row)

    assert isinstance(streaming, TrackStreamingDataWithTrackAlbumAndArtistData)
    assert asdict(streaming) == {
        "track_id": 4,
        "streaming_service": "spotify",
        "streaming_track_id": "spotify-id",
        "path": "/music/Artist/Album/track.yml",
        "album_path": "/music/Artist/Album",
        "artist_path": "/music/Artist",
        "title": "Title",
        "artist": "Artist",
        "albumartist": "Album artist",
        "album": "Album",
        "genre": "Track genre",
        "year": 2001,
        "countryCode": "US",
        "regionCode": "CA",
        "city": "City",
        "languageCode": "en",
    }
    assert (
        row_to_trackstreaming_data_with_track_album_and_artist_data(row.to_dict())
        == streaming
    )


def test_convert_without_matching_track(
    joined_trackstreaming: pd.DataFrame,
) -> None:
    row = joined_trackstreaming.loc[joined_trackstreaming["trackid"] == 99].iloc[0]
    streaming = row_to_trackstreaming_data_with_track_album_and_artist_data(row)

    assert streaming.track_id == 99
    assert streaming.streaming_service == "apple-music"
    assert streaming.streaming_track_id == "apple-id"
    assert streaming.path is None
    assert streaming.title is None
    assert streaming.album_path is None
    assert streaming.artist_path is None


@pytest.mark.parametrize(
    ("column", "value", "error"),
    [
        ("trackid", None, ValueError),
        ("streamingservice", None, ValueError),
        ("streamingtrackid", None, ValueError),
        ("title", 123, TypeError),
    ],
)
def test_convert_invalid_values_raises(
    joined_trackstreaming: pd.DataFrame,
    column: str,
    value: object,
    error: type[Exception],
) -> None:
    row = joined_trackstreaming.iloc[0].to_dict()
    row[column] = value
    with pytest.raises(error):
        row_to_trackstreaming_data_with_track_album_and_artist_data(row)
