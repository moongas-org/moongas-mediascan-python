from pathlib import Path
from typing import cast

from .album_yaml_file import AlbumYamlFile


def load_album_yaml_file(path: Path | str) -> AlbumYamlFile:
    """Load an album YAML file.

    Raises:
        FileNotFoundError: If the path does not exist.
        yaml.YAMLError: If the file contains invalid YAML.
    """
    path = Path(path) if isinstance(path, str) else path
    if not path.exists():
        raise FileNotFoundError(f"Moongas album yaml file '{path}' not found")

    with open(path, "r", encoding="utf-8") as stream:
        return cast(AlbumYamlFile, getattr(AlbumYamlFile, "from_yaml")(stream))
