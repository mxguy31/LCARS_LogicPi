# inspiration from
# https://www.guidodiepen.nl/2019/02/implementing-a-simple-plugin-framework-in-python/

import importlib
import pkgutil
import inspect
import configparser
import time
import math

from pathlib import Path

from app.database import AppDatabase
from app.database import OP_MODE, OP_STATE, TYPES
from app.syslog import get_worker_log, get_local_log
from app.constants import CONST


class Program:
    """Base class that each program must inherit from.

    Configuration files must be named the same as the Program class with
    an .ini extension

    A simple program description is recomended.
    For example:
        self.set_description('This is an awesome program.')

    To properly populate the database, program settings should be declared in
    program_init() as a dictionary.
    For example:
        self.settings = {'Set1': 23, 'Set2': 'test', 'Set3': True}
    """

    OP_MODES = OP_MODE
    OP_STATES = OP_STATE
    D_TYPES = TYPES

    def __init__(self, log_queue):
        """Please see help(Program) for more info.
        Do not override this method, user inititialization should go in
        'program_init()'
        """
        self.name = self.__class__.__name__.lower()
        self._database = AppDatabase()
        self.log = get_worker_log(self.name, log_queue)
        self.settings = dict()
        self.config = None
        config_file = Path(CONST.CONFIG_DIR, self.name).with_suffix('.ini')
        if config_file.is_file():
            try:
                self.config = configparser.ConfigParser(allow_no_value=True)
                self.config.optionxform = str  # Case sensitive option names
                self.config.read(config_file)
            except IOError:
                self.log.warning(f'Could not read config file '
                                 f'({config_file}).')

        self._database.program_write(self.name,
                                     mode='STOP',
                                     status='STOP',
                                     period=1,
                                     label=self.name,
                                     button_text=self.name)
        self.program_init()

        self.last_run = None

        if not isinstance(self.settings, dict):
            self.log.warning('Program settings information is not a dict.')
            self.settings = dict()
        else:
            current_settings = self.read_settings()
            for key, value in self.settings.items():
                if current_settings is None:
                    self.write_setting(key, value)
                elif key not in current_settings.keys():
                    self.write_setting(key, value)

    def read_setting(self, setting):
        return self._database.setting_read_single(self.name, setting)

    def read_settings(self, setting=None):
        data = self._database.setting_read_multiple(self.name, setting)
        if not data:
            return dict()
        else:
            return data[self.name]

    def write_setting(self, setting, value):
        if not isinstance(setting, str):
            return False
        else:
            return self._database.setting_write(self.name, setting, value)

    @property
    def mode(self):
        return self._database.program_read(self.name)['Mode']

    @mode.setter
    def mode(self, mode):
        if mode in self._database.OP_MODES:
            if self._database.program_write(self.name, mode=mode):
                self.log.debug(f'Program ({self.name}) mode set to ({mode}).')
            else:
                self.log.warning(f'Failed to set ({self.name}) '
                                 f'mode to ({mode}).')
        else:
            self.log.warning(f'Incorrect mode specified ({mode})')

    @property
    def status(self):
        return self._database.program_read(self.name)['Status']

    @status.setter
    def status(self, status):
        if status in self._database.OP_STATES:
            if self._database.program_write(self.name, status=status):
                self.log.debug(f'Program ({self.name}) '
                               f'status set to ({status}).')
                if status == OP_STATE.FAIL:
                    self.program_fail()
                    self.log.warning(f'Program ({self.name}) failed.')
            else:
                self.log.warning(f'Failed to set ({self.name}) status to '
                                 f'({status}).')
        else:
            self.log.warning(f'Incorrect state specified ({status})')

    @property
    def button_text(self):
        return self._database.program_read(self.name)['ButtonText']

    @button_text.setter
    def button_text(self, text):
        if self._database.program_write(self.name, button_text=text):
            self.log.debug(f'Program ({self.name}) button text set to '
                           f'({text}).')
        else:
            self.log.warning(f'Failed to set ({self.name}) button text to '
                             f'({text}).')

    @property
    def label(self):
        return self._database.program_read(self.name)['Label']

    @label.setter
    def label(self, label):
        if self._database.program_write(self.name, label=label):
            self.log.debug(f'Program ({self.name}) label set to '
                           f'({label}).')
        else:
            self.log.warning(f'Failed to set ({self.name}) label to '
                             f'({label}).')

    @property
    def description(self):
        return self._database.program_read(self.name)['Description']

    @description.setter
    def description(self, description):
        if self._database.program_write(self.name, description=description):
            self.log.debug(f'Program ({self.name}) description set to '
                           f'({description}).')
        else:
            self.log.warning(f'Failed to set ({self.name}) description to '
                             f'({description}).')

    @property
    def last_run(self):
        return self._database.program_read(self.name)['Last_Run']

    @last_run.setter
    def last_run(self, time):
        self._database.program_write(self.name, last_run=time)

    @property
    def period(self):
        return self._database.program_read(self.name)['Period']

    @period.setter
    def period(self, value):
        if self._database.program_write(self.name, period=value):
            self.log.debug(f'Program ({self.name}) period set to '
                           f'({value}).')
        else:
            self.log.warning(f'Failed to set ({self.name}) period to '
                             f'({value}).')

    def has_datapoint(self, datapoint):
        if self._database.data_read(datapoint):
            return True
        else:
            return False

    def write_datapoint(self, datapoint, value):
        return self._database.data_write(datapoint, value)

    def read_datapoint(self, datapoint):
        t_val = self._database.data_read(datapoint)
        if not t_val:
            return None
        else:
            return t_val[datapoint]

    def read_datapoints(self, datapoints):
        return self._database.data_read(datapoints)

    def search_datapoint(self, search):
        return self._database.data_search(search)

    def operate(self):
        def set_run():
            self.status = OP_STATE.RUN
            self.log.info('Program running.')

        def set_pause():
            self.status = OP_STATE.PAUSE
            self.log.info('Program paused.')

        def set_stop():
            self.status = OP_STATE.STOP
            self.log.info('Program stopped.')

        def halt_loop():
            self.running = False
            self.log.info('Program halted.')

        def run_program():
            t1 = time.time()
            self.program_run()
            t2 = time.time()

            period = self.period

            if (t2 - t1) > period:
                period = math.ceil((t2-t1) * 4.25) / 4
                self.log.warning(f'Program did not complete within its '
                                 f'designated period. Period increased to '
                                 f'{period}s (the time it took + 25%).')
                self.period = period
            elif (t2 - t1) > (period * .75):
                period += .25
                self.log.warning(f'Program required more than 75 percent of '
                                 f'its period to complete a cycle. Period '
                                 f'increased by 250ms to {period}s.')
                self.period = period

        MODE_DICT = {OP_MODE.RUN: {OP_STATE.RUN: [run_program],
                                   OP_STATE.PAUSE: [set_run,
                                                    run_program],
                                   OP_STATE.STOP: [set_run,
                                                   self.program_start,
                                                   run_program],
                                   OP_STATE.FAIL: [None]},
                     OP_MODE.PAUSE: {OP_STATE.RUN: [set_pause,
                                                    self.program_pause],
                                     OP_STATE.PAUSE: [self.program_pause],
                                     OP_STATE.STOP: [None],
                                     OP_STATE.FAIL: [None]},
                     OP_MODE.STOP: {OP_STATE.RUN: [set_stop,
                                                   self.program_stop],
                                    OP_STATE.PAUSE: [set_stop,
                                                     self.program_stop],
                                    OP_STATE.STOP: [self.program_stop],
                                    OP_STATE.FAIL: [set_stop]},
                     OP_MODE.HALT: {OP_STATE.RUN: [set_stop,
                                                   self.program_stop,
                                                   halt_loop],
                                    OP_STATE.PAUSE: [set_stop,
                                                     self.program_stop,
                                                     halt_loop],
                                    OP_STATE.STOP: [set_stop,
                                                    halt_loop],
                                    OP_STATE.FAIL: [set_stop,
                                                    halt_loop]}}
        self.running = True

        while self.running:
            loop_mode = self.mode  # Pulled up here to minimize db access
            loop_status = self.status
            self.last_run = time.time()
            for item in MODE_DICT[loop_mode][loop_status]:
                if item is not None:
                    try:
                        item()
                    except Exception:
                        self.log.exception(f'Failed to run {item.__name__} '
                                           'method.')
                        self.status = self.OP_STATES.FAIL

            wake_time = time.monotonic() + self.period
            # wake and check status every second in-case program is disabled
            # during a sleep cycle
            while True:
                if not self.running:
                    break

                diff = wake_time - time.monotonic()
                if diff <= 0:
                    break
                if 0 < diff < 1:
                    time.sleep(diff)
                    break
                else:
                    time.sleep(1)

        self.program_halt()
        self._database.close_connection()

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


def load_programs(program_dir, log_queue):
    """Read the programs folder for modules.

    Modules must contain a class definition that
    inherits from the Program class or they are ignored.
    The program folder must be provided relative to the
    program root folder.
    """
    def _is_duplicate(program_list, class_name):
        if not program_list:
            return False

        for program in program_list:
            if class_name == program.name:
                return program

        return False

    log = get_local_log('Programs')
    log.info('Looking for programs.')

    import_dir = importlib.import_module(program_dir)

    program_list = []
    for _, filename, ispkg in pkgutil.iter_modules(
                                import_dir.__path__,
                                import_dir.__name__ + '.'):
        if not ispkg:
            program_module = importlib.import_module(filename)
            members = inspect.getmembers(program_module, inspect.isclass)
            for (class_name, class_obj) in members:
                # Only add classes that are a sub class of Program,
                # but NOT Program itself, and not a duplicate class name.
                if issubclass(class_obj, Program) \
                        & (class_obj is not Program):
                    duplicate = _is_duplicate(program_list, class_name)
                    if not duplicate:
                        log.info(f'Found program: {class_name}')
                        program_list.append(class_obj(log_queue))
                    else:
                        log.warning('Duplicate program '
                                    f'"{duplicate.__module__}.{class_name}" '
                                    'found, it is being ignored.')

    return program_list
