from dataclasses import dataclass

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase


@dataclass
class TrackData(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    TrackData contains core (mandatory) track metadata,
    It has a lot of overlap with MediaFileData, naturally, but excludes fields
    specific to the local media file itself, e.g. 'format'
    """

    title: str
    artist: str
    albumartist: str
    album: str
    genre: str
    year: int
