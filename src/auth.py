import os

import spotipy
import streamlit as st
from spotipy.oauth2 import SpotifyOAuth

_SCOPES = "playlist-modify-public playlist-modify-private"


def _get_oauth() -> SpotifyOAuth:
    return SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIFY_REDIRECT_URI"],
        scope=_SCOPES,
        cache_path=".cache",
        open_browser=False,
        show_dialog=False,
    )


def handle_oauth_callback() -> None:
    """Exchange the ?code= query param for a token and store it in session state."""
    error = st.query_params.get("error")
    if error:
        st.query_params.clear()
        st.error(f"Spotify login failed: {error}")
        st.stop()

    code = st.query_params.get("code")
    if code and "spotify_token" not in st.session_state:
        oauth = _get_oauth()
        token_info = oauth.get_access_token(code, as_dict=True, check_cache=False)
        if token_info:
            st.session_state["spotify_token"] = token_info
            st.query_params.clear()
            st.rerun()


def get_spotify_client() -> spotipy.Spotify | None:
    """Return an authenticated Spotipy client, refreshing the token if needed."""
    token_info = st.session_state.get("spotify_token")
    if not token_info:
        return None
    oauth = _get_oauth()
    if oauth.is_token_expired(token_info):
        token_info = oauth.refresh_access_token(token_info["refresh_token"])
        st.session_state["spotify_token"] = token_info
    return spotipy.Spotify(auth=token_info["access_token"], requests_timeout=15)


def get_auth_url() -> str:
    return _get_oauth().get_authorize_url()


def logout() -> None:
    st.session_state.pop("spotify_token", None)
    st.session_state.pop("tracks", None)
    st.session_state.pop("playlist_name", None)
    st.session_state.pop("playlist_description", None)
    st.session_state.pop("spotify_user", None)
