import math


def ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])


def intersect(a, b, c, d):
    '''return True if AB intersect CD

    a, b, c and d are 2-tuples
    '''
    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


def distance(a_x, a_y, b_x, b_y):
    '''calculate distance between two points on the plane
    '''
    return math.sqrt((a_x - b_x)**2 + (a_y - b_y)**2)


def build_direction(from_x, from_y, to_x, to_y):
    '''build unit vector from the point to the other
    '''
    d_x = to_x - from_x
    d_y = to_y - from_y
    l = math.sqrt(d_x**2 + d_y**2)
    return (d_x / l, d_y / l)


def get_distance_to_line(p_x, p_y, a_x, a_y, b_x, b_y):
    '''return the distance from point p to line, goes through a and b
    '''
    v = (p_x - a_x, p_y - a_y)  # vector from start to point
    d = (b_x - a_x, b_y - a_y)  # direction vectro for the line
    d_length_sq = d[0]**2 + d[1]**2  # square length of the direction vector
    v_length_sq = v[0]**2 + v[1]**2  # square length of the vectro v
    return math.sqrt(v_length_sq - ((v[0] * d[0] + v[1] * d[1])**2) / d_length_sq)


def direction_vector_to_direction_index(dir_x, dir_y):
    '''return direction index, close to the input direction
    1 - up
    2 - up-left
    ...
    5 - down
    ...
    8 - up-right
    '''
    angle = math.acos(dir_x)
    if dir_y < 0:
        angle = 2*math.pi - angle
    s = int(angle // (math.pi / 8))
    m = [7, 8, 8, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7]
    return m[s % 16]


def target_to_view_angle(x, y, target_x, target_y):
    '''convert vector from (x, y) to target to angle between it and Ox direction
    '''
    v = (target_x - x, target_y - y)
    v_length = math.sqrt(v[0]**2 + v[1]**2)
    if v_length > 0.001:
        v = (v[0] / v_length, v[1] / v_length)
    angle = math.acos(v[0])
    if v[1] < 0:
        angle = 2 * math.pi - angle
    return angle


def direction_index_to_angle(dir_index):
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
