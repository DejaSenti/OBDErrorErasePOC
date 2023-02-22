import os
import sys
from tkinter.filedialog import askopenfilename

import jsonpickle

import config


def find_files_with_extension(dir_: str, ext: str) -> list[str]:
    result = [os.path.join(path, f)
              for path, folders, files in os.walk(dir_)
              for f in files if f.endswith('.' + ext)]
    return result


def save_class(object_, path: str):
    json_str = jsonpickle.encode(object_)
    json_file = open(path, "w")
    json_file.write(json_str)
    json_file.close()


def load_class(path: str):
    try:
        json_file = open(path, "r")
    except FileNotFoundError("Couldn't load class at path " + path + "\n"):
        return

    json_str = json_file.read()
    object_ = jsonpickle.decode(json_str)
    json_file.close()
    return object_


def get_brand_names() -> [str]:
    path = config.app_path + "\\ECU\\"

    ecu_files = find_files_with_extension(path, 'ecu')

    result = dict()
    result['Select Brand...'] = ['Select Brand first!']

    for file in ecu_files:
        filepath = file.split('\\')
        name = filepath[-2]
        brand = filepath[-1].removesuffix('.ecu')
        if not result.keys().__contains__(name):
            result[name] = ['Select ECU...']
        if not result[name].__contains__(brand):
            result[name].append(brand)

    return result


def browse_bin_file() -> str:
    filepath = askopenfilename(title='Select binary file...', filetypes=[('Binary Files', '*.bin')])
    if filepath is not None:
        return filepath


def get_app_path() -> str:
    path = ""
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    elif __file__:
        path = os.path.dirname(__file__)

    return path
