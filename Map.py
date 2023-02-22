from mmap import mmap

import BinHelper


class Map:
    def __init__(self, name: str, size: str, address: str, value_size: str, new_value: str, file: mmap):
        print("Trying to create new Map with following data:\n"
              "Name: " + name + "\n" +
              "Size: " + size + "\n" +
              "Address: " + address + "\n" +
              "Value Size: " + value_size + "\n" +
              "New Value: " + new_value)

        self.name = name
        self.value_size = int(int(value_size) / 4)
        self.value_size_byte = int(self.value_size / 2)
        self.size = int(size) * self.value_size_byte

        self.new_value = new_value
        if len(new_value) != self.value_size:
            if int(new_value, 16) == 0:
                self.new_value = new_value.zfill(self.value_size)
            else:
                raise ValueError('Input value does not match value size!\n')

        try:
            self.new_value = bytearray.fromhex(self.new_value)
        except ValueError("Bad new value hex conversion. Aborting."):
            return

        self.search_words = []
        self.add_search_word_at_address(int(address, 16), file)

        self.edit_on_command = True

        self.parent_ecu = None

        print("Map " + self.name + " created successfully.")

    def add_search_word_at_address(self, address: int, file: mmap):
        file.seek(address)
        initial_word = file.read(50)
        self.search_words.append(initial_word)

        print("Search word: \n" +
              str(initial_word) + "\nAppended to search words for Map " + self.name + ".")

    def find_map_start(self, file: mmap):
        for word in self.search_words:
            index = file.find(word)
            if index != -1:
                return index

        for word in self.search_words:
            index = BinHelper.precision_search(word, file, 0.15)
            if index != -1:
                self.add_search_word_at_address(index, file)
                self.parent_ecu.update_map(self)
                self.parent_ecu.update_ecu_file()
                print("Couldn't find map by search word...\n"
                      "Added new search word from similarity search.")
                return index

        print("Couldn't find start of map " + self.name)
        return -1

    def set_parent_ecu(self, parent_ecu):
        self.parent_ecu = parent_ecu
