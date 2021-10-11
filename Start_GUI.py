import signal
from kivy import Config
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '800')
from gui.lcars import LCARSApp

if __name__ == '__main__':
    gui = LCARSApp()
    signal.signal(signal.SIGTERM, gui.stop)
    gui.run()
