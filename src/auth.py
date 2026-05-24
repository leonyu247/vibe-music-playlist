import os
import time

import spotipy
import streamlit as st
from spotipy.oauth2 import SpotifyOAuth

_SCOPES = "playlist-modify-public playlist-modify-private"

# Shared across all sessions in this process. When any tab logs out, this is
# updated so that every other tab is forced out on its next render.
_logout_timestamp: float = 0.0

_SESSION_KEYS = (
    "spotify_token", "login_time", "tracks", "playlist_name",
    "playlist_description", "spotify_user", "generating", "pending_vibe",
)


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


def _clear_session() -> None:
    for key in _SESSION_KEYS:
        st.session_state.pop(key, None)


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
        try:
            token_info = oauth.get_access_token(code, as_dict=True, check_cache=False)
        except Exception:
            st.query_params.clear()
            st.error("Spotify login failed. The link may have expired — please try connecting again.")
            st.stop()
        if token_info:
            st.session_state["spotify_token"] = token_info
            st.session_state["login_time"] = time.time()
            st.query_params.clear()
            st.rerun()


def get_spotify_client() -> spotipy.Spotify | None:
    """Return an authenticated Spotipy client, refreshing the token if needed."""
    token_info = st.session_state.get("spotify_token")
    if not token_info:
        return None

    # Force this tab out if it authenticated before the last logout
    if st.session_state.get("login_time", 0) < _logout_timestamp:
        _clear_session()
        return None

    oauth = _get_oauth()
    if oauth.is_token_expired(token_info):
        try:
            token_info = oauth.refresh_access_token(token_info["refresh_token"])
            st.session_state["spotify_token"] = token_info
        except Exception:
            _clear_session()
            return None
    return spotipy.Spotify(auth=token_info["access_token"], requests_timeout=15)


def get_auth_url() -> str:
    return _get_oauth().get_authorize_url()


def logout() -> None:
    global _logout_timestamp
    _logout_timestamp = time.time()
    _clear_session()
