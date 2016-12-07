import pygame as game
from kinectwrapper import traverse
import csv
import math
import logging
import numpy as np
ANALYSIS_WIDTH = 400

FLIP = [4, 12]
D_FLIP = [5, 6, 7, 13, 14, 15, 21, 22]
# FLIP = []


class AnalysisStream(object):

    def __init__(self, kinect, filename=None):
        self._kinect = kinect  # KinectStream
        self._analysis_surface = game.Surface(
            (ANALYSIS_WIDTH, self._kinect.colorFrameDesc().Height))
        if filename:
            self.openAnalysis(filename)

    def openAnalysis(self, filename=None):
        self._file_handle = csv.reader(open("data/" + filename, "r"),
                                       delimiter=';', skipinitialspace=True) if filename else None

    def flip_coord(self, coord, mid):
        return 2 * mid - coord

    def getBody(self, body):
        if not self._file_handle:
            return None
        surface = self._analysis_surface
        frame = self.getNextFrame()
        outline = [None for i in range(25)]
        if frame:
            mid = surface.get_width() / 2
            outline[0] = (mid,
                          surface.get_height() / 4 * 3, 0)
            for count, (start_limb, end_limb) in enumerate(traverse()):
                if not outline[start_limb]:
                    continue
                length = self._kinect.getBoneLength(count)
                outline[end_limb] = self.get_coords(
                    outline[start_limb], frame[end_limb], length)

        lines = []
        for start, end in traverse():
            logging.info('{}, {}'.format(start, end))
            if end in D_FLIP:
                x1 = self.flip_coord(outline[start][0], mid)
                x2 = self.flip_coord(outline[end][0], mid)
            elif end in FLIP:
                x1 = outline[start][0]
                x2 = self.flip_coord(outline[end][0], mid)
            else:
                x1 = outline[start][0]
                x2 = outline[end][0]
            lines.append(
                ((x1, outline[start][1]), (x2, outline[end][1])))
        return lines

    def getSurface(self):
        return self._analysis_surface

    def quaternion_multiply(self, q, r):
        return [r[0] * q[0] - r[1] * q[1] - r[2] * q[2] - r[3] * q[3],
                r[0] * q[1] + r[1] * q[0] - r[2] * q[3] + r[3] * q[2],
                r[0] * q[2] + r[1] * q[3] + r[2] * q[0] - r[3] * q[1],
                r[0] * q[3] - r[1] * q[2] + r[2] * q[1] + r[3] * q[0]]

    def get_coords(self, start, quat, length):
        r = [0, 0, length, 0]
        q_conj = [quat[0], -1 * quat[1], -1 * quat[2], -1 * quat[3]]
        return [x + y for x, y in zip(self.quaternion_multiply(self.quaternion_multiply(quat, r), q_conj)[1:], start)]

    def prepSurface(self):
        self._analysis_surface.fill((0, 0, 0))
        # pass

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
