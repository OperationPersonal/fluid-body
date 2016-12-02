import pygame as game
from kinectwrapper import traverse
import csv
import math
ANALYSIS_WIDTH = 400

class AnalysisStream(object):

    def __init__(self, kinect, filename=None):
        self._kinect = kinect#KinectStream
        self._analysis_surface = game.Surface((ANALYSIS_WIDTH, self._kinect.colorFrameDesc().Height))
        self.openAnalysis(filename)

    def openAnalysis(self, filename=None):
        self._file_handle = csv.reader(open("data/" + filename, "r"),
                        delimiter=';', skipinitialspace=True) if filename else None

    def getBody(self, body):
        if not self._file_handle:
            return None
        surface = self._analysis_surface
        frame = self.getNextFrame()
        outline = [None for i in range(25)]
        if frame:
            outline[0] = (surface.get_width() / 2, 200)
            for count, (start_limb, end_limb) in enumerate(traverse()):
                if not outline[start_limb]:
                    continue
                length = self._kinect.getBoneLength(count)
                outline[end_limb] = self.get_coords(outline[start_limb], frame[end_limb], length)

        return outline

    def getSurface(self):
        return self._analysis_surface

    def get_coords(self, start, angles, length):
        y = math.sin(angles[0]) * length
        x = math.sin(angles[1]) * length
        return (start[0] + x, start[1] + y)

    def prepSurface(self):
        self._analysis_surface.fill((0, 0, 0))

    def getNextFrame(self):
        try:
            new_frame = self._file_handle.next() if self._file_handle else None
            if not new_frame:
                self._file_handle = None
                return None
            return list(eval(joint) for joint in new_frame)
        except:
            self._file_handle = None
            return None
