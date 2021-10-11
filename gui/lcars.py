import kivy
from kivy.uix.screenmanager import Screen
import psutil
import gpiod
from time import strftime

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.animation import Animation
from kivy.properties import ObjectProperty, DictProperty, BooleanProperty

from gui.constants import GUI_CONST
from gui.widgets.lcars_popup import LCARSExitPopup
from app.database import GUIDatabase, AlarmDatabase


class MainDisplay(Widget):
    info_grid_text = DictProperty()
    alarming = BooleanProperty(False)

    class Screen():
        def __init__(self):
            IO_Config = gpiod.line_request()
            IO_Config.consumer = 'lcars_gui'
            IO_Config.request_type = gpiod.line_request.DIRECTION_OUTPUT
            self._io_line = gpiod.chip(0).get_line(6)
            self._io_line.request(IO_Config)

        @property
        def status(self):
            return not self._io_line.get_value()

        @status.setter
        def status(self, onoff):
            if self._io_line.is_requested:
                if onoff in (False, 'Off'):
                    self._io_line.set_value(True)
                else:
                    self._io_line.set_value(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.db = self.app.database
        self.adb = self.app.alarm_database

        self.screen = self.Screen()
        self.fade_timer = Clock.schedule_once(self.start_screen_saver, 30)
        self.blank_timer = Clock.schedule_once(self.blank_screen, 5)
        self.touch_enabled = self.screen.status

        self.update_sys_info()

        Clock.schedule_interval(self.update_sys_info, 1)
        Clock.schedule_once(self.reset_screen_saver, 0)

    def on_touch_down(self, touch):
        touch.grab(self)
        self.reset_screen_saver()
        if self.touch_enabled:
            return super(MainDisplay, self).on_touch_down(touch)
        else:
            return True

    def start_screen_saver(self, *args):
        for widget in App.get_running_app().root_window.children:
            if isinstance(widget, Popup):
                widget.dismiss()
        self.touch_enabled = False
        Animation(opacity=0).start(self)
        self.blank_timer()

    def reset_screen_saver(self, *args):
        self.fade_timer.cancel()
        self.blank_timer.cancel()
        self.fade_timer()
        if not self.touch_enabled:
            self.screen.status = 'On'
            a = Animation(opacity=1)
            a.bind(on_complete=self.wake)
            a.start(self)

    def wake(self, *args):
        self.touch_enabled = True

    def blank_screen(self, *args):
        self.screen.status = 'Off'

    def get_cpu_temperature(self):
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = f.read()[0:3]
                return temp
        except OSError:
            return 'N/A'

    def update_sys_info(self, *args):
        self.info_grid_text[0] = strftime('%S00')
        self.info_grid_text[1] = strftime('%H%M')
        self.info_grid_text[2] = strftime('%m%d')
        self.info_grid_text[3] = strftime('%Y')

        self.info_grid_text[4] = 'M' + str(psutil.virtual_memory().percent)
        self.info_grid_text[5] = 'S' + str(psutil.swap_memory().percent)
        self.info_grid_text[6] = 'D' + str(psutil.disk_usage('/').percent)
        self.info_grid_text[7] = 'C' + str(psutil.cpu_percent())

        self.info_grid_text[8] = 'T' + self.get_cpu_temperature()

        if self.adb.is_act_alarm() != 0:
            self.alarming = not self.alarming
            if self.db.setting_read_single('alarm_scan', 'wake_on_alarm'):
                self.reset_screen_saver()
        else:
            self.alarming = False

    def alarm_silence(self):
        self.adb.silence_alarms()

    def take_screenshot(self):
        dt = strftime('%Y%m%d-%H%M%S-')
        Window.screenshot(name=f'{dt}.png')

    def close_gui(self):
        LCARSExitPopup().open()


class LCARSApp(App):
    sounds = ObjectProperty()

    LabelBase.register(name='LCARS_Bold',
                       fn_regular=str(GUI_CONST.LCARS_BOLD))
    LabelBase.register(name='LCARS_Semi_Bold',
                       fn_regular=str(GUI_CONST.LCARS_SEMI_BOLD))
    LabelBase.register(name='LCARS_Regular',
                       fn_regular=str(GUI_CONST.LCARS_REGULAR))
    LabelBase.register(name='LCARS_Light',
                       fn_regular=str(GUI_CONST.LCARS_LIGHT))
    LabelBase.register(name='LCARS_Thin',
                       fn_regular=str(GUI_CONST.LCARS_THIN))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = GUIDatabase()
        self.alarm_database = AlarmDatabase()

    def build(self):
        return MainDisplay()

    def stop(self, *args, **kwargs):
        self.alarm_database.close_connection()
        self.database.close_connection()
        super().stop(*args, **kwargs)
