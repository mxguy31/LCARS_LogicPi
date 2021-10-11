from app.program import Program
from drivers.w1_sensors import One_Wire


class W1_Board(Program):
    def program_init(self):
        self.one_wire = One_Wire()
        self.period = 3
        self.description = 'Axiris one-wire board temperature sensor scanner.'
        self.label = 'TEMPERATURE SENSORS'
        self.button_text = 'TEMP SENSORS'

    def program_start(self):
        self.one_wire.sensor_scan()
        for sensor in self.one_wire.sensors:
            self.write_datapoint(sensor.name, sensor.value)

    def program_run(self):
        for sensor in self.one_wire.sensors:
            self.write_datapoint(sensor.name, sensor.value)
