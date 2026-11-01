from pathlib import Path
from typing import cast

from .mediascan_config import MediascanConfig


def load_mediascan_config_file(path: Path | str) -> MediascanConfig:
    """Load a Moongas mediascan configuration YAML file."""
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Moongas mediascan config file '{config_path}' not found")

    with config_path.open("r", encoding="utf-8") as stream:
        return cast(
            MediascanConfig,
            getattr(MediascanConfig, "from_yaml")(stream),
        )
