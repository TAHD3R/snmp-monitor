import yaml
from config import config
from pathlib import Path
from schemas.device import Devices


def load_devices_info() -> Devices:
    devices_file = Path(config.MONITOR_DEVICES_LIST)

    with open(devices_file, mode="r", encoding="utf-8") as file:
        devices = yaml.safe_load(file)

    return Devices(**devices)


def result_to_dict(result):
    return {
        column.name: getattr(result, column.name) for column in result.__table__.columns
    }


def format_duration(seconds):
    periods = [
        ("年", 60 * 60 * 24 * 365),
        ("天", 60 * 60 * 24),
        ("小时", 60 * 60),
        ("分钟", 60),
        ("秒", 1),
    ]

    parts = []
    for name, secs_per_unit in periods:
        value, seconds = divmod(seconds, secs_per_unit)
        if value:
            parts.append(f"{value} {name}")

    return " ".join(parts)
