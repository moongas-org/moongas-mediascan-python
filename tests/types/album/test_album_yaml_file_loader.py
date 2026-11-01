from pathlib import Path

import pytest
import yaml

from mediascan.types.album.album_yaml_file_loader import load_album_yaml_file


def test_load_album_yaml_file(tmp_path: Path) -> None:
    album_yaml_path = tmp_path / "album.yml"
    album_yaml_path.write_text(
        """albumData:
  name: Example Album
  dateReleased:
    y: 1993
  explicitCover: true
""",
        encoding="utf-8",
    )

    loaded = load_album_yaml_file(album_yaml_path)

    assert loaded.album_data.name == "Example Album"
    assert loaded.album_data.date_released.y == 1993
    assert loaded.album_data.explicit_cover is True


def test_load_album_yaml_file_accepts_string_path(tmp_path: Path) -> None:
    album_yaml_path = tmp_path / "album.yml"
    album_yaml_path.write_text(
        "albumData:\n  name: Example Album\n  dateReleased: {y: 1993}\n  explicitCover: false\n",
        encoding="utf-8",
    )

    assert load_album_yaml_file(str(album_yaml_path)).album_data.name == "Example Album"


def test_load_album_yaml_file_raises_for_missing_path(tmp_path: Path) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="Moongas album yaml file .*missing.yml.* not found",
    ):
        load_album_yaml_file(tmp_path / "missing.yml")


def test_load_album_yaml_file_propagates_yaml_errors(tmp_path: Path) -> None:
    album_yaml_path = tmp_path / "invalid.yml"
    album_yaml_path.write_text("albumData: [\n", encoding="utf-8")

    with pytest.raises(yaml.YAMLError):
        load_album_yaml_file(album_yaml_path)
