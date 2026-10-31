from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase

from .media_file_acoustid_data import MediaFileAcoustIDData
from .media_file_fpcalc_data import MediaFileFpCalcData


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
    album_path: str = ""
    artist_path: str = ""
    size: Optional[int] = None
    format: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    albumartist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    duration: Optional[float] = None
    mod_time: Optional[datetime] = None

    fpcalc_data: Optional[MediaFileFpCalcData] = None
    acoustid_data: Optional[MediaFileAcoustIDData] = None
