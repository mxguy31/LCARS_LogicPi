from kivy.app import App
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.properties import ListProperty
from kivy.uix.screenmanager import Screen
from gui.widgets.lcars_sound import SoundMachine

from gui.constants import GUI_CONST

Builder.load_file(str(GUI_CONST.SCREEN_DIR.joinpath('alarm_screen.kv')))


class AlarmScreen(Screen):
    alarm_data = ListProperty()
    history_data = ListProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = App.get_running_app()
        self.adb = self.app.alarm_database
        self.db = self.app.database
        self.display_clock = Clock.schedule_interval(self.update, 1.0)
        self.display_clock.cancel()  # Just create the clock, don't run it
        self.horn_clock = Clock.schedule_interval(self.check_horn, 0.5)
        self.alarm_horn = Clock.schedule_interval(self._alarm_horn, 3.0)
        self.alarm_horn.cancel()
        self.clear_horn = Clock.schedule_interval(self._clear_horn, 3.0)
        self.alarm_horn.cancel()
        self.sounds = SoundMachine()
        self.update()

    def update(self, *args):
        t_current = self.adb.get_alarms(human_time=True)
        if t_current is None:
            t_current = list()
        self.alarm_data = t_current
        
        t_history = self.adb.get_alarm_history(human_time=True)
        if t_history is None:
            t_history = list()
        self.history_data = t_history

    def on_pre_enter(self):
        self.display_clock()  # Restart the update clock

    def on_pre_leave(self):
        self.display_clock.cancel()

    def silence(self):
        self.adb.silence_alarms()

    def accept(self):
        self.adb.acknowledge_alarms()

    def reset(self):
        self.adb.clear_alarms()

    def _alarm_horn(self, *args):
        if self.db.setting_read_single('alarm_scan', 'sound_on_alarm'):
            self.sounds.play_sound('hail')

    def _clear_horn(self, *args):
        if self.db.setting_read_single('alarm_scan', 'sound_on_clear'):
            self.sounds.play_sound('clear')

    def check_horn(self, dt):
        if self.adb.is_act_alarm() > 0:
            if not self.alarm_horn.is_triggered:
                self._alarm_horn()
                self.alarm_horn()  # Schedule repeating horn
        else:
            self.alarm_horn.cancel()

        if self.adb.is_clr_alarm():
            if not self.clear_horn.is_triggered:
                self._clear_horn()
                self.clear_horn()
        else:
            self.clear_horn.cancel()
