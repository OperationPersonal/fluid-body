from lib import gui
from lib import kinectwrapper
import os
import logging

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_secrets.json'

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('comtypes').setLevel(logging.CRITICAL)
g = gui.Gui()
g.run()

# print list(kinectwrapper.traverse())
