from dataclasses import dataclass, field
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
class NetworkGraphSettings:

    album_symbol: str = "square"
    album_colour: str = "deepskyblue"
    album_size: int = 10
    album_lowlight_size: int = 5
    album_highlight_color: str = "#EF553B"
    album_highlight_size: int = 15
    album_highlight_connection_color: str = "#00CC96"
    album_highlight_symbol: str = "circle"
    album_lowlight_color: str = "dimgrey"
    connection_colourmap: dict[str, str] = field(
        default_factory=lambda: {
            "musician": "#636EFA",
            "arranger": "#EF553B",
            "writer": "#00CC96",
            "producer": "#AB63FA",
            "unknown": "brown",
        }
    )
    person_symbol: str = "circle"
    person_colour: str = "grey"
    person_highlight_color: str = "#AB63FA"
    person_size: int = 5
    person_highlight_size: int = 10


@dataclass
class Config:

    data: Data
    network_graph: NetworkGraphSettings


def load_config(settings_path: Path) -> Config:
    with open(settings_path, "r") as steam:
        data_settings = yaml.safe_load(stream=steam)

    return Config(data=Data(**data_settings), network_graph=NetworkGraphSettings())
