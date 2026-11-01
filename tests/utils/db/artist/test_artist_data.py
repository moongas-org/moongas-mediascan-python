from dataclasses import asdict

import pandas as pd
import pytest
import sqlalchemy

from mediascan.utils.db.artist.artist_data import ArtistData, row_to_artist_data
from mediascan.utils.db.mediascan_db_loader import get_df_artist


@pytest.fixture
def artists() -> pd.DataFrame:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql(
                "CREATE TABLE artist (id INTEGER PRIMARY KEY, path TEXT UNIQUE, "
                "name TEXT, city TEXT, countrycode TEXT, regioncode TEXT, "
                "languagecode TEXT)"
            )
            conn.exec_driver_sql(
                "INSERT INTO artist VALUES "
                "(10, '/music/Artist', 'Artist', 'Los Angeles', 'US', 'CA', 'en')"
            )
            conn.exec_driver_sql(
                "INSERT INTO artist VALUES "
                "(11, '/music/Other', NULL, NULL, NULL, NULL, NULL)"
            )
        return get_df_artist(engine)
    finally:
        engine.dispose()


def test_convert_artist_row(artists: pd.DataFrame) -> None:
    row = artists.iloc[0]
    artist = row_to_artist_data(row)

    assert isinstance(artist, ArtistData)
    assert asdict(artist) == {
        "id": 10,
        "path": "/music/Artist",
        "name": "Artist",
        "city": "Los Angeles",
        "countryCode": "US",
        "regionCode": "CA",
        "languageCode": "en",
    }
    assert row_to_artist_data(row.to_dict()) == artist


def test_convert_artist_with_missing_metadata(artists: pd.DataFrame) -> None:
    artist = row_to_artist_data(artists.iloc[1])
    assert artist.id == 11
    assert artist.name is None
    assert artist.city is None
    assert artist.countryCode is None


@pytest.mark.parametrize(
    ("column", "value", "error"),
    [
        ("id", None, ValueError),
        ("path", None, ValueError),
        ("name", 123, TypeError),
    ],
)
def test_convert_invalid_values_raises(
    artists: pd.DataFrame,
    column: str,
    value: object,
    error: type[Exception],
) -> None:
    row = artists.iloc[0].to_dict()
    row[column] = value
    with pytest.raises(error):
        row_to_artist_data(row)
