from dataclasses import asdict

import pandas as pd
import pytest
import sqlalchemy

from mediascan.utils.db.mediafile.mediafile_data_with_album_and_artist_data import (
    MediaFileDataWithAlbumAndArtistData,
    row_to_mediafile_data_with_album_and_artist_data,
)
from mediascan.utils.db.mediascan_db_loader import (
    get_df_mediafile_track_album_artist_joined,
)


@pytest.fixture
def joined_mediafiles() -> pd.DataFrame:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            for statement in (
                "CREATE TABLE artist (id INTEGER PRIMARY KEY, path TEXT, name TEXT, city TEXT, countrycode TEXT, regioncode TEXT, languagecode TEXT)",
                "CREATE TABLE album (id INTEGER PRIMARY KEY, path TEXT, name TEXT, year INTEGER, explicitcover BOOLEAN, artistid INTEGER, genre TEXT)",
                "CREATE TABLE track (id INTEGER PRIMARY KEY, path TEXT, albumpath TEXT, artistpath TEXT, title TEXT, artist TEXT, albumartist TEXT, album TEXT, genre TEXT, year INTEGER, artistid INTEGER, albumid INTEGER)",
                "CREATE TABLE mediafile (id INTEGER PRIMARY KEY, path TEXT, albumpath TEXT, artistpath TEXT, title TEXT, artist TEXT, albumartist TEXT, album TEXT, genre TEXT, year INTEGER, size INTEGER, format TEXT, duration REAL, artistid INTEGER, albumid INTEGER, trackid INTEGER)",
                "INSERT INTO artist VALUES (10, '/music/Artist', 'Artist', 'Los Angeles', 'US', 'CA', 'en')",
                "INSERT INTO album VALUES (20, '/music/Artist/Album', 'Album', 2001, 0, 10, 'Album genre')",
                "INSERT INTO track VALUES (30, '/music/Artist/Album/track.yml', '/music/Artist/Album', '/music/Artist', 'Track title', 'Track artist', 'Track albumartist', 'Track album', 'Track genre', 2001, 10, 20)",
                "INSERT INTO mediafile VALUES (1, '/music/Artist/Album/song.flac', '/music/Artist/Album', '/music/Artist', 'File title', 'File artist', 'File albumartist', 'File album', 'File genre', 2002, 12345, 'flac', 201.5, 10, 20, 30)",
                "INSERT INTO mediafile VALUES (2, '/music/orphan.flac', '/music/Missing', '/music/Missing', 'Orphan', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)",
                "INSERT INTO mediafile VALUES (3, '/music/unmatched.flac', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 2003, NULL, NULL, NULL, NULL, NULL, 99)",
            ):
                conn.exec_driver_sql(statement)
        return get_df_mediafile_track_album_artist_joined(engine)
    finally:
        engine.dispose()


def test_convert_joined_mediafile_row(joined_mediafiles: pd.DataFrame) -> None:
    row = joined_mediafiles.loc[joined_mediafiles["mediafile_id"] == 1].iloc[0]
    mediafile = row_to_mediafile_data_with_album_and_artist_data(row)

    assert isinstance(mediafile, MediaFileDataWithAlbumAndArtistData)
    assert asdict(mediafile) == {
        "id": 1,
        "path": "/music/Artist/Album/song.flac",
        "album_path": "/music/Artist/Album",
        "artist_path": "/music/Artist",
        "title": "File title",
        "artist": "File artist",
        "albumartist": "File albumartist",
        "album": "File album",
        "genre": "File genre",
        "year": 2002,
        "artistid": 10,
        "albumid": 20,
        "trackid": 30,
        "size": 12345,
        "format": "flac",
        "duration": 201.5,
        "countryCode": "US",
        "regionCode": "CA",
        "city": "Los Angeles",
        "languageCode": "en",
    }
    assert row_to_mediafile_data_with_album_and_artist_data(row.to_dict()) == mediafile


@pytest.mark.parametrize("mediafile_id", [2, 3])
def test_convert_mediafile_without_track(
    joined_mediafiles: pd.DataFrame,
    mediafile_id: int,
) -> None:
    row = joined_mediafiles.loc[joined_mediafiles["mediafile_id"] == mediafile_id].iloc[
        0
    ]
    mediafile = row_to_mediafile_data_with_album_and_artist_data(row)

    assert mediafile.id == mediafile_id
    assert mediafile.album_path is None
    assert mediafile.artist_path is None
    assert mediafile.countryCode is None
    assert mediafile.regionCode is None
    assert mediafile.city is None
    assert mediafile.languageCode is None
    if mediafile_id == 2:
        assert mediafile.title == "Orphan"
        assert mediafile.year is None
    else:
        assert mediafile.title is None
        assert mediafile.year == 2003


@pytest.mark.parametrize("missing", [None, float("nan"), pd.NA])
def test_convert_missing_values(
    joined_mediafiles: pd.DataFrame, missing: object
) -> None:
    row = joined_mediafiles.iloc[0].to_dict()
    row["city"] = missing
    row["mediafile_year"] = missing
    mediafile = row_to_mediafile_data_with_album_and_artist_data(row)
    assert mediafile.city is None
    assert mediafile.year is None


def test_convert_preserves_large_integer_id(joined_mediafiles: pd.DataFrame) -> None:
    row = joined_mediafiles.iloc[0].to_dict()
    row["mediafile_id"] = 2**63 - 1
    assert row_to_mediafile_data_with_album_and_artist_data(row).id == 2**63 - 1


@pytest.mark.parametrize(
    ("column", "value", "error"),
    [
        ("mediafile_id", None, ValueError),
        ("mediafile_path", None, ValueError),
        ("mediafile_year", "bad", TypeError),
        ("mediafile_year", 2001.5, ValueError),
        ("mediafile_title", 123, TypeError),
    ],
)
def test_convert_invalid_values_raises(
    joined_mediafiles: pd.DataFrame,
    column: str,
    value: object,
    error: type[Exception],
) -> None:
    row = joined_mediafiles.iloc[0].to_dict()
    row[column] = value
    with pytest.raises(error):
        row_to_mediafile_data_with_album_and_artist_data(row)
