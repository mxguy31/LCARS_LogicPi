from kivy.app import App
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.properties import ListProperty
from kivy.uix.screenmanager import Screen

from gui.constants import GUI_CONST

Builder.load_file(str(GUI_CONST.SCREEN_DIR.joinpath('log_screen.kv')))


class LogScreen(Screen):
    log_data = ListProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = App.get_running_app()
        self.db = self.app.database
        self.clock = Clock.schedule_interval(self.update, 1)
        self.clock.cancel()  # Create the clock, don't run it
        self.update()

    def update(self, *args):
        self.log_data = self.db.get_syslog_entries(human_time=True)

    def on_pre_enter(self):
        self.clock()

    def on_pre_leave(self):
        self.clock.cancel()
