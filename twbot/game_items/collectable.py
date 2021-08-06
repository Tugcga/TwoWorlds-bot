from typing import Tuple


class Collectable:
    def __init__(self) -> None:
        pass

    def update_params(self, id: int, type: int, x: float, y: float, radius: float) -> None:
        self._id: int = id
        self._type: int = type
        self._x: float = x
        self._y: float = y
        self._radius: float = radius

    def get_position(self) -> Tuple[float, float]:
        return (self._x, self._y)

    def get_radius(self) -> float:
        return self._radius
