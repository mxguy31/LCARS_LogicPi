from kivy.logger import COLORS
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.lang.builder import Builder
from kivy.properties import (ListProperty, BooleanProperty, DictProperty)

from gui.widgets.lcars_sound import SoundMachine
from gui.constants import GUI_CONST

Builder.load_string('''
#:import LCARSCap gui.widgets.lcars_images
#:import GUI_CONST gui.constants.GUI_CONST

<DataTableRow>:
    orientation: 'horizontal'
    text: ''
    color: ''
    spacing: 5
    LCARSCap:
        orientation: 'left'
        opacity: 1 if root.selected else 0
        color: GUI_CONST.COLORS[root.color]
    Label:
        canvas.before:
            Color:
                rgba: GUI_CONST.COLORS[root.color]
            Rectangle:
                pos: self.pos
                size: self.size
        text: root.text
        font_name: 'LCARS_Bold'
        font_size: sp(18)
        color: (0, 0, 0, 1)
        shorten: True
        shorten_from: 'right'

# Data table Viewer
<LCARSDataSelector>:
    viewclass: 'DataTableRow'
    bar_width: 0
    effect_cls: 'ScrollEffect'
    SelectableRecycleBoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        default_size_hint: 1, None
        default_size: None, dp(51)
        height: self.minimum_height
        spacing: 5
        padding: 15
        multiselect: True
        touch_multiselect: True               
''')


class LCARSDataSelector(RecycleView):
    current_selection = ListProperty([])
    disp_data = DictProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(disp_data=self.get_data)

    def get_data(self, *args):
        colors = ['violet','almond','sunflower','sky','peach']
        if self.disp_data is None:
            self.data = [{'rv_key': 0,
                          'datapoint': 'None',
                          'type': 'None'}]
        else:
            last_color = 0
            t_data = list()
            for point in sorted(self.disp_data):
                if isinstance(self.disp_data[point], str):
                    continue
                t_data.append({'text': point,
                               'color': colors[last_color]})
                last_color += 1
                if last_color >= len(colors):
                    last_color = 0

        self.data = t_data


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    pass
    ''' Adds selection and focus behaviour to the view. '''


class DataTableRow(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sounds = SoundMachine()

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(DataTableRow, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(DataTableRow, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        try:
            # Parents don't exist the first time this is run
            selection = self.parent.parent.current_selection
        except Exception:
            return

        if is_selected:
            selection.append(rv.data[index]['text'])
            self.sounds.play_sound('beep')
        else:
            selection.remove(rv.data[index]['text'])
            self.sounds.play_sound('beep')
