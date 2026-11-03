from dataclasses import asdict

import pandas as pd
import pytest
import sqlalchemy

from mediascan.utils.db.mediascan_db_loader import get_df_track
from mediascan.utils.db.track.track_data import TrackData, row_to_track_data


@pytest.fixture
def tracks() -> pd.DataFrame:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql(
                "CREATE TABLE track (id INTEGER PRIMARY KEY, path TEXT, "
                "albumpath TEXT, artistpath TEXT, title TEXT, artist TEXT, "
                "albumartist TEXT, album TEXT, genre TEXT, year INTEGER, "
                "artistid INTEGER, albumid INTEGER, hasspotify BOOLEAN NOT NULL)"
            )
            conn.exec_driver_sql(
                "INSERT INTO track VALUES "
                "(1, '/music/Artist/Album/track.yml', '/music/Artist/Album', "
                "'/music/Artist', 'Title', 'Artist', 'Album artist', 'Album', "
                "'Genre', 2002, 10, 20, TRUE)"
            )
        return get_df_track(engine)
    finally:
        engine.dispose()


def test_convert_track_row(tracks: pd.DataFrame) -> None:
    row = tracks.iloc[0]
    track = row_to_track_data(row)

    assert isinstance(track, TrackData)
    assert asdict(track) == {
        "id": 1,
        "path": "/music/Artist/Album/track.yml",
        "album_path": "/music/Artist/Album",
        "artist_path": "/music/Artist",
        "title": "Title",
        "artist": "Artist",
        "albumartist": "Album artist",
        "album": "Album",
        "genre": "Genre",
        "year": 2002,
        "artistid": 10,
        "albumid": 20,
        "hasspotify": True,
    }
    assert row_to_track_data(row.to_dict()) == track


@pytest.mark.parametrize(
    ("column", "value", "error"),
    [
        ("id", None, ValueError),
        ("path", None, ValueError),
        ("hasspotify", None, ValueError),
        ("year", "bad", TypeError),
        ("year", 2001.5, ValueError),
        ("title", 123, TypeError),
    ],
)
def test_convert_invalid_values_raises(
    tracks: pd.DataFrame,
    column: str,
    value: object,
    error: type[Exception],
) -> None:
    row = tracks.iloc[0].to_dict()
    row[column] = value
    with pytest.raises(error):
        row_to_track_data(row)
