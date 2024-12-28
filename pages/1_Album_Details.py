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


def save_album_comment():
    album.comments = st.session_state.album_comment
    save_album_details()


def save_album_number():
    current_album = st.session_state.albums.pop(album.key)
    current_album.album_number = st.session_state.album_number
    st.session_state.albums.insert(current_album.key, current_album)
    albums: list[Album] = []
    for i, a in enumerate(st.session_state.albums):
        a.key = i
        albums.append(a)
    st.session_state.albums = albums
    save_album_details()
    st.session_state.key = current_album.key


def save_album_length():
    h = int(st.session_state.hours)
    m = int(st.session_state.minutes)
    s = int(st.session_state.seconds)

    total_seconds = (3600 * h) + (60 * m) + s
    album.total_time_s = total_seconds
    save_album_details()


# album title
st.markdown(f"# {album.album_title}")
st.markdown(f"{album.artist}")

# album number
title, value, buff = st.columns([2, 1, 1])
title.markdown(f"# Album Number")
value.write("")
value.write("")
album_number = value.text_input(
    " ",
    value=f"{album.album_number}",
    max_chars=4,
    label_visibility="collapsed",
    on_change=save_album_number,
    key="album_number",
)

## album time
title, value, buff = st.columns([2, 1, 1])
h, s1, m, s2, s = value.columns([3, 1, 3, 1, 3])
title.markdown(f"# Album Length")
h.write("")
h.write("")
h.text_input(
    " ",
    value=album.hours,
    max_chars=4,
    label_visibility="collapsed",
    on_change=save_album_length,
    key="hours",
)
s1.write("")
s1.write("")
s1.write(":")
m.write("")
m.write("")
m.text_input(
    " ",
    value=album.minutes,
    max_chars=4,
    label_visibility="collapsed",
    on_change=save_album_length,
    key="minutes",
)
s2.write("")
s2.write("")
s2.write(":")
s.write("")
s.write("")
s.text_input(
    " ",
    value=album.seconds,
    max_chars=4,
    label_visibility="collapsed",
    on_change=save_album_length,
    key="seconds",
)
st.markdown("# Comment")
st.text_area(
    " ",
    f"{album.comments}",
    label_visibility="collapsed",
    on_change=save_album_comment,
    key="album_comment",
)
