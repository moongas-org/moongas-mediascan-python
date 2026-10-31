from pathlib import Path
from typing import cast

from .artist_yaml_file import ArtistYamlFile


def load_artist_yaml_file(path: Path | str) -> ArtistYamlFile:
    """
    raises: FileNotFoundError, yaml.YAMLError
    """
    ret = None
    path = Path(path) if isinstance(path, str) else path
    if not path.exists():
        raise FileNotFoundError(f"Moongas artist yaml file '{path}' not found")

    with open(path, "r") as stream:
        ret = cast(ArtistYamlFile, getattr(ArtistYamlFile, "from_yaml")(stream))
    return ret
