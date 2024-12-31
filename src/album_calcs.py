from collections import defaultdict
from datetime import timedelta
import pandas as pd
from src.album import Album
import streamlit as st


def next_album(albums: list[Album]) -> Album:
    """find the next album that needs to be listened to"""
    key = min([album.album_number for album in albums if album.listened == False])
    return [album for album in albums if album.album_number == key][0]


def albums_listened_to(albums: list[Album]) -> int:
    return len([album for album in albums if album.listened == True])


def albums_previously_listened_to(albums: list[Album]) -> int:
    return len([album for album in albums if album.previous_listened == True])


def previous_listened_time(albums: list[Album]) -> timedelta:
    total_time = timedelta()
    for album in albums:
        total_time += (
            album.total_time if album.previous_listened == True else timedelta(0)
        )
    return total_time


def albums_newly_listened_to(albums: list[Album]) -> int:
    return len(
        [
            album
            for album in albums
            if (album.previous_listened == False) & (album.listened == True)
        ]
    )


def new_listened_time(albums: list[Album]) -> timedelta:
    total_time = timedelta()
    for album in albums:
        total_time += (
            album.total_time
            if (album.previous_listened == False) & (album.listened == True)
            else timedelta(0)
        )
    return total_time


def total_listened_time(albums: list[Album]) -> timedelta:
    total_time = timedelta()
    for album in albums:
        total_time += album.total_time
    return total_time


def total_albums_by_year(albums: list[Album]) -> dict[int, int]:
    """returns a dictionary of the form {year: number of albums}"""
    d = defaultdict(int)
    for album in albums:
        d[album.release_date] += 1
    return d


def album_listened_status_by_year() -> pd.DataFrame:
    """returns a dataframe of the form {Year, Status, Albums}. Status is one of "Previously Heard", "Listened", "Unlistened"
    the year is unique"""
    d = defaultdict(list)
    for album in st.session_state.albums:
        d["Year"].append(album.release_date)
        if album.previous_listened:
            status = "Previously Heard"
        elif album.listened:
            status = "Listened"
        else:
            status = "Unlistened"
        d["Status"].append(status)
        d["Albums"].append(1)

    listend_df = pd.DataFrame(d)
    listend_df = listend_df.groupby(["Year", "Status"]).sum().reset_index()
    return listend_df


def time_listened_by_year() -> pd.DataFrame:
    """returns a dataframe of the form {Year, Status, Albums}. Status is one of "Previously Heard", "Listened", "Unlistened"
    the year is unique"""
    d = defaultdict(list)
    for album in st.session_state.albums:
        if not album.listened:
            continue
        d["Year"].append(album.release_date)
        d["Time"].append(album.total_time)

    listend_df = pd.DataFrame(d)
    listend_df = listend_df.groupby(["Year"]).sum().reset_index()
    return listend_df


def listened_albums_by_year(albums: list[Album]) -> dict[int, int]:
    d = {year: 0 for year in set([album.release_date for album in albums])}
    for album in albums:
        if album.listened:
            d[album.release_date] += 1
    return d


def listened_time_by_year(albums: list[Album]) -> dict[int, float]:
    d = defaultdict(timedelta)
    for album in albums:
        if album.listened:
            d[album.release_date] += album.total_time
    d = {year: d[year].total_seconds() for year in d}
    return d
