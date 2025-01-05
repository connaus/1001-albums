import streamlit as st
import networkx as nx
import plotly.graph_objs as go

nodes = ["a", "b", "c", "d"]


def network_plot(
    nodes: list[str],
    connections: list[tuple[str, str]],
    colormap: dict[str, str] = {},
):
    G = nx.Graph()
    for i in nodes:
        G.add_node(i)

    for i, j in connections:
        G.add_edges_from([(i, j)])

    pos = nx.spring_layout(G, k=0.5, iterations=50)

    for n, p in pos.items():
        G.nodes[n]["pos"] = p

    x = []
    y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]["pos"]
        x1, y1 = G.nodes[edge[1]]["pos"]
        x += [x0, x1, None]
        y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=x, y=y, line=dict(width=0.5, color="#888"), hoverinfo="none", mode="lines"
    )
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        hoverinfo="text",
        marker=dict(
            colorscale="RdBu",
            reversescale=True,
            color=[],
            # color="blue",
            size=15,
            colorbar=dict(
                thickness=10,
                title="Node Connections",
                xanchor="left",
                titleside="right",
            ),
            line=dict(width=0),
        ),
    )

    colour_array = []
    for node in G.nodes():
        x, y = G.nodes[node]["pos"]
        node_trace["x"] += tuple([x])
        node_trace["y"] += tuple([y])
    #     colour_array.append(colormap.get(node, "blue"))
    # node_trace["marker"]["color"] = colour_array

    for node, adjacencies in enumerate(G.adjacency()):
        node_trace["marker"]["color"] += tuple([len(adjacencies[1])])
        node_info = adjacencies[0] + " # of connections: " + str(len(adjacencies[1]))
        node_trace["text"] += tuple([node_info])
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="<br>Test Plot",
            titlefont=dict(size=16),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="No. of connections",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    st.plotly_chart(fig)
