from pathlib import Path

from mediascan.artist_yaml_file_loader import load_artist_yaml_file


def test_load_artist_yaml_file(tmp_path: Path) -> None:
    artist_yaml_path = tmp_path / "artist.yml"
    artist_yaml_path.write_text("""
artistData:
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

    loaded = load_artist_yaml_file(artist_yaml_path)

    assert loaded.artist_data.artist_names == ["The Example Band"]
    assert loaded.artist_data.city == "Example City"
    assert loaded.artist_data.country_code == "US"
    assert loaded.artist_data.region_code == "US-CA"
