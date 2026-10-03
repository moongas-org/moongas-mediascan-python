from dataclasses import dataclass

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase


@dataclass
class MediaFileData(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    MediaFileData contains info scanned from a local media file,
    e.g. ID3 tag metadata.
    It has a lot of overlap with TrackData, naturally, but includes additional
    fields specific to the media file itself e.g. 'format' whereas
    TrackData focuses on an abstract representation of track metadata that may or
    may not have an associated local media file.
    TrackData contains info such as spotify_id, title, artist, album, etc.

    """

    path: str
    size: int
    format: str
    title: str
    artist: str
    albumartist: str
    album: str
    genre: str
    year: int
    duration: int


@dataclass
class MediaFileWithArtistData(MediaFileData):
    """
    Represents a mediafile with (scalar) artist data.
    This data is formed by joining the mediascan db
    mediafiles table with the artists data table.
    """

    artist_name: str
    city: str
    country_code: str
    region_code: str
    language_code: str
