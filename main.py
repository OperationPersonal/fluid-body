#!/usr/bin/python

import os
import logging

from lib import gui

"""Launches gui with logging configuration and environment variables"""

__author__ = "Leon Chou and Roy Xu"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_secrets.json'

logging.basicConfig(level=logging.WARNING)
logging.getLogger('comtypes').setLevel(logging.CRITICAL)
logging.getLogger('googleapiclient').setLevel(logging.CRITICAL)
g = gui.Gui()
g.run()
