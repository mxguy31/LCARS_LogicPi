# https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
# https://medium.com/@jonathonbao/python3-logging-with-multiprocessing-f51f460b8778

import logging
import time
import sqlite3

# pylint: disable=import-error
from logging.handlers import RotatingFileHandler
from logging.handlers import QueueHandler
from logging import FileHandler

from app.constants import CONST


'''
DEBUG       Detailed information, typically of interest only when
            diagnosing problems.
INFO        Confirmation that things are working as expected.
WARNING     An indication that something unexpected happened, or
            indicative of some problem in the near future
            (e.g. ‘disk space low’). The software is still working
            as expected.
ERROR       Due to a more serious problem, the software has not
            been able to perform some function.
CRITICAL    A serious error, indicating that the program itself
            may be unable to continue running.
'''


def get_local_log(name):
    logger = logging.getLogger(name)
    _logging_config()
    return logger


def log_listener(log_queue):
    _logging_config()
    flag = True
    while flag:
        while not log_queue.empty():
            record = log_queue.get()
            if record is None:
                flag = False
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)  # No level or filter logic applied
        time.sleep(1)


def get_worker_log(name, log_queue):
    logger = logging.getLogger(name)
    handler = QueueHandler(log_queue)
    logger.addHandler(handler)
    logger.setLevel(CONST.LOG_LEVEL)

    # Don't propogate logs up the ladder, causes multiple entries
    logger.propagate = False

    return logger


def _logging_config():
    root = logging.getLogger()
    if not root.hasHandlers():
        if not CONST.LOG_ROTATE:
            file_handler = FileHandler(CONST.LOG_FILE)
        else:
            file_handler = RotatingFileHandler(CONST.LOG_FILE,
                                               'a',
                                               CONST.LOG_MAX_SIZE,
                                               CONST.LOG_BACKUPS)
        file_handler.setFormatter(CONST.LOG_FORMAT)
        sql_handler = mySQLHandler()
        root.addHandler(file_handler)
        root.addHandler(sql_handler)
        root.setLevel(CONST.LOG_LEVEL)


class mySQLHandler(logging.Handler):
    """
    Logging handler for MySQL.

    Significant inspiration from
    https://github.com/onemoretime/mySQLHandler
    """

    sql = ("""INSERT INTO SystemLog
                (Timestamp,
                Name,
                Level,
                Message,
                Module,
                Function,
                Line)
           VALUES
                (?, ?, ?, ?, ?, ?, ?)""")

    def __init__(self, db_location=CONST.DB_FOLDER):
        """
        Constructor
        @param db_location: Location of SQLite3 Database
        @return: mySQLHandler
        """

        logging.Handler.__init__(self)
        self._dbfile = db_location.joinpath(CONST.DB_FILE)

    def emit(self, record):
        """
        Connect to DB, execute SQL Request, disconnect from DB
        @param record:
        @return:
        """
        # Use default formatting:
        self.format(record)

        # Ensure correct exception formatting
        if record.exc_info:
            record.exc_text = logging._defaultFormatter.formatException(
                                record.exc_info)
        else:
            record.exc_text = ""

        # Replace single quotes in messages
        if isinstance(record.__dict__['msg'], str):
            record.__dict__['msg'] = record.__dict__['msg'].replace("'", "''")

        vals = list()
        for item in ('created', 'name', 'levelname',
                     'msg', 'module', 'funcName',
                     'lineno'):
            vals.append(record.__dict__[item])

        # Insert log record:
        try:
            connection = sqlite3.connect(str(self._dbfile))
        except Exception as e:
            return
        try:
            connection.execute(self.sql, vals)
            connection.commit()

        except sqlite3.Error as e:
            connection.rollback()

        finally:
            if connection:
                connection.close()


'''
# Example of how to use the logger
# Imports used by the examples
import multiprocessing
from random import random, randint


def worker_process(log_queue):  # Important to pass the log_queue
    log = get_worker_log(log_queue, 'Bob')
    for i in range(3):
        sleep(random())
        log.info(f'Logging a number {i}')
        log.debug('Debug Message')


# Example of how to set up the logger in the main process
def main():

    _log = get_local_log('Poop')

    _log.info('This is a test message')
    # Must have this to set up the logger
    log_queue = multiprocessing.Queue(-1)
    listener = multiprocessing.Process(
        target=log_listener, args=(log_queue,))
    listener.start()

# Example starting processes

    workers = []
    for i in range(3):
        worker = multiprocessing.Process(target=worker_process,
                                         args=(log_queue,))
        workers.append(worker)
        worker.start()
    sleep(3)


# Absolutley last thing to do after all workers are stopped
    while not log_queue.empty():
        sleep(1)
    log_queue.put_nowait(None)
    for w in workers:
        w.join()


if __name__ == '__main__':
    main()
'''
