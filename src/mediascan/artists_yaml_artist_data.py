from dataclasses import dataclass
from dataclass_wizard.v0 import YAMLWizard

from .artist_data import ArtistData


@dataclass
class ArtistsYamlArtistDirData(YAMLWizard):
    """
    DEPRECATED (only used by deprecated artists.yml)
    an artist, including directory path and the data read from the artist.yml file in said directory
    """

    artist_data: ArtistData
    path: str
