import json

import pytest

from mediascan.types.track.streaming.streaming_service import StreamingService


def test_streaming_service_values() -> None:
    expected = [
        "spotify",
        "tencent-music",
        "youtube-music",
        "iheartradio",
        "netease-cloud-music",
        "apple-music",
        "jiosaavn",
        "amazon-music",
        "soundcloud",
        "anghami",
        "gaana",
        "pandora",
        "boomplay",
        "deezer",
        "mdundo",
        "audiomack",
        "melon",
        "kakao-music",
        "line-music",
        "kkbox",
        "tidal",
        "yandex-music",
        "joox",
        "napster",
        "rhapsody",
    ]
    assert [service.value for service in StreamingService] == expected
    assert len(StreamingService.__members__) == len(expected)
    for value in expected:
        service = StreamingService(value)
        assert isinstance(service, str)
        assert service == value
        assert str(service) == value
        assert json.loads(json.dumps(service)) == value


def test_streaming_service_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        StreamingService("unknown-service")
