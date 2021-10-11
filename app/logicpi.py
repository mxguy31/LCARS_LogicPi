import multiprocessing as mp
import time
import os

import inspect

from app.constants import CONST
from app.syslog import get_local_log
from app.syslog import log_listener
from app.database import AppDatabase
from app.database import OP_MODE, OP_STATE
from app.program import load_programs
from app.alarm_scan import Alarm_Scan


class LogicPi:
    def __init__(self):
        self.name = 'LogicPi'
        self.database = AppDatabase()
        self.database.setting_write(self.name, 'Enabled', True)

        self.log = get_local_log(self.name)
        self.log.info(f'Starting LogicPi, main App PID: {os.getpid()}')

        self.log_queue = mp.Queue(-1)
        self.log_listener = mp.Process(target=log_listener,
                                       args=(self.log_queue,))
        self.log_listener.start()

        self.program_fails = dict()
        self.programs = load_programs('programs', self.log_queue)
        self.programs.append(Alarm_Scan(self.log_queue))

    def safe_shutdown(self, signum, frame):
        """Allows for a safe shutdown from a systemd service

        In the projects root folder create a python file 'Start.py'
        with the contents:

        import signal
        from app.logicpi import LogicPi

        PLC = LogicPi()
        signal.signal(signal.SIGTERM, PLC.safe_shutdown)
        PLC.main()

        Then call this file with your systemd script, it will catch the SIGTERM
        signal and initiate a safe shutdown.

        logicpi.service contents:

        [Unit]
        Description=LogicPi PLC
        After=multi-user.target

        [Service]
        WorkingDirectory=/home/pi/LogicPi2
        User=pi
        Type=idle
        ExecStart=/usr/bin/python3 /home/pi/LogicPi2/Start.py &>/dev/null
        KillMode=mixed
        TimeoutStopSec=60

        [Install]
        WantedBy=multi-user.target

        """
        # used to enable a safe shutdown from systemd
        self.database.setting_write(self.name, 'Enabled', False)

    def stoplog_listener(self):
        self.log_queue.put_nowait(None)
        self.log_listener.join()

    def process_check(self, p_dict):
        for program in self.database.program_list():
            data = self.database.program_read(program)
            # The process won't be running under these conditions.
            if data['Mode'] == OP_MODE.STOP or data['Mode'] == OP_MODE.HALT:
                continue

            t_time = data['Period'] * CONST.PROCESS_STALL_CYCLES
            stall_time = data['Last_Run'] + t_time

            if self.program_fails[program] == -1:
                pass

            elif not p_dict[program].is_alive():
                self.log.error(f'The process ({p_dict[program].pid})'
                               f' for program {program} has died with an'
                               f' exit code {p_dict[program].exitcode}')
                self.database.data_write('Failed_Process', True)
                p_dict[program].kill()
                p_dict[program].join()

            elif data['Status'] == OP_STATE.FAIL:
                self.database.data_write('Failed_Process', True)
                p_dict[program].kill()
                p_dict[program].join()

            elif time.time() > stall_time:
                self.log.error(f'The process for program {program}, '
                               f'PID: {p_dict[program].pid} '
                               f'has stalled.')
                self.database.data_write('Stalled_Process', True)
                p_dict[program].kill()
                p_dict[program].join()

            else:
                continue

            if self.program_fails[program] >= 5:
                self.database.program_write(program, mode=OP_MODE.HALT)
                self.database.program_write(program, status=OP_STATE.STOP)
                self.log.error(f'Program: {program} has failed more than '
                               '5 times and has been halted.')
                self.program_fails[program] = -1
                continue

            else:
                self.program_fails[program] += 1
                del p_dict[program]
                self.database.program_write(program, status=OP_STATE.STOP)
                self.database.program_write(program, mode=OP_MODE.RUN)
                for prg in self.programs:
                    if prg.name == program:
                        p_dict[program] = mp.Process(target=prg.operate)
                        p_dict[program].start()
                        self.log.warning(f'Restarting program {program}, '
                                         f'PID: {p_dict[program].pid}')
                        break

    def join_process(self, process, timeout=5):
        process.join(timeout=timeout)
        if process.is_alive():
            self.log.warning(f'Program PID {process.pid} did not exit. '
                             'Killing program.')
            process.kill()
            process.join()

    def main(self):
        p_dict = dict()
        p_check_start = time.time() + CONST.PROCESS_CHECK_DELAY

        for program in self.programs:
            program.mode = OP_MODE.RUN
            self.program_fails[program.name] = 0
            p_dict[program.name] = mp.Process(target=program.operate)
            p_dict[program.name].start()
            self.log.info(f'Starting program {program.name}, '
                          f'PID: {p_dict[program.name].pid}')

        enabled = True
        while enabled:
            time.sleep(0.25)
            enabled = self.database.setting_read_single(self.name, 'Enabled')
            if (p_check_start < time.time()) or not enabled:
                break

        while enabled:
            process_check_time = time.time() + CONST.PROCESS_CHECK_TIME
            while True:
                time.sleep(0.25)
                enabled = self.database.setting_read_single(self.name,
                                                            'Enabled')
                if (process_check_time < time.time()) or not enabled:
                    break

            if enabled:
                self.process_check(p_dict)

        self.log.warning('Shutdown requested.')
        for program in self.database.program_list():
            self.database.program_write(program, mode=OP_MODE.HALT)
            self.log.info(f'Waiting on program: {program}, '
                          f'PID: {p_dict[program].pid}, to exit.')
            self.join_process(p_dict[program])
            del p_dict[program]

        if p_dict:
            for program, process in p_dict.items():
                self.log.warning(f'An orphand process was found: {program}')
                process.kill()
                self.join_process(process)

        self.stoplog_listener()
        self.log.info('System shutdown.')
        self.database.close_connection()
