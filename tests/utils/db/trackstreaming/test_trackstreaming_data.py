from dataclasses import asdict

import pandas as pd
import pytest
import sqlalchemy

from mediascan.utils.db.mediascan_db_loader import get_df_trackstreaming
from mediascan.utils.db.trackstreaming.trackstreaming_data import (
    TrackStreamingData,
    row_to_trackstreaming_data,
)


@pytest.fixture
def trackstreaming() -> pd.DataFrame:
    engine = sqlalchemy.create_engine("sqlite://")
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql(
                "CREATE TABLE trackstreaming (trackid INTEGER NOT NULL, "
                "streamingservice TEXT NOT NULL, streamingtrackid TEXT NOT NULL, "
                "streamingtrackurl TEXT)"
            )
            conn.exec_driver_sql(
                "INSERT INTO trackstreaming VALUES "
                "(4, 'spotify', 'spotify-id', 'https://open.spotify.com/track/spotify-id')"
            )
        return get_df_trackstreaming(engine)
    finally:
        engine.dispose()


def test_convert_trackstreaming_row(trackstreaming: pd.DataFrame) -> None:
    row = trackstreaming.iloc[0]
    streaming = row_to_trackstreaming_data(row)

    assert isinstance(streaming, TrackStreamingData)
    assert asdict(streaming) == {
        "track_id": 4,
        "streaming_service": "spotify",
        "streaming_track_id": "spotify-id",
        "streaming_track_url": "https://open.spotify.com/track/spotify-id",
    }
    assert row_to_trackstreaming_data(row.to_dict()) == streaming


def test_convert_trackstreaming_row_without_url_column() -> None:
    streaming = row_to_trackstreaming_data(
        {"trackid": 4, "streamingservice": "spotify", "streamingtrackid": "spotify-id"}
    )

    assert streaming.streaming_track_url is None


@pytest.mark.parametrize(
    ("column", "value", "error"),
    [
        ("trackid", None, ValueError),
        ("streamingservice", None, ValueError),
        ("streamingtrackid", None, ValueError),
        ("trackid", "bad", TypeError),
        ("streamingservice", 123, TypeError),
    ],
)
def test_convert_invalid_values_raises(
    trackstreaming: pd.DataFrame,
    column: str,
    value: object,
    error: type[Exception],
) -> None:
    row = trackstreaming.iloc[0].to_dict()
    row[column] = value
    with pytest.raises(error):
        row_to_trackstreaming_data(row)
