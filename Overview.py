from pathlib import Path
import streamlit as st

from cfg.cfg import load_config
from src.album import load_albums
import src.album_calcs as ac


def main() -> None:

    # TODO: read settings in a single place
    SETTING_PATH = Path(
        "C:/Users/ste-c/OneDrive/Documents/1001-albums/cfg/setting.yaml"
    )

    # TODO: load albums in a single place
    cfg = load_config(SETTING_PATH)
    albums = load_albums(cfg)

    st.set_page_config(
        page_title="Hello",
    )
    st.write("## 1001 Albums to Hear Before you Die")
    left, right = st.columns(2)
    left.write(f"{ac.albums_listened_to(albums)} / 1001 Albums Heard")
    right.write(f"Total Listening Time: {ac.total_listened_time(albums)}")
    st.sidebar.success("Select a page above.")


if __name__ == "__main__":
    main()
