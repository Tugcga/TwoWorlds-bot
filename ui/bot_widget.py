from PySide6 import QtWidgets, QtGui, QtCore
from twbot.tw_bot import TWBot


class BotWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # draw settings
        self._background = QtGui.QColor(171, 168, 166, 255)
        self._back_light_lines = QtGui.QColor(161, 158, 156, 255)
        self._back_dark_lines = QtGui.QColor(151, 148, 146, 255)
        self._light_grid_size = 20
        self._dark_grid_size = 80
        self.AREA_SIZE = 50

        self.width = 256
        self.height = 256

        self.setMinimumSize(self.width, self.height)
        self.setMaximumSize(self.width, self.height)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.bot = TWBot(auto_connect=True, e_qt_widget=self)
        self.draw_data = None  # place here data for drawing in the canvas

    def connect_cmd(self):
        self.bot.cmd_connect()

    def disconnect_cmd(self):
        self.bot.cmd_disconnect()

    def closeEvent(self, event):
        self.bot.terminate_threads()

    def set_draw_data(self, e_draw_data):
        '''e_draw_data is a dictionary with entities on the map

        keys:
            - players - dictionary with players data
            - bullets - dictionary with bullets
            - monsters - dictionary with monsters data
            - towers - dictionary with towers
            - collects - collectable items
            # - points - plain array of floats with coordinates of edges
            - navigation_tree - rtree with data of the map edges
            - my_id - id of the current bot
        '''
        self.draw_data = e_draw_data
        self.update()

    def draw_grid(self, painter, canvas_width, canvas_height, grid_size):
        lines = []
        # vertical lines
        steps = canvas_width // grid_size
        for i in range(steps + 1):
            c = (i - steps // 2) * grid_size + canvas_width // 2
            lines.append(QtCore.QLineF(c, 0, c, canvas_height))
        # horizontal lines
        steps = canvas_height // grid_size
        for i in range(steps + 1):
            c = (i - steps // 2) * grid_size + canvas_height // 2
            lines.append(QtCore.QLineF(0, c, canvas_width, c))
        painter.drawLines(lines)

    def draw_background(self, painter, canvas_width, canvas_height):
        painter.fillRect(0, 0, canvas_width, canvas_height, self._background)
        # draw the grid
        # draw from canvas center
        painter.setPen(self._back_light_lines)
        self.draw_grid(painter, canvas_width, canvas_height, self._light_grid_size)
        painter.setPen(self._back_dark_lines)
        self.draw_grid(painter, canvas_width, canvas_height, self._dark_grid_size)

    def paintEvent(self, event):
        canvas_width = self.size().width()
        canvas_height = self.size().height()
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.draw_background(painter, canvas_width, canvas_height)
        if self.draw_data is not None and "players" in self.draw_data:
            my_id = self.draw_data["my_id"]
            if self.draw_data["navigation_tree"] is not None and my_id is not None and my_id in self.draw_data["players"]:
                my_player = self.draw_data["players"][my_id]
                (center_x, center_y) = my_player.get_position()
                scale = canvas_width / self.AREA_SIZE
                # draw only if wa have active bot model
                for player_id, player in self.draw_data["players"].items():
                    # start with players
                    if player.is_dead():
                        painter.setPen(QtGui.QColor(64, 64, 64, 255))
                        painter.setBrush(QtGui.QColor(64, 64, 64, 128))
                    else:
                        painter.setPen(QtGui.QColor(128, 0, 0, 255))
                        painter.setBrush(QtGui.QColor(128, 0, 0, 128))
                    (pos_x, pos_y) = player.get_position()
                    local_x, local_y = pos_x - center_x, pos_y - center_y
                    r = player.get_radius()
                    if r is not None:
                        r = int(r * scale)
                        painter.drawEllipse(int(local_x * scale + canvas_width / 2) - r, int(-1 * local_y * scale + canvas_height / 2) - r, 2*r, 2*r)
                # bullets
                painter.setPen(QtGui.QColor(255, 0, 0, 192))
                painter.setBrush(QtGui.QColor(255, 0, 0, 64))
                for bullet_id, bullet in self.draw_data["bullets"].items():
                    (pos_x, pos_y) = bullet.get_position()
                    if pos_x is not None and pos_y is not None:
                        b_type = bullet.get_type()
                        if b_type in [0, 1]:
                            # draw local small point
                            local_x, local_y = pos_x - center_x, pos_y - center_y
                            r = 2
                            painter.drawEllipse(int(local_x * scale + canvas_width / 2) - r, int(-1 * local_y * scale + canvas_height / 2) - r, 2*r, 2*r)
                        if b_type in [1, 2]:
                            # draw target zone
                            r = int(bullet.get_damage_radius() * scale)
                            (target_x, target_y) = bullet.get_target_position()
                            local_x, local_y = target_x - center_x, target_y - center_y
                            painter.drawEllipse(int(local_x * scale + canvas_width / 2) - r, int(-1 * local_y * scale + canvas_height / 2) - r, 2*r, 2*r)
                # monsters
                painter.setPen(QtGui.QColor(0, 0, 128, 255))
                painter.setBrush(QtGui.QColor(0, 0, 128, 128))
                for monster_id, monster in self.draw_data["monsters"].items():
                    (pos_x, pos_y) = monster.get_position()
                    local_x, local_y = pos_x - center_x, pos_y - center_y
                    r = monster.get_radius()
                    if r is not None:
                        r = int(r * scale)
                        painter.drawEllipse(int(local_x * scale + canvas_width / 2) - r, int(-1 * local_y * scale + canvas_height / 2) - r, 2*r, 2*r)
                # towers
                for tower_id, tower in self.draw_data["towers"].items():
                    (pos_x, pos_y) = tower.get_position()
                    r = tower.get_radius()
                    if pos_x is not None and pos_y is not None and r is not None:
                        if tower.is_dead():
                            painter.setPen(QtGui.QColor(128, 128, 128, 255))
                            painter.setBrush(QtGui.QColor(128, 128, 128, 128))
                        else:
                            painter.setPen(QtGui.QColor(0, 128, 128, 255))
                            painter.setBrush(QtGui.QColor(0, 128, 128, 128))
                        local_x, local_y = pos_x - center_x, pos_y - center_y
                        r = int(r * scale)
                        painter.drawEllipse(int(local_x * scale + canvas_width / 2) - r, int(-1 * local_y * scale + canvas_height / 2) - r, 2*r, 2*r)
                # collectables
                painter.setPen(QtGui.QColor(0, 255, 0, 128))
                painter.setBrush(QtGui.QColor(0, 255, 0, 32))
                for coll_id, collect in self.draw_data["collects"].items():
                    (pos_x, pos_y) = collect.get_position()
                    r = collect.get_radius()
                    local_x, local_y = pos_x - center_x, pos_y - center_y
                    r = int(r * scale)
                    painter.drawEllipse(int(local_x * scale + canvas_width / 2) - r, int(-1 * local_y * scale + canvas_height / 2) - r, 2*r, 2*r)
                # the map
                # points = self.draw_data["points"]  # this is plain array
                navigation_tree = self.draw_data["navigation_tree"]
                entries = navigation_tree.query((center_x - self.AREA_SIZE / 2, center_y - self.AREA_SIZE / 2, center_x + self.AREA_SIZE / 2, center_y + self.AREA_SIZE / 2))
                painter.setPen(QtGui.QColor(16, 16, 16, 255))
                draw_lines = []
                # for edge_index in range(edges_count):
                for e in entries:
                    # s_x, s_y, e_x, e_y = points[4*edge_index], points[4*edge_index + 1], points[4*edge_index + 2], points[4*edge_index + 3]
                    (s_x, s_y, e_x, e_y) = e.data
                    draw_lines.append(QtCore.QLineF((s_x - center_x) * scale + canvas_width / 2,
                                                    -1 * (s_y - center_y) * scale + canvas_height / 2,
                                                    (e_x - center_x) * scale + canvas_width / 2,
                                                    -1 * (e_y - center_y) * scale + canvas_height / 2))
                painter.drawLines(draw_lines)
                # over screen, if current player is dead
                if self.draw_data["players"][my_id].is_dead():
                    painter.setPen(QtGui.QColor(0, 0, 0, 128))
                    painter.setBrush(QtGui.QColor(0, 0, 0, 128))
                    painter.drawRect(0, 0, canvas_width, canvas_height)
