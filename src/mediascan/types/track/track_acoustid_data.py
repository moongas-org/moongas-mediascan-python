from dataclasses import dataclass
from typing import Optional

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase


@dataclass
class TrackAcoustIDRecording(YAMLWizard, key_transform=LetterCase.CAMEL):
    id: str  # MusicBrainz recording ID
    title: Optional[str] = None  # Title of the recording
    length: Optional[int] = None  # Length of the recording in milliseconds
    video: Optional[bool] = None
    disambiguation: Optional[str] = None
    first_release_date: Optional[str] = None
    isrcs: Optional[list[str]] = None


@dataclass
class TrackAcoustIDResult(YAMLWizard, key_transform=LetterCase.CAMEL):
    id: str  # AcoustID result ID
    recordings: list[TrackAcoustIDRecording]
    score: float


@dataclass
class TrackAcoustIDData(YAMLWizard, key_transform=LetterCase.CAMEL):
    """TrackAcoustIDData represents a response from the AcoustID API."""

    results: list[TrackAcoustIDResult]
    status: str
