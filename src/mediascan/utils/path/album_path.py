from typing import NamedTuple, Union
from pathlib import Path
import re


class AlbumPath(NamedTuple):
    path: Path
    valid: bool
    artist_dirname: str
    album_dirname: str
    year: int


def string_contains_trailing_space(s: str) -> bool:
    """Trailing space can causes problems e.g. when burning to a BluRay on Windows,
    I was getting 'file not found' errors for some albums that had trailing space"""
    return bool(s != s.strip())


album_pattern = re.compile(r'[^:\?&#%{}\\\.`$!<>\*"+|=]*\[\d+(-\d+)?\]')
year_pattern = re.compile(r"\[(\d{4})\]")


class AlbumPathBuilder:

    @staticmethod
    def of(path: Union[Path, str]) -> AlbumPath:
        """
        Builds an AlbumPath by parsing and validating the provided absolute path
        """
        path = Path(path)  # convert to Path, if not already
        valid = False
        album_dirname = path.name
        artist_dirname = path.parent.name
        year = AlbumPathBuilder._extract_year(album_dirname)
        if path.is_dir() and AlbumPathBuilder._is_valid_album_dirname(album_dirname) and year != 0:
            valid = True
        return AlbumPath(path, valid, artist_dirname, album_dirname, year)

    @staticmethod
    def _is_valid_album_dirname(dirname: str) -> bool:
        """
        param dirname e.g. "Tha Carter IV [2011]"
        """
        return bool(album_pattern.match(dirname)) and not string_contains_trailing_space(dirname)

    @staticmethod
    def _extract_year(dirname: str) -> int:
        """
        The last value in square brackets is expected to contain the album year
        param dirname e.g. "Tha Carter IV [2011]"
        returns year value e.g. 2011
        """
        ret = 0
        tokens: list[str] = re.findall(year_pattern, dirname)
        if len(tokens):
            ret = int(tokens[-1])
        return ret
