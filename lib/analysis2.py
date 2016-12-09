#!/usr/bin/python

import pygame as game
from pykinect2 import PyKinectV2._CameraSpacePoint as csp
import ctypes

import logging
import math
import csv

import kinectwrapper as kinect

__author__ = "Leon Chou and Roy Xu"

_LOGGER = logging.getLogger('analysis')

class AnalysisStream(object):
    """Wrapper class to export an array of functions
    that takes a body and returns coordinates corresponding
    to the frame"""

    def __init__(self, kinect, filename=None):
        self._k = kinect
        if filename:
            self.open_analysis(filename)
        self._camera_to_color = self._kinect._mapper().MapCameraPointToColorSpace

    def open_analysis(self, filename):
        if filename:
            file_handle = csv.reader(
                open("data/" + filename, "r"), delimiter=';',
                skipinitialspace=True)
            self._raw_frames = [row for row in file_handle]
            self._curr_frame = 0
        else:
            self._raw_frames = None


    def close(self):
        try:
            self._kinect.close()
        except:
            pass

    def _joint_to_tuple(self, j, end=3):
        return (j.Position.x, j.Position.y, j.Position.z)[:end]

    def _get_coords(self, start, quat, length):
        r = (0.0, 0.0, length, 0.0)
        q_conj = (q[0], -q[1], -q[2], -q[3])
        end_vector = self._q_mult(self._q_mult(quat, r), q_conj)[1:]
        return (end_vector[0] + start.x, end_vector[1] + start.y, end_vector + start.z)

    def _q_mult(self, q, r):
        return (r[0] * q[0] - r[1] * q[1] - r[2] * q[2] - r[3] * q[3],
                r[0] * q[1] + r[1] * q[0] - r[2] * q[3] + r[3] * q[2],
                r[0] * q[2] + r[1] * q[3] + r[2] * q[0] - r[3] * q[1],
                r[0] * q[3] - r[1] * q[2] + r[2] * q[1] + r[3] * q[0])

    def reset_frame(self):
        self._curr_frame = 0

    def get_next_frame(self):
        try:
            return self._frames.next()
        except:
            self._frames = self._next_frames()
            return self._frames.next()

    def get_color_space_frame(self):
        try:
            return self._color_frames.next()
        except:
            self._color_frames = self._next_color_frames()
            return self._color_frames.next()

    def _next_color_frames(self):
        try:
            curr, ref = self._raw_frames[self._curr_frame:self._curr_frame+2]
            curr, ref = self._get_points(curr), self._get_points(ref)
            try:
                return self._smooth_frames(curr, ref)
            except:
                self._curr_frame += 1
                return self._next_color_frames()
        except:
            frame = self._raw_frames[-1]
            return self._get_points(frame)

    def _get_color_points(self, frame):
        outline = [None for i in range(25)]
        def body_callback(body):
            joints = body.joints
            outline[0] = csp(*self._joint_to_tuple(joints[0]))

            color_coords = [None for i in range(25)]
            for count, (start, end) in enumerate(kinect.traverse()):
                if not outline[start]:
                    continue
                length = self._kinect.getBoneLength(count)
                coords = self._get_coords(outline[start], outline[end], length)
                outline[end] = csp(*coords)
                color_coords[end] = self._camera_to_color(outline[end])
            return color_coords

        return body_callback

    # def dist_from_body(self, frame, body):
    #     joints = map(lambda j: self._joint_to_tuple(j, 2), body.joints)
    #     dists = [(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in zip(frame, body)]
    #     # These are indexes within dists
    #     xmax = max( i for i in range(len(dists)), key=lambda i:dists[i][0])
    #     ymax = max( i for i in range(len(dists)), key=lambda i:dists[i][1])
    #     return (dists, xmax, ymax)

    # def diff_in_angle(self, frame, body):


    def _smooth_color_frames(curr, ref):
        s = 0
        def body_callback(body, speed):
            if s >= speed:
                throw IndexError('Frames are exhausted')
            curr_points = curr(body)
            ref_points = ref(body)
            frame = []
            for (x1, y1), (x2, y2) in zip(curr, ref):
                dx = s * (x2 - x1) / speed
                dy = s * (y2 - y1) / speed
                frame.append( (x1 + dx, y1 + dy))
            s += 1
            return frame

        return body_callback
