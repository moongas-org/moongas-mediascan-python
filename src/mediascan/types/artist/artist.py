from dataclasses import dataclass

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase

from .artist_yaml_file import ArtistYamlFile


@dataclass
class Artist(YAMLWizard, key_transform=LetterCase.CAMEL):
    """Artist YAML metadata and the directory containing the file."""

    artist_yaml_file: ArtistYamlFile
    path: str
