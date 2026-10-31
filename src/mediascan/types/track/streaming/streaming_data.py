from dataclasses import dataclass
from typing import Any, Optional

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase

from mediascan.types.track.streaming.streaming_service import StreamingService


@dataclass
class StreamingData(YAMLWizard, key_transform=LetterCase.CAMEL):
    """Streaming service track identifiers and an unmodified API response."""

    streaming_service: StreamingService | str
    track_url: str
    track_id: str
    api_data: Any
    isrc: Optional[str] = None
