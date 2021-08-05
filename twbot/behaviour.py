from PySide6 import QtCore
import time
import math
import random
import twbot.constants as cnst
from twbot.utilities import distance, intersect, build_direction, get_distance_to_line, direction_vector_to_direction_index, target_to_view_angle, direction_index_to_angle
from rtreelib import Rect


class BehaviourClass(QtCore.QObject):
    def __init__(self, move_command=None, shot_command=None):  # these two commands and methods on the client application (to send in to the server)
        super().__init__()
        self._active = True
        self._is_update = False
        self._counter = 0
        self._world_data = None
        self._my_id = None
        self._nav_tree = None
        self._move_command = move_command
        self._shot_command = shot_command

        # bullets avoidence
        self._battle_state = False  # does not move in battel state, only avoid the bullets
        self._battle_state_start_time = time.time()
        self._move_direction = 0  # 0 - no moving, also use it in the random walk

        # random walk
        self._use_random_walk = True
        self._move_state = False  # when True, then it moving in the chosen direction
        self._move_state_start_time = time.time()
        self._move_state_time_limit = 0.0  # how long we should move in the chose direction

        # shoter
        self._shot_state = False  # if True, the we wait cooldawn
        self._shot_state_last_time = time.time()
        self._shot_players = True
        self._shot_monsters = True
        self._shot_towers = True

    def start(self):
        self._is_update = True
        while self._is_update:
            self.update()
            time.sleep(cnst.BAHAVIOUR_UPDATE_TIMER)

    def stop(self):
        self._is_update = False

    def actualize_world(self, world_data):
        '''world_data is a dictionary with keys:
            - players
            - monsters
            - bullets
            - towers
            - collects
        '''
        self._world_data = world_data

    def define_my_id(self, id):
        self._my_id = id

    def define_navigation(self, nav_tree):
        '''nav_tree is an RTree with edges of the walls
        each edge is a 4-tuple (start_x, start_y, end_x, end_y)
        '''
        self._nav_tree = nav_tree

    def is_visible(self, x, y, t_x, t_y):
        p_dist = distance(x, y, t_x, t_y)
        # check is this player on the search distance
        if p_dist < cnst.BEHAVIOUR_SEARCH_SHOT_DISTANCE:
            # next check is this player on the visible line
            is_intersections = False
            edge = (x, y, t_x, t_y)
            r = Rect(min(edge[0], edge[2]) + cnst.RTREE_DELTA, min(edge[1], edge[3]) + cnst.RTREE_DELTA, max(edge[0], edge[2]) + cnst.RTREE_DELTA, max(edge[1], edge[3]) + cnst.RTREE_DELTA)
            walls = self._nav_tree.query(r)
            for wall in walls:
                w_edge = wall.data
                if intersect((edge[0], edge[1]), (edge[2], edge[3]), (w_edge[0], w_edge[1]), (w_edge[2], w_edge[3])):
                    is_intersections = True
            return not is_intersections
        else:
            return False

    def avoid_task(self, pos_x, pos_y, my_player):
        avoid_directions = []  # store here different directions for bullets avoiding, direction as a 2d-vector
        # iterate by bullets
        for b_id, bullet in self._world_data["bullets"].items():
            if bullet.get_host_type() != 0 or bullet.get_host_id() != self._my_id:
                b_type = bullet.get_type()  # 0 - linear bullet, 1 - explosion at target, 2 - delay explosion on target
                (target_x, target_y) = bullet.get_target_position()
                if b_type in [1, 2]:
                    # print(pos_x, pos_y, target_x, target_y, distance(pos_x, pos_y, target_x, target_y), bullet.get_damage_radius())
                    if distance(pos_x, pos_y, target_x, target_y) < (bullet.get_damage_radius() + my_player.get_radius()) * 1.1:  # use slightly bigger radius
                        # we should avoid from this bullet
                        # so, need chose the direction to avoid
                        avoid_directions.append(build_direction(target_x, target_y, pos_x, pos_y))
                elif b_type in [0]:  # we should avoid the line between start and end
                    (b_x, b_y) = bullet.get_position()
                    if b_x is not None and b_y is not None:
                        d = get_distance_to_line(pos_x, pos_y, b_x, b_y, target_x, target_y)
                        # print("distance to line:", d, my_player.get_radius())
                        if d < my_player.get_radius() * 1.1:
                            # player too close to the bullet line, but may be it before or after endpoints of the bullet edge
                            line_dir = (target_x - b_x, target_y - b_y)
                            start_to_player = (pos_x - b_x, pos_y - b_y)
                            end_to_player = (pos_x - target_x, pos_y - target_y)
                            # print(line_dir[0] * start_to_player[0] + line_dir[1] * start_to_player[1] > 0, line_dir[0] * end_to_player[0] + line_dir[1] * end_to_player[1] < 0)
                            if line_dir[0] * start_to_player[0] + line_dir[1] * start_to_player[1] > 0 and line_dir[0] * end_to_player[0] + line_dir[1] * end_to_player[1] < 0:
                                # player between start and end
                                n_x = -line_dir[1]
                                n_y = line_dir[0]
                                n_length = math.sqrt(n_x**2 + n_y**2)
                                n_x = n_x / n_length
                                n_y = n_y / n_length
                                if n_x * start_to_player[0] + n_y * start_to_player[1] > 0:
                                    avoid_directions.append((n_x, n_y))
                                else:
                                    avoid_directions.append((-n_x, -n_y))
                            else:
                                # player outside start ane end, so we can only chack distance to start end end point
                                start_d = distance(pos_x, pos_y, b_x, b_y)
                                end_d = distance(pos_x, pos_y, target_x, target_y)
                                if start_d < my_player.get_radius() * 1.1:
                                    avoid_directions.append(build_direction(b_x, b_y, pos_x, pos_y))
                                if end_d < my_player.get_radius() * 1.1:
                                    avoid_directions.append(build_direction(target_x, target_y, pos_x, pos_y))
        # if there bullets for avoidence, the we should switch the player to the battle state
        if len(avoid_directions) > 0:
            self._battle_state = True
            self._move_state = False
            self._battle_state_start_time = time.time()  # update start battle state
        avv = [0.0, 0.0]
        for a_d in avoid_directions:
            avv[0] += a_d[0]
            avv[1] += a_d[1]
        # normalize
        avv_l = math.sqrt(avv[0]**2 + avv[1]**2)
        if avv_l > 0.001:
            avv[0] = avv[0] / avv_l
            avv[1] = avv[1] / avv_l
            dir_index = direction_vector_to_direction_index(avv[0], avv[1])
        else:
            dir_index = 0
        if self._battle_state and self._move_direction != dir_index:
            if self._move_command is not None:
                self._move_command(dir_index)
            self._move_direction = dir_index

    def move_task(self, pos_x, pos_y, my_player):
        if self._battle_state:
            # check, may be we should turn off the battle state
            if time.time() - self._battle_state_start_time > cnst.BEHAVOIUR_BATTLE_STATE_TIME:
                self._battle_state = False
        else:
            if self._use_random_walk:
                # player not in the battle state, so, it can move
                if self._move_state:
                    # we are moving, check we should stop
                    if time.time() - self._move_state_start_time > self._move_state_time_limit:
                        self._move_state = False
                        if self._move_direction != 0:
                            self._move_direction = 0
                            if self._move_command is not None:
                                self._move_command(0)  # command to stop moving
                        # next we should pause
                        self._move_state_start_time = time.time()
                        self._move_state_time_limit = cnst.BEHAVOIUR_MOVING_STATE_TIME * random.uniform(0.25, 0.5)
                        # print("move state:", "start pause to " + str(self._move_state_time_limit))
                else:
                    # we a pause
                    # check, way be should change the state
                    if time.time() - self._move_state_start_time > self._move_state_time_limit:
                        self._move_state = True
                        # select random direction
                        free_directions = []
                        # we will try to select direction, where there is a space
                        for dir_index in range(1, 9):
                            angle = direction_index_to_angle(dir_index)
                            dir_vector = (math.cos(angle), math.sin(angle))
                            edge = (pos_x, pos_y, pos_x + dir_vector[0] * cnst.BEHAVIOUR_MOVING_SPACE, pos_y + dir_vector[1] * cnst.BEHAVIOUR_MOVING_SPACE)
                            # next check intersection of the edge with walls
                            is_intersections = False
                            r = Rect(min(edge[0], edge[2]) + cnst.RTREE_DELTA, min(edge[1], edge[3]) + cnst.RTREE_DELTA, max(edge[0], edge[2]) + cnst.RTREE_DELTA, max(edge[1], edge[3]) + cnst.RTREE_DELTA)
                            walls = self._nav_tree.query(r)
                            for wall in walls:
                                w_edge = wall.data
                                if intersect((edge[0], edge[1]), (edge[2], edge[3]), (w_edge[0], w_edge[1]), (w_edge[2], w_edge[3])):
                                    is_intersections = True
                            if not is_intersections:
                                free_directions.append(dir_index)
                        if len(free_directions) == 0:
                            # no free direction, chose random one
                            dir_index = random.randint(0, 8)
                        else:
                            # there are free directions, chose one of them
                            dir_index = free_directions[random.randint(0, len(free_directions) - 1)]
                        if dir_index != self._move_direction:
                            self._move_direction = dir_index
                            if self._move_command is not None:
                                self._move_command(dir_index)
                        self._move_state_start_time = time.time()
                        self._move_state_time_limit = cnst.BEHAVOIUR_MOVING_STATE_TIME * random.uniform(0.75, 1.25)
                        # print("move state:", "start moving at direction " + str(self._move_direction) + " to " + str(self._move_state_time_limit))

    def shot_task(self, pos_x, pos_y, my_player):
        if self._shot_state:
            # wait cooldawn
            my_cd = my_player.get_cooldawn()
            if my_cd is not None:
                if time.time() - self._shot_state_last_time > my_cd * 1.1:
                    self._shot_state = False  # we are redy to shot
        else:
            # try to find targerts
            is_find_player = False
            if self._shot_players:
                target_player_id = None
                # we will try to find player with minimal life
                min_life = -1
                for p_id, player in self._world_data["players"].items():
                    p_life = player.get_life()
                    if p_id != self._my_id and p_life > 0:  # consider only alive players
                        (p_x, p_y) = player.get_position()
                        if self.is_visible(pos_x, pos_y, p_x, p_y):
                            # player on the visible line, try to select it
                            if min_life == -1 or p_life < min_life:
                                min_life = p_life
                                is_find_player = True
                                target_player_id = p_id
                if is_find_player:
                    # we select player target, shot to him
                    (target_pos_x, target_pos_y) = self._world_data["players"][target_player_id].get_position()
                    # we should find target point more carefull
                    # if the player is move, shift the center in this direction
                    to_target = (target_pos_x - pos_x, target_pos_y - pos_y)
                    to_target_length = math.sqrt(to_target[0]**2 + to_target[1]**2)
                    # we don't know bullet speed, so, use hardcoded values: 20.0 for model=0 and 10.0 for model=1
                    b_speed = 20.0 if my_player.get_model() == 0 else 10.0
                    dir_shift = to_target_length / b_speed
                    target_dir = self._world_data["players"][target_player_id].get_move_direction()
                    target_speed = self._world_data["players"][target_player_id].get_speed()
                    target_is_move = self._world_data["players"][target_player_id].is_move()
                    target_pos_x = target_pos_x + dir_shift * target_dir[0] * target_speed * (1.0 if target_is_move else 0.0)
                    target_pos_y = target_pos_y + dir_shift * target_dir[1] * target_speed * (1.0 if target_is_move else 0.0)
                    self._shot_command(target_pos_x, target_pos_y, target_to_view_angle(pos_x, pos_y, target_pos_x, target_pos_y))
                    self._shot_state_last_time = time.time()
                    self._shot_state = True
            if not is_find_player:
                # try to find target on towers
                is_find_tower = False
                if self._shot_towers:
                    target_tower_id = None
                    min_life = -1
                    for t_id, tower in self._world_data["towers"].items():
                        t_life = tower.get_life()
                        if t_life > 0:
                            (t_x, t_y) = tower.get_position()
                            if self.is_visible(pos_x, pos_y, t_x, t_y):
                                if min_life == -1 or t_life < min_life:
                                    min_life = t_life
                                    is_find_tower = True
                                    target_tower_id = t_id
                    if is_find_tower:
                        (target_pos_x, target_pos_y) = self._world_data["towers"][target_tower_id].get_position()
                        self._shot_command(target_pos_x, target_pos_y, target_to_view_angle(pos_x, pos_y, target_pos_x, target_pos_y))
                        self._shot_state_last_time = time.time()
                        self._shot_state = True
                if not is_find_tower:
                    # try to find on monsters
                    is_find_monster = False
                    if self._shot_monsters:
                        target_monster_id = None
                        min_life = -1
                        for m_id, monster in self._world_data["monsters"].items():
                            m_life = monster.get_life()
                            if m_life > 0:
                                (m_x, m_y) = monster.get_position()
                                if self.is_visible(pos_x, pos_y, m_x, m_y):
                                    if min_life == -1 or m_life < min_life:
                                        min_life = m_life
                                        is_find_monster = True
                                        target_monster_id = m_id
                        if is_find_monster:
                            (target_pos_x, target_pos_y) = self._world_data["monsters"][target_monster_id].get_position()
                            self._shot_command(target_pos_x, target_pos_y, target_to_view_angle(pos_x, pos_y, target_pos_x, target_pos_y))
                            self._shot_state_last_time = time.time()
                            self._shot_state = True

    def update(self):
        # print("beh update", self._counter)
        self._counter += 1
        if self._active and self._nav_tree is not None and self._my_id is not None and self._world_data is not None and "players" in self._world_data and self._my_id in self._world_data["players"] and not self._world_data["players"][self._my_id].is_dead():
            # process only with existing data and non-dead current player
            my_player = self._world_data["players"][self._my_id]
            (pos_x, pos_y) = my_player.get_position()
            self.avoid_task(pos_x, pos_y, my_player)
            self.move_task(pos_x, pos_y, my_player)
            self.shot_task(pos_x, pos_y, my_player)
