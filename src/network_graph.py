from collections import defaultdict
from dataclasses import dataclass, field
from itertools import groupby
from typing import Any
import pandas as pd
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from cfg.cfg import Config
from src.album import Album
import plotly.express as px


@dataclass
class LinkingNode:
    """A parent class to store information about nodes that link albums"""

    name: str
    _albums: list[Album] = field(default_factory=list)

    @property
    def albums(self) -> list[Album]:
        """Orders the albums by title. Necessary to ensure that"""
        self._albums.sort(key=lambda x: x.album_title)
        return self._albums

    @albums.setter
    def albums(self, album: Album) -> None:
        self._albums.append(album)

    @property
    def key_list(self) -> list[dict[str, str]]:
        """returns the list that will be hashed to create the key"""
        raise NotImplementedError(
            "The key list has not been implentented for this class"
        )

    @property
    def album_key(self) -> int:
        """returns a hash of the albums that the node is connected to. allows us to group similar nodes"""
        l = []
        for d in self.key_list:
            for key in d:
                l.append(d[key])
        hash_key = "".join(l)
        return hash(hash_key)


class Person(LinkingNode):
    """A subclass of LinkingNode specifically for album personel"""

    def album_role(self, album_title: str) -> str:
        """the role of the person within the album"""
        album = [album for album in self.albums if album.album_title == album_title][0]
        return album.personnel_role(self.name)

    @property
    def key_list(self) -> list[dict[str, str]]:
        return [
            {"Album": album.album_title, "Role": self.album_role(album.album_title)}
            for album in self.albums
        ]


class Genre(LinkingNode):
    """A subclass of LinkingNode specifically for genre data"""

    @property
    def key_list(self) -> list[dict[str, str]]:
        return [{"Album": album.album_title} for album in self.albums]


@dataclass
class Group:

    node: list[LinkingNode]
    key: int | None = None
    x: float | None = None
    y: float | None = None

    @property
    def single_node(self) -> LinkingNode:
        """returns a single node of the group."""
        return self.node[0]

    @property
    def name(self) -> str:
        if len(self.node) == 1:
            return self.single_node.name
        return f"Group {self.key}"

    @property
    def albums(self) -> list[Album]:
        return self.single_node.albums

    @property
    def num_connections(self) -> int:
        return len(self.albums)

    @property
    def group_info(self) -> pd.DataFrame:
        """returns a dataframe with info about the group for the bar cahrts"""
        group_info = self.single_node.key_list

        group_info_data = []
        for d in group_info:
            album_info: list[str | int] = [self.name]
            for key in d:
                album_info.append(d[key])
            album_info.append(1)
            group_info_data.append(album_info)

        return pd.DataFrame(
            group_info_data,
            columns=["Person"] + list(group_info[0].keys()) + ["Count"],
        )


@dataclass
class NetworkAlbum(Album):
    """A class that stores all of the album info, as well as info specific to the network graph"""

    adjacencies: list[str] | None = None
    x: float | None = None
    y: float | None = None

    @property
    def num_connections(self) -> int | None:
        """returns the number of adjacencies for this album"""
        if self.adjacencies is None:
            return None
        return len(self.adjacencies)

    @property
    def group_info(self) -> pd.DataFrame:
        """returns a dataframe with info about the group for the bar cahrts"""

        return pd.DataFrame(
            [
                [self.name, album.album_title, self.album_role(album.album_title), 1]
                for album in self.albums
            ],
            columns=["Person", "Album", "Role", "Count"],
        )


@dataclass
class NetworkAlbum(Album):
    """A class that stores all of the album info, as well as info specific to the network graph"""

    adjacencies: list[str] | None = None
    x: float | None = None
    y: float | None = None

    @property
    def num_connections(self) -> int | None:
        """returns the number of adjacencies for this album"""
        if self.adjacencies is None:
            return None
        return len(self.adjacencies)


class NetworkGraph:

    def __init__(self) -> None:
        self.config: Config = st.session_state.config
        self._adjacencies: dict[str, list[str]] | None = None
        self._albums: list[NetworkAlbum] | None = None
        self._all_links: list[LinkingNode] = []
        self._linking_groups: list[Group] | None = None
        self._graph: nx.Graph | None = None
        self._album_connections: pd.DataFrame | None = None

    @property
    def adjacencies(self) -> dict[str, list[str]]:
        """returns a dictionary of the adjacencies of the graph. the key is the name of a node, and the value is a list of nodes it is linked to"""
        if self._graph is None:
            return {}
        if self._adjacencies is not None:
            return self._adjacencies
        self._adjacencies = {
            node_name: [link for link in adjacencies]
            for node_name, adjacencies in self.graph.adjacency()
        }
        return self._adjacencies

    @staticmethod
    def graph_album(album: Album) -> bool:
        """returns true of the album should be included in the graph, flase otherwise"""
        raise NotImplementedError("This must be impleneted in the child class")

    @property
    def albums(self) -> list[NetworkAlbum]:
        if self._graph is None:
            return [
                NetworkAlbum(**album.__dict__)
                for album in st.session_state.albums
                if self.graph_album(album)
            ]
        if self._albums is not None:
            return self._albums

        self._albums = []
        for album in st.session_state.albums:
            if not self.graph_album(album):
                continue
            x, y = self.graph.nodes[album.album_title]["pos"]
            self._albums.append(
                NetworkAlbum(
                    **album.__dict__,
                    x=x,
                    y=y,
                    adjacencies=self.adjacencies[album.album_title],
                )
            )
        return self._albums

    @property
    def non_album_nodes(self) -> list[LinkingNode]:
        """returns a list of all of the nodes attached to any album"""
        raise NotImplementedError("This must be impleneted in the child class")

    @property
    def linking_groups(self) -> list[Group]:
        """returns a list of the gruops that are connected to at least two albums"""
        # return the saved list, if there is one
        if self._linking_groups is not None:
            return self._linking_groups

        # if not, calculate the list of linking groups
        self.non_album_nodes.sort(key=lambda x: x.album_key)


        linking_groups = []
        i = 1
        for _, group in groupby(self.non_album_nodes, key=lambda x: x.album_key):
            people = list(group)
            if len(people) == 1:
                linking_groups.append(Group(people))
                continue
            linking_groups.append(Group(people, i))
            i += 1

        linking_groups = [group for group in linking_groups if len(group.albums) > 1]
        # if the graph is not yet created, return this list without saving it
        if self._graph is None:
            return linking_groups

        # if the graph is created, add the x and y positions and save the list
        self._linking_groups = []
        for group in linking_groups:
            x, y = self.graph.nodes[group.name]["pos"]
            group.x = x
            group.y = y
            self._linking_groups.append(group)
        return self._linking_groups

    def group_from_name(self, name: str) -> Group:
        """given the name of a group, returns the Group object"""
        return [group for group in self.linking_groups if group.name == name][0]

    @property
    def album_connections(self) -> pd.DataFrame:
        """returns a dataframe with three columns:
        Album: This is an album that is connected to at least one other album
        Connected Album: an album with at least one node connecting the two albums
        Count: This is 1"""
        if self._album_connections is not None:
            return self._album_connections
        connections = nx.to_dict_of_lists(self.graph)
        conns: list[list[str | int]] = []
        for album in self.albums:
            joined_albums: set[str] = set()
            for node in connections[album.album_title]:
                albums = [a for a in connections[node] if a != album.album_title]
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


class PersonelNetowrkGraph(NetworkGraph):
    """A network graph with the album personel as the nodes"""

    @staticmethod
    def graph_album(album: Album) -> bool:
        """returns true of the album should be included in the graph, flase otherwise"""
        if album.personnel():
            return True
        return False

    @property
    def non_album_nodes(self) -> list[LinkingNode]:
        """returns a list of all of the nodes attached to any album"""
        if self._all_links:
            return self._all_links
        node_dict = defaultdict(list)
        for album in self.albums:
            for person in album.personnel():
                node_dict[person].append(album)
        self._all_links = [Person(name, node_dict[name]) for name in node_dict]
        return self._all_links


class GenreNetowrkGraph(NetworkGraph):
    """A network graph with the album genres as the nodes"""

    @staticmethod
    def graph_album(album: Album) -> bool:
        """returns true of the album should be included in the graph, flase otherwise"""
        if album.genres:
            return True
        return False

    @property
    def non_album_nodes(self) -> list[LinkingNode]:
        """returns a list of all of the nodes attached to any album"""
        if self._all_links:
            return self._all_links
        node_dict = defaultdict(list)
        for album in self.albums:
            for genre in album.genres:
                node_dict[genre].append(album)
        self._all_links = [Genre(name, node_dict[name]) for name in node_dict]
        return self._all_links


class PersonelNetworkLines:
    """A class that stores the data for the lines in the Personel network graph"""

    def __init__(self, network_graph: PersonelNetowrkGraph) -> None:
        self.config = network_graph.config
        self.network_graph = network_graph
        self._edge_details: list[dict[str, str]] = []
        self._scatter_plots: list[go.Scatter] | None = None

    @property
    def edge_details(self) -> list[dict[str, str]]:
        if self._edge_details:
            return self._edge_details
        for _, edge in enumerate(self.network_graph.graph.edges()):
            album_title, group_name = edge
            group = self.network_graph.group_from_name(group_name)
            if isinstance(group.single_node, Person):
                role = group.single_node.album_role(album_title)
            self._edge_details.append(
                {
                    "album_title": album_title,
                    "group_name": group_name,
                    "role": role,
                }
            )
        return self._edge_details

    @property
    def scatter_plots(self) -> list[go.Scatter]:
        if self._scatter_plots is not None:
            return self._scatter_plots
        self._scatter_plots = []
        for details in self.edge_details:
            album_title = details["album_title"]
            group_name = details["group_name"]
            role = details["role"]
            x0, y0 = self.network_graph.graph.nodes[album_title]["pos"]
            x1, y1 = self.network_graph.graph.nodes[group_name]["pos"]

            self._scatter_plots.append(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    line=dict(
                        width=1,
                        color=self.config.network_graph.connection_colourmap[role],
                    ),
                    hoverinfo="none",
                    showlegend=False,
                    mode="lines",
                )
            )
        return self._scatter_plots

    def highlight_album(self, highlight_albums: list[str]) -> None:
        """colours only the lines connected to the selected album and the albums connected to it"""
        for plt, details in zip(self.scatter_plots, self.edge_details):
            album_title = details["album_title"]
            group = self.network_graph.group_from_name(details["group_name"])
            group_albums = [album.album_title for album in group.albums]
            role = details["role"]
            if highlight_albums[0] in group_albums:
                plt.line = dict(
                    width=2,
                    color=self.config.network_graph.connection_colourmap[role],
                )
            else:
                plt.line = dict(
                    width=1,
                    color="grey",
                )

    def default_colours(self) -> None:
        """sets the default colours for the lines"""
        for plt, details in zip(self.scatter_plots, self.edge_details):
            role = details["role"]
            plt.line = dict(
                width=1,
                color=self.config.network_graph.connection_colourmap[role],
            )


class GenreNetworkLines:
    """A class that stores the data for the lines in the network graph where the nodes are Genre"""

    def __init__(self, network_graph: NetworkGraph) -> None:
        self.config = network_graph.config
        self.network_graph = network_graph
        self._edge_details: list[dict[str, str]] = []
        self._scatter_plots: list[go.Scatter] | None = None

    @property
    def edge_details(self) -> list[dict[str, str]]:
        if self._edge_details:
            return self._edge_details
        for _, edge in enumerate(self.network_graph.graph.edges()):
            album_title, group_name = edge
            self._edge_details.append(
                {
                    "album_title": album_title,
                    "group_name": group_name,
                }
            )
        return self._edge_details

    @property
    def scatter_plots(self) -> list[go.Scatter]:
        if self._scatter_plots is not None:
            return self._scatter_plots
        self._scatter_plots = []
        for details in self.edge_details:
            album_title = details["album_title"]
            group_name = details["group_name"]
            x0, y0 = self.network_graph.graph.nodes[album_title]["pos"]
            x1, y1 = self.network_graph.graph.nodes[group_name]["pos"]

            self._scatter_plots.append(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    line=dict(
                        width=1,
                        color=self.config.network_graph.connection_default_colour,
                    ),
                    hoverinfo="none",
                    showlegend=False,
                    mode="lines",
                )
            )
        return self._scatter_plots

    def highlight_album(self, highlight_albums: list[str]) -> None:
        """colours only the lines connected to the selected album and the albums connected to it"""
        for plt, details in zip(self.scatter_plots, self.edge_details):
            group = self.network_graph.group_from_name(details["group_name"])
            group_albums = [album.album_title for album in group.albums]
            if highlight_albums[0] in group_albums:
                plt.line = dict(
                    width=2,
                    color=self.config.network_graph.connection_default_colour,
                )
            else:
                plt.line = dict(
                    width=1,
                    color="grey",
                )

    def default_colours(self) -> None:
        """sets the default colours for the lines"""
        for plt in self.scatter_plots:
            plt.line = dict(
                width=1,
                color=self.config.network_graph.connection_default_colour,
            )


class AlbumPoints:
    """A class that stores the data for the lines in the network graph"""

    def __init__(self, network_graph: NetworkGraph) -> None:
        self.config = network_graph.config
        self.network_graph = network_graph
        self._album_info: list[dict[str, int | str]] = []
        self._scatter_plot: go.Scatter | None = None

    @property
    def scatter_plot(self) -> go.Scatter:
        """creates a scattter plot of the albums"""
        if self._scatter_plot is not None:
            return self._scatter_plot
        # define base graph
        self._scatter_plot = go.Scatter(
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

        for album in self.network_graph.albums:
            # check if the node is an album
            self._scatter_plot["x"] += tuple([album.x])  # type: ignore
            self._scatter_plot["y"] += tuple([album.y])  # type: ignore
            node_info = f"{album.album_title} ({album.artist})<br><i>{album.release_date}<i><br># of connections: {album.num_connections}"
            self._scatter_plot["text"] += tuple([node_info])  # type: ignore

        self._scatter_plot.marker = self.default_marker
        return self._scatter_plot

    def highlight_album(self, highlight_albums: list[str]) -> None:
        colors = []
        symbols = []
        sizes = []
        for album in self.network_graph.albums:
            if album.album_title == highlight_albums[0]:
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
        self.scatter_plot.marker = dict(
            showscale=True,
            colorscale="RdBu",
            reversescale=True,
            color=colors,
            size=sizes,
            symbol=symbols,
            opacity=1.0,
            colorbar=dict(
                thickness=10,
                title="Year of Release",
                xanchor="left",
                titleside="right",
            ),
            line=dict(width=0),
        )

    @property
    def default_marker(self) -> dict[str, Any]:
        return dict(
            showscale=True,
            colorscale="RdBu",
            reversescale=True,
            color=[album.release_date for album in self.network_graph.albums],
            size=self.config.network_graph.album_size,
            symbol=self.config.network_graph.album_symbol,
            colorbar=dict(
                thickness=10,
                title="Year of Release",
                xanchor="left",
                titleside="right",
            ),
            line=dict(width=0),
        )

    def default_colours(self) -> None:
        self.scatter_plot.marker = self.default_marker


class NonAlbumPoints:
    """A class that stores the data for the lines in the network graph"""

    def __init__(self, network_graph: NetworkGraph) -> None:
        self.config = network_graph.config

        self.network_graph = network_graph
        self._scatter_plot: go.Scatter | None = None

    @property
    def scatter_plot(self) -> go.Scatter:
        """creates a scattter plot of the albums"""
        if self._scatter_plot is not None:
            return self._scatter_plot
        # add people nodes
        self._scatter_plot = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            marker_symbol=self.config.network_graph.person_symbol,
            marker_color=self.config.network_graph.person_colour,
            hoverinfo="text",
            showlegend=False,
        )

        for group in self.network_graph.linking_groups:
            self._scatter_plot["x"] += tuple([group.x])  # type: ignore
            self._scatter_plot["y"] += tuple([group.y])  # type: ignore
            node_info = group.name
            if len(group.node) > 1:
                node_info += f" ({len(group.node)} people)"
                if len(group.node) < 6:
                    for node in group.node:
                        node_info += f"<br>{node.name}"
            if isinstance(group, Person):
                for album in group.albums:
                    role = group.album_role(album.album_title)
                    colour = self.config.network_graph.connection_colourmap[role]
                    node_info += f"<br>{album.album_title}: <span style='color:{colour}'>{role}</span>."
            else:
                for album in group.albums:
                    node_info += f"<br>{album.album_title}."
            self._scatter_plot["text"] += tuple([node_info])  # type: ignore

        return self._scatter_plot

    def highlight_album(self, highlight_albums: list[str]) -> None:
        """highlight the people connected to the highlighted album"""
        highlight_album = highlight_albums[0]
        people_colors = []
        people_size = []
        for group in self.network_graph.linking_groups:
            album_names = [album.album_title for album in group.albums]
            if highlight_album in album_names:
                if isinstance(group, Person):
                    people_colors.append(
                        self.config.network_graph.connection_colourmap[
                            group.album_role(highlight_album)
                        ]
                        # self.config.network_graph.person_highlight_color
                    )
                else:
                    people_colors.append(
                        self.config.network_graph.album_highlight_color
                    )

                people_size.append(self.config.network_graph.person_highlight_size)
            else:
                people_colors.append(self.config.network_graph.person_colour)
                people_size.append(self.config.network_graph.person_size)
        self.scatter_plot.marker = dict(
            color=people_colors, size=people_size, opacity=1.0
        )

    def default_colours(self) -> None:
        """sets the default colours for the lines"""
        self.scatter_plot.marker = dict(

            color=self.config.network_graph.person_colour,
            size=self.config.network_graph.person_size,
            opacity=1.0,
        )


class NetworkPlots:

    def __init__(self, network_lines: PersonelNetworkLines | GenreNetworkLines) -> None:
        self.config: Config = st.session_state.config
        self.network_graph = network_lines.network_graph
        self.graph = self.network_graph.graph
        self.album_connections = self.network_graph.album_connections
        self.network_lines = network_lines
        self.album_scatter = AlbumPoints(self.network_graph)
        self.non_album_scatter = NonAlbumPoints(self.network_graph)
        self._person_info: list[list[str]] = []

    @property
    def person_info(self) -> list[list[str]]:
        if self._person_info:
            return self._person_info
        self.network_plot()
        return self._person_info

    def network_plot(self, highlight_album: str | None = None) -> go.Figure:
        """creates a scatter plot of the albums and linking groups"""
        if highlight_album is not None:
            highlight_albums = [highlight_album]
            connections = self.network_graph.album_connections[
                self.network_graph.album_connections["Album"] == highlight_album
            ]["Connecting Album"].tolist()
            highlight_albums += connections

        if highlight_album is not None:
            self.album_scatter.highlight_album(highlight_albums)
            self.network_lines.highlight_album(highlight_albums)
            self.non_album_scatter.highlight_album(highlight_albums)
        else:
            self.album_scatter.default_colours()
            self.network_lines.default_colours()
            self.non_album_scatter.default_colours()


        return go.Figure(
            data=[
                *self.network_lines.scatter_plots,
                self.non_album_scatter.scatter_plot,

                self.album_scatter.scatter_plot,
            ],
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

    def top_nodes(self) -> go.Figure:
        """creates a bar plot of the top 30 people with the most connections"""
        nodes = self.network_graph.linking_groups.copy()
        nodes.sort(key=lambda x: x.num_connections, reverse=True)
        nodes = nodes[:30]
        data = pd.concat([group.group_info for group in nodes])
        if "Role" not in data.columns:
            data["Role"] = "unknown"

        return px.bar(
            data,
            x="Count",
            y="Person",
            color="Role",
            title="Top 30 People with the Most Connections",
            color_discrete_map=self.config.network_graph.connection_colourmap,
            orientation="h",
            hover_data=[col for col in data.columns if col != "Count"],
            category_orders={
                "Person": [group.name for group in nodes],
                # "Role": ["musician", "producer", "arranger", "writer", "unknown"],

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
