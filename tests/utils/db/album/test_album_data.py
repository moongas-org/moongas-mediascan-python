from dataclasses import asdict

import pandas as pd
import pytest
import sqlalchemy

from mediascan.utils.db.album.album_data import AlbumData, row_to_album_data
from mediascan.utils.db.mediascan_db_loader import get_df_album


@pytest.fixture
def albums() -> pd.DataFrame:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql(
                "CREATE TABLE album (id INTEGER PRIMARY KEY, path TEXT UNIQUE, "
                "name TEXT, year INTEGER, explicitcover BOOLEAN, "
                "artistid INTEGER, genre TEXT)"
            )
            conn.exec_driver_sql(
                "INSERT INTO album VALUES "
                "(20, '/music/Artist/Album', 'Album', 2001, 1, 10, 'Rock')"
            )
            conn.exec_driver_sql(
                "INSERT INTO album VALUES "
                "(21, '/music/Artist/Other', NULL, NULL, NULL, NULL, NULL)"
            )
        return get_df_album(engine)
    finally:
        engine.dispose()


def test_convert_album_row(albums: pd.DataFrame) -> None:
    row = albums.iloc[0]
    album = row_to_album_data(row)

    assert isinstance(album, AlbumData)
    assert asdict(album) == {
        "id": 20,
        "path": "/music/Artist/Album",
        "name": "Album",
        "year": 2001,
        "explicitcover": True,
        "artistid": 10,
        "genre": "Rock",
    }
    assert row_to_album_data(row.to_dict()) == album


def test_convert_album_with_missing_metadata(albums: pd.DataFrame) -> None:
    album = row_to_album_data(albums.iloc[1])
    assert album.id == 21
    assert album.name is None
    assert album.year is None
    assert album.explicitcover is None
    assert album.artistid is None
    assert album.genre is None


@pytest.mark.parametrize(
    ("column", "value", "error"),
    [
        ("id", None, ValueError),
        ("path", None, ValueError),
        ("year", "bad", TypeError),
        ("explicitcover", 2, ValueError),
        ("explicitcover", "yes", TypeError),
        ("genre", 123, TypeError),
    ],
)
def test_convert_invalid_values_raises(
    albums: pd.DataFrame,
    column: str,
    value: object,
    error: type[Exception],
) -> None:
    row = albums.iloc[0].to_dict()
    row[column] = value
    with pytest.raises(error):
        row_to_album_data(row)
