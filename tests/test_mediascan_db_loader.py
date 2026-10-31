import pytest
import pandas as pd
import sqlalchemy

from mediascan.utils.db.mediascan_db_loader import (
    get_df_albums,
    get_df_artists,
    get_df_files_artistdata_joined,
    get_df_tracks,
    get_df_track_streaming,
)


def test_go_database_tables_and_existing_join() -> None:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            for statement in (
                "CREATE TABLE artist (id INTEGER PRIMARY KEY, path TEXT, name TEXT, city TEXT, countrycode TEXT, regioncode TEXT, languagecode TEXT)",
                "CREATE TABLE album (id INTEGER PRIMARY KEY, path TEXT, name TEXT, year INTEGER, explicitcover BOOLEAN)",
                "CREATE TABLE mediafile (id INTEGER PRIMARY KEY, path TEXT, albumpath TEXT, artistpath TEXT, title TEXT, artist TEXT, albumartist TEXT, album TEXT, genre TEXT, year INTEGER)",
                "CREATE TABLE track (id INTEGER PRIMARY KEY, path TEXT, albumpath TEXT, artistpath TEXT, title TEXT, artist TEXT, albumartist TEXT, album TEXT, genre TEXT, year INTEGER)",
                "CREATE TABLE trackstreaming (trackid INTEGER NOT NULL REFERENCES track(id), streamingservice TEXT NOT NULL, streamingtrackid TEXT NOT NULL)",
                "INSERT INTO artist (id, path, name) VALUES (1, '/music/Artist', 'Artist')",
                "INSERT INTO album (id, path, name) VALUES (2, '/music/Artist/Album', 'Album')",
                "INSERT INTO mediafile (id, path, artistpath) VALUES (3, '/music/Artist/Album/Song.flac', '/music/Artist')",
                "INSERT INTO track (id, path, artistpath) VALUES (4, '/music/Artist/Album/Song.yml', '/music/Artist')",
                "INSERT INTO trackstreaming VALUES (4, 'spotify', 'spotify-id')",
            ):
                conn.exec_driver_sql(statement)
        assert get_df_artists(engine)["name"].tolist() == ["Artist"]
        assert get_df_albums(engine)["name"].tolist() == ["Album"]
        assert get_df_tracks(engine)["id"].tolist() == [4]
        streaming = get_df_track_streaming(engine)
        assert streaming.to_dict("records") == [
            {"trackid": 4, "streamingservice": "spotify", "streamingtrackid": "spotify-id"}
        ]
        assert get_df_files_artistdata_joined(engine)["name"].tolist() == ["Artist"]
    finally:
        engine.dispose()


def test_missing_database_table_raises() -> None:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with pytest.raises(pd.errors.DatabaseError, match="no such table: track"):
            get_df_tracks(engine)
    finally:
        engine.dispose()
