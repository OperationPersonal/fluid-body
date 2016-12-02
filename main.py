from lib import gui
from lib import audio
import os

with open('.env', 'r+') as f:
    keys = f.read().split('\n')
    for key in keys:
        if key:
            api, value = key.split('=')
            os.environ[api] = value

g = gui.Gui()
g.run()

# audio = audio.AudioInterface()
# audio.listen()
