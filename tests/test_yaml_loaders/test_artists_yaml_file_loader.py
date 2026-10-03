from pathlib import Path

import pytest
import yaml

from mediascan.artists_yaml_file_loader import load_artists_yaml_file

VALID_ARTISTS_YAML = """
artists:
  - artistData:
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
    path: /music/The Example Band
  - artistData:
      artistNames:
        - The Example Band 2
      dob:
        y: 1991
      city: Example City 2
      countryCode: CA
      regionCode: CA-ON
      languageCodes:
        - en
      members: []
    path: /music/The Example Band 2
"""


def test_load_artists_yaml_file_from_path(tmp_path: Path) -> None:
    artists_yaml_path = tmp_path / "artists.yml"
    artists_yaml_path.write_text(VALID_ARTISTS_YAML)

    loaded = load_artists_yaml_file(artists_yaml_path)

    assert len(loaded.artists) == 2
    artist = loaded.artists[0]
    assert artist.path == "/music/The Example Band"
    assert artist.artist_data.artist_names == ["The Example Band"]
    assert artist.artist_data.country_code == "US"
    assert artist.artist_data.region_code == "US-CA"

    artist2 = loaded.artists[1]
    assert artist2.path == "/music/The Example Band 2"
    assert artist2.artist_data.artist_names == ["The Example Band 2"]
    assert artist2.artist_data.country_code == "CA"
    assert artist2.artist_data.region_code == "CA-ON"


def test_load_artists_yaml_file_accepts_string_path(tmp_path: Path) -> None:
    artists_yaml_path = tmp_path / "artists.yml"
    artists_yaml_path.write_text(VALID_ARTISTS_YAML)

    loaded = load_artists_yaml_file(str(artists_yaml_path))

    assert len(loaded.artists) == 2
    artist = loaded.artists[0]
    assert artist.path == "/music/The Example Band"
    assert artist.artist_data.artist_names == ["The Example Band"]
    assert artist.artist_data.country_code == "US"
    assert artist.artist_data.region_code == "US-CA"

    artist2 = loaded.artists[1]
    assert artist2.path == "/music/The Example Band 2"
    assert artist2.artist_data.artist_names == ["The Example Band 2"]
    assert artist2.artist_data.country_code == "CA"
    assert artist2.artist_data.region_code == "CA-ON"


def test_load_artists_yaml_file_raises_for_missing_path(tmp_path: Path) -> None:
    artists_yaml_path = tmp_path / "missing.yml"

    with pytest.raises(
        FileNotFoundError,
        match="Moongas artists yaml file .*missing.yml.* not found",
    ):
        load_artists_yaml_file(artists_yaml_path)


def test_load_artists_yaml_file_propagates_yaml_errors(tmp_path: Path) -> None:
    artists_yaml_path = tmp_path / "invalid.yml"
    artists_yaml_path.write_text("artists: [\n")

    with pytest.raises(yaml.YAMLError):
        load_artists_yaml_file(artists_yaml_path)
