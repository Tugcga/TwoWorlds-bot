from PySide6 import QtWidgets, QtGui, QtCore
from ui.bot_widget import BotWidget
import random


class AdderWidget(QtWidgets.QWidget):
    click_signal = QtCore.Signal(int, int)

    def __init__(self, row, column):
        super().__init__()
        self._plus_w = 40
        self._plus_h = 160
        self.width = 256
        self.height = 256
        self._row = row
        self._column = column

        self._label = QtWidgets.QLabel("Add the bot", alignment=QtCore.Qt.AlignCenter)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self._label)

        self.setMinimumSize(self.width, self.height)
        self.setMaximumSize(self.width, self.height)

    def mousePressEvent(self, event):
        self.click_signal.emit(self._row, self._column)

    def paintEvent(self, event):
        canvas_width = self.size().width()
        canvas_height = self.size().height()
        painter = QtGui.QPainter(self)
        painter.fillRect(0, 0, canvas_width, canvas_height, QtGui.QColor(200, 200, 200, 255))
        painter.fillRect((canvas_width - self._plus_w) / 2, (canvas_height - self._plus_h) / 2, self._plus_w, self._plus_h, QtGui.QColor(220, 220, 220, 255))
        painter.fillRect((canvas_width - self._plus_h) / 2, (canvas_height - self._plus_w) / 2, self._plus_h, self._plus_w, QtGui.QColor(220, 220, 220, 255))


class BotsFabricMainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QGridLayout(self)
        self._ROW_LIMIT = 4

        adder = AdderWidget(0, 0)
        adder.click_signal.connect(self.click_on_adder)
        self.layout.addWidget(adder, 0, 0)
        self._v_spacer = QtWidgets.QSpacerItem(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self._h_spacer = QtWidgets.QSpacerItem(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.layout.addItem(self._v_spacer, 1, 0, 1, -1)
        self.layout.addItem(self._h_spacer, 0, 1, -1, 1)

        self._bot_widgets = {}  # key - tuple (row, column)

    def click_on_adder(self, row, column):
        # we should replace the adder by bot widget and add the new adder
        to_remove = self.layout.itemAtPosition(row, column).widget()
        self.layout.removeWidget(to_remove)
        to_remove.setParent(None)
        bot_widget = BotWidget()
        self._bot_widgets[(row, column)] = bot_widget
        self.layout.addWidget(bot_widget, row, column)
        if column == self._ROW_LIMIT - 1:
            row = row + 1
            column = 0
        else:
            column = column + 1

        # delete spacers
        self.layout.removeItem(self._v_spacer)
        self.layout.removeItem(self._h_spacer)

        adder = AdderWidget(row, column)
        adder.click_signal.connect(self.click_on_adder)
        self.layout.addWidget(adder, row, column)

        # add spacers back
        self.layout.addItem(self._v_spacer, row + 1, 0, 1, -1)
        self.layout.addItem(self._h_spacer, 0, column + 1, -1, 1)

    def closeEvent(self, event):
        for k, w in self._bot_widgets.items():
            w.close()


class BotsFabrciApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(BotsFabrciApp, self).__init__()
        self._main = BotsFabricMainWidget()
        self._scroll = QtWidgets.QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._scroll.setWidget(self._main)
        self.setCentralWidget(self._scroll)
        self.setMaximumWidth(1062)
        self.setMinimumWidth(1062)
        self.setWindowTitle("Two Worlds bots fabric")

    def closeEvent(self, event):
        self._main.close()
