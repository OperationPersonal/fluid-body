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

_LOGGER = logging.getLogger('analysis')


class AnalysisStream(object):
    """Wrapper class for the file reading and calculating of degrees to current body"""

    def __init__(self, kinect, filename=None):
        self._kinect = kinect
        if filename:
            self.openAnalysis(filename)
        self._curr = 0
        self._camera_to_color = self._kinect._kinect._mapper.MapCameraPointToColorSpace

    def get_width(self):
        """Wrapper for the constant ANALYSIS_WIDTH"""
        return ANALYSIS_WIDTH

    def openAnalysis(self, filename=None):
        """Creates the file handle for filename within the class instance"""
        if filename:
            file_handle = csv.reader(
                open("data/" + filename, "r"), delimiter=';',
                skipinitialspace=True)
            self._frames = [row for row in file_handle]
        else:
            self._frames = None

    def close(self):
        """Closes the kinect and the file handle cleanly"""

        try:
            self._kinect.close()
        except:
            pass

    def flip_coord(self, coord, mid):
        """Flips coordinate tuple by a point"""

        return 2 * mid - coord

    def getBody(self, body, speed=4):
        """Iterates over traverse and frame to return the next corresponding frame of the analysis"""

        try:
            return self._frames.next()
        except:
            self._frames= self.generateNextFrames(body, speed)
            return self._frames.next()

        # frame = self.getNextFrames()
        # outline = [None for i in range(25)]
        # if frame:
        #     outline[0] = PyKinectV2._CameraSpacePoint(
        #         body.joints[0].Position.x, body.joints[0].Position.y,
        #         body.joints[0].Position.z)
        #
        #     color_space = [None for i in range(25)]
        #     color_space[0] = self._camera_to_color(outline[0])
        #     for count, (start_limb, end_limb) in enumerate(kinect.traverse()):
        #         if not outline[start_limb]:
        #             continue
        #         length = self._kinect.getBoneLength(count)
        #         coords = self.get_coords(outline[start_limb],
        #                                  frame[end_limb], length)
        #         outline[end_limb] = PyKinectV2._CameraSpacePoint(*coords)
        #         color_space[end_limb] = self._camera_to_color(outline[
        #                                                       end_limb])
        #
        #     for start, end in kinect.traverse():
        #         yield ((color_space[start].x, color_space[start].y),
        #                (color_space[end].x, color_space[end].y))
        # else:
        #     yield (None, None)

    def _get_points(self, frame, body):
        outline = [None for i in range(25)]
        if frame:
            outline[0] = PyKinectV2._CameraSpacePoint(
                body.joints[0].Position.x, body.joints[0].Position.y,
                body.joints[0].Position.z)

            color_space = [None for i in range(25)]
            color_space[0] = self._camera_to_color(outline[0])
            for count, (start_limb, end_limb) in enumerate(kinect.traverse()):
                if not outline[start_limb]:
                    continue
                length = self._kinect.getBoneLength(count)
                coords = self.get_coords(outline[start_limb],
                                         frame[end_limb], length)
                outline[end_limb] = PyKinectV2._CameraSpacePoint(*coords)
                color_space[end_limb] = self._camera_to_color(outline[
                                                              end_limb])

            for start, end in kinect.traverse():
                yield ((color_space[start].x, color_space[start].y),
                       (color_space[end].x, color_space[end].y))

    def generateNextFrames(self, body, speed=4, precision=2):
        frames = list(self.getNextFrames(2))
        if len(frames) == 1:
            yield self._get_points(frames[0], body)
            return
        for i in range(len(frames) - 1):
            curr, ref = frames[i], frames[i + 1]

            curr_points, ref_points = self._get_points(curr, body), self._get_points(ref, body)

            for s in speed:
                frame = []
                for (x1, y1), (x2, y2) in zip(curr, ref):
                    dx = s * (x2 - x1) / speed
                    dy = s * (y2 - y1) / speed
                    frame.append((x1 + dx, y1 + dy))
                yield frame

    def getSurface(self):
        """Wrapper for the surface contained"""
        return self._analysis_surface

    def quaternion_multiply(self, q, r):
        """vector multiplication to rotate it"""
        return [r[0] * q[0] - r[1] * q[1] - r[2] * q[2] - r[3] * q[3],
                r[0] * q[1] + r[1] * q[0] - r[2] * q[3] + r[3] * q[2],
                r[0] * q[2] + r[1] * q[3] + r[2] * q[0] - r[3] * q[1],
                r[0] * q[3] - r[1] * q[2] + r[2] * q[1] + r[3] * q[0]]

    def get_coords(self, start, quat, length):
        """Takes a previous coordinate, a quaternion, and a scalar
        returns a tuple representing the initial vector multiplied by the quat
        with length = length"""
        r = [0.0, 0.0, length, 0.0]
        q_conj = [quat[0], -1 * quat[1], -1 * quat[2], -1 * quat[3]]
        end_v = self.quaternion_multiply(
            self.quaternion_multiply(quat, r), q_conj)[1:]
        return (end_v[0] + start.x, end_v[1] + start.y, end_v[2] + start.z)

    def prepSurface(self):
        self._analysis_surface.fill((0, 0, 0))

    def adjustFramePos(self, position):
        self._curr = position

    def resetFrame(self):
        self._curr = 0

    def frameBack(self):
        self.adjustFramePos(position - gameinterface.FPS)

    def getNextFrames(self, num=1):
        try:
            for i in range(num):
                yield list(eval(j) for j in self._frames[self._curr])
                self._curr += 1
        except:
            self._file_handle = None
            return None
