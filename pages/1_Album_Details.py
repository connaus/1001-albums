from pathlib import Path
import streamlit as st

from cfg.cfg import load_config
from src.album import Album, load_albums

SETTING_PATH = Path("C:/Users/ste-c/OneDrive/Documents/1001-albums/cfg/setting.yaml")


def update_album_key(update_value=0) -> Album:
    if "key" not in st.session_state:
        st.session_state.key = 0
    st.session_state.key += update_value
    if st.session_state.key < 0:
        st.session_state.key = 0
    elif st.session_state.key > 1000:
        st.session_state.key = 1000
    return albums[st.session_state.key]


# TODO: this will re-load the albums on every click, which is surely slow
cfg = load_config(SETTING_PATH)
albums = load_albums(cfg)
album = update_album_key(0)
left, _, right = st.columns(3)
if left.button("Previous", use_container_width=True):
    album = update_album_key(-1)
if right.button("Next", use_container_width=True):
    album = update_album_key(1)
st.markdown(f"# Album {album.album_number + 1}")
st.markdown(f"# {album.album_title}")
st.markdown(f"{album.artist}")
st.markdown(f"{album.total_time}")

st.markdown("# Comment")
st.markdown(f"{album.comments}")
