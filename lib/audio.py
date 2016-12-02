import os

import pyttsx
import speech_recognition

class AudioInterface(object):
    def __init__(self):
        self._engine = pyttsx.init()
        self._recognizer = speech_recognition.Recognizer()

    def speak(self, text):
        self._engine.say(text)
        self._engine.runAndWait()

    def listen(self):
        source = speech_recognition.Microphone()
        self._recognizer.adjust_for_ambient_noise(source)
        return source

    def parse_audio(self, source):
        audio = self._recognizer.listen(source)
        try:
            return self._recognizer.recognize_sphinx(audio)
        except speech_recognition.UnknownValueError:
            return "Could not understand audio"
        except speech_recognition.RequestError as e:
            return "Recognition Error: {0}".format(e)

    def loop(self):
        source = self.listen()
        while True:
            print parse_audio(source)

if __name__ == '__main__':
    audio = AudioInterface()
    audio.loop()
