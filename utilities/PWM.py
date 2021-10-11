# timing loop inspiration from
# https://github.com/m-lundberg/simple-pid

import time


class PWM():
    """A simple low-speed software PWM"""

    def __init__(self, period=5, reverse=False):
        """
        Initialize a new PWM control.
        :param period: The period of the PWM cycle, measured in seconds.
        :param reverse: Set to true to reverse the action of the PWM
        """
        self._period = period if period > 1 else 1
        self._reverse = bool(reverse)

        self._start_time = None
        self._output = False

    def __call__(self, demand, dt=None):
        """
        Update the PWM controller.
        Call the PWM controller with *demand*, return a true/false value
        depending on where in the cycle period the call is placed.
        :param dt: If set, uses this value for timestep instead of real time.
            This can be used in simulations when simulation time is different
            from real time.
        """

        if demand is None and not (0 <= demand <= 100):
            raise ValueError('Demand must be positive and between 0 and 100')

        now = time.monotonic()
        if self._start_time is None:
            self._start_time = now

        if dt is None:
            dt = (now - self._start_time) % self._period
        elif dt <= 0:
            raise ValueError('dt has negative value {}, '
                             'must be positive'.format(dt))

        swap_time = (1-(demand / 100)) * self._period
        if dt < swap_time:
            self._output = self._reverse

        elif dt >= swap_time:
            self._output = not self._reverse

        return self._output

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, period):
        self._period = period if period > 1 else 1

    @property
    def reverse(self):
        return self._reverse

    @ reverse.setter
    def reverse(self, reverse):
        self._reverse = bool(reverse)
