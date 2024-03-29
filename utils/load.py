import yaml
from config import config
from pathlib import Path
from schema.device import Devices


def load_devices_info() -> Devices:
    """
    Load devices information from the devices list file.

    Default file path is defined in the config file.
    """
    devices_file = Path(config.MONITOR_DEVICES_LIST)

    with open(devices_file, mode="r", encoding="utf-8") as file:
        devices = yaml.safe_load(file)

    return Devices(**devices)


def result_to_dict(result):
    return {
        column.name: getattr(result, column.name) for column in result.__table__.columns
    }
