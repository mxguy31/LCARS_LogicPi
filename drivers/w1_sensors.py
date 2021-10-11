from os import read
from pathlib import Path


class One_Wire():
    """This class requires the linux ds2482 one-wire kernel driver to function
    It may function with owfs, however it has not been tested.

    This class assumes a pi-wire+ (Axiris) or equivalent utilizing the
    following one wire bus masters. Other arrangements may cause unknown
    behaviour.

    - Address: 0x18, Device: DS2482-800 (8ch master) <- Channels 1 to 8
    - Address: 0x19, Device: DS2482-800 (8ch master) <- Channels 9 to 16
    - Address: 0x1a, Device: DS2482-100 (1ch master) <- Channel 17

    Slaves are identified by the type, the channel they are connected
    to, and then the detection order. For instance the first temperature
    sensor connected to channel 1 will be identified as Temperature_01_01
    <Type>_<Channel>_<Order>

    RPi instructions to enable Kernel Driver:
    The standard method is to add dtoverlay=ds2482 in /boot/config.txt, however
    the ds2482 overlay does not appear to work on Raspbian Buster, it has to be
    done manually.

    Add the following to the end of /etc/modules:
    ds2482

    Add the following to /etc/rc.local at the end but before 'exit 0' line, you
    will have to do this for each master you have, keep in mind they may have
    different I2C bus addresses (0x18).
    echo ds2482 0x18 > /sys/bus/i2c/devices/i2c-1/new_device
    echo ds2482 0x19 > /sys/bus/i2c/devices/i2c-1/new_device
    echo ds2482 0x1a > /sys/bus/i2c/devices/i2c-1/new_device

    Reboot

    The 1-wire slaves should be available in /sys/bus/w1/devices
    To read data from your devices a quick 'cat ./w1_slave' will return the
    full slave readback string.
    """

    class Temperature():
        def __init__(self, name, location):
            self._name = name
            self._location = Path(location)

        @property
        def name(self):
            return self._name

        @property
        def value(self):
            v = self._read('temperature')
            try:
                r_val = float(v) / 1000
                return r_val
            except ValueError:
                return None

        @property
        def serial_num(self):
            return self._read('name').rstrip('\n')

        @property
        def resolution(self):
            return self._read('resolution').rstrip('\n')

        @property
        def conv_time(self):
            return self._read('conv_time').rstrip('\n')

        def _read(self, file):
            attribute = self._location.joinpath(file)
            if not attribute.is_file():
                return None

            try:
                with open(attribute) as f:
                    readback = f.read()
            except OSError:
                return None
            else:
                return readback

    def __init__(self, device_dir='/sys/bus/w1/devices'):
        self._dev_root = Path(device_dir)
        self.sensors = list()
        self.sensor_scan()

    def sensor_scan(self):
        self.sensors.clear()
        dir_list = [f for f in self._dev_root.iterdir() if f.is_dir()]
        for directory in dir_list:
            item = 0
            if not directory.is_dir():
                continue
            if directory.name.startswith('w1_bus_master'):
                bus_num = directory.name[13:].zfill(2)
                slave_file = directory.joinpath('w1_master_slaves')
                if not slave_file.is_file():
                    continue
                with open(slave_file) as f:
                    for line in f:
                        if line.startswith('28-'):
                            item += 1
                            self._add_sensor(line, bus_num, item)

    def _add_sensor(self, sens_id, bus_num, item):
        cls_name = ('Temperature_' + bus_num + '_' + str(item).zfill(2))
        slave_dir = self._dev_root.joinpath(sens_id.strip())
        if not slave_dir.is_dir():
            return
        else:
            exec(f"self.sensors.append("
                 f"self.Temperature('{cls_name}',"
                 f"'{slave_dir}'))")
