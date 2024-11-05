from pathlib import Path
import streamlit as st

from cfg.cfg import load_config
from src.album import Album, load_albums

SETTING_PATH = Path("C:/Users/ste-c/OneDrive/Documents/1001-albums/cfg/setting.yaml")


def main() -> None:
    st.set_page_config(
        page_title="Hello",
    )
    st.write(
        "# 1001 Albums to Hear Before you Die Tracker",
    )
    st.sidebar.success("Select a page above.")


if __name__ == "__main__":
    main()
