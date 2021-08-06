import math
from typing import Tuple, Union
# from twbot.game_items_controller import GameItemsController  # type: ignore


class Monster:
    def __init__(self, item_controller) -> None:
        self._item_controller = item_controller
        self._name: Union[str, None] = None
        self._type: Union[int, None] = None
        self._radius: Union[float, None] = None
        self._damage: Union[int, None] = None
        self._damage_radius: Union[float, None] = None

    def update_params(self, id: int, life: int, max_life: int, state: int, speed: float, target_type: int, target_id: int, target_x: float, target_y: float, x: float, y: float,
                      name: str=None, type: int=None, radius: float=None, damage: int=None, damage_radius: float=None) -> None:
        self._id: int = id
        self._life: int = life
        self._max_life: int = max_life
        self._state: int = state
        self._speed: float = speed
        self._target_type: int = target_type
        self._target_id: int = target_id
        self._target_x: float = target_x
        self._target_y: float = target_y
        self._x: float = x
        self._y: float = y
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

    def update_life(self, life: int, max_life: int) -> None:
        self._life = life
        self._max_life = max_life

    def get_position(self) -> Tuple[float, float]:
        return (self._x, self._y)

    def get_radius(self) -> Union[float, None]:
        return self._radius

    def set_position(self, x, y) -> None:
        self._x = x
        self._y = y

    def get_life(self) -> int:
        return self._life

    def get_next_point(self, dt: float) -> Tuple[float, float]:
        d: Tuple[float, float]
        l: float
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
                return (self._x, self._y)
        else:
            # unknown state
            return (self._x, self._y)

    def is_dead(self) -> bool:
        return self._life <= 0
