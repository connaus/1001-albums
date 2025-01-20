from collections import defaultdict
import streamlit as st
import networkx as nx
import plotly.graph_objects as go

from cfg.cfg import Config
from src.album import Album


class NetworkGraph:

    def __init__(self) -> None:
        self.config: Config = st.session_state.config
        self.albums: list[Album] = [
            album for album in st.session_state.albums if album.personnel()
        ]
        self._all_personnel: dict[str, list[Album]] = {}
        self._linking_people: list[str] | None = None

    @property
    def all_personnel(self) -> dict[str, list[Album]]:
        if self._all_personnel:
            return self._all_personnel
        all_personnel = defaultdict(list)
        for album in self.albums:
            for person in album.personnel():
                all_personnel[person].append(album)
        return all_personnel

    @property
    def linking_people(self) -> list[str]:
        if self._linking_people is not None:
            return self._linking_people
        self._linking_people = [
            person
            for person in self.all_personnel
            if len(self.all_personnel[person]) > 1
        ]
        return self._linking_people

    @property
    def graph(self) -> nx.Graph:
        G = nx.Graph()

        all_personnel: dict[str, list[Album]] = defaultdict(list)
        for album in self.albums:
            for person in album.personnel():
                all_personnel[person].append(album)

        linking_people = [
            person for person in all_personnel if len(all_personnel[person]) > 1
        ]

        nodes = [album.album_title for album in self.albums]
        nodes.extend(linking_people)
        for i in nodes:
            G.add_node(i)

        connections = []
        for person in linking_people:
            for album in all_personnel[person]:
                connections.append((person, album.album_title))

        for i, j in connections:
            G.add_edges_from([(i, j)])

        pos = nx.spring_layout(G, k=0.9, iterations=250)

        for n, p in pos.items():
            G.nodes[n]["pos"] = p

        return G

    # edge_traces = []

    # def role_from_title(person: str, album_title: str) -> str:
    #     album = [
    #         album for album in all_personnel[person] if album.album_title == album_title
    #     ][0]
    #     return album.personnel_role(person)

    # for i, edge in enumerate(G.edges()):
    #     album_title, person = edge
    #     x0, y0 = G.nodes[album_title]["pos"]
    #     x1, y1 = G.nodes[person]["pos"]

    #     role = role_from_title(person, album_title)
    #     edge_traces.append(
    #         go.Scatter(
    #             x=[x0, x1],
    #             y=[y0, y1],
    #             line=dict(
    #                 width=3, color=config.network_graph.connection_colourmap[role]
    #             ),
    #             hoverinfo="none",
    #             showlegend=False,
    #             mode="lines",
    #         )
    #     )

    # # add album nodes
    # album_trace = go.Scatter(
    #     x=[],
    #     y=[],
    #     text=[],
    #     mode="markers",
    #     marker_symbol=config.network_graph.album_symbol,
    #     marker_color=config.network_graph.album_colour,
    #     showlegend=True,
    #     hoverinfo="text",
    #     marker=dict(
    #         showscale=True,
    #         colorscale="RdBu",
    #         reversescale=True,
    #         color=[],
    #         size=10,
    #         colorbar=dict(
    #             thickness=10,
    #             title="Year of Release",
    #             xanchor="left",
    #             titleside="right",
    #         ),
    #         line=dict(width=0),
    #     ),
    # )

    # colors = []
    # for album in albums:
    #     node = album.album_title
    #     x, y = G.nodes[node]["pos"]
    #     album_trace["x"] += tuple([x])  # type: ignore
    #     album_trace["y"] += tuple([y])  # type: ignore
    #     colors.append(album.release_date)
    # album_trace.marker.color = colors  # type: ignore

    # # add people nodes
    # person_trace = go.Scatter(
    #     x=[],
    #     y=[],
    #     text=[],
    #     mode="markers",
    #     marker_symbol=config.network_graph.person_symbol,
    #     marker_color=config.network_graph.person_colour,
    #     hoverinfo="text",
    #     showlegend=False,
    #     marker=dict(
    #         colorscale="RdBu",
    #         reversescale=True,
    #         color=[],
    #         size=5,
    #         line=dict(width=0),
    #     ),
    # )

    # for node in linking_people:
    #     x, y = G.nodes[node]["pos"]
    #     person_trace["x"] += tuple([x])  # type: ignore
    #     person_trace["y"] += tuple([y])  # type: ignore

    # album_info = {album.album_title: album.release_date for album in albums}
    # for _, adjacencies in enumerate(G.adjacency()):
    #     node, adj = adjacencies
    #     if node in album_info:
    #         node_info = (
    #             node + f" ({album_info[node]})<br># of connections: " + str(len(adj))
    #         )
    #         album_trace["text"] += tuple([node_info])  # type: ignore
    #     elif node in linking_people:
    #         node_info = node
    #         for album_title in adj:
    #             role = role_from_title(node, album_title)
    #             colour = config.network_graph.connection_colourmap[role]
    #             node_info += (
    #                 f"<br>{album_title}: <span style='color:{colour}'>{role}</span>."
    #             )
    #         person_trace["text"] += tuple([node_info])  # type: ignore

    # fig = go.Figure(
    #     data=[*edge_traces, album_trace, person_trace],
    #     layout=go.Layout(
    #         title="<br>Test Plot",
    #         titlefont=dict(size=16),
    #         showlegend=False,
    #         coloraxis_showscale=True,
    #         hovermode="closest",
    #         margin=dict(b=20, l=5, r=5, t=40),
    #         xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    #         yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    #     ),
    # )

    # st.plotly_chart(fig)
