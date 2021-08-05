import math
from twbot.utilities import intersect
from rtreelib import Rect
import twbot.constants as cnst


class Player:
    def __init__(self):
        self._radius = None
        self._name = None
        self._model = None
        self._cooldawn = None

    def update_params(self, id, life, max_life, location_x, location_y, angle, is_move, move_angle, speed,
                      name=None, radius=None, model=None, cooldawn=None):
        self._id = id
        self._life = life
        self._max_life = max_life
        self._x = location_x
        self._y = location_y
        self._is_move = is_move
        self._speed = speed
        self._direction = (math.cos(angle), math.sin(angle))
        self._move_direction = (math.cos(move_angle), math.sin(move_angle))

        if radius is not None:
            self._radius = radius
        if name is not None:
            self._name = name
        if model is not None:
            self._model = model
        if cooldawn is not None:
            self._cooldawn = cooldawn

    def update_life(self, life, max_life):
        self._life = life
        self._max_life = max_life

    def get_move_direction(self):
        return self._move_direction

    def get_model(self):
        return self._model

    def is_move(self):
        return self._is_move

    def get_cooldawn(self):
        return self._cooldawn

    def get_speed(self):
        return self._speed

    def get_next_point(self, dt, nav_tree=None):
        if self._is_move:
            target = (self._x + self._move_direction[0] * self._speed * dt, self._y + self._move_direction[1] * self._speed * dt)
            if nav_tree is None:
                return target
            else:
                # check intersections between map edges and interval from current position to target
                edge_rect = Rect(min(target[0], self._x) - cnst.RTREE_DELTA, min(target[1], self._y) - cnst.RTREE_DELTA, max(target[0], self._x) + cnst.RTREE_DELTA, max(target[1], self._y) + cnst.RTREE_DELTA)
                entityes = nav_tree.query(edge_rect)
                is_intersect = False
                intersect_edge = None
                for e in entityes:
                    if intersect((self._x, self._y), target, (e.data[0], e.data[1]), (e.data[2], e.data[3])):
                        is_intersect = True
                        intersect_edge = e.data
                if is_intersect:
                    a = (intersect_edge[2] - intersect_edge[0], intersect_edge[3] - intersect_edge[1])
                    # normalize edge vector
                    l = math.sqrt(a[0]**2 + a[1]**2)
                    a = (a[0] / l, a[1] / l)
                    # calculate dot-product with normalized a and edge
                    coeff = (target[0] - self._x) * a[0] + (target[1] - self._y) * a[1]
                    # calculate next point
                    return (self._x + coeff * a[0], self._y + coeff * a[1])
                else:
                    return target
        else:
            return (self._x, self._y)

    def set_poistion(self, x, y):
        self._x = x
        self._y = y

    def get_position(self):
        return (self._x, self._y)

    def get_radius(self):
        return self._radius

    def get_life(self):
        return self._life

    def is_dead(self):
        return self._life <= 0
