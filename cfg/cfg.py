from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Data:

    album_data_csv_name: str
    album_data_json_path: str
    csv_save_dir: str
    personal_data_csv_name: str
    personal_data_json_path: str

    raw_excel_path: str
    sheet_name: str


@dataclass
class Config:

    data: Data


def load_config(settings_path: Path) -> Config:
    with open(settings_path, "r") as steam:
        data_settings = yaml.safe_load(stream=steam)

    return Config(data=Data(**data_settings))
