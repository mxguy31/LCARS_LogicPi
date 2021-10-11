from functools import partial
from random import randint, shuffle

from kivy.utils import rgba
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.lang.builder import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.properties import (DictProperty, NumericProperty, OptionProperty)

from gui.constants import GUI_CONST

Builder.load_string('''
<LCARSInfoGrid>:
    padding: 5
<DataLabel>:
    font_name: 'LCARS_Semi_Bold'
    font_size: sp(18)
    text_size: self.size
    halign: 'right'
    valign: 'middle'
    shorten: True
                    ''')


class DataLabel(Label):
    pass


class LCARSInfoGrid(GridLayout):
    """Creates an LCARS info grid. Both the number of rows and columns must
    defined. Each grid cell is populated with a random number unless a defined
    value is added to 'text_dict'. The bottom right hand corner is index 0, and
    the index numbers increase right to left then bottom to top.
    """
    text_dict = DictProperty()
    color = GUI_CONST.COLORS['orange']
    focus_color_weak = GUI_CONST.COLORS['almond_cream']
    focus_color_strong = GUI_CONST.COLORS['white']
    cascade_pattern = OptionProperty('none', options=['random',
                                                      'waterfall',
                                                      'none'])
    cascade_interval = NumericProperty(2)
    cascade_length = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cells = 0
        self.bind(text_dict=self._bound_update)
        Clock.schedule_once(self._create_cells, -1)
        Clock.schedule_once(self.cascade, 0)
        Clock.schedule_interval(self.cascade, 2)

    def _create_cells(self, *args):
        self.cells = self.rows * self.cols
        for i in range(self.cells):
            self.add_widget(DataLabel(color=self.color))
        self._update_text(range(self.cells))

    def _bound_update(self, *args):
        if self.cascade_pattern == 'none':
            self._update_text(range(self.cells))

    def _update_text(self, cells):
        for row in range(self.rows):
            for col in range(self.cols - 1):
                cell = ((row * self.cols) + col)
                if cell not in cells:
                    continue
                if (cell - row) not in self.text_dict.keys():
                    digits = randint(2, 5)
                    number = self._digit_random(digits)
                    self.children[cell].text = str(number)
                else:
                    self.children[cell].text = self.text_dict[cell - row]
            self.children[cell + 1].text = '10' + str(self.rows - row)

    def cascade(self, *args):
        if self.cascade_pattern == 'waterfall':
            self._set_sequence(self._time_gen(range(self.rows)))
        elif self.cascade_pattern == 'random':
            r = list(range(self.rows))
            shuffle(r)
            self._set_sequence(self._time_gen(r))
        else:
            return

    def _time_gen(self, row_seq):
        interval = self.cascade_length / self.rows
        ofst1 = interval * 2
        ofst2 = ofst1 * 1.5
        ofst3 = ofst2 * 1.25

        pattern = list()
        n = 0
        for row in row_seq:
            time = interval * n
            pattern.append((row,
                            time,
                            time + ofst1,
                            time + ofst2,
                            time + ofst3))
            n = n + 1
        return pattern

    def _set_sequence(self, pattern):
        for i in pattern:
            Clock.schedule_once(partial(self._blank_row, i[0]), i[1])
            Clock.schedule_once(partial(self._focus_row_s, i[0]), i[2])
            Clock.schedule_once(partial(self._focus_row_w, i[0]), i[3])
            Clock.schedule_once(partial(self._restore_row, i[0]), i[4])

    def _blank_row(self, row, *args):
        cells = self._row_color(row, rgba('FFFFFF00'))
        self._update_text(cells)

    def _restore_row(self, row, *args):
        self._row_color(row, self.color)

    def _focus_row_s(self, row, *args):
        self._row_color(row, self.focus_color_strong)

    def _focus_row_w(self, row, *args):
        self._row_color(row, self.focus_color_weak)

    def _row_color(self, row, color):
        row += 1
        start_cell = (self.rows - row) * self.cols
        affected_cells = list()
        for col in range(self.cols):
            affected_cells.append(start_cell + col)
            self.children[start_cell + col].color = color

        return affected_cells

    def _digit_random(self, n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)
