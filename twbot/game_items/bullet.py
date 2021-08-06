import math
from typing import Tuple, Union
# from twbot.game_items_controller import GameItemsController  # type: ignore


class Bullet:
    def __init__(self, item_controller) -> None:
        self._item_controller = item_controller
        self._delta: Union[float, None] = None
        self._host_angle: Union[float, None] = None
        self._x: Union[float, None] = None
        self._y: Union[float, None] = None

    def update_params(self, id: int, bullet_type: int, host_type: int, host_id: int, damage_radius: float, speed: float, target_x: float, target_y: float,
                      delta: float=None, host_angle: float=None, x: float=None, y: float=None) -> None:
        self._id: int = id
        self._type: int = bullet_type
        self._host_type: int = host_type
        self._host_id: int = host_id
        self._damage_radius: float = damage_radius
        self._speed: float = speed
        self._target_x: float = target_x
        self._target_y: float = target_y
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
            self._direction: Tuple[float, float] = (self._target_x - self._x, self._target_y - self._y)
            if self._type in [0, 1]:
                # normalize direction
                l: float = math.sqrt(self._direction[0]**2 + self._direction[1]**2)
                self._direction = (self._direction[0] / l, self._direction[1] / l)

    def get_position(self) -> Tuple[Union[float, None], Union[float, None]]:
        return (self._x, self._y)

    def get_damage_radius(self) -> float:
        return self._damage_radius

    def get_type(self) -> int:
        return self._type

    def get_target_position(self) -> Tuple[float, float]:
        return (self._target_x, self._target_y)

    def get_host_type(self) -> int:
        return self._host_type

    def get_host_id(self) -> int:
        return self._host_id

    def set_position(self, x: float, y: float):
        self._x = x
        self._y = y

    def get_next_point(self, dt: float) -> Tuple[float, float]:
        # for type 0 and 1 we should calculate the path, for 2 it placed on target position
        if self._type == 2:
            return (self._target_x, self._target_y)
        else:
            if self._x is not None and self._y is not None:
                return (self._x + self._direction[0] * self._speed * dt, self._y + self._direction[1] * self._speed * dt)
            else:
                # if we need position, but it incorrect, return target
                return (self._target_x, self._target_y)
