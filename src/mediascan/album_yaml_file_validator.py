from pathlib import Path
from typing import cast

import yaml

from mediascan.album_yaml_file_loader import load_album_yaml_file


def validate_album_yaml_content(content: str) -> None:
    """Validate YAML syntax and the required album metadata structure."""
    document = yaml.safe_load(content)
    if not isinstance(document, dict):
        raise ValueError("albumData must be a mapping")

    document_mapping = cast(dict[str, object], document)
    album_data_value = document_mapping.get("albumData")
    if not isinstance(album_data_value, dict):
        raise ValueError("albumData must be a mapping")

    album_data = cast(dict[str, object], album_data_value)
    for required_field in ("name", "dateReleased", "explicitCover"):
        if required_field not in album_data:
            raise ValueError(f"albumData is missing required tag '{required_field}'")

    if not isinstance(album_data["name"], str):
        raise ValueError("albumData.name must be a string")
    if not isinstance(album_data["explicitCover"], bool):
        raise ValueError("albumData.explicitCover must be a boolean")

    date_released_value = album_data["dateReleased"]
    if not isinstance(date_released_value, dict):
        raise ValueError("albumData.dateReleased must be a mapping")
    date_released = cast(dict[str, object], date_released_value)
    if "y" not in date_released:
        raise ValueError("albumData.dateReleased is missing required tag 'y'")
    if type(date_released["y"]) is not int:
        raise ValueError("albumData.dateReleased.y must be an integer")
    for field in ("m", "d"):
        if field in date_released and type(date_released[field]) is not int:
            raise ValueError(f"albumData.dateReleased.{field} must be an integer")


def validate_album_yaml_file(
    album: str,
    album_path: Path,
    album_yaml_paths: list[str],
    albums_missing: list[str],
    exceptions: list[tuple[Path, Exception]],
) -> None:
    """Check an album YAML file and record missing or invalid files."""
    album_yaml_path = album_path / "album.yml"
    if not album_yaml_path.exists():
        print(f"{album_path} missing album.yml")
        albums_missing.append(album)
        return

    try:
        album_yaml_paths.remove(str(album_yaml_path))
    except ValueError as ex:
        print(f"path exists but isn't in the list, how?? '{album_yaml_path}'")
        exceptions.append((album_yaml_path, ex))

    try:
        validate_album_yaml_content(album_yaml_path.read_text(encoding="utf-8"))
        load_album_yaml_file(album_yaml_path)
    except Exception as ex:
        albums_missing.append(album)
        exceptions.append((album_yaml_path, ex))
