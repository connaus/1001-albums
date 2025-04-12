from collections import defaultdict
from dataclasses import dataclass, field
from itertools import groupby
import pandas as pd
import streamlit as st
import networkx as nx

from cfg.cfg import Config
from src.album import Album


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
        return [group for group in self.linking_groups if group.name == name][0]

    @property
    def album_connections(self) -> pd.DataFrame:
        """returns a dataframe with three columns:
        Album: This is an album that is connected to al least one other album
        Connected Album: an album with at least one person connecting the two albums
        Count: This is 1"""
        connections = nx.to_dict_of_lists(self.graph)
        conns: list[list[str | int]] = []
        for album in self.albums:
            joined_albums: set[str] = set()
            for person in connections[album.album_title]:
                albums = [a for a in connections[person] if a != album.album_title]
                joined_albums.update(albums)
            for connecting_album in joined_albums:
                conns.append([album.album_title, connecting_album, 1])
        df = pd.DataFrame(conns, columns=["Album", "Connecting Album", "Count"])
        return df

    @property
    def graph(self) -> nx.Graph:
        if self._graph is not None:
            return self._graph
        return self.create_graph()

    def create_graph(self) -> nx.Graph:
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
        return G
