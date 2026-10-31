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


def _read_joined_tables(
    conn: sqlalchemy.Connection,
    tables: tuple[str, ...],
    from_clause: str,
) -> pd.DataFrame:
    columns_by_table = {
        table: [column["name"] for column in sqlalchemy.inspect(conn).get_columns(table)]
        for table in tables
    }
    column_counts: dict[str, int] = {}
    for columns in columns_by_table.values():
        for column in columns:
            column_counts[column] = column_counts.get(column, 0) + 1

    reserved_names = {
        column for column, count in column_counts.items() if count == 1
    }
    used_names: set[str] = set()
    quote = conn.dialect.identifier_preparer.quote
    selections: list[str] = []
    for table, columns in columns_by_table.items():
        for column in columns:
            name = column
            if column_counts[column] > 1:
                name = f"{table}_{column}"
                suffix = 2
                while name in reserved_names or name in used_names:
                    name = f"{table}_{column}_{suffix}"
                    suffix += 1
            used_names.add(name)
            selection = f"{quote(table)}.{quote(column)}"
            if name != column:
                selection += f" AS {quote(name)}"
            selections.append(selection)

    query = f"SELECT {', '.join(selections)} FROM {from_clause}"
    return pd.read_sql_query(query, conn)


def get_df_track_album_artist_joined(engine: sqlalchemy.Engine) -> pd.DataFrame:
    """Return track, artist, and album columns, retaining tracks without related rows."""
    with engine.connect() as conn:
        return _read_joined_tables(
            conn,
            ("track", "artist", "album"),
            '"track" LEFT JOIN "artist" ON "track"."artistid" = "artist"."id" '
            'LEFT JOIN "album" ON "track"."albumid" = "album"."id"',
        )


def get_df_mediafile(engine: sqlalchemy.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql_query("SELECT * FROM mediafile", conn)


def get_df_mediafile_track_album_artist_joined(
    engine: sqlalchemy.Engine,
) -> pd.DataFrame:
    """Return mediafile, track, album, and artist columns, retaining mediafiles without related rows."""
    with engine.connect() as conn:
        return _read_joined_tables(
            conn,
            ("mediafile", "track", "album", "artist"),
            '"mediafile" LEFT JOIN "track" ON "mediafile"."trackid" = "track"."id" '
            'LEFT JOIN "album" ON "track"."albumid" = "album"."id" '
            'LEFT JOIN "artist" ON "track"."artistid" = "artist"."id"',
        )


def get_df_trackstreaming_track_album_artist_joined(
    engine: sqlalchemy.Engine,
) -> pd.DataFrame:
    """Return trackstreaming, track, album, and artist columns, retaining trackstreaming without related rows."""
    with engine.connect() as conn:
        return _read_joined_tables(
            conn,
            ("trackstreaming", "track", "album", "artist"),
            '"trackstreaming" LEFT JOIN "track" ON "trackstreaming"."trackid" = "track"."id" '
            'LEFT JOIN "album" ON "track"."albumid" = "album"."id" '
            'LEFT JOIN "artist" ON "track"."artistid" = "artist"."id"',
        )
