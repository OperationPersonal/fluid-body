import os
import logging

import pyttsx
import speech_recognition
import time

_LOGGER = logging.getLogger('audio')


class AudioInterface(object):

    def __init__(self, interface):
        self._engine = pyttsx.init()
        self._interface = interface
        self._mute = False

    def speak(self, text):
        if not self._mute:
            self._engine.say(text)
            self._engine.runAndWait()

    def mute(self):
        self._mute = not self._mute
        if self._mute:
            _LOGGER.info('Mute')
        else:
            _LOGGER.info('Unmute')

    def listen(self):
        recognizer = speech_recognition.Recognizer()
        microphone = speech_recognition.Microphone()
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
        _LOGGER.info('Listening in background')
        return recognizer.listen_in_background(microphone, self.parse_audio)

    def parse_audio(self, recognizer, audio):
        try:
            phrase = recognizer.recognize_sphinx(
                audio, keyword_entries=[('start', 1), ('stop', 1)])
            _LOGGER.info('Recognized phrase')
            # phrase = recognizer.recognize_google(audio)
            self._interface._state = speech_recognition.STATE_COMPARE
            if 'start' in phrase:
                _LOGGER.info('Starting analysis')
                self.speak('started analysis')
            else:
                self.speak(phrase)
        except speech_recognition.UnknownValueError:
            _LOGGER.info('Unrecognized phrase')
            self.speak("I could not understand you")
        except speech_recognition.RequestError as e:
            _LOGGER.error('Recognition Error: %s', e)
            self.speak("Recognition Error: {0}".format(e))
