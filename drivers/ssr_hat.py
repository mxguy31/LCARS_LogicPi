import gpiod


class SSR_Hat():
    class Relay():
        def __init__(self, name, line, invert=False) -> None:
            self.name = name
            self.invert = invert
            IO_Config = gpiod.line_request()
            IO_Config.consumer = self.name
            IO_Config.request_type = gpiod.line_request.DIRECTION_OUTPUT
            self._io_line = gpiod.chip(0).get_line(line)
            self._io_line.request(IO_Config)

        @property
        def value(self):
            if self.invert:
                return not self._io_line.get_value()
            else:
                return self._io_line.get_value()

        @value.setter
        def value(self, state):
            if self._io_line.is_requested:
                if self.invert:
                    state = not state
                if state is not False:
                    self._io_line.set_value(True)
                else:
                    self._io_line.set_value(False)

        def release_control(self):
            self._io_line.release()

    def __init__(self, screen=False):
        self.ssr_01 = self.Relay('SSR_01', 22)
        self.ssr_02 = self.Relay('SSR_02', 21)
        self.ssr_03 = self.Relay('SSR_03', 20)
        self.ssr_04 = self.Relay('SSR_04', 19)
        self.outputs = [self.ssr_01,
                        self.ssr_02,
                        self.ssr_03,
                        self.ssr_04]

        if screen:
            self.screen = self.Relay('Screen', 6, True)
            self.outputs.append(self.screen)

    def release_outputs(self):
        for relay in self.outputs:
            relay.value = False
            relay.release_control()
