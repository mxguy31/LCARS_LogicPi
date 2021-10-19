from app.program import Program
from drivers.custom_io import CustomIO


class DIO_Board(Program):
    def program_init(self):
        self.io = CustomIO()
        self.period = 0.25
        self.description = ('Home-brew optically isolated input and output '
                            'board scanner.')
        self.label = 'IO SCANNER'
        self.button_text = 'IO SCANNER'
        self.call_stop_every_cycle = False

        for io in self.io.get_inputs().keys():
            self.write_datapoint(io, False)

        for io in self.io.get_outputs().keys():
            self.write_datapoint(io, False)

    def program_run(self):
        database_DO = self.search_datapoint('Custom_DO')
        if not database_DO:
            pass
        else:
            self.io.set_outputs(database_DO)

        database_DI = self.search_datapoint('Custom_DI')
        board_DI = self.io.get_inputs()
        for input, value in board_DI.items():
            if input not in database_DI or database_DI[input] != value:
                self.write_datapoint(input, value)

    def program_stop(self):
        for io in self.io.get_outputs().keys():
            self.write_datapoint(io, False)

    def program_fail(self):
        for io in self.io.get_outputs().keys():
            self.write_datapoint(io, False)

    def program_halt(self):
        self.io.reset_outputs()
