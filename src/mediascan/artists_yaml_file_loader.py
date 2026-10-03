from pathlib import Path
from typing import cast

from .artists_yaml_file import ArtistsYamlFile


def load_artists_yaml_file(path: Path | str) -> ArtistsYamlFile:
    """
    DEPRECATED (only used by deprecated artists.yml)
    raises: FileNotFoundError, yaml.YAMLError
    """
    ret = None
    path = Path(path) if isinstance(path, str) else path
    if not path.exists():
        raise FileNotFoundError(f"Moongas artists yaml file '{path}' not found")

    with open(path, "r") as stream:
        ret = cast(ArtistsYamlFile, getattr(ArtistsYamlFile, "from_yaml")(stream))
    return ret
