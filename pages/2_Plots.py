from enum import Enum, StrEnum, auto
from functools import partial
import src.album_calcs as ac
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.network_graph import (
    GenreNetowrkGraph,
    GenreNetworkLines,
    NetworkPlots,
    PersonelNetowrkGraph,
    PersonelNetworkLines,
)


class Graphs(StrEnum):
    ALBUMS_LISTENED = "Albums Listened"
    TIME_LISTENED_BY_YEAR = "Time Listened by Year"
    ARTISTS_HEARD = "Artists Heard"
    GENRES = "Genre Network Graph"
    ALBUM_AVERAGES = "Album Averages"
    NETWORK_GRAPH = "Personel Network Graph"


class NetworkTypes(Enum):
    PERSONEL = auto()
    GENRE = auto()


def drop_down():
    title, selection = st.columns(2)
    title.markdown(f"# Select Plots:")
    selection.write("")
    selection.write("")
    selection.selectbox(
        " ",
        options=Graphs,
        index=0,
        label_visibility="collapsed",
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

    running = px.line(
        ac.running_albums_listened_by_year(),
        x="Year",
        y="Albums",
        title="Cumulative Albums Heard",
        markers=True,
    )
    st.plotly_chart(running)


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

    df2 = ac.running_time_listened_by_year()
    running = px.line(
        df2,
        x="Year",
        y=df2["Time"] + pd.to_datetime("1970/01/01"),
        title="Cumulative Albums Heard",
        markers=True,
    )
    st.plotly_chart(running)


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


def album_averages() -> None:
    """plotting the average length of album by year
    averages are in terms of length / album, tracks / album and length / track"""

    data = ac.annual_averages()
    avg_length_fig = px.line(
        data,
        x="Year",
        y=data["Average Length"] + pd.to_datetime("1970/01/01"),
        title="Average Album Length",
        markers=True,
    )
    st.plotly_chart(avg_length_fig)

    avg_tracks_fig = px.line(
        data,
        x="Year",
        y=data["Average Tracks"],
        title="Average Tracks per Album",
        markers=True,
    )
    st.plotly_chart(avg_tracks_fig)

    avg_track_length_fig = px.line(
        data,
        x="Year",
        y=data["Average Track Length"] + pd.to_datetime("1970/01/01"),
        title="Average Track Length",
        markers=True,
    )
    st.plotly_chart(avg_track_length_fig)


def network_graph(netowrk_type: NetworkTypes) -> None:
    """plotting the network graph, showing all the connections between people who have worked on albums"""
    if netowrk_type == NetworkTypes.PERSONEL:
        if "personel_network" not in st.session_state:
            network_plot = PersonelNetowrkGraph()
            personelnetworklines = PersonelNetworkLines(network_plot)
            st.session_state.personel_network = NetworkPlots(
                network_lines=personelnetworklines,
            )
        network_plots: NetworkPlots = st.session_state.personel_network

    if netowrk_type == NetworkTypes.GENRE:
        if "genre_network" not in st.session_state:
            network_plot = GenreNetowrkGraph()
            personelnetworklines = GenreNetworkLines(network_plot)
            st.session_state.genre_network = NetworkPlots(
                network_lines=personelnetworklines,
            )
        network_plots: NetworkPlots = st.session_state.genre_network

    left, right = st.columns([1, 3])
    left.markdown("")
    left.markdown("")
    left.button(
        "Refresh Graph", on_click=lambda: network_plots.network_graph.create_graph()
    )
    highlight_album = right.selectbox(
        "Highlight album",
        [album.album_title for album in network_plots.network_graph.albums],
        index=None,
        placeholder="Select album...",
    )
    fig = network_plots.network_plot(highlight_album)
    st.plotly_chart(fig)

    people = network_plots.top_nodes()

    st.plotly_chart(people)

    album_bar = network_plots.top_albums()

    st.plotly_chart(album_bar)


def plot_selector():
    drop_down()
    plot_type = st.session_state.plot_types
    plot_funcs = {
        Graphs.ALBUMS_LISTENED: albums_listened,
        Graphs.TIME_LISTENED_BY_YEAR: time_listened_by_year,
        Graphs.ARTISTS_HEARD: artists_heard,
        Graphs.GENRES: partial(network_graph, NetworkTypes.GENRE),
        Graphs.ALBUM_AVERAGES: album_averages,
        Graphs.NETWORK_GRAPH: partial(network_graph, NetworkTypes.PERSONEL),
    }
    plot_funcs[plot_type]()


plot_selector()
