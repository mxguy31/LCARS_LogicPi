from statistics import mean

from app.program import Program


class Cooling(Program):
    def program_init(self):
        self.period = 0.25
        self.description = ('Cooling fan logic for when tank temperature gets '
                            'too high.')
        self.label = 'COOLING CONTROL'
        self.button_text = 'COOLING'
        self.settings = {
            'FAN_A_ON': float(self.config['GENERAL']['FAN_A_ON']),
            'FAN_A_OFF': float(self.config['GENERAL']['FAN_A_OFF']),
            'SENSOR_A': self.config['SENSORS']['SENSOR_A'],
            'OUTPUT_A': self.config['GENERAL']['OUTPUT_A'],
            'FAN_B_ON': float(self.config['GENERAL']['FAN_B_ON']),
            'FAN_B_OFF': float(self.config['GENERAL']['FAN_B_OFF']),
            'SENSOR_B': self.config['SENSORS']['SENSOR_B'],
            'OUTPUT_B': self.config['GENERAL']['OUTPUT_B'],
            'Manual': False
            }

        if self.config['GENERAL']['FAIL_STATE_A'] == 'ON':
            self.settings['FAIL_STATE_A'] = True
        else:
            self.settings['FAIL_STATE_A'] = False

        if self.config['GENERAL']['FAIL_STATE_B'] == 'ON':
            self.settings['FAIL_STATE_B'] = True
        else:
            self.settings['FAIL_STATE_B'] = False

        if self.config['MISC'].getboolean('RESET_TO_INI'):
            for key, value in self.settings.items():
                self.write_setting(key, value)

        self._manual_flag = False

    def program_fail(self):
        settings = self.read_settings()
        self.write_datapoint(settings['OUTPUT_A'], settings['FAIL_STATE_A'])
        self.write_datapoint(settings['OUTPUT_B'], settings['FAIL_STATE_B'])

    def program_stop(self):
        settings = self.read_settings()
        self.write_datapoint(settings['OUTPUT_A'], False)
        self.write_datapoint(settings['OUTPUT_A'], False)

    def program_run(self):
        settings = self.read_settings()

        if settings['Manual']:
            if not self._manual_flag:
                self.log.info('Manual mode enabled.')
                self._manual_flag = True
        else:
            if self._manual_flag:
                self.log.info('Auto mode enabled.')
                self._manual_flag = False

            sensor_a = self.read_datapoint(settings['SENSOR_A'])
            if sensor_a is None:
                return
            sensor_b = self.read_datapoint(settings['SENSOR_B'])
            if sensor_b is None:
                return

            if sensor_a >= settings['FAN_A_ON']:
                self.write_datapoint(settings['OUTPUT_A'], True)
            elif sensor_a <= settings['FAN_A_OFF']:
                self.write_datapoint(settings['OUTPUT_A'], False)

            if sensor_b >= settings['FAN_B_ON']:
                self.write_datapoint(settings['OUTPUT_B'], True)
            elif sensor_b <= settings['FAN_B_OFF']:
                self.write_datapoint(settings['OUTPUT_B'], False)
