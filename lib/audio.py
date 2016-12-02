import os

import pyttsx
import speech_recognition as sr

class AudioInterface(object):
    def __init__(self):
        self._engine = pyttsx.init()
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            print("Google Speech Recognition thinks you said " + r.recognize_google(audio), key=os.environ['GOOGLE'])
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    def speak(self, text):
        self._engine.say(text)
        self._engine.runAndWait()

    def listen(self):
        pass

if __name__ == '__main__':
    audio = AudioInterface()
    audio.speak('hello, whats up')
