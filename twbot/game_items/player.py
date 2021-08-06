import math
from twbot.utilities import intersect  # type: ignore
from rtreelib import Rect, RTree  # type: ignore
import twbot.constants as cnst  # type: ignore
from typing import Tuple, Union


class Player:
    def __init__(self) -> None:
        self._radius: Union[float, None] = None
        self._name: Union[str, None] = None
        self._model: Union[int, None] = None
        self._cooldawn: Union[float, None] = None

    def update_params(self, id: int, life: int, max_life: int, location_x: float, location_y: float, angle: float, is_move: bool, move_angle: float, speed: float,
                      name: str=None, radius: float=None, model: int=None, cooldawn: float=None) -> None:
        self._id: int = id
        self._life: int = life
        self._max_life: int = max_life
        self._x: float = location_x
        self._y: float = location_y
        self._is_move: bool = is_move
        self._speed: float = speed
        self._direction: Tuple[float, float] = (math.cos(angle), math.sin(angle))
        self._move_direction: Tuple[float, float] = (math.cos(move_angle), math.sin(move_angle))

        if radius is not None:
            self._radius = radius
        if name is not None:
            self._name = name
        if model is not None:
            self._model = model
        if cooldawn is not None:
            self._cooldawn = cooldawn

    def update_life(self, life: int, max_life: int) -> None:
        self._life = life
        self._max_life = max_life

    def get_move_direction(self) -> Tuple[float, float]:
        return self._move_direction

    def get_model(self) -> Union[int, None]:
        return self._model

    def is_move(self) -> bool:
        return self._is_move

    def get_cooldawn(self) -> Union[float, None]:
        return self._cooldawn

    def get_speed(self) -> float:
        return self._speed

    def get_next_point(self, dt: float, nav_tree: RTree=None) -> Tuple[float, float]:
        if self._is_move:
            target: Tuple[float, float] = (self._x + self._move_direction[0] * self._speed * dt, self._y + self._move_direction[1] * self._speed * dt)
            if nav_tree is None:
                return target
            else:
                # check intersections between map edges and interval from current position to target
                edge_rect: Rect = Rect(min(target[0], self._x) - cnst.RTREE_DELTA, min(target[1], self._y) - cnst.RTREE_DELTA, max(target[0], self._x) + cnst.RTREE_DELTA, max(target[1], self._y) + cnst.RTREE_DELTA)
                entityes = nav_tree.query(edge_rect)
                is_intersect: bool = False
                intersect_edge: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
                for e in entityes:
                    if intersect((self._x, self._y), target, (e.data[0], e.data[1]), (e.data[2], e.data[3])):
                        is_intersect = True
                        intersect_edge = e.data
                if is_intersect:
                    a: Tuple[float, float] = (intersect_edge[2] - intersect_edge[0], intersect_edge[3] - intersect_edge[1])
                    # normalize edge vector
                    l: float = math.sqrt(a[0]**2 + a[1]**2)
                    a = (a[0] / l, a[1] / l)
                    # calculate dot-product with normalized a and edge
                    coeff: float = (target[0] - self._x) * a[0] + (target[1] - self._y) * a[1]
                    # calculate next point
                    return (self._x + coeff * a[0], self._y + coeff * a[1])
                else:
                    return target
        else:
            return (self._x, self._y)

    def set_poistion(self, x: float, y: float) -> None:
        self._x = x
        self._y = y

    def get_position(self) -> Tuple[float, float]:
        return (self._x, self._y)

    def get_radius(self) -> Union[float, None]:
        return self._radius

    def get_life(self) -> int:
        return self._life

    def is_dead(self) -> bool:
        return self._life <= 0
