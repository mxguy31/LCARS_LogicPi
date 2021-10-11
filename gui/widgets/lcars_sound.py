import configparser

from gui.constants import GUI_CONST

# from kivy.core.audio import SoundLoader
from subprocess import Popen


class SoundMachine():
    def __init__(self) -> None:
        self.sounds = dict()
        config_file = GUI_CONST.VOLUME_INI
        if config_file.is_file():
            try:
                config = configparser.ConfigParser()
                config.optionxform = str
                config.read(config_file)
                if 'SOUNDS' in config.sections():
                    for sound in config['SOUNDS']:
                        # This is a hack to ensure that volume results to 50%
                        # if it is not included
                        # https://stackoverflow.com/questions/44609040/safely-unpacking-results-of-str-split
                        file, *volume = config['SOUNDS'][sound].split(';')
                        volume = volume[0] if volume else 50.0
                        try:
                            volume = float(volume) / 100
                        except ValueError:
                            volume = 0.5

                        file = GUI_CONST.AUDIO_DIR.joinpath(file)
                        # self.sounds[sound] = SoundLoader.load(str(file))
                        # self.sounds[sound].volume = volume
                        self.sounds[sound] = file
                else:
                    self.sounds = dict()
            except IOError:
                self.sounds = dict()
        else:
            self.sounds = dict()

    def play_sound(self, sound, *args):
        if sound not in self.sounds:
            return
        else:
            if self.sounds[sound].exists():
                Popen(['aplay', '-q', self.sounds[sound]])

    '''def beep(self, *args):
        self.sounds['beep'].play()

    def accept(self, *args):
        self.sounds['accept'].play()

    def cancel(self, *args):
        self.sounds['cancel'].play()

    def deny(self, *args):
        self.sounds['deny'].play()

    def screen_off(self, *args):
        self.sounds['screen_off'].play()

    def screen_on(self, *args):
        self.sounds['screen_on'].play()

    def busy(self, *args):
        self.sounds['busy'].play()

    def hail(self, *args):
        self.sounds['hail'].play()

    def alert(self, *args):
        self.sounds['alert'].play()

    def critical(self, *args):
        self.sounds['critical'].play()

    def alarm_clear(self, *args):
        self.sounds['clear'].play()'''
