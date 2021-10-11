from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView

Builder.load_string('''
#:import GUI_CONST gui.constants.GUI_CONST

<LogEntryText@Label>:
    shorten: True
    shorten_from: 'right'
    size: self.texture_size
    halign: 'left'
    font_name: 'LCARS_Semi_Bold'
    font_size: sp(18)
    text_size: self.size
    color: GUI_CONST.COLORS['light_blue']
    colors:
        {'CRITICAL': GUI_CONST.COLORS['mars'],\
         'ERROR': GUI_CONST.COLORS['red'],\
         'WARNING': GUI_CONST.COLORS['orange'],\
         'INFO': GUI_CONST.COLORS['yellow'],\
         'N/A': GUI_CONST.COLORS['yellow']}

<LCARSSysLogHeader>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(24)
    LogEntryText:
        text: 'TIME'
        size_hint: (None, 1)
        width: 200
        font_size: sp(22)
    LogEntryText:
        text: 'SOURCE'
        size_hint: (None, 1)
        width: 120
        font_size: sp(22)
    LogEntryText:
        text: 'TYPE'
        size_hint: (None, 1)
        width: 100
        font_size: sp(22)
    LogEntryText:
        text: 'MESSAGE'
        size_hint: (1, 1)
        font_size: sp(22)

<SysLogTable@BoxLayout>:
    orientation: 'horizontal'
    log_entry: 'N/A'
    log_time: 'N/A'
    log_name: 'N/A'
    log_type: 'N/A'
    log_message: 'COULD NOT RETRIEVE ENTRIES'

    LogEntryText:
        text: root.log_time
        size_hint: (None, 1)
        width: 200
        color: self.colors[root.log_type]
    LogEntryText:
        text: root.log_name
        size_hint: (None, 1)
        width: 120
        color: self.colors[root.log_type]
    LogEntryText:
        text: root.log_type
        size_hint: (None, 1)
        width: 100
        color: self.colors[root.log_type]
    LogEntryText:
        text: root.log_message
        size_hint: (1, 1)
        color: self.colors[root.log_type]

<LCARSSysLogViewer>:
    viewclass: 'SysLogTable'
    bar_width: 0
    effect_cls: 'ScrollEffect'
    RecycleBoxLayout:
        default_size: None, dp(24)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
''')


class LCARSSysLogViewer(RecycleView):
    pass


class LCARSSysLogHeader(BoxLayout):
    pass
