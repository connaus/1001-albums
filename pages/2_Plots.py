from collections import defaultdict
from src.album import Album
import src.album_calcs as ac
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.network_graph import network_plot


def drop_down():
    title, selection = st.columns(2)
    title.markdown(f"# Select Plots:")
    # options_index = {"Albums Listened": 0, "Time Listened by Year": 1}
    selection.write("")
    selection.write("")
    selection.selectbox(
        " ",
        options=(
            "Albums Listened",
            "Time Listened by Year",
            "Artists Heard",
            "Network Graph",
        ),
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


def network_graph() -> None:
    """plotting the network graph, showing all the connections between people who have worked on albums"""
    albums = st.session_state.albums
    nodes = []
    marker_symbol = []
    marker_colour = []
    all_personnel = defaultdict(list)
    for album in albums:
        if not album.personnel(writers=True):
            continue
        nodes.append(album.album_title)
        marker_symbol.append("square")
        marker_colour.append("deepskyblue")
        for person in album.personnel(writers=True):
            if person in album.musicians:
                role = "musician"
            elif person in album.arrangers:
                role = "arranger"
            elif person in album.writers:
                role = "writer"
            elif person in album.producers:
                role = "producer"
            else:
                role = "Unknown"
            all_personnel[person].append((album.album_title, role))
    linking_people = [
        person for person in all_personnel if len(set(all_personnel[person])) > 1
    ]
    nodes.extend(linking_people)
    marker_symbol.extend(["circle" for _ in range(len(linking_people))])
    marker_colour.extend(["darkgrey" for _ in range(len(linking_people))])
    connections = []
    connection_type = []
    for person in linking_people:
        for album, role in all_personnel[person]:
            connections.append((person, album))
            connection_type.append(role)

    network_plot(
        nodes=nodes,
        connections=connections,
        marker_symbol=marker_symbol,
        marker_colour=marker_colour,
        connection_type=connection_type,
    )


def plot_selector():
    drop_down()
    plot_type = st.session_state.plot_types
    if plot_type == "Albums Listened":
        albums_listened()
    elif plot_type == "Time Listened by Year":
        time_listened_by_year()
    elif plot_type == "Artists Heard":
        artists_heard()
    elif plot_type == "Network Graph":
        network_graph()


plot_selector()
