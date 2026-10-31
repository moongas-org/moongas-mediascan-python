from dataclasses import fields

import pytest
import yaml

from mediascan.types.media_file.media_file_data import MediaFileData, MediaFileWithArtistData
from mediascan.types.track.track_id_data import TrackIdData
from mediascan.types.track.track_yaml_file import TrackYamlFile


@pytest.mark.parametrize("media_entries", [None, []])
def test_track_optional_media_files(media_entries: list[MediaFileData] | None) -> None:
    track = TrackYamlFile.from_yaml(
        "trackData: {title: Example, artist: Artist, albumartist: Artist, album: Album, genre: Rock, year: 2026}"
    )
    assert track.media_file_data is None
    track.media_file_data = media_entries
    assert TrackYamlFile.from_yaml(track.to_yaml()).media_file_data == media_entries


def test_partial_and_complete_media_files_round_trip() -> None:
    partial = {
        "fpcalcData": {"duration": 123.5, "fingerprint": "abc123"},
        "acoustidData": {
            "results": [{"id": "result", "recordings": [{"id": "recording", "isrcs": ["USSM10027739"]}], "score": 0.98}],
            "status": "ok",
        },
    }
    complete = {
        "path": "/music/example.flac",
        "size": 123456,
        "format": "FLAC",
        "title": "Example",
        "artist": "Artist",
        "albumartist": "Artist",
        "album": "Album",
        "genre": "Rock",
        "year": 2026,
        "duration": 124,
    }
    payload = {
        "trackData": {key: complete[key] for key in ("title", "artist", "albumartist", "album", "genre", "year")},
        "mediaFileData": [partial, complete],
        "trackIdData": {
            "streamingData": [
                {
                    "streamingService": "spotify",
                    "trackUrl": "https://open.spotify.com/track/example",
                    "trackId": "example",
                    "apiData": None,
                }
            ]
        },
    }
    track = TrackYamlFile.from_yaml(yaml.safe_dump(payload))
    assert track.media_file_data is not None
    fingerprinted, tagged = track.media_file_data
    assert isinstance(fingerprinted, MediaFileData)
    assert fingerprinted.path is None
    assert fingerprinted.fpcalc_data is not None
    assert fingerprinted.fpcalc_data.fingerprint == "abc123"
    assert fingerprinted.acoustid_data is not None
    assert fingerprinted.acoustid_data.results[0].recordings[0].isrcs == ["USSM10027739"]
    assert tagged.path == complete["path"]
    assert tagged.size == complete["size"]
    assert tagged.duration == complete["duration"]
    assert tagged.fpcalc_data is None
    assert tagged.acoustid_data is None
    serialized = yaml.safe_load(track.to_yaml())
    assert "fpcalcData" not in serialized["trackIdData"]
    assert "acoustidData" not in serialized["trackIdData"]
    assert serialized["mediaFileData"][0]["fpcalcData"] == partial["fpcalcData"]
    assert TrackYamlFile.from_yaml(track.to_yaml()) == track


def test_track_id_data_only_contains_streaming_fields() -> None:
    assert [field.name for field in fields(TrackIdData)] == ["streaming_data"]


def test_joined_media_file_artist_fields_remain_required() -> None:
    media_file = MediaFileWithArtistData(
        path="/music/example.flac",
        artist_name="Artist",
        city="City",
        country_code="US",
        region_code="CA",
        language_code="en",
    )
    assert media_file.path == "/music/example.flac"
    assert media_file.artist_name == "Artist"
    assert media_file.fpcalc_data is None
    with pytest.raises(TypeError):
        MediaFileWithArtistData()
