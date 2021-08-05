import math


class Monster:
    def __init__(self, item_controller):
        self._item_controller = item_controller
        self._name = None
        self._type = None
        self._radius = None
        self._damage = None
        self._damage_radius = None

    def update_params(self, id, life, max_life, state, speed, target_type, target_id, target_x, target_y, x, y,
                      name=None, type=None, radius=None, damage=None, damage_radius=None):
        self._id = id
        self._life = life
        self._max_life = max_life
        self._state = state
        self._speed = speed
        self._target_type = target_type
        self._target_id = target_id
        self._target_x = target_x
        self._target_y = target_y
        self._x = x
        self._y = y
        if name is not None:
            self._name = name
        if type is not None:
            self._type = type
        if radius is not None:
            self._radius = radius
        if damage is not None:
            self._damage = damage
        if damage_radius is not None:
            self._damage_radius = damage_radius

    def update_life(self, life, max_life):
        self._life = life
        self._max_life = max_life

    def get_position(self):
        return (self._x, self._y)

    def get_radius(self):
        return self._radius

    def set_position(self, x, y):
        self._x = x
        self._y = y

    def get_life(self):
        return self._life

    def get_next_point(self, dt):
        if self._state == 0:
            return (self._x, self._y)
        elif self._state == 1:
            # monster go to the target point
            # calculate direction
            d = (self._target_x - self._x, self._target_y - self._y)
            l = math.sqrt(d[0]**2 + d[1]**2)
            return (self._x + d[0] * self._speed * dt / l, self._y + d[1] * self._speed * dt / l)
        elif self._state == 2:
            # monster go to the target item
            (x, y) = self._item_controller.get_position(self._target_type - 1, self._target_id)  # here slightly different numeration, for player target_type = 1
            if x is not None and y is not None:
                d = (x - self._x, y - self._y)
                l = math.sqrt(d[0]**2 + d[1]**2)
                return (self._x + d[0] * self._speed * dt / l, self._y + d[1] * self._speed * dt / l)
        else:
            # unknown state
            return (self._x, self._y)

    def is_dead(self):
        return self._life <= 0
