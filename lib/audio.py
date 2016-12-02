import os

import pyttsx
import speech_recognition
import time

class AudioInterface(object):
    def __init__(self):
        self._engine = pyttsx.init()

    def speak(self, text):
        self._engine.say(text)
        self._engine.runAndWait()

    def listen(self):
        recognizer = speech_recognition.Recognizer()
        microphone = speech_recognition.Microphone()
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=5)
        return recognizer.listen_in_background(microphone, self.parse_audio)

    def parse_audio(self, recognizer, audio):
        try:
            self.speak(recognizer.recognize_google_cloud(audio, preferred_phrases=['start', 'stop']))
        except speech_recognition.UnknownValueError:
            self.speak("Could not understand you")
        except speech_recognition.RequestError as e:
            self.speak("Recognition Error: {0}".format(e))
