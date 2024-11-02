from dataclasses import dataclass
from datetime import datetime


@dataclass
class Album:

    album_number: int
    album_title: str
    artist: str
    previous_listened: bool
    listened: bool
    release_date: datetime
    comments: str = ""
    _total_time_s: int | None = None

    @property
    def total_time_s(self) -> int | None:
        return self._total_time_s

    @total_time_s.setter
    def total_time_s(self, x: int) -> None:
        self._total_time_s = x

    @property
    def total_time_hrs(self) -> int | None:
        if self.total_time_s is None:
            return None
        return self.total_time_s // 3600

    @total_time_hrs.setter
    def total_time_hrs(self, x: int) -> None:
        if self.total_time_s is None:
            self.total_time_s = x * 3600
        self.total_time_s += x * 3600

    @property
    def total_time_mins(self) -> int | None:
        if self.total_time_s is None:
            return None
        return (self.total_time_s // 60) - (60 * self.total_time_hrs)  # type: ignore (total_time_hrs only None if total_time_s is also None)

    @total_time_mins.setter
    def total_time_mins(self, x: int) -> None:
        if self.total_time_s is None:
            self.total_time_s = x * 60
        self.total_time_s += x * 60
