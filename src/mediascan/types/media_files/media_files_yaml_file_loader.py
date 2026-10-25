from pathlib import Path
from typing import cast

from .media_files_yaml_file import MediaFilesYamlFile as MediaFiles


def load_media_files_yaml_file(path: Path | str) -> MediaFiles:
    """
    raises: FileNotFoundError, yaml.YAMLError
    """
    ret: MediaFiles | None = None
    path = Path(path) if isinstance(path, str) else path
    if not path.exists():
        raise FileNotFoundError(f"Moongas mediafiles yaml file '{path}' not found")

    with open(path, "r") as stream:
        ret = cast(MediaFiles, getattr(MediaFiles, "from_yaml")(stream))
    return ret
