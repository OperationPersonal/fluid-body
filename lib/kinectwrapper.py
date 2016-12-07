#!/usr/bin/python

from pykinect2 import PyKinectV2 as kv2
from pykinect2 import PyKinectRuntime as runtime
from pykinect2.PyKinectV2 import *

import logging
import math

__author__ = "Leon Chou and Roy Xu"

"""Wrapper for kinect library. Reads from kinect"""


JointHierarchy = ((16, 17, 18, 19), (12, 13, 14, 15), (1, 20, ((
    2, 3), (8, 9, 10, ((11, 23), 24)), (4, 5, 6, ((7, 21), 22)))))

_LOGGER = logging.getLogger('kinect')


def traverse(t=JointHierarchy, p=0):
    for item in t:
        if not isinstance(item, tuple):
            yield(p, item)
            p = item
        else:
            for j in traverse(item, p):
                yield j


class KinectStream:

    def __init__(self):
        self._kinect = runtime.PyKinectRuntime(
            FrameSourceTypes_Color | FrameSourceTypes_Body)
        self._bone_lengths = [100 for i in range(25)]

    def close(self):
        self._kinect.close()
        try:
            self._file_handle.close()
        except:
            pass

    def colorFrameDesc(self):
        return self._kinect.color_frame_desc

    def surfaceAsArray(self, surface):
        return self._kinect.surface_as_array(surface)

    def getLastColorFrame(self):
        return self._kinect.get_last_color_frame()

    def hasNewColorFrame(self):
        return self._kinect.has_new_color_frame()

    def getLastBodyFrame(self):
        return self._kinect.get_last_body_frame()

    def hasNewBodyFrame(self):
        return self._kinect.has_new_body_frame()

    def refreshBody(self, old_body):
        frame = self.getLastBodyFrame()
        for body in frame.bodies:
            if not body.is_tracked:
                continue
            return body

    def traverseBody(self, angles):
        coords = [None for x in range(25)]
        coords[0] = (200, 0)
        prev = 0
        for count, x in enumerate(traverse()):
            length = self._bone_lengths[count]
            coords[x[1]] = get_coords(coords[x[0]], angles[x[1]], length)
            line = (coords[x[0]], coords[x[1]])
            yield line

    def getBoneLength(self, count):
        return self._bone_lengths[count]

    def drawBody(self, body):
        points = self._kinect.body_joints_to_color_space(body.joints)
        joints = body.joints

        for count, joint in enumerate(traverse()):
            state = (joints[joint[0]].TrackingState,
                     joints[joint[1]].TrackingState)
            if (state[0] == TrackingState_NotTracked or
                state[1] == TrackingState_NotTracked or
                    state == (TrackingState_Inferred, TrackingState_Inferred)):
                yield (None, None)
                continue
            point = (points[joint[0]], points[joint[1]])
            line = ((point[0].x, point[0].y), (point[1].x, point[1].y))
            yield line

    def initialize(self, body):
        points = self._kinect.body_joints_to_color_space(body.joints)
        joints = body.joints
        for count, joint in enumerate(traverse()):
            state = (joints[joint[0]].TrackingState,
                     joints[joint[1]].TrackingState)
            if (state[0] == TrackingState_NotTracked or
                state[1] == TrackingState_NotTracked or
                    state == (TrackingState_Inferred, TrackingState_Inferred)):
                continue
            point = (points[joint[0]], points[joint[1]])
            length = math.hypot(
                point[0].x - point[1].x, point[0].y - point[1].y)
            self._bone_lengths[count] = length
            _LOGGER.debug(
                'From joint{} to joint{} with length {}'.format(joint[0],
                                                                joint[1],
                                                                length))

    def initRecord(self):
        _LOGGER.info('Start recording')
        self._file_handle = open('./data/' + str(time.time()), "wb+")

    def recordFrame(self, body):
        angles = (str(self.orientationToQuat(
            body.joint_orientations[i].Orientation)) for i in range(25))
        self._file_handle.write(';'.join(angles) + '\n')

    def orientationToQuat(self, orientation):
        return [orientation.x, orientation.y, orientation.z, orientation.w]
