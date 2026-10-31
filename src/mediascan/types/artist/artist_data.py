from dataclasses import dataclass

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase

from ..date.date import Date


@dataclass
class ArtistData(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    ArtistData dataclass
    Data model for artist_data section of artist data YAML file

    Required fields:
        artist_names
        city
        country_code
        region_code
        language_codes
    Optional fields:
        dod (date of death)
    """

    artist_names: list[str]
    city: str
    country_code: str
    region_code: str
    language_codes: list[str]
    dob: Date | None = None
    dod: Date | None = None
