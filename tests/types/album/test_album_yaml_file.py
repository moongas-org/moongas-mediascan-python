from mediascan.types.album.album_yaml_file import AlbumYamlFile


def test_album_yaml_file_from_yaml() -> None:
    loaded = AlbumYamlFile.from_yaml("""
albumData:
  name: Example Album
  dateReleased:
    y: 1993
  explicitCover: true
""")

    assert loaded.album_data.name == "Example Album"
    assert loaded.album_data.date_released.y == 1993
    assert loaded.album_data.date_released.m is None
    assert loaded.album_data.date_released.d is None
    assert loaded.album_data.explicit_cover is True
    assert loaded.album_data.genres == []


def test_album_genres_round_trip() -> None:
    loaded = AlbumYamlFile.from_yaml("""
albumData:
  name: Example Album
  dateReleased: {y: 1993}
  explicitCover: false
  genres: [Rock, Alternative]
""")

    assert loaded.album_data.genres == ["Rock", "Alternative"]
    assert AlbumYamlFile.from_yaml(loaded.to_yaml()) == loaded


def test_album_genres_defaults_are_independent() -> None:
    content = """
albumData:
  name: Example Album
  dateReleased: {y: 1993}
  explicitCover: false
"""
    first = AlbumYamlFile.from_yaml(content)
    second = AlbumYamlFile.from_yaml(content)
    first.album_data.genres.append("Rock")

    assert second.album_data.genres == []
