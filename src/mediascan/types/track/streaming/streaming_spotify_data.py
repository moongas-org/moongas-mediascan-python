from dataclasses import dataclass, field
from typing import Optional

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase

from .streaming_data import StreamingData


@dataclass
class SpotifyExternalURLs(YAMLWizard, key_transform=LetterCase.NONE):
    spotify: str = ""


@dataclass
class SpotifyExternalIDs(YAMLWizard, key_transform=LetterCase.NONE):
    isrc: str = ""


@dataclass
class SpotifyImage(YAMLWizard, key_transform=LetterCase.NONE):
    height: Optional[int] = None
    width: Optional[int] = None
    url: str = ""


@dataclass
class SpotifyArtist(YAMLWizard, key_transform=LetterCase.NONE):
    external_urls: SpotifyExternalURLs = field(default_factory=SpotifyExternalURLs)
    href: str = ""
    id: str = ""
    name: str = ""
    type: str = ""
    uri: str = ""


@dataclass
class SpotifyAlbum(YAMLWizard, key_transform=LetterCase.NONE):
    album_type: str = ""
    artists: list[SpotifyArtist] = field(default_factory=list[SpotifyArtist])
    external_urls: SpotifyExternalURLs = field(default_factory=SpotifyExternalURLs)
    href: str = ""
    id: str = ""
    images: list[SpotifyImage] = field(default_factory=list[SpotifyImage])
    is_playable: bool = False
    name: str = ""
    release_date: str = ""
    release_date_precision: str = ""
    total_tracks: int = 0
    type: str = ""
    uri: str = ""


@dataclass
class SpotifyTrack(YAMLWizard, key_transform=LetterCase.NONE):
    album: SpotifyAlbum = field(default_factory=SpotifyAlbum)
    artists: list[SpotifyArtist] = field(default_factory=list[SpotifyArtist])
    disc_number: int = 0
    duration_ms: int = 0
    explicit: bool = False
    external_ids: SpotifyExternalIDs = field(default_factory=SpotifyExternalIDs)
    external_urls: SpotifyExternalURLs = field(default_factory=SpotifyExternalURLs)
    href: str = ""
    id: str = ""
    is_local: bool = False
    is_playable: bool = False
    name: str = ""
    track_number: int = 0
    type: str = ""
    uri: str = ""


@dataclass
class SpotifyTrackPage(YAMLWizard, key_transform=LetterCase.NONE):
    href: str = ""
    limit: int = 0
    next: Optional[str] = None
    offset: int = 0
    previous: Optional[str] = None
    total: int = 0
    items: list[SpotifyTrack] = field(default_factory=list[SpotifyTrack])


@dataclass
class SpotifyAPIData(YAMLWizard, key_transform=LetterCase.NONE):
    """Raw Spotify track search response, retaining Spotify's field names."""

    tracks: SpotifyTrackPage = field(default_factory=SpotifyTrackPage)


@dataclass
class StreamingSpotifyData(StreamingData, key_transform=LetterCase.CAMEL):
    """Spotify track identifiers and its typed search response."""

    api_data: SpotifyAPIData
