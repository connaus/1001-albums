import pandas as pd

from pathlib import Path

from cfg.cfg import Config
import cfg.schema as sch

SETTING_PATH = Path("C:/Users/ste-c/OneDrive/Documents/1001-albums/cfg/setting.yaml")


def save_csv(cfg: Config) -> None:

    excel = pd.read_excel(cfg.data.raw_excel_path, cfg.data.sheet_name)

    excel["listened"] = excel["✓"].apply(lambda x: True if x == "✓" else False)
    excel["previous_listened"] = excel.apply(
        lambda x: True if (x["✓"] == "✓") and (pd.isna(x["Comments"])) else False,
        axis=1,
    )
    excel["key"] = excel.index
    raw_data_csv = excel[
        ["key", "Album Title", "Artist", "Release Date", "Total Times (s)"]
    ]
    raw_data_csv.to_csv(
        Path(cfg.data.csv_save_dir) / f"{cfg.data.album_data_csv_name}.csv", index=False
    )
    personal_data_csv = excel[["key", "listened", "previous_listened", "Comments"]]
    personal_data_csv.to_csv(
        Path(cfg.data.csv_save_dir) / f"{cfg.data.personal_data_csv_name}.csv",
        index=False,
    )


def convert_excel_to_json(cfg: Config) -> None:

    excel = pd.read_excel(cfg.data.raw_excel_path, cfg.data.sheet_name)

    excel["listened"] = excel["✓"].apply(lambda x: True if x == "✓" else False)
    excel["previous_listened"] = excel.apply(
        lambda x: True if (x["✓"] == "✓") and (pd.isna(x["Comments"])) else False,
        axis=1,
    )
    excel["key"] = excel.index
    raw_data_csv = excel[
        [
            sch.AlbumExcelColumns.key,
            sch.AlbumExcelColumns.album_title,
            sch.AlbumExcelColumns.artist,
            sch.AlbumExcelColumns.release_date,
            sch.AlbumExcelColumns.total_time,
        ]
    ]
    raw_data_csv.rename(
        {
            sch.AlbumExcelColumns.key: sch.Album.key,
            sch.AlbumExcelColumns.album_title: sch.Album.album_title,
            sch.AlbumExcelColumns.artist: sch.Album.artist,
            sch.AlbumExcelColumns.release_date: sch.Album.release_date,
            sch.AlbumExcelColumns.total_time: sch.Album.total_time_s,
        },
        axis=1,
        inplace=True,
    )
    with open(Path(cfg.data.album_data_json_path), "w") as f:
        text = raw_data_csv.to_json(orient="records")
        f.write(text)

    personal_data_csv = excel[
        [
            sch.PersonalExcelColumns.key,
            sch.PersonalExcelColumns.listened,
            sch.PersonalExcelColumns.previous_listened,
            sch.PersonalExcelColumns.comments,
            sch.PersonalExcelColumns.listen_again,
        ]
    ]
    personal_data_csv.rename(
        {
            sch.PersonalExcelColumns.key: sch.PersonalData.key,
            sch.PersonalExcelColumns.listened: sch.PersonalData.listened,
            sch.PersonalExcelColumns.previous_listened: sch.PersonalData.previous_listened,
            sch.PersonalExcelColumns.comments: sch.PersonalData.comments,
            sch.PersonalExcelColumns.listen_again: sch.PersonalData.listen_again,
        },
        axis=1,
        inplace=True,
    )
    with open(cfg.data.personal_data_json_path, "w") as f:
        text = personal_data_csv.to_json(orient="records")
        f.write(text)
