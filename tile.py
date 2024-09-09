class Attribute:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Tile:
    def __init__(self, name, color, attributes):
        self.name = name
        self.color = color
        self.attributes = attributes

    def find_attribute(self, att_name):
        return next((att for att in self.attributes if att.name == att_name), None)

    def has_attribute(self, att_name):
        return any(att.name == att_name for att in self.attributes)
