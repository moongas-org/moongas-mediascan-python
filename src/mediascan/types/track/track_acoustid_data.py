from dataclasses import dataclass

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase


@dataclass
class TrackAcoustIDRecording(YAMLWizard, key_transform=LetterCase.CAMEL):
    id: str
    isrcs: list[str]


@dataclass
class TrackAcoustIDResult(YAMLWizard, key_transform=LetterCase.CAMEL):
    id: str
    recordings: list[TrackAcoustIDRecording]
    score: float


@dataclass
class TrackAcoustIDData(YAMLWizard, key_transform=LetterCase.CAMEL):
    """TrackAcoustIDData represents a response from the AcoustID API."""

    results: list[TrackAcoustIDResult]
    status: str
