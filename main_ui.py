from PySide6 import QtWidgets
from ui.ui_app import BotsFabrciApp

if __name__ == "__main__":
    app = QtWidgets.QApplication()
    main = BotsFabrciApp()
    main.resize(1062, 820)
    main.show()
    app.exec_()
