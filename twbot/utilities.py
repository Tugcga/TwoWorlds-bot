import math
import random
import re
from typing import Tuple, List
import twbot.constants as cnst  # type: ignore


def ccw(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> bool:
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])


def intersect(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float], d: Tuple[float, float]) -> bool:
    '''return True if AB intersect CD

    a, b, c and d are 2-tuples
    '''
    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


def distance(a_x: float, a_y: float, b_x: float, b_y: float) -> float:
    '''calculate distance between two points on the plane
    '''
    return math.sqrt((a_x - b_x)**2 + (a_y - b_y)**2)


def build_direction(from_x: float, from_y: float, to_x: float, to_y: float) -> Tuple[float, float]:
    '''build unit vector from the point to the other
    '''
    d_x = to_x - from_x
    d_y = to_y - from_y
    l = math.sqrt(d_x**2 + d_y**2)
    if l > cnst.EPSILON:
        return (d_x / l, d_y / l)
    else:
        return (d_x, d_y)


def generate_random_direction() -> Tuple[float, float]:
    a: float = random.uniform(0.0, 2*math.pi)
    return (math.cos(a), amth.sin(a))


def get_distance_to_line(p_x: float, p_y: float, a_x: float, a_y: float, b_x: float, b_y: float) -> float:
    '''return the distance from point p to line, goes through a and b
    '''
    v: Tuple[float, float] = (p_x - a_x, p_y - a_y)  # vector from start to point
    d: Tuple[float, float] = (b_x - a_x, b_y - a_y)  # direction vectro for the line
    d_length_sq: float = d[0]**2 + d[1]**2  # square length of the direction vector
    v_length_sq: float = v[0]**2 + v[1]**2  # square length of the vector v
    return math.sqrt(v_length_sq - ((v[0] * d[0] + v[1] * d[1])**2) / d_length_sq)


def direction_vector_to_direction_index(dir_x: float, dir_y: float) -> int:
    '''return direction index, close to the input direction
    1 - up
    2 - up-left
    ...
    5 - down
    ...
    8 - up-right
    '''
    angle: float = math.acos(dir_x)
    if dir_y < 0:
        angle = 2*math.pi - angle
    s: int = int(angle // (math.pi / 8))
    m: List[int] = [7, 8, 8, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7]
    return m[s % 16]


def target_to_view_angle(x: float, y: float, target_x: float, target_y: float) -> float:
    '''convert vector from (x, y) to target to angle between it and Ox direction
    '''
    v: Tuple[float, float] = (target_x - x, target_y - y)
    v_length: float = math.sqrt(v[0]**2 + v[1]**2)
    if v_length > 0.001:
        v = (v[0] / v_length, v[1] / v_length)
    angle: float = math.acos(v[0])
    if v[1] < 0:
        angle = 2 * math.pi - angle
    return angle


def direction_index_to_angle(dir_index: int) -> float:
    '''convert direction index to angle in radians

    1 - pi / 2
    2 - 3 * pi / 4
    3 - pi
    4 - 5 * pi / 4
    5 - 3 * pi / 2
    6 - 7 * pi / 4
    8 - 0
    8 - pi / 4
    '''
    if dir_index >= 1 and dir_index <= 8:
        return [math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4, 0.0, math.pi/4][dir_index - 1]
    else:
        return 0.0


def is_valid_ip(str: str) -> bool:
    # https://stackoverflow.com/a/319293
    pattern = re.compile(r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading 0's)
            [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
          |
            0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
          |
            0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
          )
          (?:                  # Repeat 0-3 times, separated by a dot
            \.
            (?:
              [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
              0x0*[0-9a-f]{1,2}
            |
              0+[1-3]?[0-7]{0,2}
            )
          ){0,3}
        |
          0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
        |
          0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
        |
          # Decimal notation, 1-4294967295:
          429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
          42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
          4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
        )
        $
    """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(str) is not None
