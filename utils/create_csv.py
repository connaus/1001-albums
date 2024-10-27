import pandas as pd

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml

SETTINGS_PATH = Path("C:/Users/ste-c/OneDrive/Documents/1001-albums/cfg/setting.yaml")


def save_csv() -> None:
    with open(SETTINGS_PATH, "r") as steam:
        csv_settings = yaml.safe_load(stream=steam)

    excel = pd.read_excel(csv_settings["raw_excel_path"], csv_settings["sheet_name"])

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
        Path(csv_settings["csv_save_dir"]) / "album_data.csv", index=False
    )
    personal_data_csv = excel[["key", "listened", "previous_listened", "Comments"]]
    personal_data_csv.to_csv(
        Path(csv_settings["csv_save_dir"]) / "personal_data.csv", index=False
    )


if __name__ == "__main__":
    save_csv()
