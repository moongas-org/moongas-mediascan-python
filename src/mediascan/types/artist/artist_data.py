from dataclasses import dataclass

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase


@dataclass
class Date(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    Data model for date in yaml format with individual y, m and d values e.g.
        y: 1948
        m: 10
        d: 13
    Year is required.
    Month and Day are optional.
    """

    y: int
    m: int | None = None
    d: int | None = None


@dataclass
class ArtistMember(YAMLWizard, key_transform=LetterCase.CAMEL):
    artist_names: list[str]
    artist_bands: list[str] | None = None
    artist_roles: list[str] | None = None
    dob: Date | None = None
    dod: Date | None = None


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
    members: list[ArtistMember]
    dob: Date | None = None
    dod: Date | None = None


@dataclass
class ArtistDataOldFmt(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    ArtistData dataclass
    Data model for artist_data section of artist data YAML file

    Deprecated
    Will be removed in the future
    Basically just keeping this around to facilitate batch YAML updates
    by converting from OldFmt to new format
    """

    artist_names: list[str]
    city: str
    country_code: str
    region_code: str
    language_codes: list[str]
