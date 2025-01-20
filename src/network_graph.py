import streamlit as st
import networkx as nx
import plotly.graph_objects as go


def network_plot(
    nodes: list[str],
    connections: list[tuple[str, str]],
    marker_symbol: list[str],
    marker_colour: list[str],
    connection_type: list[str],
):
    G = nx.Graph()
    for i in nodes:
        G.add_node(i)

    for i, j in connections:
        G.add_edges_from([(i, j)])

    pos = nx.spring_layout(G, k=0.9, iterations=250)

    for n, p in pos.items():
        G.nodes[n]["pos"] = p

    edge_traces = []
    connection_colourmap = {
        "musician": "blue",
        "arranger": "green",
        "writer": "red",
        "producer": "yellow",
        "Unknown": "brown",
    }
    for i, edge in enumerate(G.edges()):
        x0, y0 = G.nodes[edge[0]]["pos"]
        x1, y1 = G.nodes[edge[1]]["pos"]
        edge_traces.append(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                line=dict(width=3, color=connection_colourmap[connection_type[i]]),
                hoverinfo="none",
                mode="lines",
            )
        )

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        marker_symbol=marker_symbol,
        marker_color=marker_colour,
        hoverinfo="text",
        marker=dict(
            colorscale="RdBu",
            reversescale=True,
            color=[],
            size=10,
            line=dict(width=0),
        ),
    )

    for node in G.nodes():
        x, y = G.nodes[node]["pos"]
        node_trace["x"] += tuple([x])  # type: ignore
        node_trace["y"] += tuple([y])  # type: ignore

    for node, adjacencies in enumerate(G.adjacency()):
        node_info = adjacencies[0] + " # of connections: " + str(len(adjacencies[1]))
        node_trace["text"] += tuple([node_info])  # type: ignore
    fig = go.Figure(
        data=[*edge_traces, node_trace],
        layout=go.Layout(
            title="<br>Test Plot",
            titlefont=dict(size=16),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    st.plotly_chart(fig)
