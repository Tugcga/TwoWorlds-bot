class Collectable:
    def __init__(self):
        pass

    def update_params(self, id, type, x, y, radius):
        self._id = id
        self._type = type
        self._x = x
        self._y = y
        self._radius = radius

    def get_position(self):
        return (self._x, self._y)

    def get_radius(self):
        return self._radius
