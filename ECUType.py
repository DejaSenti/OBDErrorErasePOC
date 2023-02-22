import ECUManager
import config
from Map import Map


class ECUType:
    def __init__(self, car_brand: str, name: str, maps: list[Map], flip_bytes: bool):
        print("Trying to create new ECU with following data:\n"
              "Brand: " + car_brand + "\n" +
              "Name: " + name + "\n" +
              "Flip Bytes: " + str(flip_bytes) + "\n" +
              "Maps:")
        for map_ in maps:
            print("\t* " + map_.name)

        self.car_brand = car_brand
        self.name = name
        self.maps = dict()

        self.flip_bytes = flip_bytes

        for map_ in maps:
            counter = 0
            new_name = map_.name
            while True:
                if new_name in self.maps:
                    counter += 1
                    new_name = map_.name + "(" + str(counter) + ")"
                else:
                    map_.name = new_name
                    self.maps[map_.name] = map_
                    break
            map_.set_parent_ecu(self)

        print("ECU " + self.name + " created successfully.")

    def update_map(self, new_map: Map):
        self.maps[new_map.name] = new_map
        config.loaded_ecu = self

    def update_ecu_file(self):
        ECUManager.update_ecu(self)

    def reset_maps(self):
        for map_ in self.maps.values():
            map_.index = -1
