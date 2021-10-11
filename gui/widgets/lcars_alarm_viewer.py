from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView

Builder.load_string('''
#:import GUI_CONST gui.constants.GUI_CONST

<AlarmEntryText@Label>:
    shorten: True
    shorten_from: 'right'
    size: self.texture_size
    halign: 'left'
    font_name: 'LCARS_Semi_Bold'
    font_size: sp(18)
    text_size: self.size
    color: GUI_CONST.COLORS['light_blue']
    colors:
        {'1': GUI_CONST.COLORS['mars'],\
         '2': GUI_CONST.COLORS['orange'],\
         '3': GUI_CONST.COLORS['yellow'],\
         'N/A': GUI_CONST.COLORS['yellow']}

<LCARSAlarmHeader>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(24)
    AlarmEntryText:
        text: 'TIME'
        size_hint: (None, 1)
        width: 200
        font_size: sp(22)
    AlarmEntryText:
        text: 'NAME'
        size_hint: (None, 1)
        width: 200
        font_size: sp(22)
    AlarmEntryText:
        text: 'DESCRIPTION'
        size_hint: (1, 1)
        font_size: sp(22)
    AlarmEntryText:
        text: 'STATUS'
        size_hint: (None, 1)
        width: 60
        font_size: sp(22)

<AlarmTable@BoxLayout>:
    orientation: 'horizontal'
    alarm_time: 'N/A'
    alarm_id: 'N/A'
    alarm_name: 'N/A'
    alarm_description: 'N/A'
    alarm_status: 'N/A'
    alarm_priority: 'N/A'

    AlarmEntryText:
        text: root.alarm_time
        size_hint: (None, 1)
        width: 200
        color: self.colors[root.alarm_priority]
    AlarmEntryText:
        text: root.alarm_name
        size_hint: (None, 1)
        width: 200
        color: self.colors[root.alarm_priority]
    AlarmEntryText:
        text: root.alarm_description
        size_hint: (1, 1)
        color: self.colors[root.alarm_priority]
    AlarmEntryText:
        text: str(root.alarm_status)
        color: self.colors[root.alarm_priority]
        size_hint: (None, 1)
        width: 60
        halign: 'center'

<LCARSAlarmViewer>:
    viewclass: 'AlarmTable'
    bar_width: 0
    effect_cls: 'ScrollEffect'
    RecycleBoxLayout:
        default_size: None, dp(24)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
                    ''')


class LCARSAlarmViewer(RecycleView):
    pass


class LCARSAlarmHeader(BoxLayout):
    pass
