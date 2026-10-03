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
        file_path = Path(raw_path.lstrip("/")) if raw_path.startswith("/") and not raw_path.startswith("////") else Path(raw_path)
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"Moongas database file '{db_path}' not found at resolve path '{file_path.resolve()}' (Current Working Directory: {Path.cwd()})"
            )

    engine = sqlalchemy.create_engine(db_path)
    return engine


def get_df_artists(engine: sqlalchemy.Engine):
    with engine.connect() as conn:
        artists = pd.read_sql_query("SELECT * FROM artist", conn)
        return artists


def get_df_files_artistdata_joined(engine: sqlalchemy.Engine):
    with engine.connect() as conn:
        files = pd.read_sql_query(
            "SELECT * FROM mediafile LEFT JOIN artist ON mediafile.artistpath = artist.path", conn
        )
        return files
