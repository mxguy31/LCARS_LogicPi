from kivy.lang.builder import Builder
from kivy.uix.recycleview import RecycleView
from kivy.properties import (NumericProperty, StringProperty,
                             AliasProperty, ObjectProperty)

Builder.load_string('''
#:import LCARSButton gui.widgets.lcars_button
#:import LCARSCap gui.widgets.lcars_images
#:import GUI_CONST gui.constants.GUI_CONST

<SettingsTable@BoxLayout>:
    id: view_table
    orientation: 'horizontal'
    setting: 'SETTING'
    value: 'VALUE'
    type: 'TYPE'
    index: 0
    spacing: 5
    colors:
        {0: GUI_CONST.COLORS['african_violet'],\
         1: GUI_CONST.COLORS['sunflower'],\
         2: GUI_CONST.COLORS['tomato'],\
         3: GUI_CONST.COLORS['ice'],\
         4: GUI_CONST.COLORS['yellow']}

    LCARSButton:
        id: setting_desc
        text: root.setting
        size_hint: (0.25, None)
        background_color: root.colors[root.index % 5]
        on_release: root.parent.parent._update_selection(root.index)
    LCARSButton:
        text: str(root.value).upper()
        halign: 'center'
        size_hint: (0.1, None)
        background_color: root.colors[root.index % 5]
        disabled: False if root.type == 'bool' else True
        on_release: root.parent.parent._update_selection(root.index)
    LCARSButton:
        text: root.value
        halign: 'center'
        size_hint: (0.1, None)
        background_color: root.colors[root.index % 5]
        disabled: False if root.type == 'float' else True
        on_release: root.parent.parent._update_selection(root.index)
    LCARSButton:
        text: root.value
        halign: 'left'
        size_hint: (0.3, None)
        background_color: root.colors[root.index % 5]
        disabled: False if root.type == 'str' else True
        on_release: root.parent.parent._update_selection(root.index)
    LCARSCap:
        orientation: 'right'
        color: root.colors[root.index % 5]

<LCARSSettingsViewer>:
    viewclass: 'SettingsTable'
    bar_width: 0
    effect_cls: 'ScrollEffect'
    RecycleBoxLayout:
        default_size: None, dp(51)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        spacing: 5
''')


class LCARSSettingsViewer(RecycleView):
    def _get_selection(self):
        return (self.selection_index, 
                self.selection_setting,
                self.selection_value,
                self.selection_type)
    
    def _set_selection(self, selection):
        (self.selection_index, 
         self.selection_setting,
         self.selection_value,
         self.selection_type) = selection

    selection = AliasProperty(_get_selection, 
                              _set_selection,
                              bind=('selection_index',
                                    'selection_setting',
                                    'selection_value',
                                    'selection_type'))

    selection_index = NumericProperty(0)
    selection_setting = StringProperty(None)
    selection_value = StringProperty(None)
    selection_type = StringProperty(None)
    
    selection_callback = ObjectProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def _update_selection(self, id):
        self.selection = (id,
                          self.data[id]['setting'],
                          self.data[id]['value'],
                          self.data[id]['type'])
        if self.selection_callback:
            self.selection_callback(id=self.selection[0],
                                    setting=self.selection[1],
                                    value=self.selection[2],
                                    val_type=self.selection[3])
