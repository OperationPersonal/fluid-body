import os

import pyttsx
import speech_recognition
import time

class AudioInterface(object):
    def __init__(self, interface):
        self._engine = pyttsx.init()
        self._interface = interface

    def speak(self, text):
        self._engine.say(text)
        self._engine.runAndWait()

    def listen(self):
        recognizer = speech_recognition.Recognizer()
        microphone = speech_recognition.Microphone()
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
        return recognizer.listen_in_background(microphone, self.parse_audio)

    def parse_audio(self, recognizer, audio):
        try:
            phrase = recognizer.recognize_sphinx(audio, keyword_entries=[('start', 1), ('stop', 1)])
            if phrase == 'start':
                self.speak('started analysis')
                self._interface.start_analysis()
            else:
                self.speak(phrase)
        except speech_recognition.UnknownValueError:
            self.speak("I could not understand you")
        except speech_recognition.RequestError as e:
            self.speak("Recognition Error: {0}".format(e))
