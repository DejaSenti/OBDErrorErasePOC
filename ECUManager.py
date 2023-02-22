from pathlib import Path

import FileHelper
import config
from ECUType import ECUType
from Map import Map


def create_ecu_type(brand: str, ecu: str, maps: list[Map], flip_bytes: bool):
    print("Creating ECU " + ecu + " from brand " + brand + " using successfully built maps...")
    ecu_type = ECUType(brand, ecu, maps, flip_bytes)

    path = config.app_path + "\\ECU\\" + brand + "\\"

    Path(path).mkdir(parents=True, exist_ok=True)

    FileHelper.save_class(ecu_type, path + ecu + ".ecu")


def get_ecu_type(brand, name):
    path = get_ecu_path(brand, name)
    ecu = FileHelper.load_class(path)

    return ecu


def update_ecu(updated_ecu: ECUType):
    path = get_ecu_path(updated_ecu.car_brand, updated_ecu.name)
    FileHelper.save_class(updated_ecu, path)


def get_ecu_path(brand: str, name: str):
    path = config.app_path + "\\ECU\\" + brand + "\\" + name + ".ecu"
    return path
