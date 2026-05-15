import spotipy


def search_tracks(sp: spotipy.Spotify, track_suggestions: list) -> list:
    tracks = []
    for suggestion in track_suggestions:
        title = suggestion.get("title", "")
        artist = suggestion.get("artist", "")
        result = sp.search(
            q=f"track:{title} artist:{artist}",
            type="track",
            limit=1,
        )
        items = result["tracks"]["items"]
        if items:
            tracks.append(items[0])
    return tracks


def create_and_save_playlist(
    sp: spotipy.Spotify,
    tracks: list,
    name: str,
    description: str,
) -> str:
    playlist = sp._post(
        "me/playlists",
        payload={"name": name, "public": True, "description": description[:300]},
    )
    track_uris = [t["uri"] for t in tracks]
    sp.playlist_add_items(playlist["id"], track_uris)
    return playlist["external_urls"]["spotify"]
