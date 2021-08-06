from typing import Tuple, Union


class Tower:
    def __init__(self) -> None:
        self._x: Union[float, None] = None
        self._y: Union[float, None] = None
        self._life: int = 0
        self._max_life: int = 0

    def update_params(self, id: int, type: int, name: str, radius: float, x: float, y: float, minimum_distance: float, maximum_distance: float, atack_radius: float) -> None:
        self._id: int = id
        self._type: int = type
        self._name: str = name
        self._radius: float = radius
        self._x = x
        self._y = y
        self._min_distance: float = minimum_distance
        self._max_distance: float = maximum_distance
        self._atack_radius: float = atack_radius

    def update_life(self, life, max_life) -> None:
        self._life = life
        self._max_life = max_life

    def get_position(self) -> Tuple[Union[float, None], Union[float, None]]:
        return (self._x, self._y)

    def is_dead(self) -> bool:
        return self._life <= 0

    def get_radius(self) -> float:
        return self._radius

    def get_life(self) -> int:
        return self._life

    def __repr__(self) -> str:
        return "[id: " + str(self._id) + ", name: " + self._name + ", position: " + str((self._x, self._y)) + ", life: " + str(self._life) + "/" + str(self._max_life) + "]"
