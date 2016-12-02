import pyttsx

class AudioInterface(object):
    def __init__(self):
        self._engine = pyttsx.init()

    def output(self, text):
        self._engine.say(text)
        self._engine.runAndWait()

if __name__ == '__main__':
    audio = AudioInterface()
    audio.output('hello')