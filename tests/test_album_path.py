import pytest

from pathlib import Path
from typing import Generator

from mediascan.utils.path.album_path import AlbumPathBuilder


@pytest.fixture(scope="function")
def good_album_path(tmp_path: Path) -> Generator[Path, None, None]:
    """A good album path - it exists and album dir name is compliant"""
    album_path = tmp_path / 'data' / 'Music' / 'Lil Wayne' / 'Tha Carter IV [2011]'
    album_path.mkdir(parents=True, exist_ok=True)
    assert album_path.exists() and album_path.is_dir()
    yield album_path


@pytest.fixture(scope="function")
def bad_album_path_trailing_space(tmp_path: Path) -> Generator[Path, None, None]:
    """A bad album path - it exists but album dir name is non-compliant due to trailing space"""
    album_path = tmp_path / 'data' / 'Music' / 'Lil Wayne' / 'Tha Carter IV [2011] '
    album_path.mkdir(parents=True, exist_ok=True)
    assert album_path.exists() and album_path.is_dir()
    yield album_path


def test_albumpathbuilder_good_path(good_album_path: Path):
    assert good_album_path.exists()
    a = AlbumPathBuilder.of(str(good_album_path))
    assert str(a.path).endswith("/data/Music/Lil Wayne/Tha Carter IV [2011]")
    assert a.valid == True
    assert a.artist_dirname == "Lil Wayne"
    assert a.album_dirname == "Tha Carter IV [2011]"
    assert a.year == 2011


def test_albumpathbuilder_bad_path_trailing_space(bad_album_path_trailing_space: Path):
    assert bad_album_path_trailing_space.exists()
    a = AlbumPathBuilder.of(str(bad_album_path_trailing_space))
    assert str(a.path).endswith("/data/Music/Lil Wayne/Tha Carter IV [2011] ")
    assert a.valid == False
    assert a.artist_dirname == "Lil Wayne"
    assert a.album_dirname == "Tha Carter IV [2011] "
    assert a.year == 2011
