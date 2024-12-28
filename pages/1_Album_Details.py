import json
from pathlib import Path
import streamlit as st

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


def save_album_details() -> None:
    albums: list[Album] = st.session_state.albums
    with open(Path(st.session_state.config.data.album_data_json_path), "w") as f:
        json.dump(
            [album.album_details() for album in albums],
            fp=f,
            sort_keys=True,
            indent=4,
        )
    with open(Path(st.session_state.config.data.personal_data_json_path), "w") as f:
        json.dump(
            [album.personal_details() for album in albums],
            fp=f,
            sort_keys=True,
            indent=4,
        )


album = update_album_key(0)

left, right = st.columns(2)
if left.button(
    "Previous",
    use_container_width=True,
):
    album = update_album_key(-1)

if right.button(
    "Next",
    use_container_width=True,
):
    album = update_album_key(1)


def save_abum_comment():
    album.comments = st.session_state.album_comment
    save_album_details()


def save_album_number():
    print(st.session_state.album_number)


# if st.session_state.page_state == PageState.EDIT:
st.markdown(f"# Album Number")
album_number = st.text_input(
    " ",
    f"{album.album_number}",
    label_visibility="collapsed",
    on_change=save_album_number,
    key="album_number",
)
st.markdown(f"# {album.album_title}")
st.markdown(f"{album.artist}")
st.markdown(f"{album.total_time}")

st.markdown("# Comment")
st.text_area(
    " ",
    f"{album.comments}",
    label_visibility="collapsed",
    on_change=save_abum_comment,
    key="album_comment",
)


# elif st.session_state.page_state == PageState.SAVE:
#     if st.session_state.comment is not None:
#         print(st.session_state.comment)
#     st.session_state.page_state = PageState.DEFAULT

# if st.session_state.page_state == PageState.DEFAULT:
#     st.markdown(f"# Album {album.album_number}")
#     st.markdown(f"# {album.album_title}")
#     st.markdown(f"{album.artist}")
#     st.markdown(f"{album.total_time}")

#     st.markdown("# Comment")
#     st.markdown(f"{album.comments}")
