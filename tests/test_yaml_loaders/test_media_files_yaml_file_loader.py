from pathlib import Path

import pytest
import yaml

from mediascan.media_files_yaml_file_loader import load_media_files_yaml_file

VALID_MEDIA_FILES_YAML = """
files:
  - path: /music/The Example Band/Album/01 - Example Song.flac
    size: 123456789
    format: FLAC
    title: Example Song
    artist: The Example Band
    albumartist: The Example Band
    album: Example Album
    genre: Rock
    year: 2026
    duration: 245
"""


def test_load_media_files_yaml_file_from_path(tmp_path: Path) -> None:
    media_files_yaml_path = tmp_path / "files.yml"
    media_files_yaml_path.write_text(VALID_MEDIA_FILES_YAML)

    loaded = load_media_files_yaml_file(media_files_yaml_path)

    assert len(loaded.files) == 1
    media_file = loaded.files[0]
    assert media_file.path == "/music/The Example Band/Album/01 - Example Song.flac"
    assert media_file.title == "Example Song"
    assert media_file.artist == "The Example Band"
    assert media_file.format == "FLAC"
    assert media_file.duration == 245


def test_load_media_files_yaml_file_accepts_string_path(tmp_path: Path) -> None:
    media_files_yaml_path = tmp_path / "files.yml"
    media_files_yaml_path.write_text(VALID_MEDIA_FILES_YAML)

    loaded = load_media_files_yaml_file(str(media_files_yaml_path))

    assert len(loaded.files) == 1
    assert loaded.files[0].album == "Example Album"


def test_load_media_files_yaml_file_raises_for_missing_path(tmp_path: Path) -> None:
    media_files_yaml_path = tmp_path / "missing.yml"

    with pytest.raises(
        FileNotFoundError,
        match="Moongas mediafiles yaml file .*missing.yml.* not found",
    ):
        load_media_files_yaml_file(media_files_yaml_path)


def test_load_media_files_yaml_file_propagates_yaml_errors(tmp_path: Path) -> None:
    media_files_yaml_path = tmp_path / "invalid.yml"
    media_files_yaml_path.write_text("files: [\n")

    with pytest.raises(yaml.YAMLError):
        load_media_files_yaml_file(media_files_yaml_path)
