from pathlib import Path
from typing import cast

import yaml

from mediascan.artist_yaml_file_loader import load_artist_yaml_file


def validate_artist_yaml_content(content: str) -> None:
    """Validate YAML syntax and the required artist metadata structure."""
    document = yaml.safe_load(content)
    if not isinstance(document, dict):
        raise ValueError("artistData must be a mapping")

    document_mapping = cast(dict[str, object], document)
    artist_data_value = document_mapping.get("artistData")
    if not isinstance(artist_data_value, dict):
        raise ValueError("artistData must be a mapping")

    artist_data = cast(dict[str, object], artist_data_value)
    REQUIRED_FIELDS = (
        "artistNames",
        "city",
        "countryCode",
        "regionCode",
        "languageCodes",
        "members",
    )
    for required_field in REQUIRED_FIELDS:
        if required_field not in artist_data:
            raise ValueError(f"artistData is missing required tag '{required_field}'")

    if not isinstance(artist_data["members"], list):
        raise ValueError("artistData.members must be a list")

    members = cast(list[object], artist_data["members"])
    for index, member in enumerate(members):
        if not isinstance(member, dict):
            raise ValueError(f"member {index} must be a mapping")
        member = cast(dict[str, object], member)
        # REQUIRED_MEMBER_FIELDS = ("artistNames", "dob", "artistBands", "artistRoles") 
        REQUIRED_MEMBER_FIELDS = ("artistNames",) 
        for required_field in REQUIRED_MEMBER_FIELDS:
            if required_field not in member:
                raise ValueError(f"member {index} is missing required tag '{required_field}'")


def validate_artist_yaml_file(
    artist: str,
    artist_path: Path,
    artist_yaml_paths: list[str],
    artists_missing: list[str],
    exceptions: list[tuple[Path, Exception]],
) -> None:
    """Check an artist YAML file and record missing or invalid files."""
    artist_yaml_path = artist_path / "artist.yml"
    if not artist_yaml_path.exists():
        print(f"{artist_path} missing artist.yml")
        artists_missing.append(artist)
        return

    try:
        artist_yaml_paths.remove(str(artist_yaml_path))
    except Exception as ex:
        print(f"path exists but isn't in the list, how?? '{artist_yaml_path}'")
        exceptions.append((artist_yaml_path, ex))

    try:
        validate_artist_yaml_content(artist_yaml_path.read_text(encoding="utf-8"))
        adf = load_artist_yaml_file(artist_yaml_path)
        if adf.artist_data.country_code.upper() == "UK":
            raise Exception(
                "invalid countryCode 'UK' (United Kingdom country code should be 'GB', per ISO standard)"
            )
        if adf.artist_data.country_code.upper() == "EL":
            raise Exception(
                "invalid countryCode 'EL' (Greece country code should be 'GR', per ISO standard)"
            )
        if len(adf.artist_data.region_code) and "-" not in adf.artist_data.region_code:
            raise Exception(
                f"invalid regionCode '{adf.artist_data.region_code}' (missing hyphen)"
            )
        code = adf.artist_data.country_code
        code_up = adf.artist_data.country_code.upper()
        if code != code_up:
            raise Exception("invalid countryCode (lowercase letters are not allowed, {} != {})".format(code, code_up))
        code = adf.artist_data.region_code
        code_up = adf.artist_data.region_code.upper()
        if code != code_up:
            raise Exception("invalid regionCode (lowercase letters are not allowed, {} != {})".format(code, code_up))
        for language_code in adf.artist_data.language_codes:
            code = language_code
            code_up = language_code.upper()
            if code != code.lower():
                raise Exception(
                    "invalid languageCode (uppercase letters are not allowed, {} != {})".format(code, code_up)
                )
        if adf.artist_data.country_code == "":
            raise Exception("invalid countryCode (must not be empty)")
        if (
            adf.artist_data.city == "Birmingham"
            and adf.artist_data.country_code == "GB"
            and adf.artist_data.region_code != "GB-WMD"
        ):
            raise Exception(
                "The correct region code for Birmingham, UK is GB-WMD (West Midlands)"
            )
        if (
            adf.artist_data.city == "Manchester"
            and adf.artist_data.country_code == "GB"
            and adf.artist_data.region_code != "GB-NWK"
        ):
            raise Exception(
                "The correct region code for Manchester, UK is GB-NWK (North West England)"
            )
        if adf.artist_data.region_code == "GB-HER":
            raise Exception(
                "The correct region code for Herefordshire, UK is GB-WMD (West Midlands)"
            )
    except Exception as ex:
        artists_missing.append(artist)
        exceptions.append((artist_yaml_path, ex))
