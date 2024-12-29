from dataclasses import dataclass
from datetime import timedelta

from pathlib import Path
import pandas as pd
from cfg.cfg import Config
import cfg.schema as sch


@dataclass
class Album:

    key: int
    album_title: str
    artist: str
    previous_listened: bool
    listened: bool
    release_date: int
    total_time_s: int
    comments: str = ""
    listen_again: str | None = None

    @property
    def album_number(self) -> int:
        return self.key + 1

    @album_number.setter
    def album_number(self, x: int) -> None:
        x = int(x)
        self.key = x - 1

    @property
    def total_time(self) -> timedelta:
        return timedelta(seconds=self.total_time_s)

    @total_time.setter
    def total_time(self, x: timedelta):
        self.total_time_s = x.seconds

    @property
    def hours(self) -> int:
        """returns the number of hours that the album lasts for"""
        return self.total_time.seconds // 3600

    @property
    def minutes(self) -> int:
        """returns the number of minutes past the hour that the album lasts for
        will always be less than 60"""
        m = self.total_time.seconds - (3600 * self.hours)
        return m // 60

    @property
    def seconds(self) -> int:
        """returns the number of seconds past the minute that the album lasts for
        will always be less than 60"""
        s = self.total_time.seconds - (3600 * self.hours) - (60 * self.minutes)
        return s

    def album_details(self) -> dict[str, str | int]:
        return {
            sch.Album.key: self.key,
            sch.Album.album_title: self.album_title,
            sch.Album.artist: self.artist,
            sch.Album.release_date: self.release_date,
            sch.Album.total_time_s: self.total_time_s,
        }

    def personal_details(self) -> dict[str, str | int | bool | None]:
        return {
            sch.PersonalData.key: self.key,
            sch.PersonalData.listened: self.listened,
            sch.PersonalData.previous_listened: self.previous_listened,
            sch.PersonalData.comments: self.comments,
            sch.PersonalData.listen_again: self.listen_again,
        }


def load_albums(cfg: Config) -> list[Album]:
    albums = pd.read_json(Path(cfg.data.album_data_json_path), orient="records")
    personal = pd.read_json(Path(cfg.data.personal_data_json_path), orient="records")
    albums[sch.Album.total_time_s] = albums[sch.Album.total_time_s].fillna(0)

    data = albums.merge(personal, on=sch.Album.key)
    return [Album(**row) for row in data.to_dict("records")]  # type: ignore (arguemnts are of type string, not Hashable)
