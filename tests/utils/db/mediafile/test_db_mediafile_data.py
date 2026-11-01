from dataclasses import asdict

import pandas as pd
import pytest
import sqlalchemy

from mediascan.utils.db.mediafile.mediafile_data import (
    MediaFileData,
    row_to_mediafile_data,
)
from mediascan.utils.db.mediascan_db_loader import get_df_mediafile


@pytest.fixture
def mediafiles() -> pd.DataFrame:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql(
                "CREATE TABLE mediafile (id INTEGER PRIMARY KEY, path TEXT, "
                "albumpath TEXT, artistpath TEXT, title TEXT, artist TEXT, "
                "albumartist TEXT, album TEXT, genre TEXT, year INTEGER, "
                "size INTEGER, format TEXT, duration REAL, "
                "artistid INTEGER, albumid INTEGER, trackid INTEGER)"
            )
            conn.exec_driver_sql(
                "INSERT INTO mediafile VALUES "
                "(1, '/music/Artist/Album/song.flac', '/music/Artist/Album', "
                "'/music/Artist', 'Title', 'Artist', 'Album artist', 'Album', "
                "'Genre', 2002, 12345, 'flac', 201.5, 10, 20, 30)"
            )
        return get_df_mediafile(engine)
    finally:
        engine.dispose()


def test_convert_mediafile_row(mediafiles: pd.DataFrame) -> None:
    row = mediafiles.iloc[0]
    mediafile = row_to_mediafile_data(row)

    assert isinstance(mediafile, MediaFileData)
    assert asdict(mediafile) == {
        "id": 1,
        "path": "/music/Artist/Album/song.flac",
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
        "trackid": 30,
        "size": 12345,
        "format": "flac",
        "duration": 201.5,
    }
    assert row_to_mediafile_data(row.to_dict()) == mediafile


@pytest.mark.parametrize(
    ("column", "value", "error"),
    [
        ("id", None, ValueError),
        ("path", None, ValueError),
        ("year", "bad", TypeError),
        ("year", 2001.5, ValueError),
        ("title", 123, TypeError),
    ],
)
def test_convert_invalid_values_raises(
    mediafiles: pd.DataFrame,
    column: str,
    value: object,
    error: type[Exception],
) -> None:
    row = mediafiles.iloc[0].to_dict()
    row[column] = value
    with pytest.raises(error):
        row_to_mediafile_data(row)
