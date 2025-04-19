from collections import defaultdict
from dataclasses import dataclass, field
from itertools import groupby
import pandas as pd
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from cfg.cfg import Config
from src.album import Album
import plotly.express as px


@dataclass
class Person:

    name: str
    _albums: list[Album] = field(default_factory=list)

    @property
    def albums(self) -> list[Album]:
        self._albums.sort(key=lambda x: x.album_title)
        return self._albums

    @albums.setter
    def albums(self, album: Album) -> None:
        self._albums.append(album)

    def album_role(self, album_title: str) -> str:
        album = [album for album in self.albums if album.album_title == album_title][0]
        return album.personnel_role(self.name)

    @property
    def album_key(self) -> int:
        albums = [
            (album.album_title, self.album_role(album.album_title))
            for album in self.albums
        ]
        key = "".join([item for sublist in albums for item in sublist])
        return hash(key)


@dataclass
class Group:

    people: list[Person]
    key: int | None = None

    @property
    def name(self) -> str:
        if len(self.people) == 1:
            return self.people[0].name
        return f"Group {self.key}"

    @property
    def albums(self) -> list[Album]:
        return self.people[0].albums

    def album_role(self, album_title: str) -> str:
        return self.people[0].album_role(album_title)


class NetworkGraph:

    def __init__(self) -> None:
        self.config: Config = st.session_state.config
        self.albums: list[Album] = [
            album for album in st.session_state.albums if album.personnel()
        ]
        self._all_personnel: list[Person] = []
        self._linking_groups: list[Group] | None = None
        self._graph: nx.Graph | None = None
        self._album_connections: pd.DataFrame | None = None

    @property
    def all_personnel(self) -> list[Person]:
        if self._all_personnel:
            return self._all_personnel
        person_dict = defaultdict(list)
        for album in self.albums:
            for person in album.personnel():
                person_dict[person].append(album)
        self._all_personnel = [Person(name, person_dict[name]) for name in person_dict]
        return self._all_personnel

    @property
    def linking_groups(self) -> list[Group]:
        if self._linking_groups is not None:
            return self._linking_groups
        self.all_personnel.sort(key=lambda x: x.album_key)

        self._linking_groups = []
        i = 1
        for _, group in groupby(self.all_personnel, key=lambda x: x.album_key):
            people = list(group)
            if len(people) == 1:
                self._linking_groups.append(Group(people))
                continue
            self._linking_groups.append(Group(people, i))
            i += 1

        self._linking_groups = [
            group for group in self._linking_groups if len(group.albums) > 1
        ]
        return self._linking_groups

    def group_from_name(self, name: str) -> Group:
        """given the name of a group, returns the Group object"""
        return [group for group in self.linking_groups if group.name == name][0]

    @property
    def album_connections(self) -> pd.DataFrame:
        """returns a dataframe with three columns:
        Album: This is an album that is connected to al least one other album
        Connected Album: an album with at least one person connecting the two albums
        Count: This is 1"""
        if self._album_connections is not None:
            return self._album_connections
        connections = nx.to_dict_of_lists(self.graph)
        conns: list[list[str | int]] = []
        for album in self.albums:
            joined_albums: set[str] = set()
            for person in connections[album.album_title]:
                albums = [a for a in connections[person] if a != album.album_title]
                joined_albums.update(albums)
            for connecting_album in joined_albums:
                conns.append([album.album_title, connecting_album, 1])
        self._album_connections = pd.DataFrame(
            conns, columns=["Album", "Connecting Album", "Count"]
        )
        return self._album_connections

    @property
    def graph(self) -> nx.Graph:
        if self._graph is not None:
            return self._graph
        self.create_graph()
        return self.graph

    def create_graph(self) -> None:
        """creates a networkx graph of the albums and linking groups"""
        G = nx.Graph()

        nodes = [album.album_title for album in self.albums]
        nodes.extend([group.name for group in self.linking_groups])
        for i in nodes:
            G.add_node(i)

        connections = []
        for group in self.linking_groups:
            for album in group.albums:
                connections.append((group.name, album.album_title))

        for i, j in connections:
            G.add_edges_from([(i, j)])

        pos = nx.spring_layout(G, k=3, iterations=1000)

        for n, p in pos.items():
            G.nodes[n]["pos"] = p
        self._graph = G


@dataclass
class NetworkNodeColors:
    """A class to store the different methods of colouring the nodes of the network graph"""

    def __init__(self, network_graph: NetworkGraph) -> None:
        self.network_graph = network_graph

    @property
    def release_year(self) -> list[int]:
        """colours the nodes by the release date of the album"""
        return [album.release_date for album in self.network_graph.albums]

    def highlight_album(self, highlight_albums: list[str]) -> list[int]:
        """colours only the selected album and the albums connected to it"""
        base_colour = self.release_year

        return [
            base_colour[i] if album.album_title in highlight_albums else 1955
            for i, album in enumerate(self.network_graph.albums)
        ]


class NetworkPlots:

    def __init__(self) -> None:
        self.config: Config = st.session_state.config
        self.network_graph = NetworkGraph()
        self.network_graph_colors = NetworkNodeColors(self.network_graph)
        self.graph = self.network_graph.graph
        self.album_connections = self.network_graph.album_connections
        self._person_info: list[list[str]] = []

    @property
    def person_info(self) -> list[list[str]]:
        if self._person_info:
            return self._person_info
        self.network_plot()
        return self._person_info

    def _albums_points(self) -> go.Scatter:
        """creates a scattter plot of the albums"""
        # define base graph
        plt = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            marker_symbol=self.config.network_graph.album_symbol,
            showlegend=True,
            hoverinfo="text",
            marker=dict(
                showscale=True,
                colorscale="RdBu",
                reversescale=True,
                color=[],
                size=self.config.network_graph.album_size,
                colorbar=dict(
                    thickness=10,
                    title="Year of Release",
                    xanchor="left",
                    titleside="right",
                ),
                line=dict(width=0),
            ),
        )

        # add album info for hover text
        album_info = {
            album.album_title: (album.release_date, album.artist)
            for album in self.network_graph.albums
        }

        for _, adjacencies in enumerate(self.graph.adjacency()):
            album_name, adj = adjacencies
            # check if the node is an album
            if album_name in album_info:
                x, y = self.graph.nodes[album_name]["pos"]
                plt["x"] += tuple([x])  # type: ignore
                plt["y"] += tuple([y])  # type: ignore
                node_info = (
                    album_name
                    + f" ({album_info[album_name][0]})<br><i>{album_info[album_name][1]}<i><br># of connections: "
                    + str(len(adj))
                )
                plt["text"] += tuple([node_info])  # type: ignore

        return plt

    def _personel_points(self) -> go.Scatter:
        """creates a node for each person or group that links albums"""
        # add people nodes
        plt = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            marker_symbol=self.config.network_graph.person_symbol,
            marker_color=self.config.network_graph.person_colour,
            hoverinfo="text",
            showlegend=False,
        )

        linking_groups = [group.name for group in self.network_graph.linking_groups]
        self._person_info = []
        for _, adjacencies in enumerate(self.graph.adjacency()):
            group_name, adj = adjacencies
            if group_name in linking_groups:
                x, y = self.graph.nodes[group_name]["pos"]
                plt["x"] += tuple([x])  # type: ignore
                plt["y"] += tuple([y])  # type: ignore
                group = self.network_graph.group_from_name(group_name)
                node_info = group_name
                if len(group.people) > 1:
                    node_info += f" ({len(group.people)} people)"
                    if len(group.people) < 6:
                        for person in group.people:
                            node_info += f"<br>{person.name}"
                for album_title in adj:
                    role = group.album_role(album_title)
                    colour = self.config.network_graph.connection_colourmap[role]
                    node_info += f"<br>{album_title}: <span style='color:{colour}'>{role}</span>."
                    self._person_info.append([group_name, album_title, role])
                plt["text"] += tuple([node_info])  # type: ignore

        return plt

    def _network_lines(self, highlight_albums: list[str] = []) -> list[go.Scatter]:
        edge_traces = []
        for _, edge in enumerate(self.graph.edges()):
            album_title, group_name = edge
            x0, y0 = self.graph.nodes[album_title]["pos"]
            x1, y1 = self.graph.nodes[group_name]["pos"]

            group = self.network_graph.group_from_name(group_name)
            role = group.album_role(album_title)
            if not highlight_albums:
                color = self.config.network_graph.connection_colourmap[role]
            elif (album_title in highlight_albums) & (
                highlight_albums[0] in [album.album_title for album in group.albums]
            ):  # the first album is the one being highlighted
                color = self.config.network_graph.connection_colourmap[role]
            else:
                color = "grey"
            edge_traces.append(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    line=dict(
                        width=1,
                        color=color,
                    ),
                    hoverinfo="none",
                    showlegend=False,
                    mode="lines",
                )
            )
        return edge_traces

    def network_plot(self, highlight_album: str | None = None) -> go.Figure:
        """creates a scatter plot of the albums and linking groups"""
        if highlight_album is not None:
            highlight_albums = [highlight_album]
            connections = self.network_graph.album_connections[
                self.network_graph.album_connections["Album"] == highlight_album
            ]["Connecting Album"].tolist()
            highlight_albums += connections

        # the graph is created from overlaying three base graphs
        # a scatter plot of the albums:
        albums = self._albums_points()

        # a scatter plot of the linking people::
        people = self._personel_points()

        # and a set of lines linking the albums and people
        if highlight_album is not None:
            lines = self._network_lines(highlight_albums)
        else:
            lines = self._network_lines()

        if highlight_album is not None:
            colors = []
            symbols = []
            sizes = []
            for album in self.network_graph.albums:
                if album.album_title == highlight_album:
                    colors.append(self.config.network_graph.album_highlight_color)
                    symbols.append(self.config.network_graph.album_symbol)
                    sizes.append(self.config.network_graph.album_highlight_size)
                elif album.album_title in highlight_albums:
                    colors.append(
                        self.config.network_graph.album_highlight_connection_color
                    )
                    symbols.append(self.config.network_graph.album_symbol)
                    sizes.append(self.config.network_graph.album_size)
                else:
                    colors.append(self.config.network_graph.album_lowlight_color)
                    symbols.append(self.config.network_graph.album_symbol)
                    sizes.append(self.config.network_graph.album_lowlight_size)
            # colors = self.network_graph_colors.highlight_album(highlight_albums)
            albums.marker = dict(color=colors, size=sizes, symbol=symbols, opacity=1.0)  # type: ignore
            linking_groups = [group for group in self.network_graph.linking_groups]
            people_colors = []
            people_size = []
            for group in linking_groups:
                album_names = [album.album_title for album in group.albums]
                if highlight_album in album_names:
                    people_colors.append(
                        self.config.network_graph.connection_colourmap[
                            group.album_role(highlight_album)
                        ]
                        # self.config.network_graph.person_highlight_color
                    )
                    people_size.append(self.config.network_graph.person_highlight_size)
                else:
                    people_colors.append(self.config.network_graph.person_colour)
                    people_size.append(self.config.network_graph.person_size)
            people.marker = dict(color=people_colors, size=people_size, opacity=1.0)
        else:
            colors = self.network_graph_colors.release_year
            albums.marker.color = colors  # type: ignore

        return go.Figure(
            data=[*lines, people, albums],
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

    def top_people(self) -> go.Figure:
        """creates a bar plot of the top 30 people with the most connections"""
        data = pd.DataFrame(
            [[p, a, r, 1] for p, a, r in self.person_info],
            columns=["Person", "Album", "Role", "Count"],
        )
        df = data[["Person", "Count"]].groupby("Person").count()
        df = df.sort_values(["Count"], ascending=False)
        person_order = df.index.tolist()[:30]
        data = data[data["Person"].isin(person_order)]
        return px.bar(
            data,
            x="Count",
            y="Person",
            color="Role",
            title="Top 30 People with the Most Connections",
            color_discrete_map=self.config.network_graph.connection_colourmap,
            orientation="h",
            hover_data=["Person", "Album", "Role"],
            category_orders={
                "Person": person_order,
                "Role": ["musician", "producer", "arranger", "writer", "unknown"],
            },
            height=800,
        )

    def top_albums(self) -> go.Figure:
        """creates a bar plot of the top 30 albums with the most connections"""
        data = self.album_connections
        df = data[["Album", "Count"]].groupby("Album").count()
        df = df.sort_values(["Count"], ascending=False)
        album_order = df.index.tolist()[:30]
        data = data[data["Album"].isin(album_order)]
        return px.bar(
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
