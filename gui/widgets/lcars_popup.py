from kivy.properties import (StringProperty, ObjectProperty, BooleanProperty,
                             NumericProperty, OptionProperty, ColorProperty)
from kivy.uix.modalview import ModalView
from kivy.lang.builder import Builder
from kivy.clock import Clock

from gui.widgets.lcars_sound import SoundMachine
from gui.constants import GUI_CONST

Builder.load_string('''
#:import LCARSBooleanToggle gui.widgets.lcars_button
#:import LCARSBarSeparator gui.widgets.lcars_images
#:import LCARSButtonRoundRight gui.widgets.lcars_button
#:import LCARSButtonRound gui.widgets.lcars_button
#:import LCARSKeyboard gui.widgets.lcars_keyboard
#:import LCARSCap gui.widgets.lcars_images
#:import GUI_CONST gui.constants.GUI_CONST

#<Widget>
#    canvas.after:
#        Line:
#            rectangle: self.x+1,self.y+1,self.width-1,self.height-1
#            dash_offset: 5
#            dash_length: 3

<LCARSPopup>:
    _container: container
    overlay_color: (0, 0, 0, .8)
    GridLayout:
        padding: 20
        spacing: 10
        cols: 1
        size_hint: None, None
        size: root.size
        pos: root.pos
        Label:
            text: root.title
            color: root.title_color
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None
            font_size: root.title_size
            font_name: root.title_font
            halign: root.title_align
        LCARSBarSeparator:
            width: root.width
        RelativeLayout:
            id: container

<PopUpText@Label>:
    font_name: 'LCARS_Bold'
    font_size: sp(18)
    text_size: self.size
    halign: 'left'
    valign: 'middle'
    color: GUI_CONST.COLORS['orange']

<LCARSExitPopup>:
    title: ('EXIT GUI?')
    size_hint: (None, None)
    size: (375, 200)
    BoxLayout:
        orientation: 'horizontal'
        spacing: 10
        pos_hint: {'center_y': .5, 'center_x': .5}
        size_hint: (None, None)
        size: self.minimum_size
        LCARSButtonRound:
            text: 'CANCEL'
            background_color: GUI_CONST.COLORS['orange']
            on_release: root.dismiss()
        LCARSButtonRound:
            text: 'EXIT'
            background_color: GUI_CONST.COLORS['mars']
            on_release: app.stop()

<LCARSBooleanPopup>:
    title: ('BOOLEAN VALUE EDITOR')
    size_hint: (None, None)
    size: (350, 250)
    BoxLayout:
        orientation: 'vertical'
        spacing: 15
        pos_hint: {'center_y': .5, 'center_x': .5}
        size_hint: (None, None)
        size: self.minimum_size
        GridLayout:
            cols: 2
            spacing: 5
            size_hint: (1, None)
            height: 50
            PopUpText:
                halign: 'right'
                size_hint: (.3, 1)
                text: 'OWNER:'
            PopUpText:
                size_hint: (.7, 1)
                text: root.owner
            PopUpText:
                halign: 'right'
                size_hint: (.3, 1)
                text: 'SETTING:'
            PopUpText:
                size_hint: (.7, 1)
                text: root.setting
        LCARSBooleanToggle:
            pos_hint: {'center_x': .5}
            status: root.value
            selection_callback: root.enter_data
            selected: root.selected

<LCARSKeyboardPopup>:
    size_hint: (None, None)
    size: (400, 510) if self.key_type == 'numeric' else (900, 560)
    title: 'NUMERIC VALUE EDITOR' if self.key_type == 'numeric' else 'STRING VALUE EDITOR'
    BoxLayout:
        orientation: 'vertical'
        spacing: 15
        pos_hint: {'center_y': .5, 'center_x': .5}
        size_hint: (None, None)
        size: self.minimum_size
        GridLayout:
            cols: 2
            spacing: 5
            size_hint: (1, None)
            height: 50
            PopUpText:
                size_hint_x: None
                halign: 'right'
                width: 120
                text: 'OWNER:'
            PopUpText:
                text: root.owner
            PopUpText:
                size_hint_x: None
                halign: 'right'
                width: 120
                text: 'SETTING:'
            PopUpText:
                text: root.setting
        BoxLayout:
            orientation: 'horizontal'
            spacing: 5
            size_hint: (1, None)
            height: 50
            PopUpText:
                size_hint_x: None
                halign: 'right'
                width: 120
                font_size: sp(24)
                text: 'VALUE:'
            PopUpText:
                font_size: sp(24)
                text: root.value + root.cursor
        LCARSKeyboard:
            size_hint: (None, None)
            size: (350, 250) if root.key_type == 'numeric' else (850, 300)
            key_background_normal: GUI_CONST.textures('btn')
            key_background_down: GUI_CONST.textures('btn_dn')
            font_name: 'LCARS_Bold'
            on_textinput: root.key_press(*args)
            on_key_down: root.key_press(*args)
            layout: "gui/assets/lcars_numeric.json" if root.key_type == 'numeric' else "gui/assets/lcars_alphanumeric.json"

<LCARSBoolEquipmentPopup>:
    title: ('EQUIPMENT STATUS EDITOR')
    size_hint: (None, None)
    size: (350, 325)
    BoxLayout:
        orientation: 'vertical'
        spacing: 15
        pos_hint: {'center_y': .5, 'center_x': .5}
        size_hint: (None, None)
        size: self.minimum_size
        BoxLayout:
            size_hint: (1, None)
            height: 50
            PopUpText:
                font_size: sp(24)
                halign: 'center'
                text: root.disp_text
        LCARSBooleanToggle:
            pos_hint: {'center_x': .5}
            status: root.value
            selection_callback: root.enter_data
            selected: root.selected
        BoxLayout:
            orientation: 'horizontal'
            spacing: 5
            size_hint: (1, None)
            height: self.minimum_height
            Widget:
                size_hint_x: 1
            LCARSCap:
                orientation: 'left'
                opacity: 1 if root.overridden else 0
                color: GUI_CONST.COLORS['mars']
            LCARSButtonRoundRight:
                text: 'DISABLE OVERRIDE' if root.overridden else 'ENABLE OVERRIDE'
                on_release: root.override_callback(root.setting, not root.overridden)
                background_color: GUI_CONST.COLORS['mars'] if root.overridden else GUI_CONST.COLORS['peach']
''')

class LCARSPopupException(Exception):
    '''Popup exception, fired when multiple content widgets are added to the
    popup.

    .. versionadded:: 1.4.0
    '''


class LCARSPopup(ModalView):
    '''Popup class. Based on basic Kivy Popup with LCARS customizations.

    :Events:
        `on_open`:
            Fired when the Popup is opened.
        `on_dismiss`:
            Fired when the Popup is closed. If the callback returns True, the
            dismiss will be canceled.
    '''
    owner = StringProperty('NONE')
    setting = StringProperty('NONE')
    value = StringProperty()
    cursor = StringProperty('')
    title = StringProperty('No title')
    title_size = NumericProperty('30sp')
    title_align = OptionProperty('center', options=['left',
                                                    'center',
                                                    'right',
                                                    'justify'])
    title_font = StringProperty('LCARS_Bold')
    content = ObjectProperty(None)
    title_color = ColorProperty(GUI_CONST.COLORS['orange'])

    # Internal properties used for graphical representation.

    _container = ObjectProperty(None)

    def __init__(self, update_callback=None, close_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.update_callback = update_callback
        if close_callback is not None:
            self.bind(on_dismiss=close_callback)
        self.cursor_clock = Clock.schedule_interval(self.cursor_blink, .5)
        self.cursor_clock.cancel()
        self.sounds = SoundMachine()
        self.ctrls = {'backspace': lambda x: x[:-1],
                      'enter': self.enter_data,
                      'exit': self.dismiss,
                      'clear': lambda x: '',
                      'capslock': lambda x: x,
                      'shift': lambda x: x}

    def add_widget(self, widget):
        if self._container:
            if self.content:
                raise LCARSPopupException(
                    'Popup can have only one widget as content')
            self.content = widget
        else:
            super(LCARSPopup, self).add_widget(widget)


    def on_content(self, instance, value):
        if self._container:
            self._container.clear_widgets()
            self._container.add_widget(value)

    def on__container(self, instance, value):
        if value is None or self.content is None:
            return
        self._container.clear_widgets()
        self._container.add_widget(self.content)

    def on_touch_down(self, touch):
        if self.disabled and self.collide_point(*touch.pos):
            return True
        return super(LCARSPopup, self).on_touch_down(touch)

    def on_open(self):
        self.cursor_clock()

    def on_dismiss(self):
        self.cursor_clock.cancel()

    def cursor_blink(self, *args):
        if self.cursor != '_':
            self.cursor = '_'
        else:
            self.cursor = ''

    def enter_data(self, value):
        if self.update_callback is not None:
            self.update_callback(owner=self.owner,
                                 setting=self.setting,
                                 value=value)
    
    def key_press(self, *args):
        self.sounds.play_sound('beep')
        btn = args[1]
        
        if btn in self.ctrls:
            r_val = self.ctrls[btn](self.value)
            if r_val is not None:
                self.value = r_val
            return
        self.value += str(btn)

class LCARSBooleanPopup(LCARSPopup):
    selected = BooleanProperty()
    value = BooleanProperty()

    def on_open(self):
        self.selected = self.value


class LCARSBoolEquipmentPopup(LCARSPopup):
    selected = BooleanProperty()
    value = BooleanProperty()
    disp_text = StringProperty()
    overridden = BooleanProperty(False)
    override_callback = ObjectProperty()

    def on_open(self):
        self.selected = self.value


class LCARSExitPopup(LCARSPopup):
    pass


class LCARSKeyboardPopup(LCARSPopup):
    key_type = StringProperty()


class LCARSNumericPopup(LCARSKeyboardPopup):
    def __init__(self, update_callback, close_callback=None, **kwargs):
        self.key_type = 'numeric'
        super().__init__(update_callback=update_callback,
                         close_callback=close_callback,
                         **kwargs)
        self.ctrls['.'] = lambda x: x + '.' if '.' not in x else x
        self.ctrls['-'] = lambda x: '-' if len(x) == 0 else x
        
    def key_press(self, *args):
        if len(self.value) <= 8 or args[1] in self.ctrls:
            super().key_press(*args)
        else:
            super().key_press(*('', ''))

    def enter_data(self, value):
        try:
            value = float(self.value)
        except ValueError as e:
            pass
        else:
            super().enter_data(value)

class LCARSStringPopup(LCARSKeyboardPopup):
    pass
