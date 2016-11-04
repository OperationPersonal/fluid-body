# Utility Dependencies
import tempfile

from pykinect2 import PyKinectRuntime as prun
from pykinect2 import PyKinectV2 as pk
from pykinect2.PyKinectV2 import *


# Kinect Dependencies ^


class Lesson(object):

  def __init__(self, lesson=None):
    self._lesson = lesson
    # self._
