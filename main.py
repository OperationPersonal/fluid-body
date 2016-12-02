from lib import gui
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_secrets.json'

g = gui.Gui()
g.run()
