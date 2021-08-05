from PySide6 import QtCore
import time
import twbot.constants as cnst
from twbot.game_items.player import Player
from twbot.game_items.monster import Monster
from twbot.game_items.tower import Tower
from twbot.game_items.bullet import Bullet
from twbot.game_items.collectable import Collectable


class GameItemsController(QtCore.QObject):

    def __init__(self, after_update=None):
        super().__init__()
        self.players = {}
        self.monsters = {}
        self.bullets = {}
        self.towers = {}
        self.collectables = {}

        self._active = False
        self._last_ut = time.time()
        self.post_update = after_update  # this is callback of the bot, we should emit it after update tick
        self.navigation_tree = None

    def start(self):
        self._active = True
        while self._active:
            current_time = time.time()
            dt = current_time - self._last_ut
            self._last_ut = current_time
            self.update(dt)
            if self.post_update is not None:
                self.post_update({"players": self.players, "bullets": self.bullets, "monsters": self.monsters, "towers": self.towers, "collects": self.collectables})
            time.sleep(cnst.GAME_SIMULATION_TIMER)

    def stop(self):
        self._active = False

    def remove_player(self, id):
        if id in self.players:
            del self.players[id]

    def remove_mmoitem(self, kind, id):
        if kind == 0:  # monsters
            if id in self.monsters:
                del self.monsters[id]
        elif kind == 1:  # bullets
            if id in self.bullets:
                del self.bullets[id]
        elif kind == 2:  # towers
            if id in self.towers:
                del self.towers[id]
        elif kind == 3:  # collectable
            if id in self.collectables:
                del self.collectables[id]

    def set_player(self, player_id, player_life, player_max_life, player_location_x, player_location_y, player_angle, player_is_move, player_move_angle,
                   player_speed, player_name=None, player_radius=None, player_model=None, player_cooldawn=None):
        if player_id not in self.players:
            player = Player()
            self.players[player_id] = player
        player = self.players[player_id]
        player.update_params(player_id, player_life, player_max_life, player_location_x, player_location_y, player_angle, player_is_move, player_move_angle, player_speed,
                             player_name, player_radius, player_model, player_cooldawn)

    def set_monster(self, id, life, max_life, state, speed, target_type, target_id, target_x, target_y, x, y,
                    name=None, type=None, radius=None, damage=None, damage_radius=None):
        if id not in self.monsters:
            monster = Monster(self)
            self.monsters[id] = monster
        self.monsters[id].update_params(id, life, max_life, state, speed, target_type, target_id, target_x, target_y, x, y,
                                        name, type, radius, damage, damage_radius)

    def set_monster_atack(self, id, target_type, target_id, atack_time):
        # nothing to do
        pass

    def set_monster_dead(self, id):
        if id in self.monsters:
            del self.monsters[id]

    def set_bullet(self, id, bullet_type, host_type, host_id, damage_radius, speed, target_x, target_y,
                   delta=None, host_angle=None, x=None, y=None):
        if id not in self.bullets:
            bullet = Bullet(self)
            self.bullets[id] = bullet
        self.bullets[id].update_params(id, bullet_type, host_type, host_id, damage_radius, speed, target_x, target_y,
                                       delta, host_angle, x, y)

    def set_tower(self, id, life, max_life,
                  type=None, name=None, radius=None, x=None, y=None, minimum_distance=None, maximum_distance=None, atack_radius=None):
        '''if most parameters are None, then this called, when tower is resurect
        so, we should only update the life, if it exists
        '''
        if id not in self.towers:
            tower = Tower()
            self.towers[id] = tower
        tower = self.towers[id]
        tower.update_life(life, max_life)
        if type is not None:
            tower.update_params(id, type, name, radius, x, y, minimum_distance, maximum_distance, atack_radius)

    def set_collectable(self, id, type, x, y, radius, emit=None):
        '''if emit None, then this call from AoI update, so collectable appear in the area
        '''
        if emit is not None and emit is False:
            # delete the item
            if id in self.collectables:
                del self.collectables[id]
        else:
            if id not in self.collectables:
                coll = Collectable()
                self.collectables[id] = coll
            self.collectables[id].update_params(id, type, x, y, radius)

    def set_damage(self, id, type, x, y, use_bullet, hits):
        '''called when something take damage
        '''
        if use_bullet:
            # delete the bullet
            if id in self.bullets:
                del self.bullets[id]
        # recalculate life for all hits
        for hit in hits:
            t = hit["type"]
            id = hit["id"]
            life = hit["life"]
            max_life = hit["max_life"]
            is_dead = hit["is_dead"]
            block_time = hit["block"]
            if t == 0:  # player
                if id in self.players:
                    self.players[id].update_life(life, max_life)
            elif t == 1:  # monster
                if id in self.monsters:
                    self.monsters[id].update_life(life, max_life)
            elif t == 2:  # tower
                if id in self.towers:
                    self.towers[id].update_life(life, max_life)

    def get_position(self, type, id):
        '''return position of the item in the form (x, y)

        type - type of the item:
            - 0 - player
            - 1 - monster
            - 2 - tower
        '''
        if type == 0 and id in self.players:
            return self.players[id].get_position()
        elif type == 1 and id in self.monsters:
            return self.monsters[id].get_position()
        elif type == 2 and id in self.towers:
            return self.towers[id].get_position()
        else:
            return (None, None)

    def set_navigation_tree(self, nav_tree):
        # call it from the host app, when it obtain points
        self.navigation_tree = nav_tree

    def update(self, dt):
        for p_id, player in self.players.items():
            if not player.is_dead():
                (x, y) = player.get_next_point(dt, self.navigation_tree)
                player.set_poistion(x, y)
        for b_id, bullet in self.bullets.items():
            (x, y) = bullet.get_next_point(dt)
            bullet.set_position(x, y)
        for m_id, monster in self.monsters.items():
            if not monster.is_dead():
                (x, y) = monster.get_next_point(dt)
                monster.set_position(x, y)
