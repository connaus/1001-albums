from pathlib import Path
import streamlit as st

from cfg.cfg import Config, load_config
from src.album import Album, load_albums
import src.album_calcs as ac

SETTING_PATH = Path("C:/Users/ste-c/OneDrive/Documents/1001-albums/cfg/setting.yaml")


def set_albums() -> list[Album]:
    if "albums" in st.session_state:
        return st.session_state.albums
    albums = load_albums(st.session_state.config)
    st.session_state.albums = albums
    return albums


def main() -> None:

    st.session_state.config = load_config(SETTING_PATH)
    albums = set_albums()

    st.set_page_config(
        page_title="Hello",
    )
    st.write("## 1001 Albums to Hear Before you Die")
    left1, right1 = st.columns(2)
    left1.write(
        f"Albums Heard Previously\n\n{ac.albums_previously_listened_to(albums)} / 1001"
    )
    right1.write(
        f"Total Previous Listening Time\n\n{ac.previous_listened_time(albums)}"
    )

    left2, right2 = st.columns(2)
    left2.write(f"New Albums Heard\n\n{ac.albums_newly_listened_to(albums)} / 1001")
    right2.write(f"Total Previous Listening Time\n\n{ac.new_listened_time(albums)}")

    left3, right3 = st.columns(2)
    left3.markdown(f"**Albums Heard**\n\n**{ac.albums_listened_to(albums)} / 1001**")
    right3.markdown(f"**Total Listening Time**\n\n**{ac.total_listened_time(albums)}**")
    st.sidebar.success("Select a page above.")

    next_album = ac.next_album(albums)
    st.write(f"**Next Album**")
    st.write(f"Title: {next_album.album_title}")
    st.write(f"Artist: {next_album.artist}")


if __name__ == "__main__":
    main()
