import time
import smtplib
import operator
import threading
from app.program import Program
from app.database import AlarmDatabase


class Alarm_Scan(Program):
    """This is designed as a Program, however it is unique and uses sepcific
    database functions not provided through the Program structure. It is done
    this way to allow program functionality to the alarm scanning system.
    """
    ACTIVE = 'ACT'
    SILENT = 'SIL'
    ACKNOWLEDGE = 'ACK'
    CLEAR = 'CLR'


    def program_init(self):
        self.alarm_db = AlarmDatabase()
        self.period = 0.25
        self.description = ('Scans datapoints for value beyond limits')
        self.label = 'ALARM SCANNER'
        self.button_text = 'ALARMS'

        self.write_datapoint('Failed_Process', False)
        self.write_datapoint('Stalled_Process', False)

        self.alarm_db.write_alarm(alarm_name='Failed_Process',
                                  description='A running process has failed',
                                  datapoint='Failed_Process',
                                  operation='eq',
                                  value=True,
                                  delay='0:0',
                                  priority='1',
                                  enabled=True,
                                  status='CLR')

        self.alarm_db.write_alarm(alarm_name='Stalled_Process',
                                  description='A running process has stalled',
                                  datapoint='Stalled_Process',
                                  operation='eq',
                                  value=True,
                                  delay='0:0',
                                  priority='1',
                                  enabled=True,
                                  status='CLR')

        if self.config is None:
            return

        if not self.config.has_section('BASIC'):
            return  # config must have 'BASIC' section
        
        if not self.config['BASIC'].getboolean('USE_CONFIG_FILE'):
            return  # No need to load the config file if not requested
        
        for section in self.config.sections():
            if section == 'ALARMS':
                continue
            for key in self.config[section]:
                if key == 'USE_CONFIG_FILE':
                    continue
                try:
                    val = self.config[section].getboolean(key)
                    if val is None:
                        val = False
                except ValueError:
                    val = self.config[section][key]  # Default to string
                self.settings[key] = val                            

        if self.config.has_section('ALARMS'):
            for key, value in self.config['ALARMS'].items():
                att_list = value.split(';')
                try:
                    val = float(att_list[3])
                except ValueError:
                    val = att_list[3]
                try:
                    delay = int(att_list[4])
                    delay = str(delay) + ':0'
                except ValueError:
                    delay = '0:0'
                self.alarm_db.write_alarm(alarm_name=key,
                                            description=att_list[1],
                                            datapoint=att_list[0],
                                            operation=att_list[2],
                                            value=val,
                                            delay=delay,
                                            priority=att_list[5],
                                            enabled=True,
                                            status='CLR')
        
    def _check_delay(self, delay):
        limit, value = delay.split(':')
        value = float(value)
        if value != 0:
            return limit + ':0.0'
        else:
            return False

    def _increment_delay(self, delcnt, amount):
        limit, value = delcnt.split(':')
        limit = float(limit)
        value = float(value) + amount
        if value >= limit:
            value = 0
            return (str(limit) + ':' + str(value), True)
        else:
            return (str(limit) + ':' + str(value), False)

    def _manage_state(self, alarm, delta):
        n_delay, roll = self._increment_delay(alarm[5], delta)
        self.alarm_db.write_alarm(alarm[0], delay=n_delay)
        if roll:
            return True
        else:
            return False

    def _send_message(self, message, server, port, username, passwd, receiver):
        content = "\n\n".join(message)
        try:
            with smtplib.SMTP_SSL(server, port) as server:
                server.login(username, passwd)
                server.sendmail(username, receiver, content)
        except Exception as e:
            return
            
    def program_start(self):
        # this sleep allows the rest of the programs to establish their
        # datapoints before the alarm scanner starts running.
        time.sleep(5)

    def program_run(self):
        message_list = []
        alarms = self.alarm_db.get_inactive_alarms()
        if alarms is None:
            return

        a_list = list()
        for alarm in alarms:
            if alarm[4] == 'bool':
                if alarm[3] == '0':
                    avalue = False
                else:
                    avalue = True
            elif alarm[4] == 'float':
                avalue = float(alarm[3])
            else:
                avalue = alarm[3]

            datapoint = self.read_datapoint(alarm[1])
            if datapoint is None:
                continue
            elif getattr(operator, alarm[2])(datapoint, avalue):
                if alarm[6] == 'ACK':
                    continue
                elif self._manage_state(alarm, self.period):
                    a_list.append(alarm[0])
                    if alarm[0] == 'Failed_Process' or alarm[0] == 'Stalled_Process':
                        self.write_datapoint(alarm[0], False)
                    message_list.append(f'***** ALARM ACTIVE *****\n'
                                        f'Name: {alarm[0]}\n'
                                        f'Desc: "{alarm[7]}"')
            else:
                wflag = False
                t_state = None
                t_delay = None
                n_delay = self._check_delay(alarm[5])
                if alarm[6] == 'ACK':
                    t_state = 'ACLR'
                    wflag = True
                if n_delay:
                    t_delay = n_delay
                    wflag = True
                if wflag:
                    self.alarm_db.write_alarm(alarm[0],
                                              delay=t_delay,
                                              status=t_state)
                    if t_state == 'ACLR':
                        message_list.append(f'***** ALARM CLEAR *****\n'
                                            f'Name: {alarm[0]}\n'
                                            f'Desc: "{alarm[7]}"')

        if message_list and self.read_setting('send_messages'):
            server = str(self.read_setting('smtp_server'))
            port = int(self.read_setting('smtp_port'))
            login = str(self.read_setting('smtp_username'))
            passwd = str(self.read_setting('smtp_password'))
            receiver = str(self.read_setting('msg_receiver'))

            t1 = threading.Thread(target=self._send_message, 
                                  kwargs={'message': message_list,
                                          'server': server,
                                          'port': port,
                                          'username': login,
                                          'passwd': passwd,
                                          'receiver': receiver})
            t1.start()  
            # I don't join the thread as I don't want this thread to wait

        if a_list:
            self.alarm_db.activate_alarms(tuple(a_list))

        output = self.read_setting('local_out')
        if output is None:
            return

        if self.alarm_db.is_act_alarm() > 0:
            self.write_datapoint(output, True)
        else:
            self.write_datapoint(output, False)

    def program_stop(self):
        self.alarm_db.close_connection()
