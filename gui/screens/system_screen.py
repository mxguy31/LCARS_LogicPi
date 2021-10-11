from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import DictProperty, BooleanProperty
from kivy.app import App
                             
from gui.constants import GUI_CONST
from gui.widgets.lcars_popup import LCARSBoolEquipmentPopup

Builder.load_file(str(GUI_CONST.SCREEN_DIR.joinpath('system_screen.kv')))


class SystemScreen(Screen):
    status = DictProperty({None: None})
    locks = DictProperty({None: None})
    
    wc_confirm = BooleanProperty(False)
    wc_start = BooleanProperty(True)
    wc_cancel = BooleanProperty(False)
    wc_io_points = ['Custom_DO04', 'Custom_DO05',
                    'Custom_DO06', 'SSR_01',
                    'Custom_DO11']
    
    def __init__(self, **kw):
        super().__init__(**kw)

        self.popup_open = False
        self.popup = None
        self.app = App.get_running_app()

        self.db = self.app.database       
        self.display_clock = Clock.schedule_interval(self.update_display, 1)
        self.display_clock.cancel()  # Just create the clock, don't run it
        
        self.wc_btn_clock = Clock.schedule_interval(self.update_wc_btn, .5)
        self.wc_btn_clock.cancel()  # Just create the clock, don't run it
        self.wc_ini_status = None
        self.wc_ini_locks = None
        self.wc_counter = 0

    def on_pre_enter(self):
        self.display_clock()

    def on_pre_leave(self):
        self.display_clock.cancel()

    def update_display(self, *args):
        self.status = self.db.data_read().copy()
        self.locks = self.db.data_get_locks().copy()
        
        if self.popup_open and isinstance(self.popup, LCARSBoolEquipmentPopup):
            self.popup.value = self.status[self.popup.setting]
            lock = self.db.data_is_locked(self.popup.setting)
            if lock == None:
                self.popup.overridden = False
            else:
                self.popup.overridden = True

    def update_wc_btn(self, *args):
        if self.wc_cancel and self.wc_confirm:
            self.wc_counter += 1
        if self.wc_counter > 10:
            self.wc_counter = 0
            self.wc_btn_clock.cancel()
            self.wc_confirm = False
            self.wc_cancel = False

        if self.wc_confirm or self.wc_cancel:
            self.wc_start = not self.wc_start
        else:
            self.wc_start = True

    def equipment_select(self, **kwargs):
        value = self.db.data_read_single(kwargs['d_point'])
        lock = self.db.data_is_locked(kwargs['d_point'])
        if lock == None:
            overridden = False
        else:
            overridden = True

        self.popup = LCARSBoolEquipmentPopup(update_callback=self.update_equip_status,
                                             override_callback=self.update_override,
                                             close_callback=self.stop_popup_update)

        self.popup.disp_text = kwargs['disp_text']
        self.popup.setting = kwargs['d_point']
        self.popup.value = value
        self.popup.overridden = overridden
        self.popup.open()
        self.popup_open = True

    def update_equip_status(self, **kwargs):
        self.db.data_write(kwargs['setting'], kwargs['value'], self.app.name)

    def update_override(self, d_point, override):
        if override:
            self.db.data_lock(d_point, self.app.name)
        else:
            self.db.data_unlock(d_point, self.app.name)

    def stop_popup_update(self, *args):
        self.popup_open = False
    
    def start_water_change(self):
        if self.wc_cancel or self.wc_confirm:
            return
        self.wc_btn_clock()
        self.wc_confirm = True
        self.wc_cancel = True

    def confirm_water_change(self):
        self.wc_confirm = False
        self.wc_cancel = True
        
        self.wc_ini_locks = self.db.data_get_locks()
        self.wc_ini_status = self.db.data_read(self.wc_io_points)
        
        for io in self.wc_io_points:
            if io in self.wc_ini_locks:
                continue
            self.db.data_lock(io, self.app.name)
            self.db.data_write(io, False, self.app.name)

    def cancel_water_change(self):
        if self.wc_cancel and not self.wc_confirm:
            for io in self.wc_io_points:
                if io in self.wc_ini_locks:
                    continue
                self.db.data_write(io, self.wc_ini_status[io], self.app.name)
                self.db.data_unlock(io, self.app.name)

        self.wc_btn_clock.cancel()
        self.wc_confirm = False
        self.wc_cancel = False
        self.update_wc_btn()

    def not_imp(self):
        pass
