from dataclasses import dataclass
from typing import Optional

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase

from ..track.track_acoustid_data import TrackAcoustIDData
from ..track.track_fpcalc_data import TrackFpCalcData


@dataclass
class MediaFileData(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    MediaFileData contains info scanned from a local media file,
    e.g. ID3 tag metadata.
    It has a lot of overlap with TrackData, naturally, but includes additional
    fields specific to the media file itself e.g. 'format' whereas
    TrackData focuses on an abstract representation of track metadata that may or
    may not have an associated local media file.
    Fields may be absent in partial track YAML entries containing only
    fingerprints and AcoustID results.
    """

    path: Optional[str] = None
    size: Optional[int] = None
    format: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    albumartist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    duration: Optional[int] = None

    fpcalc_data: Optional[TrackFpCalcData] = None
    acoustid_data: Optional[TrackAcoustIDData] = None


@dataclass(kw_only=True)
class MediaFileWithArtistData(MediaFileData):
    """
    Represents a mediafile with (scalar) artist data.
    This data is formed by joining the mediascan db
    mediafiles table with the artists data table.
    Joined artist fields are required keyword-only arguments.
    """

    artist_name: str
    city: str
    country_code: str
    region_code: str
    language_code: str
