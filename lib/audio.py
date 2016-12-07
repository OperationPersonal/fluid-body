import os
import logging

import pyttsx
import speech_recognition
import time


class AudioInterface(object):

    def __init__(self, interface):
        self._engine = pyttsx.init()
        self._interface = interface
        self._mute = False

    def speak(self, text):
        self._engine.say(text)
        self._engine.runAndWait()

    def listen(self):
        recognizer = speech_recognition.Recognizer()
        microphone = speech_recognition.Microphone()
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
        logging.info('Listening in background')
        return recognizer.listen_in_background(microphone, self.parse_audio)

    def parse_audio(self, recognizer, audio):
        try:
            phrase = recognizer.recognize_sphinx(
                audio, keyword_entries=[('start', 1), ('stop', 1)])
            logging.info('Recognized phrase')
            # phrase = recognizer.recognize_google(audio)
            self._interface._state = speech_recognition.STATE_COMPARE
            if 'start' in phrase:
                logging.info('Starting analysis')
                self.speak('started analysis')
            else:
                self.speak(phrase)
        except speech_recognition.UnknownValueError:
            logging.info('Unrecognized phrase')
            self.speak("I could not understand you")
        except speech_recognition.RequestError as e:
            logging.error('Recognition Error: %s', e)
            self.speak("Recognition Error: {0}".format(e))
