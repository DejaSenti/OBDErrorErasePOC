import shutil
import tempfile
import mmap
from tkinter.filedialog import asksaveasfilename

import keyboard

import BinHelper
import config
from Map import Map


def process_error(mapped_file: mmap, error: str, indices_by_map) -> int:
    if config.loaded_ecu.flip_bytes:
        corrected_error = BinHelper.flip_error_bytes(error)
    else:
        corrected_error = error

    dtc = config.loaded_ecu.maps[config.DTC]
    dtc_start = indices_by_map[config.loaded_ecu.maps[config.DTC]]
    offsets = find_offsets(dtc_start, dtc, mapped_file, bytearray.fromhex(corrected_error))

    if len(offsets) == 0:
        print("Couldn't find offsets for error " + error + ".\n"
              "Possible causes:\n"
              "* The error doesn't exist\n"
              "* Map start wasn't found\n"
              "* Mismatch in error length and DTC map bit amount\n\n"
              "Aborting.\n")
        return -1

    print("Found offsets for error " + error + "... Deleting.")

    for offset in offsets:
        for map_ in indices_by_map.keys():
            if map_.edit_on_command.get():
                index = indices_by_map[map_] + offset * map_.value_size_byte
                BinHelper.write_bytes_at_offset(mapped_file, index, map_.new_value)

    print("Done!\n")

    return 0


def process_and_save(errors: [], filepath: str):
    if len(errors) == 0 or config.loaded_ecu is None or len(filepath) == 0:
        print("Error in processing! "
              "Check if you've selected a file to edit, "
              "chosen an ECU and typed in the errors you want to erase!")
        return

    print("You're about to erase the following errors:")
    for error in errors:
        print(str(error) + "")
    print("")

    print("Are you sure? (Y/N)")
    while True:
        if keyboard.is_pressed('n') or keyboard.is_pressed('N'):
            print("\nAborting.\n")
            return
        elif keyboard.is_pressed('y') or keyboard.is_pressed('Y'):
            print("")
            break

    temp_file = tempfile.TemporaryFile()
    deleted_errors = set()
    with open(filepath, 'r+b') as file:
        mapped_file = mmap.mmap(file.fileno(), 0)
        data = mapped_file.read()
        temp_file.write(data)
        mapped_temp_file = mmap.mmap(temp_file.fileno(), 0)

        indices_by_map = dict()
        for map_ in config.loaded_ecu.maps.values():
            index = map_.find_map_start(mapped_temp_file)
            if index != -1:
                print("Index of " + map_.name + " found successfully.")
                indices_by_map[map_] = index
            else:
                return -1

        for error in errors:
            result = process_error(mapped_temp_file, error, indices_by_map)
            if result == 0:
                deleted_errors.add(error)

    config.loaded_ecu.reset_maps()

    temp_file.seek(0)

    if len(deleted_errors) == 0:
        print("No changes were made.\n")
        return

    print("Successfully deleted " + str(len(deleted_errors)) + " errors: ")
    for error in deleted_errors:
        print(error)
    print("")

    print("Couldn't delete the following " + str(len(errors) - len(deleted_errors)) + " errors: ")
    for error in errors:
        if not deleted_errors.__contains__(error):
            print(error)
    print("")

    print("All done! Save your file!\n")

    new_path = asksaveasfilename(defaultextension='.bin', filetypes=[('Binary Files', '*.bin')])
    if len(new_path) == 0:
        print("Canceled saving.")
        return

    new_file = open(new_path, 'w+b')

    shutil.copyfileobj(temp_file, new_file)


def find_offsets(start_index: int, map_: Map, mapped_file: mmap, error: bytearray) -> [int]:
    end = start_index + map_.size

    offset = -1
    offsets = []
    while True:
        offset = mapped_file.find(error, start_index + offset + 1, end)

        if offset == -1:
            break

        offset -= start_index

        if offset % map_.value_size_byte == 0:
            offsets.append(int(offset / map_.value_size_byte))

    return offsets
