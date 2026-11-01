from dataclasses import asdict

import pandas as pd
import pytest
import sqlalchemy

from mediascan.utils.db.album.album_data_with_artist_data import (
    AlbumDataWithArtistData,
    row_to_album_data_with_artist_data,
)
from mediascan.utils.db.mediascan_db_loader import get_df_album_artist_joined


@pytest.fixture
def joined_albums() -> pd.DataFrame:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            for statement in (
                "CREATE TABLE artist (id INTEGER PRIMARY KEY, path TEXT UNIQUE, name TEXT, city TEXT, countrycode TEXT, regioncode TEXT, languagecode TEXT)",
                "CREATE TABLE album (id INTEGER PRIMARY KEY, path TEXT UNIQUE, name TEXT, year INTEGER, explicitcover BOOLEAN, artistid INTEGER, genre TEXT)",
                "INSERT INTO artist VALUES (10, '/music/Artist', 'Artist', 'Los Angeles', 'US', 'CA', 'en')",
                "INSERT INTO album VALUES (20, '/music/Artist/Album', 'Album', 2001, 0, 10, 'Rock')",
                "INSERT INTO album VALUES (21, '/music/Missing/Album', 'Orphan', NULL, NULL, 99, NULL)",
            ):
                conn.exec_driver_sql(statement)
        return get_df_album_artist_joined(engine)
    finally:
        engine.dispose()


def test_convert_joined_album_row(joined_albums: pd.DataFrame) -> None:
    row = joined_albums.iloc[0]
    album = row_to_album_data_with_artist_data(row)

    assert isinstance(album, AlbumDataWithArtistData)
    assert asdict(album) == {
        "id": 20,
        "path": "/music/Artist/Album",
        "name": "Album",
        "year": 2001,
        "explicitcover": False,
        "artistid": 10,
        "genre": "Rock",
        "artist_path": "/music/Artist",
        "artist_name": "Artist",
        "city": "Los Angeles",
        "countryCode": "US",
        "regionCode": "CA",
        "languageCode": "en",
    }
    assert row_to_album_data_with_artist_data(row.to_dict()) == album


def test_convert_album_without_matching_artist(joined_albums: pd.DataFrame) -> None:
    row = joined_albums.loc[joined_albums["album_id"] == 21].iloc[0]
    album = row_to_album_data_with_artist_data(row)

    assert album.id == 21
    assert album.name == "Orphan"
    assert album.artistid == 99
    assert album.explicitcover is None
    assert album.artist_path is None
    assert album.artist_name is None
    assert album.countryCode is None


@pytest.mark.parametrize(
    ("column", "value", "error"),
    [
        ("album_id", None, ValueError),
        ("album_path", None, ValueError),
        ("explicitcover", 2, ValueError),
        ("album_name", 123, TypeError),
    ],
)
def test_convert_invalid_values_raises(
    joined_albums: pd.DataFrame,
    column: str,
    value: object,
    error: type[Exception],
) -> None:
    row = joined_albums.iloc[0].to_dict()
    row[column] = value
    with pytest.raises(error):
        row_to_album_data_with_artist_data(row)
