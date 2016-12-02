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
        with speech_recognition.Microphone() as source:
            self._recognizer.adjust_for_ambient_noise(source)
            audio = self._recognizer.listen(source)
        try:
            print self._recognizer.recognize_sphinx(audio)
        except speech_recognition.UnknownValueError:
            print("Could not understand audio")
        except speech_recognition.RequestError as e:
            print("Recognition Error: {0}".format(e))
