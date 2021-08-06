# What is it

This is bot for [Two Worlds project game](http://twoworlds.azurewebsites.net/). It based on public [client-server communication guide](https://github.com/Tugcga/TwoWorldsServer/blob/master/ClientServer.md) and use [SFS Communicator](https://github.com/Tugcga/SmartFox-Python-Communicator) for connecting to SmartFox server from Python.

This bot implement basic behavior and all necessary communications with server. It use the following external Python modules:
* [PySide6](https://pypi.org/project/PySide6/) From this module it use QtThreads
* [RTreelib](https://github.com/sergkr/rtreelib) This module used only for building r-tree for walls of the location and quiring it for getting intersections. So, this module needed only in minimal configuration

The main class is `TWBot`. When the instance of this class is created, then it initialize all necessary data, create three parallel threads and start update loops. 

The brain of the bot in the `BehaviourClass`
* `update` function make all necessary decisions
* `actualize_world` method called by the host `TWBot` for setting actual state of the world: entities positions and directions.

# Example applications

There are two examples, which use the bot - with GUI and console application

## GUI application

This application based on PySide6.

![GUI applicaiton](gui_app.png?raw=true)

To run - simply call 

```
python main_ui.py
```

To add the new bot click an icon with the text "Add the bot". Small window, centered to the current bot, will appear. You can add any number of bots to the canvas.

## Console application

To run this application, simply call fromm the console

```
python main_console.py
```

This will start interactive dialog. You should print commands, and the system will execute it. For example, you can add the bot by printing `bot 0` (0 is an index of the model for the character), or you can delete the bot by printing `kill 1` (this command will delete the second bot in the list). To stop the process and delete all bots print `exit`.