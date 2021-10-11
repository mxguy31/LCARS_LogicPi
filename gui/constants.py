from kivy.utils import rgba
from app.constants import CONST


class GUI_CONST(CONST):
    # Directory Structure
    GUI_DIR = CONST.GUI_DIR
    ASSET_DIR = GUI_DIR.joinpath('assets')
    SCREEN_DIR = GUI_DIR.joinpath('screens')
    WIDGET_DIR = GUI_DIR.joinpath('widgets')
    AUDIO_DIR = ASSET_DIR.joinpath('audio')
    FONTS_DIR = ASSET_DIR.joinpath('fonts')
    TEXTURE_DIR = ASSET_DIR.joinpath('textures')

    # File Names
    VOLUME_INI = CONST.CONFIG_DIR.joinpath('sounds.ini')

    # Fonts
    LCARS_BOLD = FONTS_DIR.joinpath('Antonio-Bold.ttf')
    LCARS_SEMI_BOLD = FONTS_DIR.joinpath('Antonio-SemiBold.ttf')
    LCARS_REGULAR = FONTS_DIR.joinpath('Antonio-Regular.ttf')
    LCARS_LIGHT = FONTS_DIR.joinpath('Antonio-Light.ttf')
    LCARS_THIN = FONTS_DIR.joinpath('Antonio-Thin.ttf')

    # Textures
    def textures(texture):
        return 'atlas://' + str(GUI_CONST.TEXTURE_DIR) + '/texture/' + texture

    # colors courtesy of www.thelcars.com
    COLORS = {'white': rgba('F5F6FA'),
              'violet_cream': rgba('DDBBFF'),
              'green': rgba('009900'), #rgba('33CC99'),
              'magenta': rgba('CC4499'),
              'blue': rgba('4455FF'),
              'yellow': rgba('FFCC33'),
              'violet': rgba('9944FF'),
              'orange': rgba('FF7700'),
              'african_violet': rgba('CC88FF'),
              'red': rgba('DD4444'),
              'almond': rgba('FFAA90'),
              'almond_cream': rgba('FFBBAA'),
              'sunflower': rgba('FFCC66'),
              'light_blue': rgba('7788FF'),
              'grey': rgba('666688'),
              'sky': rgba('AAAAFF'),
              'ice': rgba('88CCFF'),
              'gold': rgba('FFAA00'),
              'mars': rgba('FF2200'),
              'peach': rgba('FF8866'),
              'butterscotch': rgba('FF9966'),
              'tomato': rgba('FF5555'),
              'lilac': rgba('CC33FF'),
              '': rgba('F5F6FA')}
