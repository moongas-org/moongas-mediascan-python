from pathlib import Path

import pytest
import yaml

from mediascan.artist_yaml_file_validator import (
    validate_artist_yaml_content,
    validate_artist_yaml_file,
)


def artist_yaml(
    *,
    city: str = "Example City",
    country_code: str = "US",
    region_code: str = "US-CA",
    language_codes: list[str] | None = None,
) -> str:
    languages = language_codes if language_codes is not None else ["en"]
    return yaml.safe_dump(
        {
            "artistData": {
                "artistNames": ["The Example Band"],
                "dob": {"y": 1990},
                "city": city,
                "countryCode": country_code,
                "regionCode": region_code,
                "languageCodes": languages,
                "members": [
                    {
                        "artistNames": ["Example Member"],
                        "dob": {"y": 1970},
                        "artistBands": ["The Example Band"],
                        "artistRoles": ["guitar"],
                    }
                ],
            }
        }
    )


def run_file_validation(
    tmp_path: Path, content: str
) -> tuple[list[str], list[tuple[Path, Exception]], list[str]]:
    artist_yaml_path = tmp_path / "artist.yml"
    artist_yaml_path.write_text(content, encoding="utf-8")
    tracked_paths = [str(artist_yaml_path)]
    artists_missing: list[str] = []
    exceptions: list[tuple[Path, Exception]] = []

    validate_artist_yaml_file(
        "The Example Band",
        tmp_path,
        tracked_paths,
        artists_missing,
        exceptions,
    )
    return artists_missing, exceptions, tracked_paths


def test_validate_artist_yaml_content_accepts_valid_yaml() -> None:
    validate_artist_yaml_content(artist_yaml())


def test_validate_artist_yaml_content_rejects_invalid_yaml() -> None:
    with pytest.raises(yaml.YAMLError):
        validate_artist_yaml_content("artist: [unterminated\n")


def test_validate_artist_yaml_content_accepts_empty_members_list() -> None:
    validate_artist_yaml_content("""artistData:
    artistNames:
        - The Example Band
    dob:
        y: 1990
    city: Example City
    countryCode: US
    regionCode: US-CA
    languageCodes:
        - en
    members: []
""")


@pytest.mark.parametrize(
    "missing_tag", ["artistNames"]
)
def test_validate_artist_yaml_content_requires_member_tags(missing_tag: str) -> None:
    member: dict[str, object] = {
        "artistNames": ["Example Member"],
        "dob": {"y": 1970},
        "artistBands": ["The Example Band"],
        "artistRoles": ["guitar"],
    }
    del member[missing_tag]
    content = yaml.safe_dump(
        {
            "artistData": {
                "artistNames": ["The Example Band"],
                "dob": {"y": 1990},
                "city": "Example City",
                "countryCode": "US",
                "regionCode": "US-CA",
                "languageCodes": ["en"],
                "members": [member],
            }
        }
    )

    with pytest.raises(ValueError, match=f"missing required tag '{missing_tag}'"):
        validate_artist_yaml_content(content)


def test_validate_artist_yaml_file_records_missing_file(tmp_path: Path) -> None:
    artists_missing: list[str] = []
    exceptions: list[tuple[Path, Exception]] = []

    validate_artist_yaml_file(
        "Missing Artist",
        tmp_path,
        [],
        artists_missing,
        exceptions,
    )

    assert artists_missing == ["Missing Artist"]
    assert exceptions == []


def test_validate_artist_yaml_file_accepts_valid_file_and_removes_tracked_path(
    tmp_path: Path,
) -> None:
    artists_missing, exceptions, tracked_paths = run_file_validation(
        tmp_path, artist_yaml()
    )

    assert artists_missing == []
    assert exceptions == []
    assert tracked_paths == []


@pytest.mark.parametrize(
    ("label", "content", "message"),
    [
        (
            "UK country code",
            artist_yaml(country_code="UK"),
            "countryCode 'UK'",
        ),
        (
            "EL country code",
            artist_yaml(country_code="EL"),
            "countryCode 'EL'",
        ),
        (
            "region without hyphen",
            artist_yaml(region_code="CA"),
            "missing hyphen",
        ),
        (
            "lowercase country code",
            artist_yaml(country_code="us"),
            "lowercase letters are not allowed",
        ),
        (
            "lowercase region code",
            artist_yaml(region_code="us-ca"),
            "lowercase letters are not allowed",
        ),
        (
            "uppercase language code",
            artist_yaml(language_codes=["EN"]),
            "languageCode",
        ),
        (
            "empty country code",
            artist_yaml(country_code=""),
            "must not be empty",
        ),
        (
            "Birmingham region",
            artist_yaml(city="Birmingham", country_code="GB", region_code="GB-ENG"),
            "Birmingham",
        ),
        (
            "Manchester region",
            artist_yaml(city="Manchester", country_code="GB", region_code="GB-ENG"),
            "Manchester",
        ),
        (
            "Herefordshire region",
            artist_yaml(country_code="GB", region_code="GB-HER"),
            "Herefordshire",
        ),
    ],
)
def test_validate_artist_yaml_file_rejects_invalid_metadata(
    tmp_path: Path, label: str, content: str, message: str
) -> None:
    artists_missing, exceptions, tracked_paths = run_file_validation(tmp_path, content)

    assert label
    assert artists_missing == ["The Example Band"]
    assert len(exceptions) == 1
    assert message in str(exceptions[0][1])
    assert tracked_paths == []
