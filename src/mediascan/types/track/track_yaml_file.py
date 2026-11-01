from dataclasses import dataclass
from typing import Optional

from dataclass_wizard.v0 import YAMLWizard, json_field
from dataclass_wizard.v0.enums import LetterCase

from ..mediafile.mediafile_data import MediaFileData
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
    mediafile_data: Optional[list[MediaFileData]] = json_field("mediaFileData", all=True, default=None)
