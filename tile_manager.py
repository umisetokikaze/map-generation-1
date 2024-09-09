import yaml
from tile import Attribute, Tile


def find_tiles_with_attribute(attribute_name, attribute_value=None):
    matching_tiles = []
    for tile in TILESET.values():
        attr = tile.find_attribute(attribute_name)
        if attr and (attribute_value is None or attr.value == attribute_value):
            matching_tiles.append(tile)
    return matching_tiles


def load_config(yaml_file):
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)

    tileset = {}
    for tile_id, tile_data in data["tiles"].items():
        attributes = [
            Attribute(attr["name"], attr["value"]) for attr in tile_data["attributes"]
        ]
        tileset[tile_id] = Tile(
            tile_data["name"], tuple(tile_data["color"]), attributes
        )

    generation_params = data["generation_params"]

    return tileset, generation_params


TILESET, GENERATION_PARAMS = load_config("tiles.yaml")
