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
