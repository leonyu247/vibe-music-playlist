import spotipy


def search_tracks(sp: spotipy.Spotify, track_suggestions: list) -> list:
    tracks = []
    for suggestion in track_suggestions:
        title = suggestion.get("title", "")
        artist = suggestion.get("artist", "")
        try:
            result = sp.search(
                q=f"track:{title} artist:{artist}",
                type="track",
                limit=1,
            )
            items = result["tracks"]["items"]
            if items:
                tracks.append(items[0])
        except Exception:
            continue
    return tracks


def create_and_save_playlist(
    sp: spotipy.Spotify,
    tracks: list,
    name: str,
    description: str,
) -> str:
    page = sp.current_user_playlists(limit=50)
    while page:
        for playlist in page.get("items") or []:
            if playlist["name"].strip().lower() == name.strip().lower():
                raise ValueError(f'You already have a playlist named "{name}". Rename it in Spotify or choose a different vibe.')
        page = sp.next(page) if page["next"] else None

    playlist = sp._post(
        "me/playlists",
        payload={"name": name, "public": True, "description": description[:300]},
    )
    track_uris = [t["uri"] for t in tracks]
    sp.playlist_add_items(playlist["id"], track_uris)
    return playlist.get("external_urls", {}).get("spotify", "https://open.spotify.com")
