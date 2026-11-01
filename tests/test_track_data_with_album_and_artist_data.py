from types import SimpleNamespace

from mediascan.types.track.track_data_with_album_and_artist_data import (
    TrackDataWithAlbumAndArtistData,
    row_to_track_data_with_album_and_artist_data,
)


def test_row_to_track_data_with_album_and_artist_data():
    track = row_to_track_data_with_album_and_artist_data(
        SimpleNamespace(
            id=1,
            path="/music/Artist/Album/track.yml",
            album_path="/music/Artist/Album",
            artist_path="/music/Artist",
            title="Track",
            artist="Artist",
            albumartist="Artist",
            album="Album",
            genre="Rock",
            year=2001,
            countrycode="US",
            regioncode="CA",
            city="Los Angeles",
            languagecode="en",
        )
    )

    assert isinstance(track, TrackDataWithAlbumAndArtistData)
    assert track.id == 1
    assert track.path == "/music/Artist/Album/track.yml"
    assert track.format == "mp3"
    assert track.album_path == "/music/Artist/Album"
    assert track.artist_path == "/music/Artist"
    assert track.countryCode == "US"
    assert track.regionCode == "CA"
    assert track.languageCode == "en"
