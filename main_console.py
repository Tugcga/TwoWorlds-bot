from twbot.tw_bot import TWBot  # type: ignore
from PySide6 import QtCore
import random


class BotsFabric:
    def __init__(self, app):
        self._bots = []
        self._app = app
        self._is_active = True
        self.key_listen()

    def key_listen(self):
        while self._is_active:
            input_str = input(":> ")
            parts = input_str.split()
            token = parts[0]
            if token == "help":
                print("There are several commands that you can use:\n\
                    - <exit> to stop the program\n\
                    - <bot [model]> to add a bot with selected model (0 or 1)\n\
                    - <botscount> to print the current count of active bots\n\
                    - <kill [index]> to delete the bot with [index] in the total list\n\
                    - <botset [count]> to add [count] bots with random model")
            elif token == "exit":
                self._is_active = False
                # stop all bots
                for b in self._bots:
                    b.terminate_threads()
                self._app.shutdown()
            elif token == "botscount":
                print("Total count of active bots: " + str(len(self._bots)))
            elif token == "kill":
                if len(parts) > 1:
                    i_str = parts[1]
                    if i_str.isnumeric():
                        i = int(i_str)
                        if i >= 0 and i < len(self._bots):
                            print("Stop bot " + str(i))
                            b = self._bots[i]
                            b.terminate_threads()
                            self._bots.remove(b)
                        else:
                            print("The index of the bot should be from 0 to the total count in the list. To obtain it - call <botscount>")
                    else:
                        print("The index of the bot shold be integer")
                else:
                    print("Input the index of the bot")
            elif token == "bot":
                if len(parts) > 1:
                    mi_str = parts[1]
                    if mi_str.isnumeric():
                        mi = int(mi_str)
                        if mi in [0, 1]:
                            self._bots.append(TWBot(model=mi, auto_connect=True))
                        else:
                            print("Invalid model. It should be 0 or 1")
                    else:
                        print("The model should be integer 0 or 1")
                else:
                    print("Add the model index (0 or 1) after <bot> command")
            elif token == "botset":
                if len(parts) > 1:
                    mi_str = parts[1]
                    if mi_str.isnumeric():
                        mi = int(mi_str)
                        if mi < 0:
                            print("The number of bots should be non-negative integer")
                        else:
                            for i in range(mi):
                                self._bots.append(TWBot(model=random.randint(0, 1), auto_connect=True))
                    else:
                        print("The number of bots should be non-negative integer")
                else:
                    print("Define the number of bots (any non-negative number) after <botset> command")
            else:
                print("Unknown token '" + token + "'. Print 'help' for valid commands")


if __name__ == "__main__":
    app = QtCore.QCoreApplication()
    fabric = BotsFabric(app)
