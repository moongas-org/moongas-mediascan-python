from pathlib import Path
from typing import cast

from .track_yaml_file import TrackYamlFile as TrackYaml


def load_track_yaml_file(path: Path) -> TrackYaml:
    """
    raises: FileNotFoundError, yaml.YAMLError
    """
    ret: TrackYaml | None = None
    if not path.exists():
        raise FileNotFoundError(f"Moongas track yaml file '{path}' not found")

    with open(path, "r") as stream:
        ret = cast(TrackYaml, getattr(TrackYaml, "from_yaml")(stream))
    return ret
