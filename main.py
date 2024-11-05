from pathlib import Path
import streamlit as st

from cfg.cfg import load_config
from src.album import Album, load_albums

SETTING_PATH = Path("C:/Users/ste-c/OneDrive/Documents/1001-albums/cfg/setting.yaml")


def update_album_key(update_value=0) -> None:
    if "key" not in st.session_state:
        st.session_state.key = 0
    st.session_state.key += update_value
    if st.session_state.key < 0:
        st.session_state.key = 1
    elif st.session_state.key > 1000:
        st.session_state.key = 1000


def main() -> None:
    cfg = load_config(SETTING_PATH)
    albums = load_albums(cfg)
    update_album_key(0)
    left, _, right = st.columns(3)
    if left.button("Previous", use_container_width=True):
        update_album_key(-1)
    if right.button("Next", use_container_width=True):
        update_album_key(1)
    st.markdown(f"# Album {albums[st.session_state.key].album_number + 1}")
    st.markdown(f"# {albums[st.session_state.key].album_title}")
    st.markdown(f"{albums[st.session_state.key].artist}")
    st.markdown(f"{albums[st.session_state.key].total_time}")

    st.markdown("# Comment")
    st.markdown(f"{albums[st.session_state.key].comments}")


if __name__ == "__main__":
    main()
