import pyttsx
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
from os import environ, path

class AudioInterface(object):
    def __init__(self):
        self._engine = pyttsx.init()
        config = Decoder.default_config()
        config.set_string('-hmm', path.join(MODELDIR, 'en-us/en-us'))
        config.set_string('-lm', path.join(MODELDIR, 'en-us/en-us.lm.bin'))
        config.set_string('-dict', path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
        decoder = Decoder(config)

    def speak(self, text):
        self._engine.say(text)
        self._engine.runAndWait()

    def listen(self):
        pass

if __name__ == '__main__':
    audio = AudioInterface()
    audio.speak('hello, whats up')
