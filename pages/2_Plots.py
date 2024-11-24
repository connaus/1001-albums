from src.album import Album

# import matplotlib.figure as fig
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import src.album_calcs as ac
import streamlit as st


albums: list[Album] = st.session_state.albums
total = ac.total_albums_by_year(albums)
listend = ac.listened_albums_by_year(albums)
listend_time = ac.listened_time_by_year(albums)

fig, axs = plt.subplots(1, 2)
ax1, ax2 = axs

labels = ("Total Albums", "Listened Albums")
ax1.bar(x=list(total.keys()), height=list(total.values()))
ax1.plot(list(listend.keys()), list(listend.values()), "ro-", markersize=3)
ax1.set_title("Albums per Year")


def format_seconds(seconds: float, _) -> str:
    return f"{int(seconds // 3600)}"


ax2.plot(list(listend_time.keys()), list(listend_time.values()), "o-", markersize=3)
ax2.yaxis.set_major_formatter(format_seconds)
ax2.set_title("Time Listened")
ax2.yaxis.set_major_locator(tkr.MultipleLocator(base=3600))
st.write(fig)
