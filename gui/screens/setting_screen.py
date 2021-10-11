from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivy.properties import (ListProperty, BooleanProperty,
                             StringProperty, NumericProperty)
from kivy.clock import Clock
from gui.constants import GUI_CONST

from gui.widgets.lcars_sound import SoundMachine
from gui.widgets.lcars_popup import (LCARSBooleanPopup, LCARSNumericPopup,
                                     LCARSStringPopup)

Builder.load_file(str(GUI_CONST.SCREEN_DIR.joinpath('setting_screen.kv')))


class SettingScreen(Screen):
    base_buttons = [None, None, None, None, None]
    button_text = ListProperty(base_buttons.copy())
    selected = NumericProperty(-1)
    next_enabled = BooleanProperty(False)
    prev_enabled = BooleanProperty(False)
    screen_open = BooleanProperty(False)
    owner = StringProperty('None')
    settings = ListProperty([{'setting': 'N/A',
                              'value': 'N/A',
                              'type': 'str',
                              'index': 0}])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sounds = SoundMachine()
        self.app = App.get_running_app()
        self.db = self.app.database

        self.display_clock = Clock.schedule_interval(self.update_display, 1)
        self.display_clock.cancel()  # Just create the clock, don't run it

        self.current_page = 1
        self.sel_pg_btn = (1, -1)
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

        for owner in self.db.setting_owners():
            book[page][btn] = owner
            btn += 1
            if btn == 5:
                page += 1
                btn = 0
                book[page] = _bdict.copy()

        return book

    def assign_buttons(self):
        setting_book = self.create_book()
        for btn in setting_book[self.current_page]:
            self.button_text[btn] = setting_book[self.current_page][btn]

        pg, btn = self.sel_pg_btn
        if pg == self.current_page:
            self.selected = btn
        else:
            self.selected = -1

        if len(setting_book) == 1:
            self.prev_enabled = False
            self.next_enabled = False
        elif self.current_page == 1:
            self.prev_enabled = False
            self.next_enabled = True
        elif self.current_page == len(setting_book):
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

    def open_setting_group(self, *args):
        if not self.screen_open:
            id = self.sel_pg_btn[1]
            self.owner = self.button_text[id]
            self.screen_open = True
            self.sounds.play_sound('screen_on')
            self.update_display()

    def close_setting_group(self, *args):
        if self.screen_open:
            self.screen_open = False
            self.sounds.play_sound('screen_off')
            self.update_display()

    def group_select(self, id):
        pg, btn = self.sel_pg_btn
        self.close_setting_group()

        if pg != self.current_page or btn != id:
            if self.sel_pg_btn[1] != -1:
                self.sel_pg_btn = (self.current_page, id)
                Clock.schedule_once(self.open_setting_group, 0.5)
            else:
                self.sel_pg_btn = (self.current_page, id)
                self.open_setting_group()
        elif pg == self.current_page and btn == id:
            self.sel_pg_btn = (self.current_page, -1)
        self.selected = self.sel_pg_btn[1]

    def update_display(self, *args):
        self.settings = list()
        index = 0
        st = self.db.setting_read_multiple(self.owner)
        if st is None:
            return
        for setting, value in st[self.owner].items():
            self.settings.append({'setting': str(setting),
                                  'value': str(value),
                                  'type': str(type(value).__name__),
                                  'index': index})
            index += 1

        if self.popup_open and isinstance(self.popup, LCARSBooleanPopup):
            self.popup.value = self.db.setting_read_single(self.owner,
                                                           self.popup.setting)

    def setting_select(self, **kwargs):
        if kwargs['val_type'] == 'bool':
            self.popup = LCARSBooleanPopup(update_callback=self.update_setting,
                                           close_callback=self.stop_popup_update)
        elif kwargs['val_type'] == 'float':
            self.popup = LCARSNumericPopup(update_callback=self.update_setting,
                                           close_callback=self.stop_popup_update)
        else:
            self.popup = LCARSStringPopup(update_callback=self.update_setting,
                                          close_callback=self.stop_popup_update)

        self.popup.owner = self.owner
        self.popup.setting = kwargs['setting']
        self.popup.value = kwargs['value']
        self.popup.open()
        self.popup_open = True
    
    def update_setting(self, **kwargs):
        self.db.setting_write(kwargs['owner'],
                              kwargs['setting'],
                              kwargs['value'])
        
    def stop_popup_update(self, *args):
        self.popup_open = False
