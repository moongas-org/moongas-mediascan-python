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
