#!/usr/bin/python

import pygame as game
from pykinect2 import PyKinectV2
import ctypes

import logging
import math
import csv

import kinectwrapper as kinect

"""Analyzes stored file streams for analysis surface"""

__author__ = "Leon Chou and Roy Xu"

ANALYSIS_WIDTH = 400

FLIP = [4, 12]
D_FLIP = [5, 6, 7, 13, 14, 15, 21, 22]

_LOGGER = logging.getLogger('analysis')


class AnalysisStream(object):

    def __init__(self, kinect, filename=None):
        self._kinect = kinect
        self._analysis_surface = game.Surface(
            (ANALYSIS_WIDTH, self._kinect.colorFrameDesc().Height))
        if filename:
            self.openAnalysis(filename)
        self._curr = 0

    def get_width(self):
        return ANALYSIS_WIDTH

    def openAnalysis(self, filename=None):
        if filename:
            file_handle = csv.reader(
                open("data/" + filename, "r"), delimiter=';',
                skipinitialspace=True)
            self._frames = [row for row in file_handle]
        else:
            self._frames = None

    def close(self):
        try:
            self._kinect.close()
        except:
            pass

    def flip_coord(self, coord, mid):
        return 2 * mid - coord

    def getBody(self, body):
        if not self._frames:
            return None
        surface = self._analysis_surface
        frame = self.getNextFrame()
        outline = [None for i in range(25)]
        if frame:
            mid = surface.get_width() / 2
            outline[0] = PyKinectV2._CameraSpacePoint(
                body.joints[0].Position.x, body.joints[0].Position.y,
                body.joints[0].Position.z)
            # outline[0] = (mid,
            #               surface.get_height() / 2, 0)
            for count, (start_limb, end_limb) in enumerate(kinect.traverse()):
                if not outline[start_limb]:
                    continue
                length = self._kinect.getBoneLength(count)
                outline[end_limb] = PyKinectV2._CameraSpacePoint(
                    *self.get_coords(outline[start_limb],
                                     frame[end_limb], length))
                # outline[end_limb] = self.get_coords(
                #     outline[start_limb], frame[end_limb], length)

            color_space = [
                self._kinect._kinect._mapper.MapCameraPointToColorSpace(x)
                for x in outline]

            lines = []
            for start, end in kinect.traverse():
                #     if end in D_FLIP:
                #         x1 = self.flip_coord(outline[start][0], mid)
                #         x2 = self.flip_coord(outline[end][0], mid)
                #     elif end in FLIP:
                #         x1 = outline[start][0]
                #         x2 = self.flip_coord(outline[end][0], mid)
                #     else:
                #         x1 = outline[start][0]
                #         x2 = outline[end][0]
                lines.append(
                    ((color_space[start].x, color_space[start].y),
                     (color_space[end].x, color_space[end].y)))
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
        end_v = self.quaternion_multiply(
            self.quaternion_multiply(quat, r), q_conj)[1:]
        return (end_v[0] + start.x, end_v[1] + start.y, + end_v[2] + start.z)

    def prepSurface(self):
        self._analysis_surface.fill((0, 0, 0))

    def adjustFramePos(self, position):
        self._curr = position

    def frameBack(self):
        self.adjustFramePos(position - gameinterface.FPS)

    def getNextFrame(self):
        try:
            new_frame = self._frames[self._curr]
            self._curr += 1
            return list(eval(joint) for joint in new_frame)
        except:
            self._file_handle = None
            return None
