import json
from copy import deepcopy
from typing import Any

import pytest
import yaml
from dataclass_wizard.v0 import asdict, fromdict

from mediascan.types.track.streaming.streaming_data import StreamingData
from mediascan.types.track.streaming.streaming_spotify_data import (
    SpotifyAPIData,
    SpotifyTrack,
    StreamingSpotifyData,
)
from mediascan.types.track.track_id_data import TrackIdData
from mediascan.types.track.track_yaml_file import TrackYamlFile


@pytest.fixture
def spotify_response() -> dict[str, Any]:
    artist = {
        "external_urls": {"spotify": "https://open.spotify.com/artist/1L0y9srZMyh9XUnYGv37IP"},
        "href": "https://api.spotify.com/v1/artists/1L0y9srZMyh9XUnYGv37IP",
        "id": "1L0y9srZMyh9XUnYGv37IP",
        "name": "'Til Tuesday",
        "type": "artist",
        "uri": "spotify:artist:1L0y9srZMyh9XUnYGv37IP",
    }
    track = {
        "album": {
            "album_type": "album",
            "artists": [artist],
            "external_urls": {"spotify": "https://open.spotify.com/album/1y4s0JN8CQMRwPTJ64jCUp"},
            "href": "https://api.spotify.com/v1/albums/1y4s0JN8CQMRwPTJ64jCUp",
            "id": "1y4s0JN8CQMRwPTJ64jCUp",
            "images": [
                {"height": size, "width": size, "url": f"https://i.scdn.co/image/artwork-{size}"} for size in (640, 300, 64)
            ],
            "is_playable": True,
            "name": "Voices Carry (Expanded Edition)",
            "release_date": "1985-06-01",
            "release_date_precision": "day",
            "total_tracks": 14,
            "type": "album",
            "uri": "spotify:album:1y4s0JN8CQMRwPTJ64jCUp",
        },
        "artists": [artist],
        "disc_number": 1,
        "duration_ms": 263573,
        "explicit": False,
        "external_ids": {"isrc": "USSM10027739"},
        "external_urls": {"spotify": "https://open.spotify.com/track/0ZYf6N5eBeXStMri0mf3DZ"},
        "href": "https://api.spotify.com/v1/tracks/0ZYf6N5eBeXStMri0mf3DZ",
        "id": "0ZYf6N5eBeXStMri0mf3DZ",
        "is_local": False,
        "is_playable": True,
        "name": "Voices Carry",
        "track_number": 5,
        "type": "track",
        "uri": "spotify:track:0ZYf6N5eBeXStMri0mf3DZ",
    }
    second_track = deepcopy(track)
    second_track.update(
        id="23zAhaNLZGR0YnMhOs1Aax",
        duration_ms=261800,
        track_number=17,
        external_urls={"spotify": "https://open.spotify.com/track/23zAhaNLZGR0YnMhOs1Aax"},
        href="https://api.spotify.com/v1/tracks/23zAhaNLZGR0YnMhOs1Aax",
        uri="spotify:track:23zAhaNLZGR0YnMhOs1Aax",
    )
    second_track["album"].update(
        album_type="compilation",
        name="The Most Fun You Had All Decade: The 80's",
        release_date="2004-07-06",
        total_tracks=18,
    )
    return {
        "tracks": {
            "href": "https://api.spotify.com/v1/search?offset=0&limit=5&query=isrc%3AUSSM10027739&type=track",
            "limit": 5,
            "next": None,
            "offset": 0,
            "previous": None,
            "total": 0,
            "items": [track, second_track],
        }
    }


@pytest.mark.parametrize("format", ["json", "yaml"])
def test_spotify_response_round_trip(spotify_response: dict[str, Any], format: str) -> None:
    payload = {
        "streamingService": "spotify",
        "trackUrl": "https://open.spotify.com/track/0ZYf6N5eBeXStMri0mf3DZ",
        "trackId": "0ZYf6N5eBeXStMri0mf3DZ",
        "isrc": "USSM10027739",
        "apiData": spotify_response,
    }
    text = json.dumps(payload) if format == "json" else yaml.safe_dump(payload)
    data = StreamingSpotifyData.from_yaml(text)

    assert isinstance(data, StreamingData)
    assert isinstance(data.api_data, SpotifyAPIData)
    assert data.track_id == payload["trackId"]
    assert data.track_url == payload["trackUrl"]
    assert data.isrc == "USSM10027739"
    page = data.api_data.tracks
    assert page.limit == 5
    assert page.total == 0
    assert page.next is None
    assert page.previous is None
    assert len(page.items) == 2
    first, second = page.items
    assert isinstance(first, SpotifyTrack)
    assert first.duration_ms == 263573
    assert first.external_ids.isrc == "USSM10027739"
    assert first.explicit is False
    assert first.is_playable is True
    assert first.artists[0].name == "'Til Tuesday"
    assert first.album.release_date == "1985-06-01"
    assert [image.height for image in first.album.images] == [640, 300, 64]
    assert second.id == "23zAhaNLZGR0YnMhOs1Aax"
    assert second.album.album_type == "compilation"
    assert second.duration_ms == 261800
    assert yaml.safe_load(data.to_yaml()) == payload
    assert json.loads(json.dumps(asdict(data))) == payload


def test_spotify_pagination_and_nullable_images(spotify_response: dict[str, Any]) -> None:
    page = spotify_response["tracks"]
    page["next"] = "https://api.spotify.com/v1/search?offset=5"
    page["previous"] = "https://api.spotify.com/v1/search?offset=0"
    page["items"][0]["album"]["images"][0].update(height=None, width=None)
    data = SpotifyAPIData.from_yaml(json.dumps(spotify_response))

    assert data.tracks.next == page["next"]
    assert data.tracks.previous == page["previous"]
    image = data.tracks.items[0].album.images[0]
    assert image.height is None
    assert image.width is None
    assert yaml.safe_load(data.to_yaml()) == spotify_response


def test_spotify_empty_and_sparse_results() -> None:
    empty = SpotifyAPIData.from_yaml('{"tracks":{"total":0,"items":[]}}')
    assert empty.tracks.items == []
    assert empty.tracks.total == 0
    sparse = SpotifyAPIData.from_yaml(
        '{"tracks":{"items":[{"id":"first","album":{"images":[{"url":"artwork"}]}},{"id":"second"}]}}'
    )
    assert [track.id for track in sparse.tracks.items] == ["first", "second"]
    image = sparse.tracks.items[0].album.images[0]
    assert image.height is None
    assert image.width is None
    assert sparse.tracks.items[0].artists is not sparse.tracks.items[1].artists


@pytest.mark.parametrize(
    "api_data",
    [
        {"tracks": {"limit": "five"}},
        {"tracks": {"items": [{"duration_ms": "long"}]}},
    ],
)
def test_spotify_rejects_invalid_numeric_data(api_data: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        SpotifyAPIData.from_yaml(json.dumps(api_data))


def test_track_id_data_generic_services(spotify_response: dict[str, Any]) -> None:
    entries = [
        {
            "streamingService": "spotify",
            "isrc": "USSM10027739",
            "trackUrl": "https://open.spotify.com/track/example",
            "trackId": "example",
            "apiData": spotify_response,
        },
        {
            "streamingService": "apple-music",
            "trackUrl": "https://music.apple.com/track/example",
            "trackId": "apple-example",
            "apiData": None,
            "isrc": None,
        },
    ]
    payload = {
        "streamingData": entries,
    }
    data = TrackIdData.from_yaml(yaml.safe_dump(payload))
    assert data.streaming_data is not None
    spotify, apple = data.streaming_data
    assert isinstance(spotify, StreamingData)
    assert spotify.api_data == spotify_response
    assert apple.isrc is None
    assert apple.api_data is None
    assert yaml.safe_load(data.to_yaml()) == payload

    apple_without_isrc = fromdict(StreamingData, {key: value for key, value in entries[1].items() if key != "isrc"})
    assert apple_without_isrc.isrc is None
    assert TrackIdData.from_yaml("{}").streaming_data is None
    assert TrackIdData.from_yaml("streamingData: []").streaming_data == []


def test_typed_spotify_serialization_in_track_file(spotify_response: dict[str, Any]) -> None:
    spotify = StreamingSpotifyData(
        streaming_service="spotify",
        track_url="https://open.spotify.com/track/example",
        track_id="example",
        api_data=fromdict(SpotifyAPIData, spotify_response),
    )
    data = TrackYamlFile.from_yaml(
        "trackData: {title: Example, artist: Artist, albumartist: Artist, album: Album, genre: Rock, year: 2026}"
    )
    data.track_id_data = TrackIdData(streaming_data=[spotify])
    serialized = yaml.safe_load(data.to_yaml())
    assert serialized["trackIdData"]["streamingData"][0]["apiData"] == spotify_response
    loaded = TrackYamlFile.from_yaml(data.to_yaml())
    assert loaded.track_id_data is not None
    assert loaded.track_id_data.streaming_data is not None
    assert loaded.track_id_data.streaming_data[0].api_data == spotify_response
