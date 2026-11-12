from types import SimpleNamespace

import pandas as pd
import pytest
import sqlalchemy

from mediascan.utils.db.track.track_data_with_album_and_artist_data import (
    TrackDataWithAlbumAndArtistData,
    row_to_track_data_with_album_and_artist_data,
)
from mediascan.utils.db.mediascan_db_loader import get_df_track_album_artist_joined


def test_row_to_track_data_with_album_and_artist_data():
    track = row_to_track_data_with_album_and_artist_data(
        SimpleNamespace(
            track_id=1,
            track_path="/music/Artist/Album/track.yml",
            album_path="/music/Artist/Album",
            artist_path="/music/Artist",
            title="Track",
            artist="Artist",
            albumartist="Artist",
            album="Album",
            genre="Rock",
            track_year=2001,
            track_artistid=10,
            albumid=20,
            hasspotify=True,
            hasmedia=True,
            haslyricstxt=False,
            haslyricslrc=True,
            countrycode="US",
            regioncode="CA",
            city="Los Angeles",
            languagecode="en",
        )
    )

    assert isinstance(track, TrackDataWithAlbumAndArtistData)
    assert track.id == 1
    assert track.path == "/music/Artist/Album/track.yml"
    assert track.album_path == "/music/Artist/Album"
    assert track.artist_path == "/music/Artist"
    assert track.artistid == 10
    assert track.albumid == 20
    assert track.countryCode == "US"
    assert track.regionCode == "CA"
    assert track.languageCode == "en"


@pytest.mark.parametrize("album_has_genre", [False, True])
def test_convert_actual_joined_track_dataframe(album_has_genre: bool) -> None:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            for statement in (
                "CREATE TABLE artist (id INTEGER PRIMARY KEY, path TEXT, name TEXT, city TEXT, countrycode TEXT, regioncode TEXT, languagecode TEXT)",
                "CREATE TABLE album (id INTEGER PRIMARY KEY, path TEXT, name TEXT, year INTEGER)",
                "CREATE TABLE track (id INTEGER PRIMARY KEY, path TEXT, albumpath TEXT, artistpath TEXT, title TEXT, artist TEXT, albumartist TEXT, album TEXT, genre TEXT, year INTEGER, artistid INTEGER, albumid INTEGER, hasspotify BOOLEAN NOT NULL DEFAULT FALSE, hasmedia BOOLEAN NOT NULL DEFAULT FALSE, haslyricstxt BOOLEAN NOT NULL DEFAULT FALSE, haslyricslrc BOOLEAN NOT NULL DEFAULT FALSE)",
                "INSERT INTO artist VALUES (10, '/music/Artist', 'Artist', 'Los Angeles', 'US', 'CA', 'en')",
                "INSERT INTO album VALUES (20, '/music/Artist/Album', 'Album', 1999)",
                "INSERT INTO track VALUES (1, '/music/Artist/Album/track.yml', '/music/Artist/Album', '/music/Artist', 'Track', 'Artist', 'Artist', 'Album', 'Rock', 2001, 10, 20, TRUE, TRUE, FALSE, TRUE)",
            ):
                conn.exec_driver_sql(statement)
            if album_has_genre:
                conn.exec_driver_sql("ALTER TABLE album ADD COLUMN genre TEXT")
                conn.exec_driver_sql("UPDATE album SET genre = 'Album genre'")
        dataframe = get_df_track_album_artist_joined(engine)
        _, row = next(dataframe.iterrows())
        track = row_to_track_data_with_album_and_artist_data(row)
        assert track == TrackDataWithAlbumAndArtistData(
            id=1,
            path="/music/Artist/Album/track.yml",
            album_path="/music/Artist/Album",
            artist_path="/music/Artist",
            title="Track",
            artist="Artist",
            albumartist="Artist",
            album="Album",
            genre="Rock",
            year=2001,
            hasspotify=True,
            hasmedia=True,
            haslyricstxt=False,
            haslyricslrc=True,
            artistid=10,
            albumid=20,
            countryCode="US",
            regionCode="CA",
            city="Los Angeles",
            languageCode="en",
        )
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    ("artist_id", "album_id"),
    [(10, 20), (10, None), (None, 20), (None, None), (99, 99)],
)
@pytest.mark.parametrize("year", [2001, None])
def test_convert_nullable_track_from_loader(
    artist_id: int | None,
    album_id: int | None,
    year: int | None,
) -> None:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            for statement in (
                "CREATE TABLE artist (id INTEGER PRIMARY KEY, path TEXT, name TEXT, city TEXT, countrycode TEXT, regioncode TEXT, languagecode TEXT)",
                "CREATE TABLE album (id INTEGER PRIMARY KEY, path TEXT, name TEXT, year INTEGER, genre TEXT)",
                "CREATE TABLE track (id INTEGER PRIMARY KEY, path TEXT, title TEXT, artist TEXT, albumartist TEXT, album TEXT, genre TEXT, year INTEGER, artistid INTEGER, albumid INTEGER, hasspotify BOOLEAN NOT NULL DEFAULT FALSE, hasmedia BOOLEAN NOT NULL DEFAULT FALSE, haslyricstxt BOOLEAN NOT NULL DEFAULT FALSE, haslyricslrc BOOLEAN NOT NULL DEFAULT FALSE)",
                "INSERT INTO artist VALUES (10, '/music/Artist', 'Artist', 'City', 'US', 'CA', 'en')",
                "INSERT INTO album VALUES (20, '/music/Artist/Album', 'Album', 1999, 'Rock')",
            ):
                conn.exec_driver_sql(statement)
            conn.exec_driver_sql(
                "INSERT INTO track (id, path, year, artistid, albumid) "
                "VALUES (1, '/music/track.yml', ?, ?, ?)",
                (year, artist_id, album_id),
            )
        row = get_df_track_album_artist_joined(engine).iloc[0]
        track = row_to_track_data_with_album_and_artist_data(row)
        assert track.id == 1
        assert track.path == "/music/track.yml"
        assert track.year == year
        assert track.hasspotify is False
        assert track.hasmedia is False
        assert track.haslyricstxt is False
        assert track.haslyricslrc is False
        assert track.artistid == artist_id
        assert track.albumid == album_id
        assert track.title is None
        assert track.artist is None
        assert track.albumartist is None
        assert track.album is None
        assert track.genre is None
        assert track.album_path == ("/music/Artist/Album" if album_id == 20 else None)
        assert track.artist_path == ("/music/Artist" if artist_id == 10 else None)
        assert track.city == ("City" if artist_id == 10 else None)
        assert track.countryCode == ("US" if artist_id == 10 else None)
        assert track.regionCode == ("CA" if artist_id == 10 else None)
        assert track.languageCode == ("en" if artist_id == 10 else None)
    finally:
        engine.dispose()


@pytest.fixture
def nullable_track_row() -> SimpleNamespace:
    return SimpleNamespace(
        track_id=1,
        track_path="/music/track.yml",
        album_path=None,
        artist_path=None,
        title=None,
        artist=None,
        albumartist=None,
        album=None,
        track_genre=None,
        track_year=None,
        hasspotify=None,
        hasmedia=None,
        haslyricstxt=None,
        haslyricslrc=None,
        track_artistid=None,
        albumid=None,
        countrycode=None,
        regioncode=None,
        city=None,
        languagecode=None,
    )


@pytest.mark.parametrize("missing", [None, float("nan"), pd.NA])
def test_convert_track_missing_values(
    nullable_track_row: SimpleNamespace,
    missing: object,
) -> None:
    values = vars(nullable_track_row).copy()
    for column in values:
        if column not in ("track_id", "track_path"):
            values[column] = missing
    track = row_to_track_data_with_album_and_artist_data(
        pd.Series(values, dtype=object)
    )
    for field in (
        "album_path",
        "artist_path",
        "title",
        "artist",
        "albumartist",
        "album",
        "genre",
        "year",
        "hasspotify",
        "hasmedia",
        "haslyricstxt",
        "haslyricslrc",
        "artistid",
        "albumid",
        "countryCode",
        "regionCode",
        "city",
        "languageCode",
    ):
        assert getattr(track, field) is None


def test_convert_track_preserves_empty_and_zero_values(
    nullable_track_row: SimpleNamespace,
) -> None:
    nullable_track_row.track_id = 2**63 - 1
    nullable_track_row.title = ""
    nullable_track_row.countrycode = ""
    nullable_track_row.track_year = 0
    track = row_to_track_data_with_album_and_artist_data(nullable_track_row)
    assert track.id == 2**63 - 1
    assert track.title == ""
    assert track.countryCode == ""
    assert track.year == 0


@pytest.mark.parametrize("column", ["track_id", "track_path"])
@pytest.mark.parametrize("missing", [None, float("nan"), pd.NA])
def test_convert_track_requires_identity(
    nullable_track_row: SimpleNamespace,
    column: str,
    missing: object,
) -> None:
    setattr(nullable_track_row, column, missing)
    with pytest.raises(ValueError, match=f"{column} must not be missing"):
        row_to_track_data_with_album_and_artist_data(nullable_track_row)


@pytest.mark.parametrize(
    ("column", "value", "error"),
    [
        ("track_id", 1.5, ValueError),
        ("track_id", True, TypeError),
        ("track_year", "bad", TypeError),
        ("track_year", 2001.5, ValueError),
        ("track_year", True, TypeError),
        ("title", 123, TypeError),
    ],
)
def test_convert_track_rejects_invalid_metadata(
    nullable_track_row: SimpleNamespace,
    column: str,
    value: object,
    error: type[Exception],
) -> None:
    setattr(nullable_track_row, column, value)
    with pytest.raises(error):
        row_to_track_data_with_album_and_artist_data(nullable_track_row)
