from dataclasses import dataclass
from typing import Optional

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase

from ..media_file.media_file_data import MediaFileData
from .track_data import TrackData
from .track_id_data import TrackIdData


@dataclass
class TrackYamlFile(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    TrackYamlFile contains abstract track metadata, streaming identifiers,
    and optional local media-file metadata and fingerprints.
    """

    track_data: TrackData  # Mandatory core track metadata
    track_id_data: Optional[TrackIdData] = None  # Optional track identifiers for various streaming services
    media_file_data: Optional[list[MediaFileData]] = None
