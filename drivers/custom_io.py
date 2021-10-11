from drivers.mcp23017 import MCP23017


class CustomIO:
    _mcp23017_map_in = {
        1:  8,  2:  7,  3:  9,  4:  6,
        5:  10, 6:  5,  7:  11, 8:  4,
        9:  12, 10: 3,  11: 13, 12: 2,
        13: 14, 14: 1,  15: 15, 16: 0
    }

    _mcp23017_map_out = {
        0:  8,  1:  7,  2:  9,  3:  6,
        4:  10, 5:  5,  6:  11, 7:  4,
        8:  12, 9:  3,  10: 13, 11: 2,
        12: 14, 13: 1,  14: 15, 15: 0
    }

    _default_config = {
        'address_out': 0x20, 'address_in': 0x21,
        'Custom_DI00': 1,  'Custom_DI01': 2,
        'Custom_DI02': 3,  'Custom_DI03': 4,
        'Custom_DI04': 5,  'Custom_DI05': 6,
        'Custom_DI06': 7,  'Custom_DI07': 8,
        'Custom_DI08': 9,  'Custom_DI09': 10,
        'Custom_DI10': 11, 'Custom_DI11': 12,
        'Custom_DI12': 13, 'Custom_DI13': 14,
        'Custom_DI14': 15, 'Custom_DI15': 16,
        'Custom_DO01': 0,  'Custom_DO02': 1,
        'Custom_DO03': 2,  'Custom_DO04': 3,
        'Custom_DO05': 4,  'Custom_DO06': 5,
        'Custom_DO07': 6,  'Custom_DO08': 7,
        'Custom_DO09': 8,  'Custom_DO10': 9,
        'Custom_DO11': 10, 'Custom_DO12': 11,
        'Custom_DO13': 12, 'Custom_DO14': 13,
        'Custom_DO15': 14, 'Custom_DO16': 15
    }

    def __init__(self, config=None):
        self._config = self._default_config.copy()
        if isinstance(config, dict):
            self._config.update(config)

        self._output_driver = MCP23017(self._config['address_out'])
        self.reset_outputs()
        self._input_driver = MCP23017(self._config['address_in'])
        del self._config['address_out']
        del self._config['address_in']

    def get_inputs(self, inputs=None):
        if not isinstance(inputs, list):
            inputs = list()
        r_dict = dict()
        stat = self._input_driver.get_stat16() & 0xFFFF

        for io_item, card_map in self._config.items():
            if (
                (io_item in inputs or len(inputs) is 0)
                and io_item.startswith('Custom_DI')
               ):
                tval = stat >> self._mcp23017_map_in[card_map] & 1
                r_dict[io_item] = bool(tval)

        return r_dict

    def reset_outputs(self):
        self._output_driver.set_stat16(0xFFFF)
        self._output_driver.set_dir16(0x0)

    def set_outputs(self, relays=None):
        if not isinstance(relays, dict):
            relays = dict()

        stat = self._output_driver.get_stat16() & 0xFFFF
        temp_compare = stat
        for relay, value in relays.items():
            if relay in self._config:
                if not value:
                    stat |= (1 << self._mcp23017_map_out[self._config[relay]])
                else:
                    stat &= ~(1 << self._mcp23017_map_out[self._config[relay]])

        stat &= 0xFFFF
        if stat != temp_compare:
            self._output_driver.set_stat16(stat)

    def get_outputs(self, relays=None):
        if not isinstance(relays, list):
            relays = list()
        r_dict = dict()
        stat = ~self._output_driver.get_stat16() & 0xFFFF

        for io_item, card_map in self._config.items():
            if (
                (io_item in relays or len(relays) is 0)
                and io_item.startswith('Custom_DO')
               ):
                tval = stat >> self._mcp23017_map_out[card_map] & 1
                r_dict[io_item] = bool(tval)

        return r_dict
