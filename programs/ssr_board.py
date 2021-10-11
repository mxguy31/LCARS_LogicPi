from app.program import Program
from drivers.ssr_hat import SSR_Hat


class SSR_Board(Program):
    def program_init(self):
        self.ssr_hat = SSR_Hat()
        self.period = 0.25
        self.description = 'Home-brew solid state relay control board scanner.'
        self.label = 'SSR CONTROL'
        self.button_text = 'SSR CONTROL'

        for output in self.ssr_hat.outputs:
            self.write_datapoint(output.name, False)

    def program_run(self):
        for output in self.ssr_hat.outputs:
            d_point = self.read_datapoint(output.name)
            if d_point is True:
                output.value = True
            else:
                output.value = False

    def program_stop(self):
        for output in self.ssr_hat.outputs:
            output.value = False

    def program_fail(self):
        for output in self.ssr_hat.outputs:
            output.value = False

    def program_halt(self):
        self.ssr_hat.release_outputs()
