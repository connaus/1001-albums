from collections import defaultdict
from datetime import timedelta

from src.album import Album



def total_albums_by_year(albums: list[Album]) -> dict[int, int]:
    d = defaultdict(int)
    for album in albums:
        d[album.release_date] += 1
    return d


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
