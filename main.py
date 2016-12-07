from lib import gui
from lib import kinectwrapper
import os
import logging

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_secrets.json'

print list(kinectwrapper.traverse())

logging.basicConfig(level=logging.INFO)
logging.getLogger('comtypes').setLevel(logging.CRITICAL)
g = gui.Gui()
g.run()
