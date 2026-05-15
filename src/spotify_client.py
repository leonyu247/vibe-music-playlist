import spotipy


def get_recommendations(sp: spotipy.Spotify, features: dict, limit: int = 20) -> list:
    seed_genres = features.get("seed_genres", ["pop"])
    # Spotify allows max 5 combined seeds; cap genres at 3
    params = {
        "seed_genres": seed_genres[:3],
        "limit": limit,
    }
    for key in (
        "target_energy",
        "target_valence",
        "target_danceability",
        "target_acousticness",
        "target_instrumentalness",
        "target_tempo",
        "target_popularity",
    ):
        if key in features:
            params[key] = features[key]

    result = sp.recommendations(**params)
    return result.get("tracks", [])


def create_and_save_playlist(
    sp: spotipy.Spotify,
    tracks: list,
    name: str,
    description: str,
) -> str:
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(
        user_id,
        name,
        public=True,
        description=description[:300],
    )
    track_uris = [t["uri"] for t in tracks]
    sp.playlist_add_items(playlist["id"], track_uris)
    return playlist["external_urls"]["spotify"]
