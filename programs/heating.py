from statistics import mean

# pylint: disable=import-error
from app.program import Program
from utilities.PID import PID
from utilities.PWM import PWM


class Heating(Program):
    DEFAULT_PID_P = 100
    DEFAULT_PID_I = 0
    DEFAULT_PID_D = 0
    DEFAULT_SETPOINT = 26
    DEFAULT_MANUAL = False
    DEFAULT_OUTPUT = None

    NS_WAIT = 10  # Seconds before the program fails due to no sensors
    LS_WAIT = 30  # Seconds between low sensor log inputs

    def program_init(self):
        self.period = 0.25
        self.description = 'Calculates heater duty cycle based on temperature.'
        self.label = 'HEATING CONTROL'
        self.button_text = 'HEATING'
        self.settings = {
            'PID_P': float(self.config['PID']['PROPORTIONAL']),
            'PID_I': float(self.config['PID']['INTEGRAL']),
            'PID_D': float(self.config['PID']['DERIVATIVE']),
            'Setpoint': float(self.config['PID']['SETPOINT']),
            'Manual': False,
            'Output': self.config['MISC']['OUTPUT'],
            'PID_Sample_Time': float(self.config['PID']['PID_SAMPLE_TIME']),
            'PWM_Period': float(self.config['MISC']['PWM_PERIOD']),
            'PWM_Reverse': self.config['MISC'].getboolean('PWM_REVERSE')
            }

        if self.config['MISC'].getboolean('RESET_TO_INI'):
            for key, value in self.settings.items():
                self.write_setting(key, value)

        self.datapoints = {
            'HEAT_DEMAND': 0,
            'HEAT_AVG_TEMP': 0,
            'HEAT_DRIFT': 0,
            'HEAT_ENGAGED': False
            }

        count = 0
        t_sensor_list = list()
        for item in self.config['SENSORS']:
            count += 1
            self.log.info(f'Sensor {item} identified per config file.')
            t_sensor_list.append(item)

        self.settings['Sensors'] = ','.join(t_sensor_list)

        if count < 2:
            self.log.warning('Less than two sensors identified.')

        self._PID = PID()
        self._PID.output_limits = (0, 100)
        self._PID.sample_time = 5
        self._low_snsr_count = 0
        self._low_flag = False
        self._no_snsr_count = 0
        self._manual_flag = False

        self._PWM_Controller = PWM()

    def program_start(self):
        self._PID.reset()

    def program_fail(self):
        try:
            demand = float(self.config['PID']['FAIL_DEMAND'])
        except ValueError:
            self.log.warning('Incorrect failure demand specified, using 0')
            demand = 0
        self.write_datapoint('HEAT_DEMAND', demand)

    def program_stop(self):
        output = self.read_setting('Output')
        self.write_datapoint(output, False)

    def program_run(self):
        sensor_vals = list()
        average = None
        past_sensors = self.settings['Sensors']
        self.settings = self.read_settings()

        for item in self.settings['Sensors'].split(','):
            if item not in past_sensors:
                self.log.info(f'A change to sensor {item} has occured.')
            value = self.read_datapoint(item)
            if not value:
                continue
            else:
                sensor_vals.append(value)

        if self.settings['Manual']:
            if not self._manual_flag:
                self._PID.set_auto_mode(False)
                self.log.info('Manual mode enabled.')
                self._manual_flag = True
        else:
            if self._manual_flag:
                current_demand = self.read_datapoint('T_CONTROL_DEMAND')
                if current_demand:
                    self._PID.set_auto_mode(True, current_demand)
                    self.log.info('Auto mode enabled.')
                    self._manual_flag = False
                else:
                    self.log.error('Could not return to manual mode.')

        drift = 0.0
        period = self.period
        if len(sensor_vals) == 0:
            self._no_snsr_count += 1
            average = None
            if self._no_snsr_count > self.NS_WAIT / period:
                self.log.error('No sensors available.')
                self.status = self.OP_STATES.FAIL

        elif len(sensor_vals) == 1:
            self._no_snsr_count -= 1 if self._no_snsr_count > 0 else 0
            if self._low_snsr_count < self.LS_WAIT / period:
                self._low_snsr_count += 1

            if (self._low_snsr_count == self.LS_WAIT / period
               and not self._low_flag):
                self.log.warning('Only 1 sensor available.')
                self._low_flag = True

            for value in sensor_vals:
                if value is not None:
                    average = value

        else:
            self._no_snsr_count -= 1 if self._no_snsr_count > 0 else 0
            self._low_snsr_count -= 1 if self._low_snsr_count > 0 else 0
            if self._low_snsr_count == 0 and self._low_flag:
                self.log.warning('More than one sensor now available.')
                self._low_flag = False
            average = mean(sensor_vals)
            drift = float(round((max(sensor_vals) - min(sensor_vals)), 3))

        PID_P = self.settings['PID_P']
        PID_I = self.settings['PID_I']
        PID_D = self.settings['PID_D']
        Setpoint = self.settings['Setpoint']

        self._PID.tunings = (PID_P, PID_I, PID_D)
        self._PID.setpoint = Setpoint
        self._PID.sample_time = self.settings['PID_Sample_Time']

        PID_return = 0.0
        if average:
            average = float(round(average, 3))
            PID_return = self._PID(average)

        try:
            # Float cast is required for when the value rounds to an integer
            demand = float(round(PID_return, 3))
        except TypeError:
            self.log.warning('Type error when evaluating PID response.')
            self.status = self.OP_STATES.FAIL
            demand = None

        self.write_datapoint('HEAT_AVG_TEMP', average)
        self.write_datapoint('HEAT_DRIFT', drift)

        if not self._manual_flag:
            self.write_datapoint('HEAT_DEMAND', demand)

        demand = self.read_datapoint('HEAT_DEMAND')

        if demand is None:
            demand = 0

        if demand > 5:
            self.write_datapoint('HEAT_ENGAGED', True)
        else:
            self.write_datapoint('HEAT_ENGAGED', False)

        period = self.settings['PWM_Period']
        output = self.settings['Output']
        reverse = self.settings['PWM_Reverse']
        self._PWM_Controller.period = period
        self._PWM_Controller.reverse = reverse

        pwm_out = self._PWM_Controller(demand)
        self.write_datapoint(output, pwm_out)
