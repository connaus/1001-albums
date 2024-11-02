from enum import StrEnum


class Albums(StrEnum):

    key = "key"
    album_title = "Album Title"
    artist = "Artist"
    release_date = "Release Date"
    total_time = "Total Times (s)"


class PersonalData(StrEnum):

    key = "key"
    listened = "listened"
    previous_listened = "previous_listened"
    comments = "Comments"
