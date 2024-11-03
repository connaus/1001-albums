from pathlib import Path
from cfg.cfg import load_config
from utils.create_csv import save_csv

SETTINGS_PATH = Path("C:/Users/ste-c/OneDrive/Documents/1001-albums/cfg/setting.yaml")


def main() -> None:
    cfg = load_config(SETTINGS_PATH)
    save_csv(cfg)


if __name__ == "__main__":
    main()
