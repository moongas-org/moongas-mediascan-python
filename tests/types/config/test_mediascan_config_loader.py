from pathlib import Path

import pytest
import yaml

from mediascan.types.config.mediascan_config_loader import load_mediascan_config_file


def test_load_mediascan_config_file(tmp_path: Path) -> None:
    config_path = tmp_path / "mediascan-config.yml"
    config_path.write_text(
        "mediaDirs:\n"
        "  - Music\n"
        "mediaExts:\n"
        "  - .mp3\n"
        "  - .m4a\n"
        "excludePaths:\n"
        "  - ignored\n"
    )

    config = load_mediascan_config_file(config_path)

    assert config.media_dirs == ["Music"]
    assert config.media_exts == [".mp3", ".m4a"]


def test_load_mediascan_config_file_raises_for_missing_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="mediascan-config.yml"):
        load_mediascan_config_file(tmp_path / "mediascan-config.yml")


def test_load_mediascan_config_file_propagates_yaml_errors(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid.yml"
    config_path.write_text("mediaDirs: [\n")

    with pytest.raises(yaml.YAMLError):
        load_mediascan_config_file(config_path)
