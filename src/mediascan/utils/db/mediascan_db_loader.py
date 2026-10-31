from pathlib import Path
from urllib.parse import urlparse
import pandas as pd
import sqlalchemy

"""
Utility functions for working with moongas mediascan.db
"""


def load_db(db_path: str = "sqlite:///../../out/mediascan.db"):
    """
    Load a Moongas sqlite3 database file
    """
    parsed = urlparse(db_path)

    # Extract relative or absolute path from sqlite URL
    if parsed.scheme == "sqlite":
        # Handle file paths (handles sqlite:///path/to/db or relative sqlite:///../db)
        raw_path = parsed.path
        # On Unix, a relative path like 'sqlite:///../../db' leaves leading slashes on path
        # Normalizing via Path strips redundant slashes while maintaining relative depth
        file_path = (
            Path(raw_path.lstrip("/"))
            if raw_path.startswith("/") and not raw_path.startswith("////")
            else Path(raw_path)
        )

        if not file_path.exists():
            raise FileNotFoundError(
                f"Moongas database file '{db_path}' not found at resolve path '{file_path.resolve()}' (Current Working Directory: {Path.cwd()})"
            )

    engine = sqlalchemy.create_engine(db_path)
    return engine


def get_df_artist(engine: sqlalchemy.Engine):
    with engine.connect() as conn:
        artists = pd.read_sql_query("SELECT * FROM artist", conn)
        return artists


def get_df_album(engine: sqlalchemy.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql_query("SELECT * FROM album", conn)


def get_df_track(engine: sqlalchemy.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql_query("SELECT * FROM track", conn)


def get_df_trackstreaming(engine: sqlalchemy.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql_query("SELECT * FROM trackstreaming", conn)


def get_df_track_album_artist_joined(engine: sqlalchemy.Engine) -> pd.DataFrame:
    """Return track, artist, and album columns, retaining tracks without related rows."""
    with engine.connect() as conn:
        files = pd.read_sql_query(
            "SELECT track.*, artist.*, album.* FROM track "
            "LEFT JOIN artist ON track.artistid = artist.id "
            "LEFT JOIN album ON track.albumid = album.id",
            conn,
        )
        return files


def get_df_mediafile(engine: sqlalchemy.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql_query("SELECT * FROM mediafile", conn)


def get_df_mediafile_track_album_artist_joined(
    engine: sqlalchemy.Engine,
) -> pd.DataFrame:
    """Return mediafile, track, album, and artist columns, retaining mediafiles without related rows."""
    with engine.connect() as conn:
        return pd.read_sql_query(
            "SELECT mediafile.*, track.*, album.*, artist.* FROM mediafile "
            "LEFT JOIN track ON mediafile.trackid = track.id "
            "LEFT JOIN album ON track.albumid = album.id "
            "LEFT JOIN artist ON track.artistid = artist.id",
            conn,
        )


def get_df_trackstreaming_track_album_artist_joined(
    engine: sqlalchemy.Engine,
) -> pd.DataFrame:
    """Return trackstreaming, track, album, and artist columns, retaining trackstreaming without related rows."""
    with engine.connect() as conn:
        return pd.read_sql_query(
            "SELECT trackstreaming.*, track.*, album.*, artist.* FROM trackstreaming "
            "LEFT JOIN track ON trackstreaming.trackid = track.id "
            "LEFT JOIN album ON track.albumid = album.id "
            "LEFT JOIN artist ON track.artistid = artist.id",
            conn,
        )
