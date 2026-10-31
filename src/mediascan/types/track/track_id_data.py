from dataclasses import dataclass
from typing import Optional

from .streaming.streaming_data import StreamingData

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase


@dataclass
class TrackIdData(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    TrackIdData contains streaming service data for an abstract track.
    """

    streaming_data: Optional[list[StreamingData]] = None
