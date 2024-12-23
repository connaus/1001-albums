import json
from pathlib import Path
import streamlit as st

from cfg.cfg import Config
from src.album import Album


def update_album_key(update_value=0) -> Album:
    if "key" not in st.session_state:
        st.session_state.key = 0
    st.session_state.key += update_value
    if st.session_state.key < 0:
        st.session_state.key = 0
    elif st.session_state.key > 1000:
        st.session_state.key = 1000
    return st.session_state.albums[st.session_state.key]


def save_album_details(cfg: Config) -> None:
    albums: list[Album] = st.session_state.albums
    with open(Path(cfg.data.album_data_json_path), "w") as f:
        json.dump(
            [album.album_details() for album in albums],
            fp=f,
            sort_keys=True,
            indent=4,
        )


class PageState:

    DEFAULT = "default"
    EDIT = "edit"
    SAVE = "save"


if "page_state" not in st.session_state:
    st.session_state.page_state = PageState.DEFAULT

album = update_album_key(0)

left, middle, right = st.columns(3)
if middle.button(
    "Edit",
    use_container_width=True,
):
    if st.session_state.page_state == PageState.DEFAULT:
        st.session_state.page_state = PageState.EDIT
    elif st.session_state.page_state == PageState.EDIT:
        st.session_state.page_state = PageState.SAVE
if left.button(
    "Previous",
    use_container_width=True,
    disabled=(
        False
        if st.session_state.page_state in (PageState.DEFAULT, PageState.SAVE)
        else True
    ),
):
    album = update_album_key(-1)

if right.button(
    "Next",
    use_container_width=True,
    disabled=(
        False
        if st.session_state.page_state in (PageState.DEFAULT, PageState.SAVE)
        else True
    ),
):
    album = update_album_key(1)

if st.session_state.page_state == PageState.EDIT:
    st.markdown(f"# Album Number")
    album_number = st.text_area(
        " ", f"{album.album_number}", label_visibility="collapsed"
    )
    st.markdown(f"# {album.album_title}")
    st.markdown(f"{album.artist}")
    st.markdown(f"{album.total_time}")

    st.markdown("# Comment")
    comment = st.text_area(" ", f"{album.comments}", label_visibility="collapsed")
    st.button("Save")
    st.session_state.page_state = PageState.SAVE

elif st.session_state.page_state == PageState.SAVE:
    print("Saving Data")
    st.session_state.page_state = PageState.DEFAULT

if st.session_state.page_state == PageState.DEFAULT:
    st.markdown(f"# Album {album.album_number}")
    st.markdown(f"# {album.album_title}")
    st.markdown(f"{album.artist}")
    st.markdown(f"{album.total_time}")

    st.markdown("# Comment")
    st.markdown(f"{album.comments}")
