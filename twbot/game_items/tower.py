class Tower:
    def __init__(self):
        self._x = None
        self._y = None
        self._life = 0

    def update_params(self, id, type, name, radius, x, y, minimum_distance, maximum_distance, atack_radius):
        self._id = id
        self._type = type
        self._name = name
        self._radius = radius
        self._x = x
        self._y = y
        self._min_distance = minimum_distance
        self._max_distance = maximum_distance
        self._atack_radius = atack_radius

    def update_life(self, life, max_life):
        self._life = life
        self._max_life = max_life

    def get_position(self):
        return (self._x, self._y)

    def is_dead(self):
        return self._life <= 0

    def get_radius(self):
        return self._radius

    def get_life(self):
        return self._life

    def __repr__(self):
        return "[id: " + str(self._id) + ", name: " + self._name + ", position: " + str((self._x, self._y)) + ", life: " + str(self._life) + "/" + str(self._max_life) + "]"
