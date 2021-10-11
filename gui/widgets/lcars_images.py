from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from gui.constants import GUI_CONST
from kivy.lang.builder import Builder
from kivy.properties import (OptionProperty,
                             StringProperty,
                             ListProperty,
                             ColorProperty)


Builder.load_string('''
#:import GUI_CONST gui.constants.GUI_CONST
<LCARSElbowTall>:
    size_hint: (None, None)
    size: (dp(190), dp(90))
    allow_stretch: True
    keep_ratio: True
    Label:
        font_name: 'LCARS_Bold'
        size: self.texture_size
        font_size: sp(18)
        color: 'black'
        text: root.id_number
        x: root.x + root.label_pos[0]
        y: root.y + root.label_pos[1]

<LCARSElbow>:
    size_hint: (None, None)
    size: (dp(190), dp(70))
    allow_stretch: True
    keep_ratio: True

<LCARSCap>:
    size_hint: (None, None)
    size: (dp(38), dp(51))
    allow_stretch: True
    keep_ratio: True

<LCARSBar>:
    size_hint: (None, None)
    height: dp(23)
    allow_stretch: True

<LCARSBarCap>:
    size_hint: (None, None)
    size: (dp(15), dp(23))
    allow_stretch: True
    keep_ratio: True

<LCARSBarSeparator>:
    orientation: 'horizontal'
    size_hint: (0, None)
    height: self.minimum_height
    spacing: 5
    LCARSBarCap:
        orientation: 'left'
        color: root.l_cap_color
    LCARSBar:
        size_hint_x: 1
        color: root.bar_color
    LCARSBarCap:
        orientation: 'right'
        color: root.r_cap_color

<LCARSOval>:
    source: GUI_CONST.textures('oval')
    size_hint: (None, None)
    size: (dp(45), dp(30))
    allow_stretch: True
    keep_ratio: True
                    ''')


class LCARSElbow(Image):
    orientation = OptionProperty('top_left', options=['top_left',
                                                      'top_right',
                                                      'bottom_left',
                                                      'bottom_right'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._image_update()
        self.bind(orientation=self._image_update)

    def _image_update(self, *args):
        image_dict = {'top_left': GUI_CONST.textures('elbow_tl'),
                      'top_right': GUI_CONST.textures('elbow_tr'),
                      'bottom_left': GUI_CONST.textures('elbow_bl'),
                      'bottom_right': GUI_CONST.textures('elbow_br')}
        self.source = image_dict[self.orientation]


class LCARSElbowTall(Image):
    id_number = StringProperty()
    label_pos = ListProperty()
    orientation = OptionProperty('top_left', options=['top_left',
                                                      'top_right',
                                                      'bottom_left',
                                                      'bottom_right'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._image_update()
        self.bind(orientation=self._image_update)

    def _image_update(self, *args):
        image_dict = {'top_left': (GUI_CONST.textures('elbow_tall_tl'),
                                   [70, 10]),
                      'top_right': (GUI_CONST.textures('elbow_tall_tr'),
                                    [50, 10]),
                      'bottom_left': (GUI_CONST.textures('elbow_tall_bl'),
                                      [70, 60]),
                      'bottom_right': (GUI_CONST.textures('elbow_tall_br'),
                                       [50, 60])}
        self.source = image_dict[self.orientation][0]
        self.label_pos = image_dict[self.orientation][1]


class LCARSCap(Image):
    orientation = OptionProperty('right', options=['right', 'left'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._image_update()
        self.bind(orientation=self._image_update)

    def _image_update(self, *args):
        image_dict = {'left': GUI_CONST.textures('cap_l'),
                      'right': GUI_CONST.textures('cap_r')}
        self.source = image_dict[self.orientation]


class LCARSBar(Image):
    pass


class LCARSBarSeparator(BoxLayout):
    l_cap_color = ColorProperty(GUI_CONST.COLORS['tomato'])
    bar_color = ColorProperty(GUI_CONST.COLORS['african_violet'])
    r_cap_color = ColorProperty(GUI_CONST.COLORS['tomato'])


class LCARSBarCap(Image):
    orientation = OptionProperty('right', options=['right', 'left'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._image_update()
        self.bind(orientation=self._image_update)

    def _image_update(self, *args):
        image_dict = {'left': GUI_CONST.textures('cap_bar_l'),
                      'right': GUI_CONST.textures('cap_bar_r')}
        self.source = image_dict[self.orientation]


class LCARSOval(Image):
    pass
