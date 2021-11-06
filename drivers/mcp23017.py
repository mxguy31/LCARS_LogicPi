from smbus2 import SMBus


class Error(Exception):
    pass


class MCP23017:
    """Raw communication driver over I2C with an MCP23017"""
    class Register_IDs:
        """Register ID's used by the MCP23017"""
        # MCP23017 Register definitions
        # Interrupts are not included in this driver.
        # Commented registers are all interrupt related
        IODIRA = 0x00
        IODIRB = 0x01
        IOPOLA = 0x02
        IOPOLB = 0x03
        # GPINTENA    = 0x04
        # GPINTENB    = 0x05
        # DEFVALA     = 0x06
        # DEFVALB     = 0x07
        # INTCONA     = 0x08
        # INTCONB     = 0x09
        # IOCON       = 0x0A
        GPPUA = 0x0C
        GPPUB = 0x0D
        # INTFA       = 0x0E
        # INTFB       = 0x0F
        # INTCAPA     = 0x10
        # INTCAPB     = 0x11
        GPIOA = 0x12
        GPIOB = 0x13
        OLATA = 0x14
        OLATB = 0x15

    OUTPUT = 0
    INPUT = 1
    HIGH = 1
    LOW = 0

    def __init__(self,
                 address,
                 busnum=1,
                 iodira=0xFF,
                 iodirb=0xFF,
                 gppua=0,
                 gppub=0,
                 ipola=0,
                 ipolb=0,
                 porta=0,
                 portb=0):

        self._busnum = busnum
        self._address = address

        # Assign values
        self.iodira = iodira
        self.iodirb = iodirb
        self.gppua = gppua
        self.gppub = gppub
        self.ipola = ipola
        self.ipolb = ipolb
        self.porta = porta
        self.portb = portb

    def _setregister(self, register, value):
        """
        Sets a single register in the MCP23017

        Args:
            register (Byte): Register to write to
            value (Byte): Value to write

        Raises:
            Error: If the device or the i2c bus is inaccessible
        """
        try:
            with SMBus(self._busnum) as bus:
                bus.write_byte_data(self._address, register, value)

        except OSError as e:
            raise Exception('I2C device at address '
                            + str(hex(self._address))
                            + ' could not be accessed.') from e

    def _getregister(self, register):
        """
        Gets a single register from the MCP23017

        Args:
            register (Byte): Register to read from

        Raises:
            Error: If the device or the i2c bus is inaccessible

        Returns:
            Byte: The value of the register
        """
        try:
            with SMBus(self._busnum) as bus:
                value = bus.read_byte_data(self._address, register)

        except OSError as e:
            raise Exception('I2C device at address '
                            + str(hex(self._address))
                            + ' could not be accessed.') from e

        else:
            return value

    def _changebit(self, bitmap, bit, value):
        """Changes a particular bit in a byte

        Args:
            bitmap (Byte): The byte to be modified
            bit (Int): The number of the bit to change
            value (bit): The new value of the bit

        Returns:
            Byte: The modified byte
        """
        assert value == 1 or value == 0, "Value must be 1 or 0"
        if value == 0:
            return bitmap & ~(1 << bit)
        elif value == 1:
            return bitmap | (1 << bit)

    def _modifyregister(self, register, bit, value):
        """[summary]

        Args:
            register ([type]): [description]
            bit ([type]): [description]
            value ([type]): [description]

        Returns:
            [type]: [description]
        """
        assert 0 <= bit < 8, "Only bit numbers 0-7 are valid"
        currvalue = self._getregister(register)
        newvalue = self._changebit(currvalue, bit, value)
        self._setregister(register, newvalue)
        return newvalue

    @property
    def porta(self):
        """8-Bit PortB value, each bit represents one pin, 1 = high, 0 = low"""
        return self._getregister(self.Register_IDs.GPIOA)

    @porta.setter
    def porta(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater"
                             " than 8-bits to a port")
        self._setregister(self.Register_IDs.OLATA, value)

    @property
    def portb(self):
        """8-Bit PortB value, each bit represents one pin, 1 = high, 0 = low"""
        return self._getregister(self.Register_IDs.GPIOB)

    @portb.setter
    def portb(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater"
                             " than 8-bits to a port")
        self._setregister(self.Register_IDs.OLATB, value)

    @property
    def iodira(self):
        """8-Bit PortA direction value, each bit represents one pin,
        1 = input, 0 = output"""
        return self._getregister(self.Register_IDs.IODIRA)

    @iodira.setter
    def iodira(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater"
                             " than 8-bits to a port direction")
        self._setregister(self.Register_IDs.IODIRA, value)

    @property
    def iodirb(self):
        """8-Bit PortB direction value, each bit represents one pin,
        1 = input, 0 = output"""
        return self._getregister(self.Register_IDs.IODIRB)

    @iodirb.setter
    def iodirb(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater"
                             " than 8-bits to a port direction")
        self._setregister(self.Register_IDs.IODIRB, value)

    @property
    def gppua(self):
        """8-Bit PortA weak pull-up value, each bit represents one pin,
        1 = enabled, 0 = disabled"""
        return self._getregister(self.Register_IDs.GPPUA)

    @gppua.setter
    def gppua(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater"
                             " than 8-bits to a port direction")
        self._setregister(self.Register_IDs.GPPUA, value)

    @property
    def gppub(self):
        """8-Bit PortB weak pull-up value, each bit represents one pin,
        1 = enabled, 0 = disabled"""
        return self._getregister(self.Register_IDs.GPPUB)

    @gppub.setter
    def gppub(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater"
                             " than 8-bits to a port direction")
        self._setregister(self.Register_IDs.GPPUB, value)

    def get_dir16(self):
        return (self.iodirb << 8) | self.iodira

    def set_dir16(self, direction):
        self.iodirb = (direction >> 8) & 0xFF
        self.iodira = direction & 0xFF

    def get_stat16(self):
        return (self.portb << 8) | self.porta

    def set_stat16(self, status):
        self.portb = (status >> 8) & 0xFF
        self.porta = status & 0xFF
