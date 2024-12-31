import src.album_calcs as ac
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def drop_down():
    title, selection = st.columns(2)
    title.markdown(f"# Select Plots:")
    # options_index = {"Albums Listened": 0, "Time Listened by Year": 1}
    selection.write("")
    selection.write("")
    selection.selectbox(
        " ",
        options=("Albums Listened", "Time Listened by Year", "Artists Heard"),
        index=0,
        label_visibility="collapsed",
        # on_change=plot_selector,
        key="plot_types",
    )


def albums_listened():
    fig = px.bar(
        ac.album_listened_status_by_year(),
        x="Year",
        y="Albums",
        color="Status",
        barmode="stack",
        title="Album Status by Year",
        color_discrete_map={
            "Unlistened": "darkgrey",
            "Listened": "green",
            "Previously Heard": "greenyellow",
        },
    )
    st.plotly_chart(fig)


def time_listened_by_year():
    df = ac.time_listened_by_year()
    fig = px.line(
        df,
        x="Year",
        y=df["Time"] + pd.to_datetime("1970/01/01"),
        title="Time Listened by Year",
        markers=True,
    )
    figure = go.Figure(data=fig)
    figure.update_layout(yaxis_tickformat="%H:%M.%f")
    st.plotly_chart(fig)


def artists_heard():
    df = ac.artists_heard()
    fig = px.pie(
        df,
        values="Artist Count",
        names="Status",
        title="Artists Listened to",
        hole=0.3,
        color="Status",
        color_discrete_map={
            "Not Started": "darkgrey",
            "Finished": "green",
            "In Progress": "greenyellow",
        },
    )

    st.plotly_chart(fig)


def plot_selector():
    drop_down()
    plot_type = st.session_state.plot_types
    if plot_type == "Albums Listened":
        albums_listened()
    elif plot_type == "Time Listened by Year":
        time_listened_by_year()
    elif plot_type == "Artists Heard":
        artists_heard()


plot_selector()
