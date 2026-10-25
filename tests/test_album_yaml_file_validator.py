from pathlib import Path

import pytest
import yaml

from mediascan.types.album.album_yaml_file_validator import (
    validate_album_yaml_content,
    validate_album_yaml_file,
)


def album_yaml(
    *, name: str = "Example Album", year: int = 1993, explicit_cover: bool = True
) -> str:
    return yaml.safe_dump(
        {
            "albumData": {
                "name": name,
                "dateReleased": {"y": year},
                "explicitCover": explicit_cover,
            }
        }
    )


def run_file_validation(
    tmp_path: Path, content: str
) -> tuple[list[str], list[tuple[Path, Exception]], list[str]]:
    album_yaml_path = tmp_path / "album.yml"
    album_yaml_path.write_text(content, encoding="utf-8")
    tracked_paths = [str(album_yaml_path)]
    albums_missing: list[str] = []
    exceptions: list[tuple[Path, Exception]] = []

    validate_album_yaml_file(
        "Example Album",
        tmp_path,
        tracked_paths,
        albums_missing,
        exceptions,
    )
    return albums_missing, exceptions, tracked_paths


def test_validate_album_yaml_content_accepts_valid_yaml() -> None:
    validate_album_yaml_content(album_yaml())


def test_validate_album_yaml_content_rejects_invalid_yaml() -> None:
    with pytest.raises(yaml.YAMLError):
        validate_album_yaml_content("albumData: [unterminated\n")


@pytest.mark.parametrize("missing_tag", ["name", "dateReleased", "explicitCover"])
def test_validate_album_yaml_content_requires_album_tags(missing_tag: str) -> None:
    album_data: dict[str, object] = {
        "name": "Example Album",
        "dateReleased": {"y": 1993},
        "explicitCover": True,
    }
    del album_data[missing_tag]

    with pytest.raises(ValueError, match=f"missing required tag '{missing_tag}'"):
        validate_album_yaml_content(yaml.safe_dump({"albumData": album_data}))


def test_validate_album_yaml_content_requires_release_year() -> None:
    with pytest.raises(ValueError, match="dateReleased is missing required tag 'y'"):
        validate_album_yaml_content(
            "albumData:\n  name: Example Album\n  dateReleased: {}\n  explicitCover: true\n"
        )


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (
            "albumData:\n  name: 1993\n  dateReleased: {y: 1993}\n  explicitCover: true\n",
            "albumData.name must be a string",
        ),
        (
            'albumData:\n  name: Example Album\n  dateReleased: {y: 1993}\n  explicitCover: "yes"\n',
            "albumData.explicitCover must be a boolean",
        ),
        (
            "albumData:\n  name: Example Album\n  dateReleased: {y: '1993'}\n  explicitCover: true\n",
            "albumData.dateReleased.y must be an integer",
        ),
    ],
)
def test_validate_album_yaml_content_rejects_invalid_field_types(
    content: str, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_album_yaml_content(content)


def test_validate_album_yaml_file_records_missing_file(tmp_path: Path) -> None:
    albums_missing: list[str] = []
    exceptions: list[tuple[Path, Exception]] = []

    validate_album_yaml_file("Missing Album", tmp_path, [], albums_missing, exceptions)

    assert albums_missing == ["Missing Album"]
    assert exceptions == []


def test_validate_album_yaml_file_accepts_valid_file_and_removes_tracked_path(
    tmp_path: Path,
) -> None:
    albums_missing, exceptions, tracked_paths = run_file_validation(
        tmp_path, album_yaml()
    )

    assert albums_missing == []
    assert exceptions == []
    assert tracked_paths == []


def test_validate_album_yaml_file_records_invalid_file(tmp_path: Path) -> None:
    albums_missing, exceptions, tracked_paths = run_file_validation(
        tmp_path, "albumData: {}\n"
    )

    assert albums_missing == ["Example Album"]
    assert len(exceptions) == 1
    assert "missing required tag 'name'" in str(exceptions[0][1])
    assert tracked_paths == []
