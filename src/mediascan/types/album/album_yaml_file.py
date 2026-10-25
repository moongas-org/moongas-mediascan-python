from dataclasses import dataclass

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase

from .album_data import AlbumData


@dataclass
class AlbumYamlFile(YAMLWizard, key_transform=LetterCase.CAMEL):
    """AlbumYamlFile represents an album.yml file."""

    album_data: AlbumData
