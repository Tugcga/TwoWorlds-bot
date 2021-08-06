from PySide6 import QtCore
import time
import twbot.constants as cnst  # type: ignore
from twbot.game_items.player import Player  # type: ignore
from twbot.game_items.monster import Monster  # type: ignore
from twbot.game_items.tower import Tower  # type: ignore
from twbot.game_items.bullet import Bullet  # type: ignore
from twbot.game_items.collectable import Collectable  # type: ignore
from rtreelib import RTree  # type: ignore
from typing import Tuple, Union, List, Dict, Any


class GameItemsController(QtCore.QObject):
    def __init__(self, after_update=None) -> None:
        super().__init__()
        self._players: Dict[int, Player] = {}
        self._monsters: Dict[int, Monster] = {}
        self._bullets: Dict[int, Bullet] = {}
        self._towers: Dict[int, Tower] = {}
        self._collectables: Dict[int, Collectable] = {}

        self._active: bool = False
        self._last_ut: float = time.time()
        self.post_update = after_update  # this is callback of the bot, we should emit it after update tick
        self._navigation_tree: Union[RTree, None] = None

    def start(self) -> None:
        self._active = True
        while self._active:
            current_time: float = time.time()
            dt: float = current_time - self._last_ut
            self._last_ut = current_time
            self.update(dt)
            if self.post_update is not None:
                self.post_update({"players": self._players, "bullets": self._bullets, "monsters": self._monsters, "towers": self._towers, "collects": self._collectables})
            time.sleep(cnst.GAME_SIMULATION_TIMER)

    def stop(self) -> None:
        self._active = False

    def remove_player(self, id: int) -> None:
        if id in self._players:
            del self._players[id]

    def remove_mmoitem(self, kind: int, id: int) -> None:
        if kind == 0:  # monsters
            if id in self._monsters:
                del self._monsters[id]
        elif kind == 1:  # bullets
            if id in self._bullets:
                del self._bullets[id]
        elif kind == 2:  # towers
            if id in self._towers:
                del self._towers[id]
        elif kind == 3:  # collectable
            if id in self._collectables:
                del self._collectables[id]

    def set_player(self, player_id: int, player_life: int, player_max_life: int, player_location_x: float, player_location_y: float, player_angle: float, player_is_move: bool, player_move_angle: float,
                   player_speed: float, player_name: str=None, player_radius: float=None, player_model: int=None, player_cooldawn: float=None) -> None:
        if player_id not in self._players:
            player: Player = Player()
            self._players[player_id] = player
        self._players[player_id].update_params(player_id, player_life, player_max_life, player_location_x, player_location_y, player_angle, player_is_move, player_move_angle, player_speed,
                             player_name, player_radius, player_model, player_cooldawn)

    def set_monster(self, id: int, life: int, max_life: int, state: int, speed: float, target_type: int, target_id: int, target_x: float, target_y: float, x: float, y: float,
                    name: str=None, type: int=None, radius: float=None, damage: int=None, damage_radius: float=None) -> None:
        if id not in self._monsters:
            monster: Monster = Monster(self)
            self._monsters[id] = monster
        self._monsters[id].update_params(id, life, max_life, state, speed, target_type, target_id, target_x, target_y, x, y,
                                        name, type, radius, damage, damage_radius)

    def set_monster_atack(self, id: int, target_type: int, target_id: int, atack_time: float) -> None:
        # nothing to do
        pass

    def set_monster_dead(self, id: int) -> None:
        if id in self._monsters:
            del self._monsters[id]

    def set_bullet(self, id: int, bullet_type: int, host_type: int, host_id: int, damage_radius: float, speed: float, target_x: float, target_y: float,
                   delta: float=None, host_angle: float=None, x: float=None, y: float=None) -> None:
        if id not in self._bullets:
            bullet: Bullet = Bullet(self)
            self._bullets[id] = bullet
        self._bullets[id].update_params(id, bullet_type, host_type, host_id, damage_radius, speed, target_x, target_y,
                                       delta, host_angle, x, y)

    def set_tower(self, id: int, life: int, max_life: int,
                  type: int=None, name: str=None, radius: float=None, x: float=None, y: float=None, minimum_distance: float=None, maximum_distance: float=None, atack_radius: float=None) -> None:
        '''if most parameters are None, then this called, when tower is resurect
        so, we should only update the life, if it exists
        '''
        if id not in self._towers:
            tower: Tower = Tower()
            self._towers[id] = tower
        self._towers[id].update_life(life, max_life)
        if type is not None:
            self._towers[id].update_params(id, type, name, radius, x, y, minimum_distance, maximum_distance, atack_radius)

    def set_collectable(self, id: int, type: int, x:float, y: float, radius: float, emit: bool=None) -> None:
        '''if emit None, then this call from AoI update, so collectable appear in the area
        '''
        if emit is not None and emit is False:
            # delete the item
            if id in self._collectables:
                del self._collectables[id]
        else:
            if id not in self._collectables:
                coll: Collectable = Collectable()
                self._collectables[id] = coll
            self._collectables[id].update_params(id, type, x, y, radius)

    def set_damage(self, id: int, type: int, x: float, y: float, use_bullet: bool, hits: List[Dict[str, Any]]):
        '''called when something take damage
        '''
        if use_bullet:
            # delete the bullet
            if id in self._bullets:
                del self._bullets[id]
        # recalculate life for all hits
        for hit in hits:
            t: int = hit["type"]
            t_id: int = hit["id"]
            life: int = hit["life"]
            max_life: int = hit["max_life"]
            is_dead: bool = hit["is_dead"]
            block_time: bool = hit["block"]
            if t == 0:  # player
                if t_id in self._players:
                    self._players[t_id].update_life(life, max_life)
            elif t == 1:  # monster
                if t_id in self._monsters:
                    self._monsters[t_id].update_life(life, max_life)
            elif t == 2:  # tower
                if t_id in self._towers:
                    self._towers[t_id].update_life(life, max_life)

    def get_position(self, type: int, id: int) -> Tuple[Union[float, None], Union[float, None]]:
        '''return position of the item in the form (x, y)

        type - type of the item:
            - 0 - player
            - 1 - monster
            - 2 - tower
        '''
        if type == 0 and id in self._players:
            return self._players[id].get_position()
        elif type == 1 and id in self._monsters:
            return self._monsters[id].get_position()
        elif type == 2 and id in self._towers:
            return self._towers[id].get_position()
        else:
            return (None, None)

    def set_navigation_tree(self, nav_tree: RTree) -> None:
        # call it from the host app, when it obtain points
        self._navigation_tree = nav_tree

    def update(self, dt: float):
        for p_id, player in self._players.items():
            if not player.is_dead():
                (x, y) = player.get_next_point(dt, self._navigation_tree)
                player.set_poistion(x, y)
        for b_id, bullet in self._bullets.items():
            (x, y) = bullet.get_next_point(dt)
            bullet.set_position(x, y)
        for m_id, monster in self._monsters.items():
            if not monster.is_dead():
                (x, y) = monster.get_next_point(dt)
                monster.set_position(x, y)
