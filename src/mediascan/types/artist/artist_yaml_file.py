from dataclasses import dataclass
from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase

from .artist_data import ArtistData, ArtistDataOldFmt


@dataclass
class ArtistYamlFile(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    ArtistYamlFile dataclass
    Data model for a single artist.yml YAML file

    """

    artist_data: ArtistData


@dataclass
class ArtistYamlFileOldFmt(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    ArtistYamlFile dataclass
    Data model for a single artist.yml YAML file

    """

    artist_data: ArtistDataOldFmt
