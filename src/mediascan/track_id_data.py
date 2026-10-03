from dataclasses import dataclass
from typing import Optional

from dataclass_wizard.v0 import YAMLWizard
from dataclass_wizard.v0.enums import LetterCase


@dataclass
class TrackIdData(YAMLWizard, key_transform=LetterCase.CAMEL):
    """
    TrackIdData contains identifiers and URLs for a track across various streaming services.
    """

    # Industry standard key for cross-platform matching
    isrc: Optional[str] = None

    # Spotify
    spotify_id: Optional[str] = None
    spotify_uri: Optional[str] = None
    spotify_url: Optional[str] = None

    # Apple Music
    apple_music_id: Optional[str] = None
    apple_music_url: Optional[str] = None

    # YouTube & YouTube Music
    youtube_music_id: Optional[str] = None  # Explicitly for ://youtube.com
    youtube_music_url: Optional[str] = None
    youtube_video_id: Optional[str] = None  # Standard video streaming ID
    youtube_video_url: Optional[str] = None

    # Amazon Music
    amazon_music_id: Optional[str] = None
    amazon_music_url: Optional[str] = None

    # Tidal
    tidal_id: Optional[str] = None
    tidal_url: Optional[str] = None

    # Deezer
    deezer_id: Optional[str] = None
    deezer_url: Optional[str] = None
