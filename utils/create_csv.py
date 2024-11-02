import pandas as pd

from pathlib import Path

from cfg.cfg import Config


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
