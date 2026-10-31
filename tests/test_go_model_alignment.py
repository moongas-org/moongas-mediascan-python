from dataclasses import fields
from datetime import datetime, timezone

import pytest
import yaml
from dataclass_wizard.v0 import fromdict
from dataclass_wizard.v0.errors import MissingFields

from mediascan.types.album.album import Album
from mediascan.types.artist.artist import Artist
from mediascan.types.artist.artist_data import ArtistData
from mediascan.types.date.date import Date
from mediascan.types.media_file.media_file_acoustid_data import (
    MediaFileAcoustIDData,
    MediaFileAcoustIDRecording,
    MediaFileAcoustIDResult,
)
from mediascan.types.media_file.media_file_data import MediaFileData
from mediascan.types.media_file.media_file_fpcalc_data import MediaFileFpCalcData
from mediascan.types.track.streaming.streaming_data import StreamingData
from mediascan.types.track.track import Track
from mediascan.types.track.track_data import TrackData
from mediascan.types.track.track_yaml_file import TrackYamlFile


def test_path_wrappers_round_trip() -> None:
    artist = fromdict(
        Artist,
        {
            "path": "/music/Artist",
            "artistYamlFile": {
                "artistData": {
                    "artistNames": ["Artist"],
                    "city": "",
                    "countryCode": "US",
                    "regionCode": "",
                    "languageCodes": ["en"],
                    "dob": {"y": 1970},
                }
            },
        },
    )
    album = fromdict(
        Album,
        {
            "path": "/music/Artist/Album",
            "albumYamlFile": {
                "albumData": {"name": "Album", "dateReleased": {"y": 2000, "m": 6, "d": 1}, "explicitCover": False}
            },
        },
    )
    track = fromdict(
        Track,
        {
            "path": "/music/Artist/Album/Song.yml",
            "trackYamlFile": {
                "trackData": {
                    "title": "Song",
                    "artist": "Artist",
                    "albumartist": "Artist",
                    "album": "Album",
                    "genre": "",
                    "year": 2000,
                }
            },
        },
    )
    assert isinstance(artist.artist_yaml_file.artist_data.dob, Date)
    assert album.album_yaml_file.album_data.date_released == Date(2000, 6, 1)
    assert track.track_yaml_file.track_data.title == "Song"
    for wrapper in (artist, album, track):
        assert type(wrapper).from_yaml(wrapper.to_yaml()) == wrapper


def test_media_file_paths_fractional_duration_and_timestamp() -> None:
    data = fromdict(
        MediaFileData,
        {
            "path": "/music/Artist/Album/Song.flac",
            "albumPath": "/music/Artist/Album",
            "artistPath": "/music/Artist",
            "size": 123456789,
            "format": "FLAC",
            "duration": 263.573,
            "modTime": "2026-10-31T12:55:20Z",
            "fpcalcData": {"duration": 263.62, "fingerprint": "fingerprint"},
            "acoustidData": {
                "results": [{"id": "match", "recordings": [{"id": "recording", "isrcs": []}], "score": 0.98}],
                "status": "ok",
            },
        },
    )
    assert data.album_path == "/music/Artist/Album"
    assert data.artist_path == "/music/Artist"
    assert data.duration == 263.573
    assert data.mod_time == datetime(2026, 10, 31, 12, 55, 20, tzinfo=timezone.utc)
    assert isinstance(data.fpcalc_data, MediaFileFpCalcData)
    assert isinstance(data.acoustid_data, MediaFileAcoustIDData)
    assert isinstance(data.acoustid_data.results[0], MediaFileAcoustIDResult)
    assert isinstance(data.acoustid_data.results[0].recordings[0], MediaFileAcoustIDRecording)
    serialized = yaml.safe_load(data.to_yaml())
    assert serialized["duration"] == 263.573
    assert serialized["albumPath"] == data.album_path
    assert serialized["artistPath"] == data.artist_path
    assert "modTime" in serialized
    assert MediaFileData.from_yaml(data.to_yaml()) == data


def test_artist_fields_match_go() -> None:
    assert [field.name for field in fields(ArtistData)] == [
        "artist_names",
        "city",
        "country_code",
        "region_code",
        "language_codes",
        "dob",
        "dod",
    ]


@pytest.mark.parametrize(
    ("model", "payload", "required"),
    [
        (
            TrackData,
            {"title": "", "artist": "", "albumartist": "", "album": "", "genre": "", "year": 0},
            ["title", "artist", "albumartist", "album", "genre", "year"],
        ),
        (
            TrackYamlFile,
            {"trackData": {"title": "", "artist": "", "albumartist": "", "album": "", "genre": "", "year": 0}},
            ["trackData"],
        ),
        (
            StreamingData,
            {"streamingService": "custom-service", "trackUrl": "", "trackId": "", "apiData": None},
            ["streamingService", "trackUrl", "trackId", "apiData"],
        ),
        (MediaFileAcoustIDData, {"results": [], "status": ""}, ["results", "status"]),
        (MediaFileAcoustIDResult, {"id": "", "recordings": [], "score": 0.0}, ["id", "recordings", "score"]),
        (MediaFileAcoustIDRecording, {"id": ""}, ["id"]),
    ],
)
def test_required_fields_accept_zero_values_but_not_missing(model: type, payload: dict, required: list[str]) -> None:
    fromdict(model, payload)
    for key in required:
        incomplete = dict(payload)
        del incomplete[key]
        with pytest.raises(MissingFields):
            fromdict(model, incomplete)
