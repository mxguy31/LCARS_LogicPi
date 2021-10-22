import signal
from kivy import Config
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '800')
from gui.lcars import LCARSApp
from app.constants import CONST

from logging import FileHandler
from logging.handlers import RotatingFileHandler
from app.syslog import mySQLHandler
from kivy.logger import Logger

if __name__ == '__main__':

    if not CONST.LOG_ROTATE:
        file_handler = FileHandler(CONST.LOG_FILE)
    else:
        file_handler = RotatingFileHandler(CONST.LOG_FILE,
                                            'a',
                                            CONST.LOG_MAX_SIZE,
                                            CONST.LOG_BACKUPS)
    file_handler.setFormatter(CONST.LOG_FORMAT)
    sql_handler = mySQLHandler()
    Logger.addHandler(file_handler)
    Logger.addHandler(sql_handler)

    gui = LCARSApp()
    signal.signal(signal.SIGTERM, gui.stop)
    gui.run()
