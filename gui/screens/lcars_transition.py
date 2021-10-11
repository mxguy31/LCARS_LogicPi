from kivy.uix.screenmanager import TransitionBase
from kivy.properties import NumericProperty


class LCARSTransition(TransitionBase):
    '''LCARS Transition, changes screen with subtle blanking between screens.
    '''
    duration = NumericProperty(0.3)

    def start(self, manager):
        super(LCARSTransition, self).start(manager)
        self.screen_out.x = manager.x + manager.width
        self.screen_in.x = manager.x + manager.width

    def on_complete(self):
        self.screen_in.pos = self.manager.pos
        self.screen_out.pos = self.manager.pos
        super(LCARSTransition, self).on_complete()