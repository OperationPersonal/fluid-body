import pyttsx

class AudioInterface(object):
    def __init__(self):
        self._engine = pyttsx.init()

    def queue(self, text):
        self._engine.say(text)

    def speak(self):
        self._engine.runAndWait()
