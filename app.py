import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

from src.auth import get_auth_url, get_spotify_client, handle_oauth_callback, logout
from src.ai_client import get_playlist_from_vibe
from src.spotify_client import create_and_save_playlist, search_tracks

st.set_page_config(page_title="Vibe Music Playlist", page_icon="🎵", layout="centered")

# --- Auth ---
handle_oauth_callback()
sp = get_spotify_client()

if not sp:
    st.title("Vibe Music Playlist")
    st.write("Describe a mood or scene — get a Spotify playlist instantly.")
    st.info("Connect your Spotify account to get started.")
    st.link_button("Connect to Spotify", get_auth_url(), use_container_width=True, type="primary")
    st.stop()

# --- Sidebar ---
with st.sidebar:
    if "spotify_user" not in st.session_state:
        st.session_state["spotify_user"] = sp.current_user()
    st.write(f"Logged in as **{st.session_state['spotify_user']['display_name']}**")
    if st.button("Logout"):
        logout()
        st.rerun()

# --- Main UI ---
st.title("Vibe Music Playlist")
st.caption("Describe a mood or scene — get a Spotify playlist instantly.")

vibe = st.text_area(
    "What's your vibe?",
    placeholder="e.g. late night drive through a rainy city",
    max_chars=200,
    height=80,
)
st.caption(f"{len(vibe)}/200 characters")

if st.button("Generate Playlist", type="primary", disabled=not vibe.strip()):
    # Clear previous results when generating a new playlist
    for key in ("tracks", "playlist_name", "playlist_description"):
        st.session_state.pop(key, None)

    vibe_error = None
    with st.spinner("Curating your playlist with AI..."):
        try:
            playlist_data = get_playlist_from_vibe(vibe)
        except (ValueError, TimeoutError) as e:
            vibe_error = str(e)
        except Exception as e:
            vibe_error = f"Could not interpret vibe: {e}"

    if vibe_error:
        st.error(vibe_error)
        st.stop()

    spotify_error = None
    with st.spinner("Finding tracks on Spotify..."):
        try:
            tracks = search_tracks(sp, playlist_data.get("tracks", []))
        except Exception as e:
            spotify_error = f"Spotify error: {e}"

    if spotify_error:
        st.error(spotify_error)
        st.stop()

    if not tracks:
        st.warning("No tracks found for this vibe. Try rephrasing it.")
        st.stop()

    st.session_state["tracks"] = tracks
    st.session_state["playlist_name"] = playlist_data.get("playlist_name", "Vibe Playlist")
    st.session_state["playlist_description"] = playlist_data.get("description", "")

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
