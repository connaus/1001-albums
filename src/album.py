from dataclasses import dataclass
from datetime import datetime, timedelta

from pathlib import Path
from typing import Any
import pandas as pd
from cfg.cfg import Config
import cfg.schema as sch


@dataclass
class Album:

    album_number: int
    album_title: str
    artist: str
    previous_listened: bool
    listened: bool
    release_date: int
    total_time: timedelta
    comments: str = ""


def load_albums(cfg: Config) -> list[Album]:
    albums = pd.read_csv(
        Path(cfg.data.csv_save_dir) / f"{cfg.data.album_data_csv_name}.csv"
    )
    personal = pd.read_csv(
        Path(cfg.data.csv_save_dir) / f"{cfg.data.personal_data_csv_name}.csv"
    )
    albums[sch.Albums.total_time] = albums[sch.Albums.total_time].fillna(0)
    albums[sch.Albums.total_time] = albums[sch.Albums.total_time].apply(
        lambda x: timedelta(seconds=x)
    )
    albums.rename(
        {
            sch.Albums.key: "album_number",
            sch.Albums.album_title: "album_title",
            sch.Albums.artist: "artist",
            sch.Albums.release_date: "release_date",
            sch.Albums.total_time: "total_time",
        },
        axis=1,
        inplace=True,
    )

    personal.rename(
        {
            sch.PersonalData.key: "album_number",
            sch.PersonalData.previous_listened: "previous_listened",
            sch.PersonalData.listened: "listened",
            sch.PersonalData.comments: "comments",
        },
        axis=1,
        inplace=True,
    )

    data = albums.merge(personal, on="album_number")
    return [Album(**row) for row in data.to_dict("records")]  # type: ignore (arguemnts are of type string, not Hashable)
