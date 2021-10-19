from app.program import Program


class Cooling(Program):
    def program_init(self):
        self.period = 0.25
        self.description = ('Cooling fan logic for when tank temperature gets '
                            'too high.')
        self.label = 'COOLING CONTROL'
        self.button_text = 'COOLING'
        self.settings = {
            'FAN_A_ON': self.config['GENERAL'].getfloat('FAN_A_ON', 26.3),
            'FAN_A_OFF': self.config['GENERAL'].getfloat('FAN_A_OFF', 26.0),
            'SENSOR_A': self.config['SENSORS'].get('SENSOR_A'),
            'OUTPUT_A': self.config['GENERAL'].get('OUTPUT_A'),
            'FAN_B_ON': self.config['GENERAL'].getfloat('FAN_B_ON', 26.5),
            'FAN_B_OFF': self.config['GENERAL'].getfloat('FAN_B_OFF', 26.2),
            'SENSOR_B': self.config['SENSORS'].get('SENSOR_B'),
            'OUTPUT_B': self.config['GENERAL'].get('OUTPUT_B'),
            'FAIL_STATE_A': self.config['GENERAL'].getboolean('FAIL_STATE_A', False),
            'FAIL_STATE_B': self.config['GENERAL'].getboolean('FAIL_STATE_B', False)
            }

        self.call_stop_every_cycle = False
        if self.config['MISC'].getboolean('RESET_TO_INI', False):
            for key, value in self.settings.items():
                self.write_setting(key, value)

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
        sensor_a = self.read_datapoint(settings['SENSOR_A'])
        sensor_b = self.read_datapoint(settings['SENSOR_B'])

        if sensor_a is not None:
            if sensor_a >= settings['FAN_A_ON']:
                self.write_datapoint(settings['OUTPUT_A'], True)
            elif sensor_a <= settings['FAN_A_OFF']:
                self.write_datapoint(settings['OUTPUT_A'], False)
            
        if sensor_b is not None:
            if sensor_b >= settings['FAN_B_ON']:
                self.write_datapoint(settings['OUTPUT_B'], True)
            elif sensor_b <= settings['FAN_B_OFF']:
                self.write_datapoint(settings['OUTPUT_B'], False)
