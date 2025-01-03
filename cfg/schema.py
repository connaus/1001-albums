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
    total_time_s = "total_time_s"
    tracks = "tracks"
    genres = "genres"
    musicians = "musicians"
    producers = "producers"
    writers = "writers"
    arrangers = "arrangers"


class PersonalExcelColumns(StrEnum):

    key = "key"
    listened = "listened"
    previous_listened = "previous_listened"
    comments = "Comments"
    listen_again = "Listen again?"


class PersonalData(StrEnum):

    key = "key"
    listened = "listened"
    previous_listened = "previous_listened"
    comments = "comments"
    listen_again = "listen_again"
