#!/usr/bin/python

import pygame as game
from pykinect2.PyKinectV2 import _CameraSpacePoint as csp
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
        self._kinect = kinect
        if filename:
            self.open_analysis(filename)
            self._curr_frame = 0
            self._color_frames = self.get_next_color_frame()
        self._camera_to_color = self._kinect._mapper() \
            .MapCameraPointToColorSpace

    def open_analysis(self, filename):
        if filename:
            file_handle = csv.reader(
                open("data/" + filename, "r"), delimiter=';',
                skipinitialspace=True)
            self._raw_frames = [[eval(q) for q in row] for row in file_handle]
            self._curr_frame = 0
        else:
            self._raw_frames = None

    def close(self):
        try:
            self._kinect.close()
        except:
            pass

    def points_to_lines(self, points):
        points = list(points)
        for start, end in kinect.traverse():
            try:
                yield (points[start], points[end])
            except:
                yield (None, None)

    def _joint_to_tuple(self, j, end=3):
        _LOGGER.info(j)
        return (j.Position.x, j.Position.y, j.Position.z)[:end]

    def _get_coords(self, start, quat, length):
        r = (0.0, 0.0, length, 0.0)
        q_conj = (quat[0], -quat[1], -quat[2], -quat[3])
        end_vector = self._q_mult(self._q_mult(quat, r), q_conj)[1:]
        return (end_vector[0] + start.x,
                end_vector[1] + start.y, end_vector[2] + start.z)

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
        if not self._color_frames:
            self.get_next_color_frame()
        return self._color_frames

    def get_next_color_frame(self):
        self._curr_frame += 1
        self._color_frames = self._next_color_frames()

    def _next_color_frames(self):
        try:
            _LOGGER.debug('curr {}'.format(self._curr_frame))
            curr, ref = self._raw_frames[self._curr_frame:self._curr_frame + 2]
            curr, ref = self._get_color_points(
                curr), self._get_color_points(ref)
            _LOGGER.debug('curr {} ref {}'.format(curr, ref))
            return self._smooth_color_frames(curr, ref)
        except:
            self._curr_frame -= 1
            return self._next_color_frames()

    def _get_color_points(self, frame):
        outline = [None for i in range(25)]

        def body_callback(body, frame_type='COLOR'):
            joints = body.joints
            outline[0] = csp(*self._joint_to_tuple(joints[0]))
            color_coords = [None for i in range(25)]
            color_coords[0] = self._camera_to_color(outline[0])
            for count, (start, end) in enumerate(kinect.traverse()):
                if not outline[start]:
                    continue
                length = self._kinect.getBoneLength(count)
                coords = self._get_coords(
                    outline[start], frame[end], length)
                outline[end] = csp(*coords)
                color_coords[end] = self._camera_to_color(outline[end])
            if frame_type == 'COLOR':
                return color_coords
            else:
                return outline

        return body_callback

    def _cs_to_tuple(self, cs, end=2):
        return (cs.x, cs.y)[:end]

    def _smooth_color_frames(self, curr, ref):
        s = [0]

        def body_callback(body, speed=4, frame_type='COLOR'):
            if s[0] >= speed:
                self.get_next_color_frame()
            curr_points = curr(body, frame_type)
            ref_points = ref(body, frame_type)
            frame = [None for i in range(25)]
            for count, (j1, j2) in enumerate(zip(curr_points, ref_points)):
                if j1 is None or j2 is None:
                    continue
                if frame_type == 'COLOR':
                    x1, y1 = self._cs_to_tuple(j1)
                    x2, y2 = self._cs_to_tuple(j2)
                    dx = s[0] * (x2 - x1) / speed
                    dy = s[0] * (y2 - y1) / speed
                    frame[count] = (x1 + dx, y1 + dy)
                else:
                    x1, y1, z1 = self._camera_to_tuple(j1)
                    x2, y2, z2 = self._camera_to_tuple(j2)
                    dx = s[0] * (x2 - x1) / speed
                    dy = s[0] * (y2 - y1) / speed
                    dz = s[0] * (z2 - z1) / speed
                    frame[count] = (x1 + dx, y1 + dy, z1 + dz)
            s[0] += 1
            _LOGGER.warning('speed {} frame {}'.format(s, frame))
            return frame

        return body_callback

    def dist_from_body(self, frame, body):
        _LOGGER.info('before map')
        joints = map(lambda j: self._joint_to_tuple(  # YOU HAVE TO MAKE THAT PARAMTER A 3
            j, 2), (body.joints[i] for i in range(25)))
        _LOGGER.info('joints {}'.format(joints))
        dists = [(x2 - x1, y2 - y1)
                 for (x1, y1), (x2, y2) in zip(frame, joints)]
        # These are indexes within dists
        xmax = max((i for i in range(len(dists))),
                   key=lambda i: abs(dists[i][0]))
        ymax = max((i for i in range(len(dists))),
                   key=lambda i: abs(dists[i][1]))
        return (dists, xmax, ymax)
