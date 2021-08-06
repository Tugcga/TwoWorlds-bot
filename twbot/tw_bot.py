from PySide6 import QtCore, QtWidgets
from twbot.game_items_controller import GameItemsController  # type: ignore
from twbot.behaviour import BehaviourClass  # type: ignore
from twbot.network.sfs_connector import SFSConnector  # type: ignore
from rtreelib import Rect, RTree  # type: ignore
import twbot.constants as cnst  # type: ignore
import requests
from twbot.utilities import is_valid_ip  # type: ignore
from typing import Tuple, List, Union, Dict, Any


class TWBot():
    '''One bot instance
    '''

    def __init__(self, model: int=0, auto_connect: bool=False, e_qt_widget: QtWidgets.QWidget=None) -> None:
        self._qt_widget: Union[QtWidgets.QWidget, None] = e_qt_widget  # None if we use it without gui
        self._my_id: Union[int, None] = None
        # self.navigation_points = None
        self._navigation_rtree: Union[RTree, None] = None

        self._gi_thread: QtCore.QThread = QtCore.QThread()
        self._gi_controller: GameItemsController = GameItemsController(self.set_draw_data)  # here we define self.set_draw_data as post-update method in gi_controller
        self._gi_controller.moveToThread(self._gi_thread)
        self._gi_thread.started.connect(self._gi_controller.start)
        self._gi_thread.start()

        self._connector_thread: QtCore.QThread = QtCore.QThread()
        self._connector: SFSConnector = SFSConnector(model_index=model)
        self._connector.define_callbacks(c_set_navigation=self.set_navigation,
                                        c_set_id=self.set_id,
                                        c_set_player=self._gi_controller.set_player,
                                        c_set_monster=self._gi_controller.set_monster,
                                        c_set_monster_atack=self._gi_controller.set_monster_atack,
                                        c_set_monster_dead=self._gi_controller.set_monster_dead,
                                        c_set_bullet=self._gi_controller.set_bullet,
                                        c_set_tower=self._gi_controller.set_tower,
                                        c_set_collectable=self._gi_controller.set_collectable,
                                        c_set_damage=self._gi_controller.set_damage,
                                        c_remove_player=self._gi_controller.remove_player,
                                        c_remove_mmoitem=self._gi_controller.remove_mmoitem)
        self._connector.moveToThread(self._connector_thread)
        self._connector_thread.started.connect(self._connector.updating)
        self._connector_thread.start()

        self._beh_thread: QtCore.QThread = QtCore.QThread()
        self._beh: BehaviourClass = BehaviourClass(self._connector.move_command, self._connector.shot_command)
        self._beh.moveToThread(self._beh_thread)
        self._beh_thread.started.connect(self._beh.start)
        self._beh_thread.start()

        if auto_connect:
            self.cmd_connect()

    def cmd_connect(self) -> None:
        resp = requests.get(cnst.NETWORK_GET_IP_ADDRESS)
        ip_text: str = resp.text
        if not is_valid_ip(ip_text):
            ip_text = "127.0.0.1"
        self._connector.cmd_connect(ip_text, 9933, "OpenWorldZone")

    def cmd_disconnect(self) -> None:
        self._connector.cmd_disconnect()

    def set_navigation(self, points: List[float]) -> None:
        def edge_to_rect(sx: float, sy: float, ex: float, ey: float) -> Rect:
            return Rect(min(sx, ex) - cnst.RTREE_DELTA, min(sy, ey) - cnst.RTREE_DELTA, max(sx, ex) + cnst.RTREE_DELTA, max(sy, ey) + cnst.RTREE_DELTA)

        self._navigation_rtree = RTree()
        edge_count: int = len(points) // 4
        for e_index in range(edge_count):
            edge: List[float] = points[4*e_index:4*e_index + 4]
            self._navigation_rtree.insert(tuple(edge), edge_to_rect(*edge))
        self._beh.define_navigation(self._navigation_rtree)  # transfer navigation tree to the behaviour class
        self._gi_controller.set_navigation_tree(self._navigation_rtree)

    def set_id(self, id: int) -> None:
        self._my_id = id
        self._beh.define_my_id(id)  # transfer current bot id to the bahaviour class

    def set_draw_data(self, e_draw_data: Dict[str, Any]) -> None:
        self._beh.actualize_world(e_draw_data)  # actualize states of all in-game entities (players, bullets and so on), we call this every simulation tick update
        if self._qt_widget is not None:  # update draw in the widget, if it exists
            # e_draw_data["points"] = self.navigation_points  # add points to the dictionary
            e_draw_data["navigation_tree"] = self._navigation_rtree
            e_draw_data["my_id"] = self._my_id
            self._qt_widget.set_draw_data(e_draw_data)

    def terminate_threads(self) -> None:
        self.cmd_disconnect()
        self._connector.stop_updating()
        self._gi_controller.stop()
        self._beh.stop()
        self._connector_thread.terminate()
        self._gi_thread.terminate()
        self._beh_thread.terminate()
        self._connector_thread.wait()
        self._gi_thread.wait()
        self._beh_thread.wait()
