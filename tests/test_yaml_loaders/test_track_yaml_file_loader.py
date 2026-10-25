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
  - isrc: US-EX1-26-00001
    spotifyId: example-track-id
    acoustidData:
      results:
        - id: 2344a322-fa91-46a1-b70d-e9c8539de5f9
          recordings:
            - id: 0c652621-96d6-46bb-a886-b277b87bafd4
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
    assert loaded.track_id_data[0].isrc == "US-EX1-26-00001"
    assert loaded.track_id_data[0].spotify_id == "example-track-id"
    assert loaded.track_id_data[0].acoustid_data is not None
    assert loaded.track_id_data[0].acoustid_data.status == "ok"
    assert (
        loaded.track_id_data[0].acoustid_data.results[0].recordings[0].id
        == "0c652621-96d6-46bb-a886-b277b87bafd4"
    )
    assert loaded.track_id_data[0].acoustid_data.results[0].score == 0.98905593


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
