from enum import StrEnum


class AlbumExcelColumns(StrEnum):

    key = "key"
    album_title = "Album Title"
    artist = "Artist"
    release_date = "Release Date"
    total_time = "Total Times (s)"


class Album(StrEnum):

    key = "key"
    album_title = "album_title"
    artist = "artist"
    release_date = "release_date"
    total_time = "total_time_s"


class PersonalExcelColumns(StrEnum):

    key = "key"
    listened = "listened"
    previous_listened = "previous_listened"
    comments = "Comments"


class PersonalData(StrEnum):

    key = "key"
    listened = "listened"
    previous_listened = "previous_listened"
    comments = "comments"
