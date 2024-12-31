import src.album_calcs as ac
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

fig = px.bar(
    ac.album_listened_status_by_year(),
    x="Year",
    y="Albums",
    color="Status",
    barmode="stack",
    title="Album Status by Year",
)
# fig.show()
st.plotly_chart(fig)

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
# fig.show()
st.plotly_chart(fig)
