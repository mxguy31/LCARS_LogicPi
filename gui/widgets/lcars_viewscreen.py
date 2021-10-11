from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import (BooleanProperty,
                             NumericProperty,
                             ColorProperty,
                             ListProperty)
from kivy.lang.builder import Builder
from kivy.animation import Animation
from gui.constants import GUI_CONST
from kivy.clock import Clock

Builder.load_string('''
<LCARSViewScreen>:
#:import GUI_CONST gui.constants.GUI_CONST
    canvas.after:
        # Screen blanking rectangle
        Color:
            rgba: root.blank_color
        Rectangle:
            pos: root.pos
            size: root.size

        Color:
            rgba: root.cap_color
        # Top bar caps
        Rectangle:
            source: GUI_CONST.textures('cap_bar_l')
            pos: root.t_bar_pos
            size: (15, 23)
        Rectangle:
            source: GUI_CONST.textures('cap_bar_r')
            pos: (root.t_bar_pos[0] + root.bar_width + 25, root.t_bar_pos[1])
            size: (15, 23)
        # Bottom bar caps
        Rectangle:
            source: GUI_CONST.textures('cap_bar_l')
            pos: root.b_bar_pos
            size: (15, 23)
        Rectangle:
            source: GUI_CONST.textures('cap_bar_r')
            pos: (root.b_bar_pos[0] + root.bar_width + 25, root.b_bar_pos[1])
            size: (15, 23)

        Color:
            rgba: root.bar_color
        # Bars
        Rectangle:
            pos: (root.t_bar_pos[0] + 20, root.t_bar_pos[1])
            size: (root.bar_width, 23)
        Rectangle:
            pos: (root.b_bar_pos[0] + 20, root.b_bar_pos[1])
            size: (root.bar_width, 23)
''')


class LCARSViewScreen(RelativeLayout):
    open_screen = BooleanProperty(False)
    animation_time = NumericProperty(0.2)
    blank_color = ColorProperty([0, 0, 0, 1])
    t_bar_pos = ListProperty([0, 0])
    b_bar_pos = ListProperty([0, 0])
    bar_width = NumericProperty(0)
    cap_color = ColorProperty(GUI_CONST.COLORS['tomato'])
    bar_color = ColorProperty(GUI_CONST.COLORS['african_violet'])

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self.update_view)
        self.bind(size=self.update_view)
        self.bind(open_screen=self.update_view)
        self.screen_is_open = False
        self.in_progress = False

        self.cap_color[3] = 0

    def update_view(self, *args):
        animate = None
        if self.screen_is_open and self.open_screen:
            # Screen is open
            self.t_bar_pos = (self.x, self.y + self.height - 23)
            self.b_bar_pos = (self.x, self.y)
            self.bar_width = self.width - 40
        elif not self.screen_is_open and self.open_screen:
            if self.in_progress:
                # if an animation is in progress wait until it is complete
                Clock.schedule_once(self.update_view, 0)
                return
            # Open the screen
            self.screen_is_open = self.open_screen
            screen_opacity = Animation(blank_color=(0, 0, 0, 0),
                                       d=self.animation_time / 4)

            bar_scale = Animation(bar_width=self.width - 40,
                                  t_bar_pos=(self.x,
                                             (self.y + self.height - 23) / 2),
                                  b_bar_pos=(self.x,
                                             (self.y + self.height - 23) / 2),
                                  d=self.animation_time / 2)

            bar_move = Animation(t_bar_pos=(self.x,
                                            self.y + self.height - 23),
                                 b_bar_pos=(self.x, self.y),
                                 d=self.animation_time / 2)
            bar_opacity = Animation(cap_color=(self.cap_color[0],
                                               self.cap_color[1],
                                               self.cap_color[2],
                                               1),
                                    d=self.animation_time / 4
                                    )
            animate = bar_opacity + bar_scale + bar_move + screen_opacity
        elif self.screen_is_open and not self.open_screen:
            if self.in_progress:
                # if an animation is in progress wait until it is complete
                Clock.schedule_once(self.update_view, 0)
                return
            # Close the screen
            self.screen_is_open = self.open_screen
            screen_opacity = Animation(blank_color=(0, 0, 0, 1),
                                       d=self.animation_time / 4)

            bar_scale = Animation(bar_width=0,
                                  t_bar_pos=(self.x + (self.width / 2),
                                             (self.y + self.height - 23) / 2),
                                  b_bar_pos=(self.x + (self.width / 2),
                                             (self.y + self.height - 23) / 2),
                                  d=self.animation_time / 2)

            bar_move = Animation(t_bar_pos=(self.x,
                                            (self.y + self.height - 23) / 2),
                                 b_bar_pos=(self.x,
                                            (self.y + self.height - 23) / 2),
                                 d=self.animation_time / 2)
            bar_opacity = Animation(cap_color=(self.cap_color[0],
                                               self.cap_color[1],
                                               self.cap_color[2],
                                               0),
                                    d=self.animation_time / 4)
            animate = screen_opacity + bar_move + bar_scale + bar_opacity
        else:
            # Screen is closed
            self.t_bar_pos = (self.x + (self.width / 2),
                              (self.y + self.height - 23) / 2)
            self.b_bar_pos = (self.x + (self.width / 2),
                              (self.y + self.height - 23) / 2)
            self.bar_width = 0

        if animate:
            animate.bind(on_complete=self.complete)
            self.in_progress = True
            animate.start(self)

    def complete(self, *args):
        self.in_progress = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.screen_is_open:
                return super(LCARSViewScreen, self).on_touch_down(touch)
            else:
                return True
