from dataclasses import dataclass

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase

from .artist_data import Date


@dataclass
class AlbumData(YAMLWizard, key_transform=LetterCase.CAMEL):
    """AlbumData contains the contents of the album_data block of an album.yml file."""

    name: str
    date_released: Date
    explicit_cover: bool
