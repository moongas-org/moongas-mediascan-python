from datetime import datetime, timezone

import pytest
import yaml

from mediascan.types.track.track_yaml_file_validator import validate_track_yaml_content


def track_document() -> dict[str, object]:
    return {
        "trackData": {
            "title": "Song",
            "artist": "Artist",
            "albumartist": "Artist",
            "album": "Album",
            "genre": "Rock",
            "year": 2026,
        }
    }


@pytest.mark.parametrize("duration", [0, 123, 263.573, None])
def test_accepts_media_file_duration(duration: int | float | None) -> None:
    document = track_document()
    document["mediaFileData"] = [{"duration": duration}]
    assert validate_track_yaml_content(yaml.safe_dump(document)) == document


@pytest.mark.parametrize("quoted", [False, True])
def test_accepts_modification_timestamp(quoted: bool) -> None:
    content = yaml.safe_dump(track_document()) + "mediaFileData:\n  - modTime: "
    content += "'2026-10-31T12:55:20Z'\n" if quoted else "2026-10-31T12:55:20Z\n"
    assert validate_track_yaml_content(content) == yaml.safe_load(content)


def test_accepts_complete_track_and_preserves_raw_api_data() -> None:
    document = track_document()
    document["trackIdData"] = {
        "streamingData": [
            {
                "streamingService": "custom-service",
                "trackUrl": "https://example.com/song",
                "trackId": "song",
                "isrc": None,
                "apiData": {"arbitrary_key": [None, False, 0, {"nested": "data"}]},
            },
            {"streamingService": "spotify", "trackUrl": "url", "trackId": "id", "apiData": None},
        ]
    }
    document["mediaFileData"] = [
        {
            "path": "song.flac",
            "albumPath": "Album",
            "artistPath": "Artist",
            "size": 100,
            "format": "FLAC",
            "title": "Song",
            "artist": "Artist",
            "albumartist": "Artist",
            "album": "Album",
            "genre": "Rock",
            "year": 2026,
            "duration": 263.573,
            "modTime": datetime(2026, 10, 31, 12, 55, 20, tzinfo=timezone.utc),
            "fpcalcData": {"duration": 263.62, "fingerprint": "fingerprint"},
            "acoustidData": {
                "status": "ok",
                "results": [
                    {
                        "id": "result",
                        "score": 0.98,
                        "recordings": [
                            {
                                "id": "recording",
                                "title": "Song",
                                "length": 263573,
                                "video": False,
                                "disambiguation": "",
                                "firstReleaseDate": "1985-06-01",
                                "isrcs": [],
                            }
                        ],
                    }
                ],
            },
        }
    ]
    assert validate_track_yaml_content(yaml.safe_dump(document)) == document


@pytest.mark.parametrize(
    "acoustid",
    [
        {},
        {"status": "ok"},
        {"results": []},
        {"status": 1, "results": []},
        {"status": "ok", "results": {}},
        {"status": "ok", "results": [None]},
        {"status": "ok", "results": [{"id": "id", "score": 0.5, "recordings": None}]},
        {"status": "ok", "results": [{"id": "id", "score": 0.5, "recordings": [None]}]},
        {"status": "ok", "results": [{"id": "id", "score": 0.5}]},
        {"status": "ok", "results": [{"id": 1, "score": 0.5, "recordings": []}]},
        {"status": "ok", "results": [{"id": "id", "score": True, "recordings": []}]},
        {"status": "ok", "results": [{"id": "id", "score": "0.5", "recordings": []}]},
        {"status": "ok", "results": [{"id": "id", "score": 0.5, "recordings": [{}]}]},
        {"status": "ok", "results": [{"id": "id", "score": 0.5, "recordings": [{"id": "r", "video": "false"}]}]},
        {"status": "ok", "results": [{"id": "id", "score": 0.5, "recordings": [{"id": "r", "length": True}]}]},
        {"status": "ok", "results": [{"id": "id", "score": 0.5, "recordings": [{"id": "r", "isrcs": [1]}]}]},
        {"status": "ok", "results": [{"id": "id", "score": 0.5, "recordings": [{"id": "r", "extra": True}]}]},
        {"status": "ok", "results": [], "extra": "field"},
    ],
)
def test_rejects_invalid_acoustid_data(acoustid: object) -> None:
    document = track_document()
    document["mediaFileData"] = [{"acoustidData": acoustid}]
    with pytest.raises(ValueError, match=r"mediaFileData\[0\]\.acoustidData"):
        validate_track_yaml_content(yaml.safe_dump(document))


@pytest.mark.parametrize(
    "media_file",
    [
        {"duration": True},
        {"duration": "123.5"},
        {"duration": float("inf")},
        {"size": False},
        {"size": 1.5},
        {"year": "2026"},
        {"modTime": "not-a-date"},
        {"modTime": "2026-10-31"},
        {"modTime": 123},
        {"fpcalcData": []},
        {"fpcalcData": {"duration": True}},
        {"fpcalcData": {"duration": "12"}},
        {"fpcalcData": {"fingerprint": 123}},
        {"fpcalcData": {"unknown": "field"}},
        {"acoustidData": []},
        {"path": 123},
        {"unexpected": "field"},
    ],
)
def test_rejects_invalid_media_file_fields(media_file: object) -> None:
    document = track_document()
    document["mediaFileData"] = [media_file]
    with pytest.raises(ValueError, match=r"mediaFileData\[0\]"):
        validate_track_yaml_content(yaml.safe_dump(document))


@pytest.mark.parametrize(
    "content",
    ["", "null", "[]", "trackData: [", "trackData: {}\ntrackData: {}\n", "1: value"],
)
def test_rejects_invalid_documents(content: str) -> None:
    with pytest.raises((ValueError, yaml.YAMLError)):
        validate_track_yaml_content(content)


@pytest.mark.parametrize(
    "key,value",
    [
        ("trackData", None),
        ("trackData", {}),
        ("trackIdData", []),
        ("trackIdData", {"spotifyId": "old-id"}),
        ("trackIdData", {"streamingData": {}}),
        ("mediaFileData", {}),
        ("mediaFileData", [None]),
        ("unknown", None),
    ],
)
def test_rejects_invalid_top_level_fields(key: str, value: object) -> None:
    document = track_document()
    document[key] = value
    with pytest.raises(ValueError):
        validate_track_yaml_content(yaml.safe_dump(document))


@pytest.mark.parametrize("field", ["title", "artist", "albumartist", "album", "genre", "year"])
def test_rejects_missing_core_fields(field: str) -> None:
    document = yaml.safe_load(yaml.safe_dump(track_document()))
    del document["trackData"][field]
    with pytest.raises(ValueError, match="six core"):
        validate_track_yaml_content(yaml.safe_dump(document))


@pytest.mark.parametrize("field,value", [("title", " "), ("artist", 123), ("year", True), ("year", 2026.5)])
def test_rejects_invalid_core_values(field: str, value: object) -> None:
    document = yaml.safe_load(yaml.safe_dump(track_document()))
    document["trackData"][field] = value
    with pytest.raises(ValueError, match=f"trackData.{field}"):
        validate_track_yaml_content(yaml.safe_dump(document))


@pytest.mark.parametrize("field", ["streamingService", "trackUrl", "trackId", "apiData"])
def test_rejects_missing_streaming_fields(field: str) -> None:
    streaming = {"streamingService": "spotify", "trackUrl": "url", "trackId": "id", "apiData": None}
    del streaming[field]
    document = track_document()
    document["trackIdData"] = {"streamingData": [streaming]}
    with pytest.raises(ValueError, match=field):
        validate_track_yaml_content(yaml.safe_dump(document))


@pytest.mark.parametrize(
    "streaming",
    [
        None,
        {"unexpected": None},
        {"streamingService": " ", "trackUrl": "url", "trackId": "id", "apiData": None},
        {"streamingService": "spotify", "trackUrl": 1, "trackId": "id", "apiData": None},
        {"streamingService": "spotify", "trackUrl": "url", "trackId": False, "apiData": None},
        {"streamingService": "spotify", "trackUrl": "url", "trackId": "id", "apiData": None, "isrc": 123},
    ],
)
def test_rejects_invalid_streaming_fields(streaming: object) -> None:
    document = track_document()
    document["trackIdData"] = {"streamingData": [streaming]}
    with pytest.raises(ValueError, match=r"trackIdData\.streamingData\[0\]"):
        validate_track_yaml_content(yaml.safe_dump(document))


def test_rejects_duplicate_fields_in_otherwise_valid_track() -> None:
    content = yaml.safe_dump(track_document())
    with pytest.raises(ValueError, match="Duplicate YAML field 'trackData'"):
        validate_track_yaml_content(content + content)


def test_rejects_unsafe_yaml_tags() -> None:
    with pytest.raises(yaml.YAMLError):
        validate_track_yaml_content("!!python/object:builtins.object {}")


@pytest.mark.parametrize("optional", [None, {}, {"streamingData": None}, {"streamingData": []}])
def test_accepts_optional_identifiers(optional: object) -> None:
    document = track_document()
    document["trackIdData"] = optional
    document["mediaFileData"] = None
    assert validate_track_yaml_content(yaml.safe_dump(document)) == document


def test_accepts_null_optional_recording_fields_and_zero_values() -> None:
    document = track_document()
    document["mediaFileData"] = [
        {
            "acoustidData": {
                "status": "",
                "results": [
                    {
                        "id": "",
                        "score": 0,
                        "recordings": [
                            {
                                "id": "",
                                "title": None,
                                "length": None,
                                "video": None,
                                "disambiguation": None,
                                "firstReleaseDate": None,
                                "isrcs": None,
                            }
                        ],
                    }
                ],
            }
        }
    ]
    assert validate_track_yaml_content(yaml.safe_dump(document)) == document


def test_accepts_empty_and_null_optional_media_data() -> None:
    document = track_document()
    document["mediaFileData"] = [
        {},
        {"fpcalcData": None, "acoustidData": None, "modTime": None},
        {"fpcalcData": {"duration": None, "fingerprint": None}, "acoustidData": {"results": [], "status": "ok"}},
    ]
    assert validate_track_yaml_content(yaml.safe_dump(document)) == document
