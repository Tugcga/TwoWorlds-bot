from PySide6 import QtCore
from twbot.game_items_controller import GameItemsController
from twbot.behaviour import BehaviourClass
from twbot.network.sfs_connector import SFSConnector
from rtreelib import Rect, RTree
import twbot.constants as cnst


class TWBot():
    '''One bot instance
    '''

    def __init__(self, auto_connect=False, e_qt_widget=None):
        self.qt_widget = e_qt_widget  # None if we use it without gui
        self.my_id = None
        # self.navigation_points = None
        self.navigation_rtree = None

        self.gi_thread = QtCore.QThread()
        self.gi_controller = GameItemsController(self.set_draw_data)  # here we define self.set_draw_data as post-update method in gi_controller
        self.gi_controller.moveToThread(self.gi_thread)
        self.gi_thread.started.connect(self.gi_controller.start)
        self.gi_thread.start()

        self.connector_thread = QtCore.QThread()
        self.connector = SFSConnector()
        self.connector.define_callbacks(c_set_navigation=self.set_navigation,
                                        c_set_id=self.set_id,
                                        c_set_player=self.gi_controller.set_player,
                                        c_set_monster=self.gi_controller.set_monster,
                                        c_set_monster_atack=self.gi_controller.set_monster_atack,
                                        c_set_monster_dead=self.gi_controller.set_monster_dead,
                                        c_set_bullet=self.gi_controller.set_bullet,
                                        c_set_tower=self.gi_controller.set_tower,
                                        c_set_collectable=self.gi_controller.set_collectable,
                                        c_set_damage=self.gi_controller.set_damage,
                                        c_remove_player=self.gi_controller.remove_player,
                                        c_remove_mmoitem=self.gi_controller.remove_mmoitem)
        self.connector.moveToThread(self.connector_thread)
        self.connector_thread.started.connect(self.connector.updating)
        self.connector_thread.start()

        self.beh_thread = QtCore.QThread()
        self.beh = BehaviourClass(self.connector.move_command, self.connector.shot_command)
        self.beh.moveToThread(self.beh_thread)
        self.beh_thread.started.connect(self.beh.start)
        self.beh_thread.start()

        if auto_connect:
            self.cmd_connect()

    def cmd_connect(self):
        self.connector.cmd_connect("127.0.0.1", 9933, "OpenWorldZone")

    def cmd_disconnect(self):
        self.connector.cmd_disconnect()

    def set_navigation(self, points):
        def edge_to_rect(sx, sy, ex, ey):
            return Rect(min(sx, ex) - cnst.RTREE_DELTA, min(sy, ey) - cnst.RTREE_DELTA, max(sx, ex) + cnst.RTREE_DELTA, max(sy, ey) + cnst.RTREE_DELTA)

        self.navigation_rtree = RTree()
        edge_count = len(points) // 4
        for e_index in range(edge_count):
            edge = points[4*e_index:4*e_index + 4]
            self.navigation_rtree.insert(tuple(edge), edge_to_rect(*edge))
        self.beh.define_navigation(self.navigation_rtree)  # transfer navigation tree to the behaviour class
        self.gi_controller.set_navigation_tree(self.navigation_rtree)

    def set_id(self, id):
        self.my_id = id
        self.beh.define_my_id(id)  # transfer current bot id to the bahaviour class

    def set_draw_data(self, e_draw_data):
        self.beh.actualize_world(e_draw_data)  # actualize states of all in-game entities (players, bullets and so on), we call this every simulation tick update
        if self.qt_widget is not None:  # update draw in the widget, if it exists
            # e_draw_data["points"] = self.navigation_points  # add points to the dictionary
            e_draw_data["navigation_tree"] = self.navigation_rtree
            e_draw_data["my_id"] = self.my_id
            self.qt_widget.set_draw_data(e_draw_data)

    def terminate_threads(self):
        self.cmd_disconnect()
        self.connector.stop_updating()
        self.gi_controller.stop()
        self.beh.stop()
        self.connector_thread.terminate()
        self.gi_thread.terminate()
        self.beh_thread.terminate()
        self.connector_thread.wait()
        self.gi_thread.wait()
        self.beh_thread.wait()

    # def __del__(self):
        # self.terminate_threads()
