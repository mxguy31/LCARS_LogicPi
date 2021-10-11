from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang.builder import Builder
from kivy.properties import (NumericProperty, BooleanProperty, ColorProperty,
                             DictProperty, StringProperty, ObjectProperty,
                             OptionProperty)
from gui.widgets.lcars_sound import SoundMachine
from gui.constants import GUI_CONST

Builder.load_string('''
#:import GUI_CONST gui.constants.GUI_CONST
#:import LCARS_Cap gui.widgets.lcars_images
<LCARSButton>:
    background_normal: GUI_CONST.textures('btn')
    background_down: GUI_CONST.textures('btn_dn')
    background_disabled_normal: self.background_normal
    background_disabled_down: self.background_down
    opacity: 0 if self.disabled else 1

    font_name: 'LCARS_Bold'
    text_size: self.size
    font_size: sp(18)
    halign: 'right'
    valign: 'bottom'
    padding: (15, 10)
    color: 'black'
    disabled_color: 'black'

    size_hint: (None, None)
    size: (dp(150), dp(51))
    border: 0,0,0,0

<LCARSButtonRound@LCARSButton>:
    background_normal: GUI_CONST.textures('btn_rnd')
    background_down: GUI_CONST.textures('btn_rnd_dn')

<LCARSButtonRoundLeft@LCARSButton>:
    background_normal: GUI_CONST.textures('btn_left')
    background_down: GUI_CONST.textures('btn_left_dn')

<LCARSButtonRoundRight@LCARSButton>:
    background_normal: GUI_CONST.textures('btn_right')
    background_down: GUI_CONST.textures('btn_right_dn')

<LCARSButtonSideBarShort@LCARSButton>:
    size: (dp(150), dp(51))

<LCARSButtonSideBarMed@LCARSButton>:
    size: (dp(150), dp(102))

<LCARSButtonSideBarTall@LCARSButton>:
    size: (dp(150), dp(153))

<LCARSButtonIncrease@LCARSButton>:
    size: (dp(38), dp(51))
    text: '' if self.text is not None else '' # Text is not allowed
    background_normal: GUI_CONST.textures('increase')
    background_down: GUI_CONST.textures('increase_dn')

<LCARSButtonDecrease@LCARSButton>:
    size: (dp(38), dp(51))
    text: '' if self.text is not None else '' # Text is not allowed
    background_normal: GUI_CONST.textures('decrease')
    background_down: GUI_CONST.textures('decrease_dn')

<LCARSOvalButton@LCARSButton>:
    size: (dp(45), dp(30))
    text: '' if self.text is not None else '' # Text is not allowed
    background_normal: GUI_CONST.textures('oval')
    background_down: GUI_CONST.textures('oval_dn')

<LCARSBooleanToggle>:
    orientation: 'horizontal'
    spacing: 5
    size_hint: (None, None)
    size: self.minimum_size
    LCARSCap:
        orientation: 'left'
        color: GUI_CONST.COLORS['magenta']
    LCARSButton:
        text: root.false_label
        width: dp(100)
        background_color: root.color_normal if self.state == 'normal' else root.color_down
        background_down: GUI_CONST.textures('btn')
        on_release: root.btn_push(False)
        state: root.btn_state[False]
    LCARSButton:
        text: root.true_label
        width: dp(100)
        background_color: root.color_normal if self.state == 'normal' else root.color_down
        background_down: GUI_CONST.textures('btn')
        on_release: root.btn_push(True)
        state: root.btn_state[True]
    LCARSCap:
        orientation: 'right'
        color: GUI_CONST.COLORS['magenta']

<LCARSModeToggle>:
    orientation: 'horizontal'
    spacing: 5
    size_hint: (None, None)
    size: self.minimum_size
    LCARSCap:
        orientation: 'left'
        color: GUI_CONST.COLORS['magenta']
    LCARSButton:
        text: 'RUN'
        width: dp(100)
        background_color: root.color_normal if self.state == 'normal' else root.color_down
        background_down: GUI_CONST.textures('btn')
        on_release: root.btn_push('RUN')
        state: root.btn_state['RUN']
    LCARSButton:
        text: 'PAUSE'
        width: dp(100)
        background_color: root.color_normal if self.state == 'normal' else root.color_down
        background_down: GUI_CONST.textures('btn')
        on_release: root.btn_push('PAUSE')
        state: root.btn_state['PAUSE']
    LCARSButton:
        text: 'STOP'
        width: dp(100)
        background_color: root.color_normal if self.state == 'normal' else root.color_down
        background_down: GUI_CONST.textures('btn')
        on_release: root.btn_push('STOP')
        state: root.btn_state['STOP']
    LCARSCap:
        orientation: 'right'
        color: GUI_CONST.COLORS['magenta']

<LCARSButtonBoolEquipment>:
    background_normal: GUI_CONST.textures('btn')
    background_down: GUI_CONST.textures('btn_dn')
    background_disabled_normal: self.background_normal
    background_disabled_down: self.background_down
    size_hint: (None, None)
    border: 0,0,0,0
''')


class LCARSButton(Button):
    long_press_time = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_long_press')
        self.sounds = SoundMachine()

    def on_state(self, instance, value):
        if value == 'down':
            l_time = self.long_press_time
            self._clock = Clock.schedule_once(self._do_action, l_time)
        else:
            self._clock.cancel()

    def _do_action(self, *args):
        self.dispatch('on_long_press')

    def on_long_press(self, *args):
        pass

    def on_press(self):
        self.sounds.play_sound('beep')


class LCARSBooleanToggle(BoxLayout):
    status = BooleanProperty(None)
    selected = BooleanProperty(None)

    selection_callback = ObjectProperty()

    color_down = ColorProperty(GUI_CONST.COLORS['sunflower'])
    color_normal = ColorProperty(GUI_CONST.COLORS['grey'])
    true_label = StringProperty('TRUE')
    false_label = StringProperty('FALSE')
    btn_state = DictProperty({False: 'normal', True: 'normal'})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(status=self.update_selection)
        self.bind(selected=self.update_selection)
        self.blinker = Clock.schedule_interval(self.blink, 0.5)
        self.blinker.cancel()  # Create the clock, don't let it run
        self.update_selection()

    def btn_push(self, btn):
        self.selected = btn
        if self.selection_callback:
            self.selection_callback(btn)
        self.update_selection()

    def blink(self, *args):
        if self.btn_state[self.selected] == 'normal':
            self.btn_state[self.selected] = 'down'
        else:
            self.btn_state[self.selected] = 'normal'

    def update_selection(self, *args):
        for btn in self.btn_state.keys():
            self.btn_state[btn] = 'normal'
        self.btn_state[self.status] = 'down'

        if self.selected is None:
            self.selected = self.status

        if self.status != self.selected:
            if not self.blinker.is_triggered:
                self.blinker()
        else:
            self.blinker.cancel()


class LCARSModeToggle(BoxLayout):
    status = OptionProperty(None, options=('RUN',
                                           'PAUSE',
                                           'STOP',
                                           'FAIL',
                                           None))
    mode = OptionProperty(None, options=('RUN',
                                         'PAUSE',
                                         'STOP',
                                         'HALT',
                                         None))

    selection_callback = ObjectProperty()

    color_down = ColorProperty(GUI_CONST.COLORS['sunflower'])
    color_normal = ColorProperty(GUI_CONST.COLORS['grey'])
    btn_state = DictProperty({'RUN': 'normal',
                              'PAUSE': 'normal',
                              'STOP': 'normal',
                              'HALT': 'normal'})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(status=self.update_selection)
        self.bind(mode=self.update_selection)
        self.blinker = Clock.schedule_interval(self.blink, 0.5)
        self.blinker.cancel()  # Create the clock, don't let it run
        self.update_selection()

    def btn_push(self, btn):
        self.mode = btn
        if self.selection_callback:
            self.selection_callback(btn)
        self.update_selection()

    def blink(self, *args):
        if self.status == 'FAIL':
            for state in self.btn_state.keys():
                if self.btn_state[state] == 'down':
                    self.btn_state[state] = 'normal'
                else:
                    self.btn_state[state] = 'down'
        else:
            if self.btn_state[self.mode] == 'normal':
                self.btn_state[self.mode] = 'down'
            else:
                self.btn_state[self.mode] = 'normal'

    def update_selection(self, *args):
        for state in self.btn_state.keys():
            self.btn_state[state] = 'normal'
        
        if self.mode != 'HALT':
            self.btn_state[self.status] = 'down'

        if self.status != self.mode:
            if not self.blinker.is_triggered:
                self.blinker()
        else:
            self.blinker.cancel()

class LCARSButtonBoolEquipment(Button):
    status = OptionProperty(None, options=(True,
                                           False,
                                           None))
    color_true = ColorProperty(GUI_CONST.COLORS['green'])
    color_false = ColorProperty(GUI_CONST.COLORS['sky'])
    color_none = ColorProperty(GUI_CONST.COLORS['grey'])
    color_override = ColorProperty(GUI_CONST.COLORS['orange'])

    blink_on = OptionProperty(None, options=(True,
                                             False,
                                             None))
    override = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(status=self._update_color,
                  override=self._update_color,
                  color_true=self._update_color,
                  color_false=self._update_color,
                  color_none=self._update_color,
                  color_override=self._update_color)
        self.sounds = SoundMachine()
        self.background_color = self.color_none
        
        self.update_clock = Clock.schedule_once(self._update_color, 0.5)
        self.update_clock.cancel()  # Just create the clock, don't run it
        
    def on_press(self):
        self.sounds.play_sound('beep')

    def _blink(self, color_norm, color_blink):
        if self.background_color != color_norm:
            self.background_color = color_norm
        else:
            self.background_color = color_blink

    def _update_color(self, *args):
        if self.status is True:
            c_norm = self.color_true
        elif self.status is False:
            c_norm = self.color_false
        else:
            c_norm = self.color_none

        if self.override:
            c_blink = self.color_override
        else:
            c_blink = self.color_none

        if self.blink_on == self.status or self.override:
            self._blink(c_norm, c_blink)
            if not self.update_clock.is_triggered:
                self.update_clock()
        else:
            self.background_color = c_norm
            self.update_clock.cancel()
