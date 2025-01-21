from collections import defaultdict
from cfg.cfg import Config
import src.album_calcs as ac
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.network_graph import NetworkGraph


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
    config: Config = st.session_state.config
    network_graph = NetworkGraph()
    G = network_graph.graph

    edge_traces = []

    def role_from_title(person: str, album_title: str) -> str:
        album = [
            album
            for album in network_graph.all_personnel[person]
            if album.album_title == album_title
        ][0]
        return album.personnel_role(person)

    for _, edge in enumerate(G.edges()):
        album_title, person = edge
        x0, y0 = G.nodes[album_title]["pos"]
        x1, y1 = G.nodes[person]["pos"]

        role = role_from_title(person, album_title)
        edge_traces.append(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                line=dict(
                    width=3, color=config.network_graph.connection_colourmap[role]
                ),
                hoverinfo="none",
                showlegend=False,
                mode="lines",
            )
        )

    # add album nodes
    album_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        marker_symbol=config.network_graph.album_symbol,
        marker_color=config.network_graph.album_colour,
        showlegend=True,
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="RdBu",
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=10,
                title="Year of Release",
                xanchor="left",
                titleside="right",
            ),
            line=dict(width=0),
        ),
    )

    colors = []
    for album in network_graph.albums:
        node = album.album_title
        x, y = G.nodes[node]["pos"]
        album_trace["x"] += tuple([x])  # type: ignore
        album_trace["y"] += tuple([y])  # type: ignore
        colors.append(album.release_date)
    album_trace.marker.color = colors  # type: ignore

    # add people nodes
    person_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        marker_symbol=config.network_graph.person_symbol,
        marker_color=config.network_graph.person_colour,
        hoverinfo="text",
        showlegend=False,
        marker=dict(
            colorscale="RdBu",
            reversescale=True,
            color=[],
            size=5,
            line=dict(width=0),
        ),
    )

    for node in network_graph.linking_people:
        x, y = G.nodes[node]["pos"]
        person_trace["x"] += tuple([x])  # type: ignore
        person_trace["y"] += tuple([y])  # type: ignore

    album_info = {
        album.album_title: album.release_date for album in network_graph.albums
    }
    # person_info: dict[str, list[tuple[str, str]]] = defaultdict(list)
    person_info: list[list[str]] = []
    for _, adjacencies in enumerate(G.adjacency()):
        node, adj = adjacencies
        if node in album_info:
            node_info = (
                node + f" ({album_info[node]})<br># of connections: " + str(len(adj))
            )
            album_trace["text"] += tuple([node_info])  # type: ignore
        elif node in network_graph.linking_people:
            node_info = node
            for album_title in adj:
                role = role_from_title(node, album_title)
                colour = config.network_graph.connection_colourmap[role]
                node_info += (
                    f"<br>{album_title}: <span style='color:{colour}'>{role}</span>."
                )
                person_info.append([node, album_title, role])
            person_trace["text"] += tuple([node_info])  # type: ignore

    fig = go.Figure(
        data=[*edge_traces, album_trace, person_trace],
        layout=go.Layout(
            title="<br>Network Graph",
            titlefont=dict(size=16),
            showlegend=False,
            coloraxis_showscale=True,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    st.plotly_chart(fig)

    data = pd.DataFrame(
        [[p, a, r, 1] for p, a, r in person_info],
        columns=["Person", "Album", "Role", "Count"],
    )
    df = data[["Person", "Count"]].groupby("Person").count()
    df = df.sort_values(["Count"], ascending=False)
    person_order = df.index.tolist()[:30]
    data = data[data["Person"].isin(person_order)]
    bar = px.bar(
        data,
        x="Count",
        y="Person",
        color="Role",
        title="Top 30 People with the Most Connections",
        color_discrete_map=config.network_graph.connection_colourmap,
        orientation="h",
        hover_data=["Person", "Album", "Role"],
        category_orders={
            "Person": person_order,
            "Role": ["musician", "producer", "arranger", "writer", "unknown"],
        },
        height=800,
    )

    st.plotly_chart(bar)

    data = network_graph.album_connections
    df = data[["Album", "Count"]].groupby("Album").count()
    df = df.sort_values(["Count"], ascending=False)
    album_order = df.index.tolist()[:30]
    data = data[data["Album"].isin(album_order)]
    album_bar = px.bar(
        data,
        x="Count",
        y="Album",
        title="Top 30 Albums with the Most Connections",
        orientation="h",
        hover_data=["Album", "Connecting Album"],
        category_orders={
            "Album": album_order,
        },
        height=800,
    )

    st.plotly_chart(album_bar)


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
