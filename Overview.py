import streamlit as st


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
