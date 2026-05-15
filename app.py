import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.auth import get_auth_url, get_spotify_client, handle_oauth_callback, logout
from src.gemini_client import get_audio_features_from_vibe
from src.spotify_client import create_and_save_playlist, get_recommendations

st.set_page_config(page_title="Vibe Music Playlist", page_icon="🎵", layout="centered")

# --- Auth ---
handle_oauth_callback()
sp = get_spotify_client()

if not sp:
    st.title("Vibe Music Playlist")
    st.write("Describe a mood or scene — get a Spotify playlist instantly.")
    st.info("Connect your Spotify account to get started.")
    st.link_button("Connect to Spotify", get_auth_url(), use_container_width=True)
    st.stop()

# --- Sidebar ---
with st.sidebar:
    user = sp.current_user()
    st.write(f"Logged in as **{user['display_name']}**")
    if st.button("Logout"):
        logout()
        st.rerun()

# --- Main UI ---
st.title("Vibe Music Playlist")
st.caption("Describe a mood or scene — get a Spotify playlist instantly.")

vibe = st.text_input(
    "What's your vibe?",
    placeholder="e.g. late night drive through a rainy city",
)

if st.button("Generate Playlist", type="primary", disabled=not vibe):
    # Clear previous results when generating a new playlist
    for key in ("tracks", "playlist_name", "playlist_description"):
        st.session_state.pop(key, None)

    with st.spinner("Interpreting your vibe with AI..."):
        try:
            features = get_audio_features_from_vibe(vibe)
        except Exception as e:
            st.error(f"Could not interpret vibe: {e}")
            st.stop()

    with st.spinner("Finding tracks on Spotify..."):
        try:
            tracks = get_recommendations(sp, features)
        except Exception as e:
            st.error(f"Spotify error: {e}")
            st.stop()

    if not tracks:
        st.warning("No tracks found for this vibe. Try rephrasing it.")
        st.stop()

    st.session_state["tracks"] = tracks
    st.session_state["playlist_name"] = features.get("playlist_name", "Vibe Playlist")
    st.session_state["playlist_description"] = features.get("description", "")

# --- Track List ---
if "tracks" in st.session_state:
    tracks = st.session_state["tracks"]
    name = st.session_state.get("playlist_name", "Your Playlist")
    description = st.session_state.get("playlist_description", "")

    st.subheader(name)
    if description:
        st.caption(description)

    st.divider()

    for track in tracks:
        artists = ", ".join(a["name"] for a in track["artists"])
        col_img, col_info = st.columns([1, 5])
        with col_img:
            images = track["album"].get("images")
            if images:
                st.image(images[-1]["url"], width=55)
        with col_info:
            st.write(f"**{track['name']}**")
            st.caption(artists)

    st.divider()

    if st.button("Save to Spotify", type="primary", use_container_width=True):
        with st.spinner("Creating playlist on Spotify..."):
            try:
                url = create_and_save_playlist(
                    sp,
                    tracks,
                    name,
                    description,
                )
            except Exception as e:
                st.error(f"Could not save playlist: {e}")
                st.stop()
        st.success("Playlist saved to your Spotify account!")
        st.link_button("Open in Spotify", url, use_container_width=True)
