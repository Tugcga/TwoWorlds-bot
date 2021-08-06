from PySide6 import QtCore
import twbot.network.SFSCommunicator as sfs  # type: ignore
import time
import twbot.constants as cnst  # type: ignore
from typing import Tuple, Union, List, Dict, Any


class SFSConnector(QtCore.QObject):
    def __init__(self, name: str="Python_Bot", model_index: int=0) -> None:
        super().__init__()
        self._is_active: bool = False
        self._client: sfs.SFSClient = sfs.SFSClient()
        self._name: str = name
        self._model_index: int = model_index

    def define_callbacks(self, c_set_navigation,
                         c_set_id,
                         c_set_player,
                         c_set_monster,
                         c_set_monster_atack,
                         c_set_monster_dead,
                         c_set_bullet,
                         c_set_tower,
                         c_set_collectable,
                         c_set_damage,
                         c_remove_player,
                         c_remove_mmoitem) -> None:
        self.set_navigation = c_set_navigation
        self.set_id = c_set_id
        self.set_player = c_set_player
        self.set_monster = c_set_monster
        self.set_monster_atack = c_set_monster_atack
        self.set_monster_dead = c_set_monster_dead
        self.set_bullet = c_set_bullet
        self.set_tower = c_set_tower
        self.set_collectable = c_set_collectable
        self.set_damage = c_set_damage
        self.remove_player = c_remove_player
        self.remove_mmoitem = c_remove_mmoitem

    def updating(self) -> None:
        self._is_active = True
        while self._is_active:
            self.updating_call()
            time.sleep(cnst.NETWORK_UPDATE_TIMER)

    def process_user(self, data: sfs.DataContainer) -> None:
        cl_id: int = data.get_user_id()
        cl_name: str = data.get_user_string("n")
        cl_model: int = data.get_user_int("mi")
        cl_cooldawn: float = data.get_user_float("cd")
        cl_radius: float = data.get_user_float("r")
        cl_max_life: int = data.get_user_int("ml")
        cl_life: int = data.get_user_int("l")
        cl_speed: float = data.get_user_float("sp")
        cl_location_x: float = data.get_user_double("x")
        cl_location_y: float = data.get_user_double("y")
        cl_is_move: bool = data.get_user_bool("im")
        cl_move_angle: float = data.get_user_float("ma")
        cl_angle: float = data.get_user_float("a")
        self.set_player(cl_id, cl_life, cl_max_life, cl_location_x, cl_location_y, cl_angle, cl_is_move, cl_move_angle, cl_speed, player_name=cl_name, player_radius=cl_radius, player_model=cl_model, player_cooldawn=cl_cooldawn)

    def process_mmoitem(self, d: sfs.DataContainer) -> None:
        i_kind: int = d.get_mmoitem_int("sik")
        if i_kind == 0:
            m_id: int = d.get_mmoitem_int("i")
            m_name: str = d.get_mmoitem_string("n")
            m_speed: float = d.get_mmoitem_float("sp")
            m_type: int = d.get_mmoitem_int("sit")
            m_radius: float = d.get_mmoitem_float("r")
            m_max_life: int = d.get_mmoitem_int("ml")
            m_life: int = d.get_mmoitem_int("l")
            m_damage: int = d.get_mmoitem_int("md")
            m_damage_radius: float = d.get_mmoitem_float("mdr")
            m_x: float = d.get_mmoitem_double("x")
            m_y: float = d.get_mmoitem_double("y")
            m_state: int = d.get_mmoitem_int("st")
            m_target_x: float = d.get_mmoitem_double("tlx")
            m_target_y: float = d.get_mmoitem_double("tly")
            m_target_type: int = d.get_mmoitem_int("tet")
            m_target_id: int = d.get_mmoitem_int("tei")
            self.set_monster(m_id, m_life, m_max_life, m_state, m_speed, m_target_type, m_target_id, m_target_x, m_target_y, m_x, m_y,
                             m_name, m_type, m_radius, m_damage, m_damage_radius)
        elif i_kind == 1:
            bt_id: int = d.get_mmoitem_int("i")
            bt_speed: float = d.get_mmoitem_float("sp")
            bt_type: int = d.get_mmoitem_int("sit")
            bt_radius: float = d.get_mmoitem_float("r")
            bt_atacker_type: int = d.get_mmoitem_int("bht")
            bt_atacker_id: int = d.get_mmoitem_int("bhi")
            bt_x: float = d.get_mmoitem_double("x")
            bt_y: float = d.get_mmoitem_double("y")
            bt_target_x: float = d.get_mmoitem_double("tlx")
            bt_target_y: float = d.get_mmoitem_double("tly")
            self.set_bullet(bt_id, bt_type, bt_atacker_type, bt_atacker_id, bt_radius, bt_speed, bt_target_x, bt_target_y,
                            x=bt_x, y=bt_y)
        elif i_kind == 2:
            t_id: int = d.get_mmoitem_int("i")
            t_type: int = d.get_mmoitem_int("sit")
            t_name: str = d.get_mmoitem_string("n")
            t_max_life: int = d.get_mmoitem_int("ml")
            t_life: int = d.get_mmoitem_int("l")
            t_radius: float = d.get_mmoitem_float("r")
            t_x: float = d.get_mmoitem_double("x")
            t_y: float = d.get_mmoitem_double("y")
            t_minimum_distance: float = d.get_mmoitem_float("tmmi")
            t_maximum_distance: float = d.get_mmoitem_float("tmma")
            t_atack_radius: float = d.get_mmoitem_float("tar")
            self.set_tower(t_id, t_life, t_max_life,
                           t_type, t_name, t_radius, t_x, t_y, t_minimum_distance, t_maximum_distance, t_atack_radius)
        elif i_kind == 3:
            col_id: int = d.get_mmoitem_int("i")
            col_type: int = d.get_mmoitem_int("sit")
            col_x: float = d.get_mmoitem_double("x")
            col_y: float = d.get_mmoitem_double("y")
            col_radius: float = d.get_mmoitem_float("r")
            self.set_collectable(col_id, col_type, col_x, col_y, col_radius)

    def updating_call(self) -> None:
        '''call during update routine

        we update events and collect events data only if thise data exists
        '''
        datas_list: List[sfs.DataContainer] = self._client.update()
        if len(datas_list) > 0:
            # datas_list contains array of DataContainers, which contains data from each event
            for d in datas_list:
                d_name: str = d.get_event_name()  # d_name is event name
                if d_name == "connection":
                    is_success: bool = d.get_bool("success")
                    # print("connection: " + str(is_success))
                    if is_success:
                        # self._client.login("python", 0, True)  # paramters for login
                        data: sfs.DataContainer = sfs.DataContainer()
                        data.put_byte("modelIndex", self._model_index)
                        data.put_bool("needMap", True)
                        self._client.login(self._name, "", "OpenWorldZone", data)
                elif d_name == "connection_lost":
                    pass
                elif d_name == "login":
                    # get out name
                    name: str = d.get_string("$FS_NEW_LOGIN_NAME")
                    id: int = self._client.get_my_id()
                    # print("login with name: " + name + ", id: " + str(id))
                    self.set_id(id)
                elif d_name == "join_room":
                    pass
                elif d_name == "user_update":
                    self.process_user(d)
                elif d_name == "mmoitem_update":
                    self.process_mmoitem(d)
                elif d_name == "proximity_update":
                    add_user_list: List[sfs.DataContainer] = d.get_list_add_users()
                    remove_user_list: List[sfs.DataContainer] = d.get_list_remove_users()
                    add_mmoitem_list: List[sfs.DataContainer] = d.get_list_add_mmoitems()
                    remove_mmoitem_list: List[sfs.DataContainer] = d.get_list_remove_mmoitems()
                    # print("proximity_update", len(add_user_list), len(remove_user_list), len(add_mmoitem_list), len(remove_mmoitem_list))
                    for user in add_user_list:
                        self.process_user(user)
                    for item in add_mmoitem_list:
                        self.process_mmoitem(item)
                    for user in remove_user_list:
                        self.remove_player(user.get_user_id())
                    for item in remove_mmoitem_list:
                        i_kind: int = item.get_mmoitem_int("sik")
                        i_id: int = item.get_mmoitem_int("i")
                        self.remove_mmoitem(i_kind, i_id)
                elif d_name == "extension":
                    cmd: str = d.get_command()
                    m_id: int
                    m_target_type: int
                    m_target_id: int
                    bt_id: int
                    if cmd == "RPCTowerResurect":
                        t_id: int = d.get_int("id")
                        t_life: int = d.get_int("life")
                        t_max_life: int = d.get_int("maxLife")
                        self.set_tower(t_id, t_life, t_max_life)
                    elif cmd == "RPCMonsterStartAtack":
                        m_id = d.get_int("monsterId")
                        m_target_type = d.get_byte("targetType")
                        m_target_id = d.get_int("targetId")
                        m_atack_time: float = d.get_float("atackTime")
                        self.set_monster_atack(m_id, m_target_type, m_target_id, m_atack_time)
                    elif cmd == "RPCMonsterDead":
                        m_id = d.get_int("monsterId")
                        self.set_monster_dead(m_id)
                    elif cmd == "RPCMonsterChangeState":
                        m_id = d.get_int("id")
                        m_life: int = d.get_int("life")
                        m_max_life: int = d.get_int("maxLife")
                        m_state: int = d.get_byte("state")
                        m_speed: float = d.get_float("speed")
                        m_target_type = d.get_byte("targetType")
                        m_target_id = d.get_int("targetId")
                        m_target_x: float = d.get_double("targetPositionX")
                        m_target_y: float = d.get_double("targetPositionY")
                        m_x: float = d.get_double("positionX")
                        m_y: float = d.get_double("positionY")
                        self.set_monster(m_id, m_life, m_max_life, m_state, m_speed, m_target_type, m_target_id, m_target_x, m_target_y, m_x, m_y)
                    elif cmd == "RPCClientUpdate":
                        cl_id: int = d.get_int("id")
                        cl_life: int = d.get_int("life")
                        cl_max_life: int = d.get_int("maxLife")
                        cl_location_x: float = d.get_double("locationX")
                        cl_location_y: float = d.get_double("locationY")
                        cl_angle: float = d.get_float("angle")
                        cl_is_move: bool = d.get_bool("isMove")
                        cl_move_angle: float = d.get_float("moveAngle")
                        cl_speed: float = d.get_float("speed")
                        self.set_player(cl_id, cl_life, cl_max_life, cl_location_x, cl_location_y, cl_angle, cl_is_move, cl_move_angle, cl_speed)
                    elif cmd == "RPCStartBullet":
                        bt_host_type: int = d.get_byte("hostType")
                        bt_host_id: int = d.get_int("hostId")
                        bt_host_angle: float = d.get_float("hostAngle")
                        bt_id = d.get_int("id")
                        bt_bullet_type: int = d.get_byte("bulletType")
                        bt_damage_radius: float = d.get_float("damageRadius")
                        bt_speed: float = d.get_float("speed")
                        bt_target_x: float = d.get_double("targetX")
                        bt_target_y: float = d.get_double("targetY")
                        bt_delay: float = d.get_float("delay")
                        self.set_bullet(bt_id, bt_bullet_type, bt_host_type, bt_host_id, bt_damage_radius, bt_speed, bt_target_x, bt_target_y,
                                        delta=bt_delay, host_angle=bt_host_angle)
                    elif cmd == "RPCDestoyBullet":
                        bt_id = d.get_int("id")
                        bt_type: int = d.get_byte("type")
                        bt_x: float = d.get_double("x")
                        bt_y: float = d.get_double("y")
                        bt_use_bullet: bool = d.get_bool("useBullet")
                        bt_hit_data: List[sfs.DataContainer] = d.get_sfs_array("hitData")
                        bt_hits: List[Dict[str, Any]] = []
                        for hd in bt_hit_data:
                            hd_type: int = hd.get_byte("type")
                            hd_id: int = hd.get_int("id")
                            hd_life: int = hd.get_int("life")
                            hd_max_life: int = hd.get_int("maxLife")
                            hd_dead: bool = hd.get_bool("isDead")
                            hd_block: float = hd.get_float("blockTime")
                            bt_hits.append({"id": hd_id,
                                            "type": hd_type,
                                            "life": hd_life,
                                            "max_life": hd_max_life,
                                            "is_dead": hd_dead,
                                            "block": hd_block})
                        self.set_damage(bt_id, bt_type, bt_x, bt_y, bt_use_bullet, bt_hits)
                    elif cmd == "RPCKillsMessage":
                        '''array = d.get_sfs_array("killsArray")
                        for kd in array:
                            kd_id = kd.get_int("id")
                            kd_name = kd.get_string("name")
                            kd_kills = kd.get_int("totalKills")
                            kd_pl_kills = kd.get_int("playerKills")
                            kd_mn_kills = kd.get_int("monsterKills")
                            kd_tw_kills = kd.get_int("towerKills")
                            kd_death = kd.get_int("death")'''
                        pass
                    elif cmd == "RPCMap":
                        points: List[float] = d.get_double_array("points")
                        self.set_navigation(points)
                    elif cmd == "RPCChatMessage":
                        '''cht_sender = d.get_string("sender")
                        cht_sender_id = d.get_int("senderId")
                        cht_message = d.get_string("message")'''
                        # does not use chat
                        pass
                    elif cmd == "RPCProcessCollect":
                        col_id: int = d.get_int("id")
                        col_type: int = d.get_int("type")
                        col_x: float = d.get_double("x")
                        col_y: float = d.get_double("y")
                        col_radius: float = d.get_float("radius")
                        col_emit: bool = d.get_bool("emit")
                        self.set_collectable(col_id, col_type, col_x, col_y, col_radius,
                                             col_emit)
                elif d_name == "admin_message":
                    adm_message: str = d.get_string("message")
                    print("admin message:", adm_message)

    def move_command(self, dir_index: int, view_angle: float=0.0) -> None:
        data: sfs.DataContainer = sfs.DataContainer()
        data.put_byte("dirIndex", dir_index)
        data.put_float("angle", view_angle)
        self._client.send_command("RPCClientSendMovementKey", data)

    def shot_command(self, pos_x: float, pos_y: float, view_angle: float) -> None:
        data: sfs.DataContainer = sfs.DataContainer()
        data.put_float("posX", pos_x)
        data.put_float("posY", pos_y)
        data.put_float("angle", view_angle)
        self._client.send_command("RPCFire", data)

    def stop_updating(self) -> None:
        self._is_active = False

    def cmd_connect(self, host: str, port: int, zone: str) -> None:
        self._client.connect(host, port, zone)

    def cmd_disconnect(self) -> None:
        self._client.disconnect()
