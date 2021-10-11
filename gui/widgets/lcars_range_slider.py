"""
Slider
======

.. image:: images/slider.jpg

The :class:`Slider` widget looks like a scrollbar. It supports horizontal and
vertical orientations, min/max values and a default value.

To create a slider from -100 to 100 starting from 25::

    from kivy.uix.slider import Slider
    s = Slider(min=-100, max=100, value=25)

To create a vertical slider::

    from kivy.uix.slider import Slider
    s = Slider(orientation='vertical')

To create a slider with a red line tracking the value::

    from kivy.uix.slider import Slider
    s = Slider(value_track=True, value_track_color=[1, 0, 0, 1])


Kv Example::

    BoxLayout:
        Slider:
            id: slider
            min: 0
            max: 100
            step: 1
            orientation: 'vertical'

        Label:
            text: str(slider.value)

"""
__all__ = ('Slider', )
from kivy.lang import Builder
from kivy.uix.widget import Widget
from gui.constants import GUI_CONST
from kivy.properties import (NumericProperty, AliasProperty, OptionProperty,
                             ReferenceListProperty, BoundedNumericProperty,
                             StringProperty, ListProperty, BooleanProperty,
                             ColorProperty)

# Added to override the native .kv description to include two cursors.
Builder.load_string('''
<LCARSRangeSlider>:
    canvas:
        Color:
            rgba: root.background_color
        BorderImage:
            border: self.border_horizontal if self.orientation == 'horizontal' else self.border_vertical
            pos: (self.x + self.padding, self.center_y - self.background_width / 2) if self.orientation == 'horizontal' else (self.center_x - self.background_width / 2, self.y + self.padding)
            size: (self.width - self.padding * 2, self.background_width) if self.orientation == 'horizontal' else (self.background_width, self.height - self.padding * 2)
            source: (self.background_disabled_horizontal if self.orientation == 'horizontal' else self.background_disabled_vertical) if self.disabled else (self.background_horizontal if self.orientation == 'horizontal' else self.background_vertical)
        Color:
            rgba: root.value_track_color if self.value_track and self.orientation == 'horizontal' else [1, 1, 1, 0]
        Line:
            width: self.value_track_width
            points: self.value1_pos[0], self.center_y, self.value2_pos[0], self.center_y
        Color:
            rgba: root.value_track_color if self.value_track and self.orientation == 'vertical' else [1, 1, 1, 0]
        Line:
            width: self.value_track_width
            points: self.center_x, self.value1_pos[1], self.center_x, self.value2_pos[1]
        Color:
            rgba: root.background_color
    Image:
        pos: (root.value1_pos[0] - root.cursor_width / 2, root.center_y - root.cursor_height / 2) if root.orientation == 'horizontal' else (root.center_x - root.cursor_width / 2, root.value1_pos[1] - root.cursor_height / 2)
        size: root.cursor_size
        source: root.cursor_disabled_image if root.disabled else root.cursor_image
        allow_stretch: True
        keep_ratio: False
        color: root.cursor_color
    Image:
        pos: (root.value2_pos[0] - root.cursor_width / 2, root.center_y - root.cursor_height / 2) if root.orientation == 'horizontal' else (root.center_x - root.cursor_width / 2, root.value2_pos[1] - root.cursor_height / 2)
        size: root.cursor_size
        source: root.cursor_disabled_image if root.disabled else root.cursor_image
        allow_stretch: True
        keep_ratio: False
        color:root.cursor_color
''')


class LCARSRangeSlider(Widget):
    """Class for creating a Slider widget.

    Check module documentation for more details.
    """
    ##############################
    # Modification
    # The following two methods allow the value property to be a list of
    # value1 and value2

    def _get_value(self):
        return [self.value1, self.value2]

    def _set_value(self, value):
        self.value1, self.value2 = value

    # Now represents both value1 and value2
    value = AliasProperty(_get_value, _set_value, bind=('value1', 'value2'))
    '''Current value used for the both sliders.

    :attr:`value` is an :class:`~kivy.properties.AliasProperty` and defaults
    to [0, 0].'''

    value1 = NumericProperty(0.)
    '''Current value used for the first slider.

    :attr:`value` is a :class:`~kivy.properties.NumericProperty` and defaults
    to 0.'''

    value2 = NumericProperty(100.)
    '''Current value used for the second slider.

    :attr:`value` is a :class:`~kivy.properties.NumericProperty` and defaults
    to 0.'''
    
    # added to allow a minimum difference between the sliders
    min_diff = NumericProperty(0.)

    # End of Modification
    ##############################

    min = NumericProperty(0.)
    '''Minimum value allowed for :attr:`value`.

    :attr:`min` is a :class:`~kivy.properties.NumericProperty` and defaults to
    0.'''

    max = NumericProperty(100.)
    '''Maximum value allowed for :attr:`value`.

    :attr:`max` is a :class:`~kivy.properties.NumericProperty` and defaults to
    100.'''

    padding = NumericProperty('16sp')
    '''Padding of the slider. The padding is used for graphical representation
    and interaction. It prevents the cursor from going out of the bounds of the
    slider bounding box.

    By default, padding is 16sp. The range of the slider is reduced from
    padding \\*2 on the screen. It allows drawing the default cursor of 32sp
    width without having the cursor go out of the widget.

    :attr:`padding` is a :class:`~kivy.properties.NumericProperty` and defaults
    to 16sp.'''

    orientation = OptionProperty('horizontal', options=(
        'vertical', 'horizontal'))
    '''Orientation of the slider.

    :attr:`orientation` is an :class:`~kivy.properties.OptionProperty` and
    defaults to 'horizontal'. Can take a value of 'vertical' or 'horizontal'.
    '''

    range = ReferenceListProperty(min, max)
    '''Range of the slider in the format (minimum value, maximum value)::

        >>> slider = Slider(min=10, max=80)
        >>> slider.range
        [10, 80]
        >>> slider.range = (20, 100)
        >>> slider.min
        20
        >>> slider.max
        100

    :attr:`range` is a :class:`~kivy.properties.ReferenceListProperty` of
    (:attr:`min`, :attr:`max`) properties.
    '''

    step = BoundedNumericProperty(0, min=0)
    '''Step size of the slider.

    .. versionadded:: 1.4.0

    Determines the size of each interval or step the slider takes between
    :attr:`min` and :attr:`max`. If the value range can't be evenly
    divisible by step the last step will be capped by slider.max.
    A zero value will result in the smallest possible intervals/steps,
    calculated from the (pixel) position of the slider.

    :attr:`step` is a :class:`~kivy.properties.NumericProperty` and defaults
    to 0.'''

    background_horizontal = StringProperty(
        GUI_CONST.textures('btn'))
    """Background of the slider used in the horizontal orientation.

    .. versionadded:: 1.10.0

    :attr:`background_horizontal` is a :class:`~kivy.properties.StringProperty`
    and defaults to `atlas://data/images/defaulttheme/sliderh_background`.
    """

    background_disabled_horizontal = StringProperty(
        GUI_CONST.textures('btn_dn'))
    """Background of the disabled slider used in the horizontal orientation.

    .. versionadded:: 1.10.0

    :attr:`background_disabled_horizontal` is a
    :class:`~kivy.properties.StringProperty` and defaults to
    `atlas://data/images/defaulttheme/sliderh_background_disabled`.
    """

    background_vertical = StringProperty(
        GUI_CONST.textures('btn'))
    """Background of the slider used in the vertical orientation.

    .. versionadded:: 1.10.0

    :attr:`background_vertical` is a :class:`~kivy.properties.StringProperty`
    and defaults to `atlas://data/images/defaulttheme/sliderv_background`.
    """

    background_disabled_vertical = StringProperty(
        GUI_CONST.textures('btn_dn'))
    """Background of the disabled slider used in the vertical orientation.

    .. versionadded:: 1.10.0

    :attr:`background_disabled_vertical` is a
    :class:`~kivy.properties.StringProperty` and defaults to
    `atlas://data/images/defaulttheme/sliderv_background_disabled`.
    """

    background_width = NumericProperty('8dp')
    """Slider's background's width (thickness), used in both horizontal
    and vertical orientations.

    .. versionadded 1.10.0

    :attr:`background_width` is a
    :class:`~kivy.properties.NumericProperty` and defaults to 36sp.
    """

    background_color = ColorProperty(GUI_CONST.COLORS['grey'])

    cursor_image = StringProperty(GUI_CONST.textures('oval'))
    """Path of the image used to draw the slider cursor.

    .. versionadded 1.10.0

    :attr:`cursor_image` is a :class:`~kivy.properties.StringProperty`
    and defaults to `atlas://data/images/defaulttheme/slider_cursor`.
    """

    cursor_disabled_image = StringProperty(GUI_CONST.textures('oval_dn'))
    """Path of the image used to draw the disabled slider cursor.

    .. versionadded 1.10.0

    :attr:`cursor_image` is a :class:`~kivy.properties.StringProperty`
    and defaults to `atlas://data/images/defaulttheme/slider_cursor_disabled`.
    """

    cursor_width = NumericProperty('45dp')
    """Width of the cursor image.

    .. versionadded 1.10.0

    :attr:`cursor_width` is a :class:`~kivy.properties.NumericProperty`
    and defaults to 32sp.
    """

    cursor_height = NumericProperty('30dp')
    """Height of the cursor image.

    .. versionadded 1.10.0

    :attr:`cursor_height` is a :class:`~kivy.properties.NumericProperty`
    and defaults to 32sp.
    """

    cursor_size = ReferenceListProperty(cursor_width, cursor_height)
    """Size of the cursor image.

    .. versionadded 1.10.0

    :attr:`cursor_size` is a :class:`~kivy.properties.ReferenceListProperty`
    of (:attr:`cursor_width`, :attr:`cursor_height`) properties.
    """

    cursor_color = ColorProperty(GUI_CONST.COLORS['african_violet'])
    """Color of the cursor
    """

    border_horizontal = ListProperty([0, 18, 0, 18])
    """Border used to draw the slider background in horizontal orientation.

    .. versionadded 1.10.0

    :attr:`border_horizontal` is a :class:`~kivy.properties.ListProperty`
    and defaults to [0, 18, 0, 18].
    """

    border_vertical = ListProperty([18, 0, 18, 0])
    """Border used to draw the slider background in vertical orientation.

    .. versionadded 1.10.0

    :attr:`border_horizontal` is a :class:`~kivy.properties.ListProperty`
    and defaults to [18, 0, 18, 0].
    """

    value_track = BooleanProperty(False)
    """Decides if slider should draw the line indicating the
    space between :attr:`min` and :attr:`value` properties values.

    .. versionadded 1.10.0

    :attr:`value_track` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to False.
    """

    value_track_color = ColorProperty(GUI_CONST.COLORS['grey'])
    """Color of the :attr:`value_line` in rgba format.

    .. versionadded 1.10.0

    :attr:`value_track_color` is a :class:`~kivy.properties.ColorProperty`
    and defaults to [1, 1, 1, 1].

    .. versionchanged:: 2.0.0
        Changed from :class:`~kivy.properties.ListProperty` to
        :class:`~kivy.properties.ColorProperty`.
    """

    value_track_width = NumericProperty('3dp')
    """Width of the track line.

    .. versionadded 1.10.0

    :attr:`value_track_width` is a :class:`~kivy.properties.NumericProperty`
    and defaults to 3dp.
    """

    # This no longer functions as it was causing problems with having two
    # cursors.
    # TODO add this functionality back.
    sensitivity = OptionProperty('all', options=('all', 'handle'))
    """Whether the touch collides with the whole body of the widget
    or with the slider handle part only.

    .. versionadded:: 1.10.1

    :attr:`sensitivity` is a :class:`~kivy.properties.OptionProperty`
    and defaults to 'all'. Can take a value of 'all' or 'handle'.
    """

    # The following two methods constrain the slider's value
    # to range(min,max). Otherwise it may happen that self.value < self.min

    def on_min(self, *largs):
        # Modified to include both sliders
        self.value1 = min(self.min, max(self.min, self.value1))
        self.value2 = max(self.min, self.value2)

    def on_max(self, *largs):
        # Modified to include both sliders
        self.value1 = min(self.max, self.value1)
        self.value2 = max(self.max, min(self.max, self.value2))

    def get_norm_value1(self):
        # Modified to be slider 1
        vmin = self.min
        d = self.max - vmin
        if d == 0:
            return 0
        return (self.value1 - vmin) / float(d)

    def get_norm_value2(self):
        # Added to cover slider 2
        vmin = self.min
        d = self.max - vmin
        if d == 0:
            return 0
        return (self.value2 - vmin) / float(d)

    def set_norm_value1(self, value):
        # Modified for slider 1 and to use slider 2 as its max position value
        vmin = self.min
        vmax = self.max
        step = self.step
        val = min(value * (vmax - vmin) + vmin, vmax)
        if step == 0:
            self.value1 = val
        else:
            self.value1 = min(round((val - vmin) / step) * step + vmin,
                              self.value2)

    def set_norm_value2(self, value):
        # Added to cover slider 2
        vmin = self.min
        vmax = self.max
        step = self.step
        val = min(value * (vmax - vmin) + vmin, vmax)
        if step == 0:
            self.value2 = val
        else:
            self.value2 = max(self.value1,
                              round((val - vmin) / step) * step + vmin)

    # Modified for value 1
    value1_normalized = AliasProperty(get_norm_value1, set_norm_value1,
                                      bind=('value1', 'min', 'max'),
                                      cache=True)
    # Added for value 2
    value2_normalized = AliasProperty(get_norm_value2, set_norm_value2,
                                      bind=('value2', 'min', 'max'),
                                      cache=True)

    '''Normalized value inside the :attr:`range` (min/max) to 0-1 range::

        >>> slider = Slider(value=50, min=0, max=100)
        >>> slider.value
        50
        >>> slider.value_normalized
        0.5
        >>> slider.value = 0
        >>> slider.value_normalized
        0
        >>> slider.value = 100
        >>> slider.value_normalized
        1

    You can also use it for setting the real value without knowing the minimum
    and maximum::

        >>> slider = Slider(min=0, max=200)
        >>> slider.value_normalized = .5
        >>> slider.value
        100
        >>> slider.value_normalized = 1.
        >>> slider.value
        200

    :attr:`value_normalized` is an :class:`~kivy.properties.AliasProperty`.
    '''

    def get_value1_pos(self):
        # Modifed for value 1
        padding = self.padding
        x = self.x
        y = self.y
        nval = self.value1_normalized
        if self.orientation == 'horizontal':
            return (x + padding + nval * (self.width - 2 * padding), y)
        else:
            return (x, y + padding + nval * (self.height - 2 * padding))

    def get_value2_pos(self):
        # Added for value 1
        padding = self.padding
        x = self.x
        y = self.y
        nval = self.value2_normalized
        if self.orientation == 'horizontal':
            return (x + padding + nval * (self.width - 2 * padding), y)
        else:
            return (x, y + padding + nval * (self.height - 2 * padding))

    def set_value1_pos(self, pos):
        # Modifed for value 1
        padding = self.padding
        x = min(self.right - padding, max(pos[0], self.x + padding))
        y = min(self.top - padding, max(pos[1], self.y + padding))
        if self.orientation == 'horizontal':
            if self.width == 0:
                self.value1_normalized = 0
            else:
                self.value1_normalized = (x - self.x - padding
                                          ) / float(self.width - 2 * padding)
        else:
            if self.height == 0:
                self.value1_normalized = 0
            else:
                self.value1_normalized = (y - self.y - padding
                                          ) / float(self.height - 2 * padding)

    def set_value2_pos(self, pos):
        # Added for value 2
        padding = self.padding
        x = min(self.right - padding, max(pos[0], self.x + padding))
        y = min(self.top - padding, max(pos[1], self.y + padding))
        if self.orientation == 'horizontal':
            if self.width == 0:
                self.value2_normalized = 0
            else:
                self.value2_normalized = (x - self.x - padding
                                          ) / float(self.width - 2 * padding)
        else:
            if self.height == 0:
                self.value2_normalized = 0
            else:
                self.value2_normalized = (y - self.y - padding
                                          ) / float(self.height - 2 * padding)

    # Modified for value 1
    value1_pos = AliasProperty(get_value1_pos, set_value1_pos,
                               bind=('pos', 'size', 'min', 'max', 'padding',
                                     'value1_normalized', 'orientation'),
                               cache=True)
    # Added for value 2
    value2_pos = AliasProperty(get_value2_pos, set_value2_pos,
                               bind=('pos', 'size', 'min', 'max', 'padding',
                                     'value2_normalized', 'orientation'),
                               cache=True)

    '''Position of the internal cursor, based on the normalized value.

    :attr:`value_pos` is an :class:`~kivy.properties.AliasProperty`.
    '''

    def _touch_normalized_value(self, touch):
        # Added to calculate the normalized position of the touch, this is used
        # to determine which cursor is being requested.
        pos = touch.pos
        padding = self.padding
        x = min(self.right - padding, max(pos[0], self.x + padding))
        y = min(self.top - padding, max(pos[1], self.y + padding))
        if self.orientation == 'horizontal':
            value = (x - self.x - padding
                     ) / float(self.width - 2 * padding)
        else:
            value = (y - self.y - padding
                     ) / float(self.height - 2 * padding)
        return value

    def on_touch_down(self, touch):
        # Removed mouse scroll support as it doesn't make sense with two
        # cursors. Removed sensitivity support as this causes conflicts with
        # two cursors.
        # Modified to also determine which cursor is being requested
        if self.disabled or not self.collide_point(*touch.pos):
            return
        touch.grab(self)
        t_value = self._touch_normalized_value(touch)
        tv1 = abs(self.value1_normalized - t_value)
        tv2 = abs(self.value2_normalized - t_value)
        if (tv1 < tv2) or (t_value < self.value1_normalized):
            self.value1_pos = touch.pos
            touch.ud['cursorid'] = 1
        elif (tv1 > tv2) or (t_value > self.value2_normalized):
            self.value2_pos = touch.pos
            touch.ud['cursorid'] = 2
        return True

    def on_touch_move(self, touch):
        # Modified to move the requested cursor
        if touch.grab_current == self:
            if 'cursorid' in touch.ud:
                if touch.ud['cursorid'] == 1:
                    self.value1_pos = touch.pos
                    if self.value1 > self.value2 - self.min_diff:
                        self.value1 = self.value2 - self.min_diff
                elif touch.ud['cursorid'] == 2:
                    self.value2_pos = touch.pos
                    if self.value2 < self.value1 + self.min_diff:
                        self.value2 = self.value1 + self.min_diff
                return True

    def on_touch_up(self, touch):
        # Modified to just release the grab, as down and move will position
        # the cursor.
        if touch.grab_current == self:
            touch.ungrab(self)
            return True


if __name__ == '__main__':
    from kivy.app import App

    class SliderApp(App):
        def build(self):
            return LCARSRangeSlider(padding=25)

    SliderApp().run()
