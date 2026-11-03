import pytest
import pandas as pd
import sqlalchemy

from mediascan.utils.db.mediascan_db_loader import (
    get_df_album,
    get_df_album_artist_joined,
    get_df_artist,
    get_df_mediafile,
    get_df_mediafile_track_album_artist_joined,
    get_df_track,
    get_df_track_album_artist_joined,
    get_df_trackstreaming,
    get_df_trackstreaming_track_album_artist_joined,
)


def test_go_database_tables_and_existing_join() -> None:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            for statement in (
                "CREATE TABLE artist (id INTEGER PRIMARY KEY, path TEXT, name TEXT, city TEXT, countrycode TEXT, regioncode TEXT, languagecode TEXT)",
                "CREATE TABLE album (id INTEGER PRIMARY KEY, path TEXT, name TEXT, year INTEGER, explicitcover BOOLEAN)",
                "CREATE TABLE mediafile (id INTEGER PRIMARY KEY, path TEXT, trackid INTEGER REFERENCES track(id))",
                "CREATE TABLE track (id INTEGER PRIMARY KEY, path TEXT, albumpath TEXT, artistpath TEXT, title TEXT, artist TEXT, albumartist TEXT, album TEXT, genre TEXT, year INTEGER, artistid INTEGER REFERENCES artist(id), albumid INTEGER REFERENCES album(id), hasspotify BOOLEAN NOT NULL DEFAULT FALSE)",
                "CREATE TABLE trackstreaming (trackid INTEGER NOT NULL REFERENCES track(id), streamingservice TEXT NOT NULL, streamingtrackid TEXT NOT NULL)",
                "INSERT INTO artist (id, path, name) VALUES (1, '/music/Artist', 'Artist')",
                "INSERT INTO album (id, path, name) VALUES (2, '/music/Artist/Album', 'Album')",
                "INSERT INTO mediafile (id, path, trackid) VALUES (3, '/music/Artist/Album/Song.flac', 4)",
                "INSERT INTO track (id, path, artistpath, artistid, albumid) VALUES (4, '/music/Artist/Album/Song.yml', '/music/Artist', 1, 2)",
                "INSERT INTO trackstreaming VALUES (4, 'spotify', 'spotify-id')",
            ):
                conn.exec_driver_sql(statement)
        assert get_df_artist(engine)["name"].tolist() == ["Artist"]
        assert get_df_album(engine)["name"].tolist() == ["Album"]
        assert get_df_track(engine)["id"].tolist() == [4]
        assert get_df_track(engine)["hasspotify"].tolist() == [0]
        streaming = get_df_trackstreaming(engine)
        assert streaming.to_dict("records") == [
            {"trackid": 4, "streamingservice": "spotify", "streamingtrackid": "spotify-id"}
        ]
        joined = get_df_track_album_artist_joined(engine)
        assert joined.loc[0, "artist_name"] == "Artist"
        assert joined.loc[0, "album_name"] == "Album"
        assert joined.loc[0, "hasspotify"] == 0
        assert joined.columns.is_unique
        assert get_df_mediafile(engine)["id"].tolist() == [3]
        mediafile_joined = get_df_mediafile_track_album_artist_joined(engine)
        assert mediafile_joined["trackid"].tolist() == [4]
        assert mediafile_joined["track_id"].tolist() == [4]
        assert mediafile_joined.columns.is_unique
        streaming_joined = get_df_trackstreaming_track_album_artist_joined(engine)
        assert streaming_joined["artist_name"].tolist() == ["Artist"]
        assert streaming_joined["album_name"].tolist() == ["Album"]
        assert streaming_joined.columns.is_unique
    finally:
        engine.dispose()


def test_missing_database_table_raises() -> None:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with pytest.raises(pd.errors.DatabaseError, match="no such table: track"):
            get_df_track(engine)
    finally:
        engine.dispose()


def test_album_join_uses_ids_and_preserves_missing_relations() -> None:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            for statement in (
                "CREATE TABLE artist (id INTEGER PRIMARY KEY, path TEXT, name TEXT, city TEXT)",
                "CREATE TABLE album (id INTEGER PRIMARY KEY, path TEXT, name TEXT, year INTEGER, artistid INTEGER)",
                "INSERT INTO artist VALUES (10, '/music/Artist', 'Artist', 'City')",
                "INSERT INTO album VALUES (1, '/music/Artist/Album', 'Matched', 2026, 10)",
                "INSERT INTO album VALUES (2, '/music/Other/Album', 'Missing', 2025, NULL)",
                "INSERT INTO album VALUES (3, '/music/Artist/Other', 'Unmatched', 2024, 99)",
            ):
                conn.exec_driver_sql(statement)
        joined = get_df_album_artist_joined(engine)
        expected_columns = [
            "album_id", "album_path", "album_name", "year", "artistid",
            "artist_id", "artist_path", "artist_name", "city",
        ]
        assert joined.columns.tolist() == expected_columns
        assert joined.columns.is_unique
        assert len(joined) == 3
        albums = joined.set_index("album_name")
        assert albums.loc["Matched", "album_id"] == 1
        assert albums.loc["Matched", "artist_id"] == 10
        assert albums.loc["Matched", "artist_name"] == "Artist"
        assert albums.loc["Matched", "city"] == "City"
        assert albums.loc["Matched", "album_path"] == "/music/Artist/Album"
        assert albums.loc["Matched", "artist_path"] == "/music/Artist"
        assert albums.loc["Matched", "year"] == 2026
        for name in ("Missing", "Unmatched"):
            assert pd.isna(albums.loc[name, "artist_id"])
            assert pd.isna(albums.loc[name, "artist_name"])
        with engine.begin() as conn:
            conn.exec_driver_sql("DELETE FROM album")
        empty = get_df_album_artist_joined(engine)
        assert empty.empty
        assert empty.columns.tolist() == expected_columns
    finally:
        engine.dispose()


def test_album_join_aliases_do_not_collide_with_existing_columns() -> None:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql("CREATE TABLE artist (id INTEGER PRIMARY KEY, name TEXT)")
            conn.exec_driver_sql(
                "CREATE TABLE album (id INTEGER PRIMARY KEY, name TEXT, artistid INTEGER, album_name TEXT, album_name_2 TEXT)"
            )
            conn.exec_driver_sql("INSERT INTO artist VALUES (10, 'Artist')")
            conn.exec_driver_sql("INSERT INTO album VALUES (1, 'Album', 10, 'Existing', 'Also existing')")
        joined = get_df_album_artist_joined(engine)
        assert joined.columns.is_unique
        assert joined.loc[0, "album_name"] == "Existing"
        assert joined.loc[0, "album_name_2"] == "Also existing"
        assert joined.loc[0, "album_name_3"] == "Album"
        assert joined.loc[0, "artist_name"] == "Artist"
    finally:
        engine.dispose()


def test_track_join_uses_ids_and_preserves_missing_relations() -> None:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            for statement in (
                "CREATE TABLE artist (id INTEGER PRIMARY KEY, name TEXT, city TEXT)",
                "CREATE TABLE album (id INTEGER PRIMARY KEY, name TEXT, explicitcover BOOLEAN)",
                "CREATE TABLE track (id INTEGER PRIMARY KEY, title TEXT, artistid INTEGER, albumid INTEGER)",
                "INSERT INTO artist VALUES (10, 'Artist', 'City')",
                "INSERT INTO album VALUES (20, 'Album', 1)",
                "INSERT INTO track VALUES (1, 'Both', 10, 20)",
                "INSERT INTO track VALUES (2, 'Artist only', 10, NULL)",
                "INSERT INTO track VALUES (3, 'Album only', NULL, 20)",
                "INSERT INTO track VALUES (4, 'Neither', NULL, NULL)",
                "INSERT INTO track VALUES (5, 'Unmatched', 99, 99)",
            ):
                conn.exec_driver_sql(statement)
        joined = get_df_track_album_artist_joined(engine).set_index("title")
        assert len(joined) == 5
        assert joined.loc["Both", "city"] == "City"
        assert joined.loc["Both", "explicitcover"] == 1
        assert joined.loc["Both", "artist_name"] == "Artist"
        assert joined.loc["Both", "album_name"] == "Album"
        assert joined.columns.is_unique
        assert joined.loc["Artist only", "city"] == "City"
        assert pd.isna(joined.loc["Artist only", "explicitcover"])
        assert pd.isna(joined.loc["Album only", "city"])
        assert joined.loc["Album only", "explicitcover"] == 1
        assert pd.isna(joined.loc["Neither", "artist_name"])
        assert pd.isna(joined.loc["Neither", "album_name"])
        assert pd.isna(joined.loc["Unmatched", "artist_name"])
        assert pd.isna(joined.loc["Unmatched", "album_name"])
        with engine.begin() as conn:
            conn.exec_driver_sql("DELETE FROM track")
        empty = get_df_track_album_artist_joined(engine)
        assert empty.empty
        assert "city" in empty.columns
        assert "explicitcover" in empty.columns
    finally:
        engine.dispose()
