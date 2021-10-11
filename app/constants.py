import json
import logging

from pathlib import Path


class CONST:
    # Directory Structure
    ROOT_FOLDER = Path(__file__).resolve().parent.parent
    APP_DIR = ROOT_FOLDER.joinpath('app')
    CONFIG_DIR = ROOT_FOLDER.joinpath('config')
    DRIVER_DIR = ROOT_FOLDER.joinpath('drivers')
    GUI_DIR = ROOT_FOLDER.joinpath('gui')
    LOGGING_DIR = ROOT_FOLDER.joinpath('log')
    PROGRAM_DIR = ROOT_FOLDER.joinpath('programs')

    DB_FOLDER = APP_DIR

    # File Names
    SYSLOG_FILE = 'syslog.log'
    DB_FILE = 'logicpi.db'
    ALARM_INI = CONFIG_DIR.joinpath('alarms.ini')

    # System Logging
    LOG_ON = True
    LOG_LEVEL = 'INFO'
    LOG_ROTATE = False  # Rotate the log if size exceeds max bytes
    LOG_MAX_SIZE = 100000  # 100KB
    LOG_BACKUPS = 5  # Number of old logs to keep
    LOG_FILE = LOGGING_DIR.joinpath(SYSLOG_FILE)
    LOG_FORMAT = logging.Formatter('%(asctime)s - '
                                   '%(name)-12s '
                                   '%(levelname)-8s '
                                   '%(message)s',
                                   '%Y-%m-%d %H:%M:%S')

    # Misc
    # How many stalled process cycles before triggering alarm
    PROCESS_STALL_CYCLES = 10
    # How many seconds between process checks
    PROCESS_CHECK_TIME = 5
    # How many seconds to allow processes to start running
    PROCESS_CHECK_DELAY = 5

    DB_CREATE_STRS = (
        """CREATE TABLE IF NOT EXISTS Data (
            id INTEGER PRIMARY KEY,
            Datapoint TEXT UNIQUE NOT NULL,
            Value TEXT NOT NULL,
            Type TEXT NOT NULL,
            Override TEXT,
            Calibration TEXT)
        """,
        """CREATE TABLE IF NOT EXISTS DataLog (
            id INTEGER PRIMARY KEY,
            Data_ID INTEGER NOT NULL
            REFERENCES Data(id),
            Value TEXT NOT NULL,
            Timestamp REAL NOT NULL DEFAULT
            ((julianday('now') - 2440587.5)*86400.0))
        """,
        """CREATE TRIGGER IF NOT EXISTS Data_Update
            AFTER UPDATE ON Data
            WHEN old.Value <> new.Value
            BEGIN
                INSERT INTO DataLog(Data_ID,
                                    Value)
                VALUES (new.id,
                        new.Value);
            END
        """,
        """CREATE TRIGGER IF NOT EXISTS Data_Insert
            AFTER INSERT ON Data
            BEGIN
                INSERT INTO DataLog(Data_ID,
                                    Value)
                VALUES (new.id,
                        new.Value);
            END
        """,
        """CREATE TRIGGER IF NOT EXISTS DataLog_Timelimit
            AFTER INSERT ON DataLog
            BEGIN
                DELETE FROM DataLog
                WHERE
                Timestamp < ((julianday('now') - 2440601.5)*86400.0);
            END
        """,
        """CREATE TABLE IF NOT EXISTS Programs (
            id INTEGER PRIMARY KEY,
            Name TEXT UNIQUE NOT NULL,
            Mode TEXT,
            Status TEXT,
            Period REAL,
            Last_Run REAL,
            Description TEXT,
            Label Text,
            ButtonText Text)
        """,
        """CREATE TABLE IF NOT EXISTS Settings (
            id INTEGER PRIMARY KEY,
            Owner TEXT NOT NULL,
            Setting TEXT NOT NULL,
            Value TEXT,
            Type TEXT NOT NULL,
            UNIQUE(Owner, Setting))
        """,
        """CREATE TABLE IF NOT EXISTS SystemLog (
            id INTEGER PRIMARY KEY,
            Timestamp REAL NOT NULL DEFAULT
                ((julianday('now') - 2440587.5)*86400.0),
            Name TEXT,
            Level TEXT,
            Message TEXT,
            Module TEXT,
            Function TEXT,
            Line INTEGER)
        """,
        """CREATE TABLE IF NOT EXISTS Alarms (
            id INTEGER PRIMARY KEY,
            Name TEXT NOT NULL UNIQUE,
            Description TEXT,
            Enabled TEXT,
            LastEvent REAL,
            Status TEXT,
            Datapoint TEXT,
            Operation TEXT,
            Value TEXT,
            ValType TEXT,
            Delay TEXT,
            Priority INTEGER)
        """,
        """CREATE TABLE IF NOT EXISTS AlarmsLog (
            id INTEGER PRIMARY KEY,
            Alarm_ID INTEGER NOT NULL REFERENCES Alarmss(id),
            Status TEXT NOT NULL,
            Timestamp REAL NOT NULL DEFAULT
                ((julianday('now') - 2440587.5)*86400.0))
        """,
        """CREATE TRIGGER IF NOT EXISTS Alarms_insert
            AFTER INSERT ON Alarms
            BEGIN
                INSERT INTO AlarmsLog(Alarm_ID,
                                        Status)
                VALUES (new.id,
                        new.Status);
            END
        """,
        """CREATE TRIGGER IF NOT EXISTS Alarms_update
            AFTER UPDATE ON Alarms
            WHEN old.Status <> new.Status
            BEGIN
                INSERT INTO AlarmsLog(Alarm_ID,
                                        Status)
                VALUES (new.id,
                        new.Status);
            END
        """
    )
