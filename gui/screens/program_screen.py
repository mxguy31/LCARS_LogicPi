from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivy.properties import (ListProperty, BooleanProperty,
                             StringProperty, NumericProperty,
                             DictProperty)
from kivy.clock import Clock
from gui.constants import GUI_CONST
from gui.widgets.lcars_sound import SoundMachine
from gui.widgets.lcars_popup import LCARSNumericPopup

Builder.load_file(str(GUI_CONST.SCREEN_DIR.joinpath('program_screen.kv')))


class ProgramScreen(Screen):
    base_buttons = [None, None, None, None, None]
    button_text = ListProperty(base_buttons.copy())
    selected = NumericProperty(-1)
    next_enabled = BooleanProperty(False)
    prev_enabled = BooleanProperty(False)
    screen_open = BooleanProperty(False)
    program = StringProperty('None')
    program_data = DictProperty({'Name': 'None',
                                 'Mode': 'HALT',
                                 'Status': 'STOP',
                                 'Period': 0.0,
                                 'Last_Run': 0.0,
                                 'Description': 'None',
                                 'Label': 'None',
                                 'ButtonText': 'None'})
    log_data = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sounds = SoundMachine()
        self.app = App.get_running_app()
        self.db = self.app.database

        self.display_clock = Clock.schedule_interval(self.update_display, 1)
        self.display_clock.cancel()  # Just create the clock, don't run it

        self.current_page = 1
        self.sel_pg_btn = (1, -1)
        self.program_book = self.create_book()
        self.assign_buttons()
        self.popup = None
        self.popup_open = False

    def on_pre_enter(self):
        self.display_clock()

    def on_pre_leave(self):
        self.display_clock.cancel()

    def create_book(self):
        _bdict = {0: self.base_buttons[0],
                  1: self.base_buttons[1],
                  2: self.base_buttons[2],
                  3: self.base_buttons[3],
                  4: self.base_buttons[4]}
        book = {1: _bdict.copy()}
        btn = 0
        page = 1

        for program in self.db.program_list():
            book[page][btn] = program
            btn += 1
            if btn == 5:
                page += 1
                btn = 0
                book[page] = _bdict.copy()

        return book

    def assign_buttons(self):
        for btn in self.program_book[self.current_page]:
            program = self.program_book[self.current_page][btn]
            if program is None:
                btn_text = None
            else:
                btn_text = self.db.program_read(program)['ButtonText']
            self.button_text[btn] = btn_text

        pg, btn = self.sel_pg_btn
        if pg == self.current_page:
            self.selected = btn
        else:
            self.selected = -1

        if len(self.program_book) == 1:
            self.prev_enabled = False
            self.next_enabled = False
        elif self.current_page == 1:
            self.prev_enabled = False
            self.next_enabled = True
        elif self.current_page == len(self.program_book):
            self.prev_enabled = True
            self.next_enabled = False
        else:
            self.prev_enabled = True
            self.next_enabled = True

    def next_page(self):
        self.current_page += 1
        self.assign_buttons()

    def prev_page(self):
        self.current_page -= 1
        self.assign_buttons()

    def open_group(self, *args):
        if not self.screen_open:
            id = self.sel_pg_btn[1]
            self.program = self.program_book[self.current_page][id]
            self.screen_open = True
            self.sounds.play_sound('screen_on')
            self.update_display()

    def close_group(self, *args):
        if self.screen_open:
            self.screen_open = False
            self.sounds.play_sound('screen_off')
            self.update_display()

    def group_select(self, id):
        pg, btn = self.sel_pg_btn
        self.close_group()

        if pg != self.current_page or btn != id:
            if self.sel_pg_btn[1] != -1:
                self.sel_pg_btn = (self.current_page, id)
                Clock.schedule_once(self.open_group, 0.5)
            else:
                self.sel_pg_btn = (self.current_page, id)
                self.open_group()
        elif pg == self.current_page and btn == id:
            self.sel_pg_btn = (self.current_page, -1)
        self.selected = self.sel_pg_btn[1]

    def update_display(self, *args):
        t_data = self.db.program_read(self.program)
        t_logs = self.db.get_syslog_entries(name=self.program,
                                            human_time=True)
        if t_data is not None:
            self.program_data = t_data
        
        if t_logs is not None:
            self.log_data = t_logs

    def period_popup(self, *args):
        self.popup = LCARSNumericPopup(update_callback=self._popup_callback)
        self.popup.owner = self.program
        self.popup.setting = 'Period'
        self.popup.value = str(self.program_data['Period'])
        self.popup.open()
        self.popup_open = True
    
    def _popup_callback(self, **kwargs):
        self.update_program(name=kwargs['owner'], period=kwargs['value'])
        
    def update_program(self, **kwargs):
        self.db.program_write(**kwargs)
    
    def detail_request(self):
        print('Detail screen for',
              self.program,
              'has not been implemented.')