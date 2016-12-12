#!/usr/bin/python

import pyttsx
import speech_recognition

import logging
import threading
import time

import gameinterface

__author__ = "Leon Chou and Roy Xu"

"""Handles audio. Speech recognition and output"""

_LOGGER = logging.getLogger('audio')
VOICE = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\\'
VOICE_F = VOICE + 'TTS_MS_EN-US_ZIRA_11.0'
VOICE_M = VOICE + 'TTS_MS_EN-US_DAVID_11.0'


class AudioInterface(object):

    def __init__(self, interface=None):
        self._interface = interface
        self._mute = False
        self._line = ''
        self._speaker = threading.Thread(
            target=self.start_audio, name='speaker')
        self._speaker.start()
        self.keep_speaking = True

    def start_audio(self):
        engine = pyttsx.init()
        engine.setProperty(
            'voice', VOICE_F)
        logging.info('Started Audio')
        while self.keep_speaking:
            if not self._mute:
                if self._line:
                    engine.say(self._line)
                    engine.runAndWait()
                    self._line = ''
        logging.info('Stopped Audio')

    def speak(self, line):
        self._line = line

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
            if self._mute:
                return
            phrase = recognizer.recognize_google(audio)
            if self._mute:
                return
            _LOGGER.info('Recognized {}'.format(phrase))
            if 'start' in phrase:
                _LOGGER.info('Starting analysis')
                self.speak('started analysis')
                self._interface.toggle_state()
            elif 'stop' in phrase:
                _LOGGER.info('Stop analysis')
                self.speak('started analysis')
                self._interface.toggle_state()
            elif 'hello' in phrase:
                self.speak('hello')
        except speech_recognition.UnknownValueError:
            _LOGGER.info('Unrecognized phrase')
            # self.speak("I could not understand you")
        except speech_recognition.RequestError as e:
            _LOGGER.error('Recognition Error: %s', e)
            self.speak("Recognition Error: {0}".format(e))
