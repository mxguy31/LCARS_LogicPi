# LogicPi
A basic RaspberryPi based logic engine which is expandable through a simple API

This engine maintains a database and acts as a watchdog for logic and IO programs added by the user. A multiprocessing environment is utilized to ensure that failures in a user program are isolated and do not propogate to a system failure.

A basic expandable GUI is provided based on the Star Trek LCARS interface using the Kivy framework.

## Usage
All user programs are located in the "programs" folder, they must inherit from the Program class. 
All IO Drivers are located in the "drivers" folder, form and function are up to the end user.
All Utilities are located in the "utilities" folder, form and function are up to the end user.
GUI design elements are in the "GUI" folder, there are a series of custom LCARS widgets that can be utilized to develop custom displays, see the Kivy Framework for information on use.

## Programs
Programs must inherit from the Program class available in the app folder

Configuration files must be named the same as the Program class with
an .ini extension and stored in the 'config' folder

Basic variables should be created, otherwise defaults will be used, for example:
```
    self.description('This is an awesome program.')
    self.period = 0.25  # Seconds
    self.label = "My Program"  # Used in the GUI program screen
    self.button_text = "Program"  # Used in the GUI 
```

To properly populate the database, program settings should be declared in
program_init() as a dictionary.
For example:
```
    self.settings = {'Set1': 23, 'Set2': 'test', 'Set3': True}
```

The functional elements used the the Program class are:
```
    def program_init(self):
        """ Called once when the program is initialized """
        pass

    def program_start(self):
        """ Called when the program starts or restarts after a stop """
        pass

    def program_run(self):
        """ Called every program operation cycle """
        pass

    def program_pause(self):
        """ Called when the program goes into a paused state """
        pass

    def program_stop(self):
        """ Called when the program is stopped """
        pass

    def program_fail(self):
        """ Called then the program fails """
        pass

    def program_halt(self):
        """ Called before the program in deleted from memory """
        pass
```
User functions not required by the main engine should start with an underscore (_).

        
## LCARS GUI
The GUI is based on Star Trek LCARS. GUI design elements are in the "GUI" folder, there are a series of custom LCARS widgets that can be utilized to develop custom displays, see the Kivy Framework for information on use.

Main Display
![main display](https://github.com/mxguy31/LCARS_LogicPi/blob/main/screenshot/MainDisplay.png)

Program Screen
![Program Screen](https://github.com/mxguy31/LCARS_LogicPi/blob/main/screenshot/ProgramScreen.png)

System Trends
![System Trends](https://github.com/mxguy31/LCARS_LogicPi/blob/main/screenshot/SystemTrends.png)

Alarm Screen
![Alarm Screen](https://github.com/mxguy31/LCARS_LogicPi/blob/main/screenshot/AlarmScreen.png)


