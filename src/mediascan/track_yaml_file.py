from dataclasses import dataclass
from typing import Optional

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase

from mediascan.track_data import TrackData
from mediascan.track_id_data import TrackIdData


@dataclass
class TrackYamlFile(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    TrackYamlFile contains abstract track metadata,
    It has a lot of overlap with MediaFileData, naturally, but includes additional fields
    such as track identifiers for various streaming services
    whereas MediaFileData contains info specific to a local media file,
    e.g. 'format', which are omitted from TrackYamlFile.
    """

    track_data: TrackData  # Mandatory core track metadata
    track_id_data: Optional[list[TrackIdData]] = (
        None  # Optional track identifiers for various streaming services
    )
