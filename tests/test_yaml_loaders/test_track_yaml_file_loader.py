from pathlib import Path

import pytest
import yaml

from mediascan.types.track.track_yaml_file_loader import load_track_yaml_file

VALID_TRACK_YAML = """
trackData:
  title: Example Song
  artist: The Example Band
  albumartist: The Example Band
  album: Example Album
  genre: Rock
  year: 2026
trackIdData:
  streamingData:
    - streamingService: spotify
      isrc: US-EX1-26-00001
      trackId: example-track-id
      trackUrl: https://open.spotify.com/track/example-track-id
      apiData:
        tracks:
          items: []
mediaFileData:
  - fpcalcData:
      duration: 263.62
      fingerprint: example-fingerprint
    acoustidData:
      results:
        - id: 2344a322-fa91-46a1-b70d-e9c8539de5f9
          recordings:
            - id: 0c652621-96d6-46bb-a886-b277b87bafd4
              title: Bingo Bango (radio mix)
              length: 225493
              video: false
              disambiguation: ""
              firstReleaseDate: "2000-04-03"
              isrcs:
                - GBBKS0000003
                - GBBKS0000042
            - id: 30cd7bd2-ac63-4dd7-a745-864d298f34cf
          score: 0.98905593
      status: ok
"""


def test_load_track_yaml_file(tmp_path: Path) -> None:
    track_yaml_path = tmp_path / "track.yml"
    track_yaml_path.write_text(VALID_TRACK_YAML)

    loaded = load_track_yaml_file(track_yaml_path)

    assert loaded.track_data.title == "Example Song"
    assert loaded.track_data.artist == "The Example Band"
    assert loaded.track_data.album == "Example Album"
    assert loaded.track_data.year == 2026
    assert loaded.track_id_data is not None
    assert loaded.track_id_data.streaming_data is not None
    streaming = loaded.track_id_data.streaming_data[0]
    assert streaming.isrc == "US-EX1-26-00001"
    assert streaming.track_id == "example-track-id"
    assert streaming.track_url == "https://open.spotify.com/track/example-track-id"
    assert streaming.api_data == {"tracks": {"items": []}}
    assert loaded.media_file_data is not None
    media_file = loaded.media_file_data[0]
    assert media_file.path is None
    assert media_file.fpcalc_data is not None
    assert media_file.fpcalc_data.duration == 263.62
    assert media_file.fpcalc_data.fingerprint == "example-fingerprint"
    assert media_file.acoustid_data is not None
    assert media_file.acoustid_data.status == "ok"
    assert (
        media_file.acoustid_data.results[0].recordings[0].id
        == "0c652621-96d6-46bb-a886-b277b87bafd4"
    )
    assert media_file.acoustid_data.results[0].recordings[0].isrcs == [
        "GBBKS0000003",
        "GBBKS0000042",
    ]
    recording = media_file.acoustid_data.results[0].recordings[0]
    assert recording.title == "Bingo Bango (radio mix)"
    assert recording.length == 225493
    assert recording.video is False
    assert recording.disambiguation == ""
    assert recording.first_release_date == "2000-04-03"
    minimal_recording = media_file.acoustid_data.results[0].recordings[1]
    assert minimal_recording.id == "30cd7bd2-ac63-4dd7-a745-864d298f34cf"
    assert minimal_recording.title is None
    assert minimal_recording.length is None
    assert minimal_recording.video is None
    assert minimal_recording.disambiguation is None
    assert minimal_recording.first_release_date is None
    assert minimal_recording.isrcs is None
    assert media_file.acoustid_data.results[0].score == 0.98905593
    serialized = yaml.safe_load(loaded.to_yaml())
    assert isinstance(serialized["trackIdData"], dict)
    serialized_recording = serialized["mediaFileData"][0]["acoustidData"]["results"][0]["recordings"][0]
    assert serialized_recording["firstReleaseDate"] == "2000-04-03"
    assert "first-release-date" not in serialized_recording


@pytest.mark.parametrize("identifiers", [None, {}, {"streamingData": []}])
def test_load_track_yaml_file_optional_identifiers(tmp_path: Path, identifiers: dict[str, object] | None) -> None:
    payload = yaml.safe_load(VALID_TRACK_YAML)
    payload["trackIdData"] = identifiers
    path = tmp_path / "track.yml"
    path.write_text(yaml.safe_dump(payload))
    loaded = load_track_yaml_file(path)
    if identifiers is None:
        assert loaded.track_id_data is None
    else:
        assert loaded.track_id_data is not None
        assert loaded.track_id_data.streaming_data == identifiers.get("streamingData")
    assert yaml.safe_load(loaded.to_yaml())["trackIdData"] == (
        None if identifiers is None else {"streamingData": identifiers.get("streamingData")}
    )


def test_load_track_yaml_file_without_identifiers(tmp_path: Path) -> None:
    payload = yaml.safe_load(VALID_TRACK_YAML)
    del payload["trackIdData"]
    path = tmp_path / "track.yml"
    path.write_text(yaml.safe_dump(payload))
    assert load_track_yaml_file(path).track_id_data is None


def test_load_track_yaml_file_raises_for_missing_path(tmp_path: Path) -> None:
    track_yaml_path = tmp_path / "missing.yml"

    with pytest.raises(
        FileNotFoundError,
        match="Moongas track yaml file .*missing.yml.* not found",
    ):
        load_track_yaml_file(track_yaml_path)


def test_load_track_yaml_file_propagates_yaml_errors(tmp_path: Path) -> None:
    track_yaml_path = tmp_path / "invalid.yml"
    track_yaml_path.write_text("trackData: [\n")

    with pytest.raises(yaml.YAMLError):
        load_track_yaml_file(track_yaml_path)
