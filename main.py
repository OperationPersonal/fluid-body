from lib import gui
import os

with open('.env', 'r+') as f:
    keys = f.read().split('\n')
    for key in keys:
        api, value = key.split('=')
        os.environ[api] = value

g = gui.Gui()
g.run()
