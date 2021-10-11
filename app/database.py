# https://docs.python.org/3/library/sqlite3.html
# https://www.sqlite.org/index.html

# The SQL standard says that strings must use 'single quotes',
# and identifiers (such as table and column names), when quoted,
# must use "double quotes".

import time

import sqlite3
from app.constants import CONST
from app.syslog import get_local_log


class OP_MODE:
    RUN = 'RUN'
    PAUSE = 'PAUSE'
    STOP = 'STOP'
    HALT = 'HALT'


class OP_STATE:
    RUN = 'RUN'
    PAUSE = 'PAUSE'
    STOP = 'STOP'
    FAIL = 'FAIL'


class TYPES:
    STR = 'str'
    FLOAT = 'float'
    BOOL = 'bool'


class BasicDatabase:
    """Don't use this class directly, it is intended to be used by the
    classes below.
    """
    OP_MODES = [OP_MODE.RUN, OP_MODE.PAUSE, OP_MODE.STOP, OP_MODE.HALT]
    OP_STATES = [OP_STATE.RUN, OP_STATE.PAUSE, OP_STATE.STOP, OP_STATE.FAIL]
    TYPES = [TYPES.STR, TYPES.FLOAT, TYPES.BOOL]

    def __init__(self, location=CONST.DB_FOLDER):
        self._log = get_local_log('Database')
        self._dbfile = location.joinpath(CONST.DB_FILE)
        self.connection = None
        if not self._dbfile.exists():
            self._log.info(f'Creating new database with sqlite version: '
                           f'{sqlite3.sqlite_version}')
            for statement in CONST.DB_CREATE_STRS:
                self.sql_write(statement)

    def _get_connection(self):
        """Create and return a simple connection"""
        try:
            if not (self.connection):
                self.connection = sqlite3.connect(str(self._dbfile))
                self.connection.execute('PRAGMA JOURNAL_MODE=WAL')
                self.connection.execute('PRAGMA SYNCHRONOUS=NORMAL')

        except Exception as e:
            self._log.error(f'Could not establish database connection. {e}')
            raise

        return self.connection

    def typecast(self, value, type):
        """will cast the value to the type requested. Returns the cast value,
        or returns None if the value can not be cast correctly.

        Args:
            value (str): the string representation of the value
            type (type): the type to cast the value to
        """
        try:
            if type == 'bool':
                if value == '1':
                    return True
                else:
                    return False
            elif type == 'float':
                return float(value)
            else:
                return value
        except ValueError:
            return None

    def typeset(self, value):
        d_type = str(type(value).__name__)
        if d_type == 'int':
            d_type = 'float'
        return d_type

    def sql_write(self, sql, data=None):
        """Multiple row write function with error handling

        Args:
            sql (str): SQL scentence to be executed
            data (list of tuple, optional): Supporting data for SQL scentence.
            Defaults to None.

        Returns:
            Number of affected rows, False if error
        """
        connection = self._get_connection()
        cursor = connection.cursor()

        try:
            if data is None:
                cursor.execute(sql)
            else:
                cursor.executemany(sql, data)
            connection.commit()

        except sqlite3.Error as e:
            self._log.error(f'Database error, sql: {sql} data: {data}. {e}')
            connection.rollback()
            return False

        finally:
            cursor.close()

        return cursor.rowcount

    def sql_read(self, sql, data=None):
        """Basic sql read function with error handling

        Args:
            sql (str): SQL scentance to be executed
            data (tuple, single datapoint, optional): Any supporting
            data required.
            Defaults to None.

        Returns:
            Tuple containing the row(s) returned from the databse.
            None is returned if no data was found.
            False is returned if an error ocurred
        """
        connection = self._get_connection()
        cursor = connection.cursor()
        rows = None
        try:
            if data is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, data)
            rows = cursor.fetchall()

        except sqlite3.Error as e:
            self._log.info(f'Database error, sql: {sql} data: {data}. {e}')
            return False

        finally:
            cursor.close()

        if len(rows) == 0:
            return None
        return rows

    def close_connection(self):
        if self.connection:
            self.connection.close()


###############################################################################
# Logic Engine Database Class
###############################################################################
class AppDatabase(BasicDatabase):
    def __init__(self):
        super().__init__()

# *********** Program Functions ************

    def program_write(self, name, mode=None, status=None, period=None,
                      last_run=None, description=None, label=None,
                      button_text=None):
        """Sets an attribute of a program

        Args:
            name (str): Name of the program to modify / create.
            mode (str, optional): RUN,PAUSE,STOP,HALT.
            status (str, optional): RUN,PAUSE,STOP,FAIL.
            period (float, optional): Program cycle period.
            last_run (datetime, optional): Last time the program ran.
            description (str, optional): Brief description.
            label (str, optional): Human readable label for GUI displays
            buttontext (Str, optional): Specific text for GUI Buttons

        Returns:
            bool: True - Update successfull, False - Update unsuccessfull
        """

        sql = ("""INSERT INTO Programs
                        (Name,
                        Mode,
                        Status,
                        Period,
                        Last_Run,
                        Description,
                        Label,
                        ButtonText)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(Name)
                    DO UPDATE SET
                        Mode = COALESCE(excluded.Mode, Mode),
                        Status = COALESCE(excluded.Status, Status),
                        Period = COALESCE(excluded.Period, Period),
                        Last_Run = COALESCE(excluded.Last_Run, Last_Run),
                        Description = COALESCE(excluded.Description,
                                                Description),
                        Label = COALESCE(excluded.Label, Label),
                        ButtonText = COALESCE(excluded.ButtonText,
                                                ButtonText)
                    """)

        if period:
            try:  # Ensure period is a float value
                period = float(period)
            except ValueError:
                return False

        _params = [(name, mode, status, period, last_run,
                    description, label, button_text)]

        ret_val = self.sql_write(sql, _params)
        if ret_val is False:
            self._log.info(f'Failed to update program ({name}), ({label}) '
                           f'({description}) ({mode}) ({status}) '
                           f'({last_run}) ({period}) ({name})')
            return False
        elif ret_val == 0:
            return False
        else:
            return True

    def program_read(self, name, attribute=None):
        """Gets an attribute from a program

        Args:
            name (str): Name of the program
            attribute (tuple, optional): Specific attributes to retrieve,
            None returns all. Defaults to None.
            Possible Attributes: Name, Mode, Status, Period,
            Description, Last_Run, Label, ButtonText

        Returns:
            dict / None: Program attributes, None if no data found
        """

        sql = ('''SELECT * FROM Programs WHERE Name=?''')
        atr_dict = {'Name': 1,
                    'Mode': 2,
                    'Status': 3,
                    'Period': 4,
                    'Last_Run': 5,
                    'Description': 6,
                    'Label': 7,
                    'ButtonText': 8}

        data = self.sql_read(sql, (name,))
        if not data:
            return None
        else:
            data = data[0]

        ret_dict = dict()
        for att, id in atr_dict.items():
            if attribute is None:
                ret_dict[att] = data[id]
            elif att in attribute:
                ret_dict[att] = data[id]

        return ret_dict

    def program_list(self):
        """Returns a list of available programs

        Returns:
            [list]: A list of programs
        """

        sql = '''SELECT Name FROM Programs'''
        data = self.sql_read(sql)

        if not data:
            return []
        else:
            return [item[0] for item in data]

# ************** Data Functions ****************

    def data_write(self, datapoint, value, override=None):
        """Writes a datapoint to the database

        Args:
            datapoint (str): Name of the datapoint to write
            value (str, float, bool): Data to be written
            override (str, optional): Name of override owner if the
                                      datapoint is overriden.
                                      Defaults to None.
        Returns:
            [bool]: True - Datapoint record was written / updated,
                    False - Datapoint record was not written / updated
        """

        if datapoint is None:
            return

        if ' ' in datapoint:
            self._log.warning(f'Can not write datapoint {datapoint}, '
                              'spaces are not allowed')
            return False

        if value is None:
            self._log.debug(f'Write to datapoint {datapoint} was given a '
                            f'value of None.')
            return False

        sql = ('''INSERT INTO Data
                      (Datapoint, Value, Type)
                  VALUES
                      (?, ?, ?)
                  ON CONFLICT(Datapoint)
                  DO UPDATE SET
                      Value = excluded.Value
                  WHERE
                      (Override=? OR Override IS NULL)
                      AND Type=excluded.Type''')

        d_type = self.typeset(value)
        if d_type not in self.TYPES:
            self._log.warning(f'Incorrect data type ({d_type}) used '
                              f'when updating data value ({datapoint}).')
            return False

        ret_val = self.sql_write(sql, [(datapoint, value, d_type, override)])

        if ret_val is False:
            self._log.warning(f'Failed to write datapoint ({datapoint}).')
            return False
        elif ret_val == 0:
            return False
        else:
            return True

    def data_read(self, datapoint=None):
        """Reads a single, tuple, or all datapoints from the database

        Args:
            datapoint (str, tuple): Name of the datapoint(s)
                                    Defaults to None (all datapoints)

        Returns:
            [dict]: {Datapoint1: Value1, Datapoint2: Value2}
        """
        sql = ('''SELECT Datapoint,
                         CASE
                            WHEN Type='float' THEN
                                Value + IFNULL(Calibration, 0)
                            ELSE
                                Value
                            END,
                         Type
                  FROM Data''')

        if datapoint is not None:
            if type(datapoint) is not tuple:
                if type(datapoint) is list:
                    datapoint = tuple(datapoint)
                else:
                    datapoint = (datapoint,)

            sql = (sql + " WHERE Datapoint IN (" +
                   ",".join("?"*len(datapoint)) + ")")

        data = self.sql_read(sql, datapoint)
        if data is None:
            return None
        elif data is False:
            self._log.warning(f'Error reading datapoint(s): {datapoint}')
            return False

        r_dict = dict()
        for row in data:
            r_dict[row[0]] = self.typecast(row[1], row[2])
        return r_dict

    def data_search(self, search):
        """Returns datapoints where the name contains the search string

        Args:
            search (str): String to search for in the datapoint name.
        """
        sql = ('''SELECT Datapoint,
                         CASE
                            WHEN Type='float' THEN
                                Value + IFNULL(Calibration, 0)
                            ELSE
                                Value
                            END,
                         Type
                  FROM Data
                  WHERE Datapoint LIKE ?''')

        search = ('%' + str(search) + '%',)

        data = self.sql_read(sql, search)
        if data is None:
            return None
        elif data is False:
            self._log.warning(f'Error searching for datapoints containing: '
                              f'{search}')
            return False

        r_dict = dict()
        for row in data:
            r_dict[row[0]] = self.typecast(row[1], row[2])
        return r_dict

# ************ Settings Functions ************

    def setting_write(self, owner, setting, value):
        """Writes a setting to the database

        Args:
            owner (str): Name of the owener of the setting
            setting (str): Name of the setting
            value (str, float, bool): The setting value

        Returns:
            bool: True - Setting written
                  False - Setting not written
        """

        sql = ('''INSERT INTO Settings
                      (Owner, Setting, Value, Type)
                  VALUES
                      (?, ?, ?, ?)
                  ON CONFLICT(Owner, Setting)
                  DO UPDATE SET
                      Value = excluded.Value
                  WHERE
                      Owner=excluded.Owner AND
                      Setting=excluded.Setting AND
                      Type=excluded.Type''')

        d_type = self.typeset(value)
        if d_type not in self.TYPES:
            self._log.warning(f'Incorrect type ({d_type}) used '
                              f'when updating setting value '
                              f'({owner}:{setting}).')
            return False

        ret_val = self.sql_write(sql, [(owner, setting, value, d_type)])

        if ret_val is False:
            self._log.warning(f'Failed to write setting ({owner}:{setting}).')
            return False
        elif ret_val == 0:
            return False
        else:
            return True

    def setting_read_single(self, owner, setting):
        """Returns the requested setting from the database

        Args:
            owner (str): Setting Owner
            setting (str): Setting
        """
        sql = ("""
                SELECT
                    Value,
                    Type
                FROM
                    Settings
                WHERE
                    Owner = :owner
                    AND
                    Setting = :setting
               """)

        data = self.sql_read(sql, {'owner': owner, 'setting': setting})

        if data is None:
            return None
        elif data is False:
            self._log.warning(f'Error reading setting(s): {owner} / {setting}')
            return None

        data = data[0]
        return self.typecast(data[0], data[1])

    def setting_read_multiple(self, owner=None, settings=None):
        """Returns requested settings from the database

        Args:
            owner (string): name of the setting owner
            settings (tuple, optional): tuple of settings to retrive,
            If no tuple is provided all settings owned by that owner
            are returned. Defaults to None.

        Returns:
            [dict]: {Setting1: Value1, Setting2: Value2,...}
            None: if no data is found
        """
        sql = ("""
                SELECT
                    Owner,
                    Setting,
                    Value,
                    Type
                FROM
                    Settings
                WHERE
                    CASE WHEN :owner IS NOT NULL
                        THEN Owner = :owner
                        ELSE 1
                    END
                """)

        if settings is not None:
            if not isinstance(settings, tuple):
                if isinstance(settings, list):
                    settings = tuple(settings)
                else:
                    settings = (settings,)

        else:
            settings = ()

        data = self.sql_read(sql, {'owner': owner})

        if data is None:
            return None
        elif data is False:
            self._log.warning(f'Error reading setting(s): {settings}')
            return False

        r_dict = dict()
        for row in data:
            if len(settings) > 0 and row[1] not in settings:
                continue
            if row[0] not in r_dict:
                r_dict[row[0]] = dict()
            r_dict[row[0]][row[1]] = self.typecast(row[2], row[3])
        return r_dict


###############################################################################
# Alarm Logic Specific Database Class
###############################################################################
class AlarmDatabase(BasicDatabase):
    def __init__(self):
        super().__init__()

    def has_alarm(self, alarm_name):
        """Checks to see if an alarm exists

        Args:
            alarm (str): The name of the alarm

        Returns:
            bool: True - The setting exists
                  False - The setting does not exist
        """
        sql = ('''SELECT id FROM Alarms WHERE Name=?''')

        if not self.sql_read(sql, alarm_name):
            return False
        else:
            return True

    def write_alarm(self, alarm_name, description=None, datapoint=None,
                    operation=None, value=None, delay=None, priority=None,
                    enabled=None, status=None):
        """Creates an alarm in the database

        Args:
            alarm_name (str): Name of the alarm
            description (str): A brief description
            datapoint (str): Related datapoint
            operation (str): The related logic operator
            value (str): The trigger value
            delay (int): alarm delay
            priority (int): 1-high, 2-med, 3-low
            enabled (bool): defaults to True
            status (str): Alarm status ('CLR', 'ACT', 'ACK', 'SIL')

        Returns:
            bool: True - Alarm written
                  False - Alarm not written
        """
        sql = ('''INSERT INTO Alarms
                    (Name,
                    Description,
                    Enabled,
                    Datapoint,
                    Operation,
                    Value,
                    ValType,
                    Delay,
                    Priority,
                    Status)
                VALUES(?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(Name)
                DO UPDATE SET
                    Description=coalesce(excluded.Description, Description),
                    Enabled=coalesce(excluded.Enabled, Enabled),
                    Datapoint=coalesce(excluded.Datapoint, Datapoint),
                    Operation=coalesce(excluded.Operation, Operation),
                    Value=coalesce(excluded.Value, Value),
                    Delay=coalesce(excluded.Delay, Delay),
                    Priority=coalesce(excluded.Priority, Priority),
                    Status=coalesce(excluded.Status, Status)
                ''')

        if operation not in ('eq', 'ne', 'gt', 'ge', 'lt', 'le', None):
            return False

        d_type = None
        if value is not None:
            d_type = self.typeset(value)
            if d_type not in self.TYPES:
                self._log.warning(f'Incorrect type ({d_type}) used to update '
                                  f'alarm value ({alarm_name}:{value}).')
                return False
            elif d_type == 'str':
                if operation not in ('eq', 'nt'):
                    return False

        if not self.sql_write(sql, [(alarm_name,
                                     description,
                                     enabled,
                                     datapoint,
                                     operation,
                                     value,
                                     d_type,
                                     delay,
                                     priority,
                                     status)]):
            self._log.warning(f'Failure to write alarm ({alarm_name})')
            return False
        else:
            return True

    def read_alarm(self, alarm_names=None, parameters=None):
        """Returns requested alarm data from the database

        Args:
            alarm_names (tuple, optional): tuple of alarms to retrieve,
            if none provided all alarms are returned.
            Defaults to None.
            parameters (tuple, optional): tuple of parameters to retrive,
            If no tuple is provided all paramters for that alarm are retrieved.
            Defaults to None.

        Returns:
            dict: A tuple containing the alarm parameters requested.
            None: if no data is found
        """
        if parameters is None:
            params = ('Name, Description, Enabled, LastEvent, Status, '
                      'Datapoint, Operation, Value, ValType, Delay, '
                      'Count, Priority')
        else:
            params = ''
            if 'Name' not in parameters:
                params = 'Name, '

            if 'Value' in parameters and 'ValType' not in parameters:
                params += 'ValType, ' + ', '.join(parameters)
            else:
                params += ', '.join(parameters)

        if alarm_names is None:
            sql = (f'''SELECT {params} FROM Alarms''')
        else:
            names = ', '.join('?' * len(alarm_names))
            sql = (f'''SELECT {params} FROM Alarms WHERE Name in ({names})''')

        data = self.sql_read(sql, alarm_names)

        if not data:
            return None

        return_dict = dict()
        for row in data:
            row_dict = dict()
            pnum = 0
            for param in params.split(', '):
                if param == 'Name':
                    rowname = row[pnum]
                elif param == 'Enabled':
                    row_dict[param] = bool(row[pnum])
                elif param == 'Value':
                    rowval = row[pnum]
                elif param == 'ValType':
                    rowvt = row[pnum]
                else:
                    row_dict[param] = row[pnum]
                pnum += 1

            if rowvt == 'bool':
                if rowval == '0':
                    row_dict['Value'] = False
                else:
                    row_dict['Value'] = True
            elif rowvt == 'float':
                row_dict['Value'] = float(rowval)
            else:
                row_dict['Value'] = rowval

            return_dict[rowname] = row_dict

        return return_dict

    def activate_alarms(self, names):
        """Sets the alarm status to 'ACTIVE'
        Args:
            name (tuple, str): The name(s) of the affected alarm(s)
        """
        if names is None:
            return False
        else:
            if type(names) is not tuple:
                names = (names,)

            a_str = ', '.join('"{0}"'.format(i) for i in names)

        sql = (f'''UPDATE Alarms SET
               Status="ACT", LastEvent=((julianday('now') - 2440587.5)*86400.0)
               WHERE Name IN ({a_str})''')
        if self.sql_write(sql) is False:
            self._log.warning(f'Failure to activate alarm(s) ({names}).')
            return False
        else:
            return True

    def acknowledge_alarms(self):
        """Sets any alarms not in the CLEAR state to ACKNOWLEDGE.
        """
        sql = '''UPDATE Alarms SET Status="ACK"
                 WHERE NOT instr(Status, "CLR")'''
        if self.sql_write(sql) is False:
            self._log.warning(f'Failure to acknowledge alarm(s).')
            return False
        else:
            return True

    def silence_alarms(self):
        """Silences any active alarms.
        """
        sql = '''UPDATE Alarms SET Status="SIL" WHERE Status="ACT"'''
        if self.sql_write(sql) is False:
            self._log.warning(f'Failure to silence alarm(s).')
            return False
        else:
            return True

    def clear_alarms(self):
        """Clears any acknowledged alarms.
        """
        sql = '''UPDATE Alarms SET Status="CLR" WHERE Status="ACLR"'''
        if self.sql_write(sql) is False:
            self._log.warning(f'Failure to clear alarm(s).')
            return False
        else:
            return True

    def get_alarm_history(self, human_time=False):
        """Return the entries in the alarm history log

        Args:
            length (int, optional): how many record to return, None = all
        Returns:
            list of dict: A list of dicts, each dict is one entry.
        """
        sql = ("""SELECT
                      AlarmsLog.Timestamp,
                      AlarmsLog.Alarm_ID,
                      Alarms.Name,
                      Alarms.Description,
                      AlarmsLog.Status,
                      Alarms.Priority
                  FROM
                      Alarms,
                      AlarmsLog
                  WHERE
                      AlarmsLog.Alarm_ID=Alarms.ID
                  ORDER BY
                      AlarmsLog.Timestamp DESC""")

        entries = self.sql_read(sql)

        if not entries:
            return None

        r_list = list()
        for entry in entries:
            if human_time:
                t = time.localtime(entry[0])
                msec = str(entry[0]).split('.')[1][:3]
                alarm_time = time.strftime("%Y-%m-%d %H:%M:%S", t) + '.' + msec
            else:
                alarm_time = str(entry[0])
            r_list.append({'alarm_time': alarm_time,
                           'alarm_id': str(entry[1]),
                           'alarm_name': str(entry[2]),
                           'alarm_description': str(entry[3]),
                           'alarm_status': str(entry[4]),
                           'alarm_priority': str(entry[5])})
        return r_list

    def get_alarms(self, human_time=False):
        """Returns any alarms that are not in the CLR state

        Args:
            length (int, optional): how many record to return, None = all

        Returns:
            list of dict: A list of dicts, each dict is one entry.
        """
        pass
        sql = ("""SELECT id,
                         LastEvent,
                         Name,
                         Status,
                         Description,
                         Priority
                  FROM Alarms WHERE Status!="CLR"
                  ORDER BY LastEvent DESC""")

        entries = self.sql_read(sql)

        if not entries:
            return None

        r_list = list()
        for entry in entries:
            if human_time:
                t = time.localtime(entry[1])
                msec = str(entry[1]).split('.')[1][:3]
                alarm_time = time.strftime("%Y-%m-%d %H:%M:%S", t) + '.' + msec
            else:
                alarm_time = str(entry[1])
            r_list.append({'alarm_id': str(entry[0]),
                           'alarm_time': alarm_time,
                           'alarm_name': str(entry[2]),
                           'alarm_status': str(entry[3]),
                           'alarm_description': str(entry[4]),
                           'alarm_priority': str(entry[5])})
        return r_list

    def is_act_alarm(self):
        """Returns alarm level if an alarm is in the active state.

        Returns:
            int: Returns highest alarm level of any alarm in the active state
        """
        sql = ("""SELECT MIN(Priority) FROM Alarms WHERE Status='ACT'""")
        level = self.sql_read(sql)[0][0]
        if not level:
            return 0
        else:
            if level in (1, 2, 3):
                return level
            else:
                return 3

    def is_clr_alarm(self):
        """Returns True if an alarm has cleared.

        Returns:
            Bool: Return True if an alarm has cleared
        """
        sql = ("""SELECT * FROM Alarms WHERE Status='ACLR'""")
        if not self.sql_read(sql):
            return False
        else:
            return True

    def get_inactive_alarms(self):
        """Returns All alarms that are not in the active state (ACT, SIL).
        """
        sql = ('''SELECT Name,
                         Datapoint,
                         Operation,
                         Value,
                         ValType,
                         Delay,
                         Status,
                         Description
                  FROM Alarms WHERE Status NOT IN ('ACT', 'SIL') AND Enabled
               ''')
        return self.sql_read(sql)


###############################################################################
# GUI Specific Database Class
###############################################################################
class GUIDatabase(AppDatabase):
    def __init__(self):
        super().__init__()

# *********** Program Functions ************

    def program_write(self, name, mode=None, period=None,
                      description=None, label=None, button_text=None):
        """Sets an attribute of a program

        Args:
            name (str): Name of the program to modify
            mode (str, optional): RUN,PAUSE,STOP,HALT.
            period (float, optional): Program cycle period.
            description (str, optional): Brief description.
            label (str, optional): Human readable label for GUI displays
            buttontext (Str, optional): Specific text for GUI Buttons

        Returns:
            bool: True - Update successfull, False - Update unsuccessfull
        """

        sql = ("""UPDATE Programs SET
                  Mode = COALESCE(?, Mode),
                  Period = COALESCE(?, Period),
                  Description = COALESCE(?, Description),
                  Label = COALESCE(?, Label),
                  ButtonText = COALESCE(?, ButtonText)
                  WHERE Name=?
                """)

        if period:
            try:  # Ensure period is a float value
                period = float(period)
            except ValueError:
                return False

        _params = [(mode, period, description, label, button_text, name)]

        ret_val = self.sql_write(sql, _params)
        if ret_val is False:
            self._log.info(f'Failed to update program ({name}), ({label}) '
                           f'({description}) ({mode}) '
                           f'({period}) ({name})')
            return False
        elif ret_val == 0:
            return False
        else:
            return True

# *********** Data Functions *************

    def data_exists(self, datapoint):
        if self.data_read(datapoint):
            return True
        else:
            return False

    def data_read_single(self, datapoint):
        t_val = self.data_read(datapoint)
        if not t_val:
            return None
        else:
            return t_val[datapoint]

    def data_get_locks(self):
        """Returns holders of any data locks

        Returns:
            Dict: dict of d_point:lock owner
        """
        sql = ('''SELECT Datapoint, Override FROM Data WHERE Override IS NOT NULL''')

        data = self.sql_read(sql)
        if not data:
            return {}
        else:
            r_dict = dict()
            for row in data:
                r_dict[row[0]] = row[1]
            return r_dict

    def data_is_locked(self, datapoint):
        """Returns the holder (if any) of a data lock

        Args:
            datapoint (str): The datapoint to check

        Returns:
            str: The name of the datapoint lock holder
        """
        sql = ('''SELECT Override FROM Data WHERE Datapoint=?''')

        current = self.sql_read(sql, (datapoint,))
        if current is False:
            self._log.warning(f'Datapoint {datapoint} cold not be read.')
            return False
        elif current is None:
            return None
        else:
            return current[0][0]

    def data_lock(self, datapoint, owner):
        """Lock a datapoint to prevent updating of the selected datapoint.

        Args:
            datapoint (str): Name of the datapoint
            owner (str): name of the lock owner

        Returns:
            bool: True - Lock set
                  False - Lock not set (or already locked)
        """
        sql = ('''UPDATE Data SET Override=?
                  WHERE Datapoint=? AND (Override=? OR Override IS NULL)''')

        override = str(owner)

        r_val = self.sql_write(sql, [(override, datapoint, override)])

        if r_val is False:
            self._log.warning(f'Failure to override datapoint ({datapoint}) '
                              f'by ({override}).')
            return False
        elif r_val == 0:
            self._log.info(f'Attempt to override datapoint ({datapoint}) '
                           f'by ({override}) blocked as datapoint is '
                           f'currently overriden.')
            return False
        else:
            self._log.info(f'Datapoint ({datapoint}) overriden by '
                           f'({override}).')
            return True

    def data_unlock(self, datapoint, owner):
        """Clears the lock on a datapoint to allow general updating

        Args:
            datapoint (str): Name of the datapoint
            owner (str): Name of the lock owner

        Returns:
            bool: True - Datapoint lock cleared
                  False - Datapoint lock not cleared
        """
        sql = ('''UPDATE Data SET Override=?
                  WHERE Datapoint=? AND Override=?''')

        override = str(owner)

        r_val = self.sql_write(sql, [(None, datapoint, override)])

        if r_val is False:
            self._log.warning(f'Failure to clear override on datapoint '
                              f'({datapoint}) by ({override}).')
            return False
        elif r_val == 0:
            self._log.info(f'Attempt to clear override on datapoint '
                           f'({datapoint}) by ({override}) blocked.')
            return False
        else:
            self._log.info(f'Override on ({datapoint}) cleared by '
                           f'({override}).')
            return True

    def data_set_calibration(self, datapoint, value):
        """Sets a calibration value for a selected float value in the
        database.

        Args:
            datapoint (str): The name of the datapoint
            value (float): The calibration value

        Returns:
            bool: Calibration successfull or not
        """
        sql = """UPDATE Data
                 SET Calibration=?
                 WHERE Datapoint=?
                    AND Type='float'"""

        try:
            value = float(value)
        except ValueError:
            return False

        ret_val = self.sql_write(sql, [(value, datapoint)])

        if ret_val is False:
            self._log.warning(f'Failed to set calibration for {datapoint}.')
            return False
        elif ret_val == 0:
            return False
        else:
            return True

    def data_get_calibration(self, datapoint):
        """Gets the calibration value for a selected float value in the
        database.

        Args:
            datapoint (str): The datapoint in question

        Returns:
            float: The calibration value
        """

        sql = """SELECT Calibration
                    FROM Data
                    WHERE Datapoint=? AND Type='float'"""

        data = self.sql_read(sql, (datapoint,))

        if data is None:
            return 0.0
        elif data is False:
            self._log.warning(f'Error reading calibration for {datapoint}')
            return 0.0
        else:
            if data[0][0] is None:
                return 0.0
            return float(data[0][0])

# **************** Settings Functions ***************

    def setting_owners(self):
        """Returns a list of owners that have settings availble

        Returns:
            List: List of owners
        """
        sql = ("""SELECT DISTINCT Owner FROM Settings""")
        data = self.sql_read(sql)
        if not data:
            return False
        else:
            return [item[0] for item in data]

# *********** Log entry reading **********************

    def get_syslog_entries(self,
                           name=None,
                           daterange=(None, None),
                           human_time=False):
        """Returns requested log entries

        Args:
            name (str): Log entry source name
            daterange (tuple): (start date, stop date) Unix timestamps,
            None removes that date limit

        Returns:
            list of dict:
        """

        sql = ("""
                SELECT
                    ID,
                    Timestamp,
                    Name,
                    Level,
                    Message
                FROM
                    SystemLog
                WHERE
                    Timestamp
                        BETWEEN
                            IFNULL(:start, 0)
                        AND
                            IFNULL(:end, :current)
                AND
                    CASE WHEN :name IS NOT NULL
                        THEN Name = :name
                        ELSE 1
                    END
                ORDER BY
                    Timestamp
                DESC""")

        parameters = {'name': name,
                      'start': daterange[0],
                      'end': daterange[1],
                      'current': time.time()}

        entries = self.sql_read(sql, parameters)
        if not entries:
            return None

        r_list = list()
        for entry in entries:
            if human_time:
                t = time.localtime(entry[1])
                msec = str(entry[1]).split('.')[1][:3]
                log_time = time.strftime("%Y-%m-%d %H:%M:%S", t) + '.' + msec
            else:
                log_time = str(entry[1])
            r_list.append({'log_entry': str(entry[0]),
                           'log_time': log_time,
                           'log_name': str(entry[2]),
                           'log_type': str(entry[3]),
                           'log_message': str(entry[4])})

        return r_list

    def get_datalog_entries(self, datapoint):
        sql = ("""SELECT
                    DataLog.Timestamp,
                    DataLog.Value,
                    Data.Type
                FROM
                    Data,
                    DataLog
                WHERE
                    DataLog.Data_ID=Data.id
                    AND
                    Data.DataPoint=?
                ORDER BY
                    DataLog.Timestamp DESC""")

        data = self.sql_read(sql, (datapoint,))

        if not data:
            return None
        else:
            castlist = list()
            for entry in data:
                castlist.append((entry[0], self.typecast(entry[1], entry[2])))

        return castlist

    def get_datalog_minmax_time(self, datapoint):
        sql = ("""SELECT
                    MIN(DataLog.Timestamp),
                    MAX(DataLog.Timestamp)
                FROM
                    Data,
                    DataLog
                WHERE
                    DataLog.Data_ID=Data.id
                    AND
                    Data.DataPoint=?""")

        data = self.sql_read(sql, (datapoint,))

        if not data:
            return None
        else:
            return data[0]
