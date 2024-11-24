from dataclasses import dataclass
from datetime import timedelta

import json
from pathlib import Path
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
    total_time_s: int
    comments: str = ""

    @property
    def total_time(self) -> timedelta:
        return timedelta(seconds=self.total_time_s)

    def album_details(self) -> dict[str, str | int]:
        return {
            "album_number": self.album_number,
            "album_title": self.album_title,
            "artist": self.artist,
            "release_date": self.release_date,
            "total_time_s": self.total_time_s,
        }


def load_albums(cfg: Config) -> list[Album]:
    # albums = pd.read_json(Path(cfg.data.album_data_json_path), orient="records")
    albums = pd.read_csv(
        Path(cfg.data.csv_save_dir) / f"{cfg.data.album_data_csv_name}.csv"
    )
    personal = pd.read_csv(
        Path(cfg.data.csv_save_dir) / f"{cfg.data.personal_data_csv_name}.csv"
    )
    albums[sch.AlbumExcelColumns.total_time] = albums[
        sch.AlbumExcelColumns.total_time
    ].fillna(0)
    albums[sch.AlbumExcelColumns.total_time] = albums[
        sch.AlbumExcelColumns.total_time
    ].apply(lambda x: timedelta(seconds=x))
    albums.rename(
        {
            sch.AlbumExcelColumns.key: "album_number",
            sch.AlbumExcelColumns.album_title: "album_title",
            sch.AlbumExcelColumns.artist: "artist",
            sch.AlbumExcelColumns.release_date: "release_date",
            sch.AlbumExcelColumns.total_time: "total_time",
        },
        axis=1,
        inplace=True,
    )

    personal.rename(
        {
            sch.PersonalExcelColumns.key: "album_number",
            sch.PersonalExcelColumns.previous_listened: "previous_listened",
            sch.PersonalExcelColumns.listened: "listened",
            sch.PersonalExcelColumns.comments: "comments",
        },
        axis=1,
        inplace=True,
    )

    data = albums.merge(personal, on="album_number")
    return [Album(**row) for row in data.to_dict("records")]  # type: ignore (arguemnts are of type string, not Hashable)
