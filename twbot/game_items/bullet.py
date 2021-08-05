import math


class Bullet:
    def __init__(self, item_controller):
        self._item_controller = item_controller
        self._delta = None
        self._host_angle = None
        self._x = None
        self._y = None

    def update_params(self, id, bullet_type, host_type, host_id, damage_radius, speed, target_x, target_y,
                      delta=None, host_angle=None, x=None, y=None):
        self._id = id
        self._type = bullet_type
        self._host_type = host_type
        self._host_id = host_id
        self._damage_radius = damage_radius
        self._speed = speed
        self._target_x = target_x
        self._target_y = target_y
        if delta is not None:
            self._delta = delta
        if host_angle is not None:
            self._host_angle = host_angle
        # is x and y are None, then it calls by RPC StartBullet
        # if x and y are not None, then it calls by change AoI
        if x is not None and y is not None:
            self._x = x
            self._y = y
        else:
            # here we should get bullet position from the host
            self._x, self._y = self._item_controller.get_position(self._host_type, self._host_id)
        if self._x is not None and self._y is not None:
            # if _x and _y are None, then we can not get position of the host item
            # in this case in simulation we will return target position
            self._direction = (self._target_x - self._x, self._target_y - self._y)
            if self._type in [0, 1]:
                # normalize direction
                l = math.sqrt(self._direction[0]**2 + self._direction[1]**2)
                self._direction = (self._direction[0] / l, self._direction[1] / l)

    def get_position(self):
        return (self._x, self._y)

    def get_damage_radius(self):
        return self._damage_radius

    def get_type(self):
        return self._type

    def get_target_position(self):
        return (self._target_x, self._target_y)

    def get_host_type(self):
        return self._host_type

    def get_host_id(self):
        return self._host_id

    def set_position(self, x, y):
        self._x = x
        self._y = y

    def get_next_point(self, dt):
        # for type 0 and 1 we should calculate the path, for 2 it placed on target position
        if self._type == 2:
            return (self._target_x, self._target_y)
        else:
            if self._x is not None and self._y is not None:
                return (self._x + self._direction[0] * self._speed * dt, self._y + self._direction[1] * self._speed * dt)
            else:
                # if we need position, but it incorrect, return target
                return (self._target_x, self._target_y)
