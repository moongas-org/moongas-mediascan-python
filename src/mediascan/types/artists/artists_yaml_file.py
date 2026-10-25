from dataclasses import dataclass
from dataclass_wizard.v0 import YAMLWizard

from .artists_yaml_artist_data import ArtistsYamlArtistDirData


@dataclass
class ArtistsYamlFile(YAMLWizard):
    """
    DEPRECATED (only used by deprecated artists.yml)
    Data model for artists.yml file (deprecated)
    artists.yml (plural) = consolidated yml file built from multiple artist.yml output by mediascan cmd/scanartists
    """

    artists: list[ArtistsYamlArtistDirData]
