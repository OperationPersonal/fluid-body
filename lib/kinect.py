#!/usr/bin/python

from pykinect2 import PyKinectV2 as kv2
from pykinect2 import PyKinectRuntime as runtime
from pykinect2.PyKinectV2 import *

import logging
import math
import time
import os

__author__ = "Leon Chou and Roy Xu"

"""Wrapper for kinect library. Reads from kinect"""


JOINT_HIERARCHY = ((16, 17, 18, 19), (12, 13, 14, 15), (1, 20, ((
    2, 3), (8, 9, 10, ((11, 23), 24)), (4, 5, 6, ((7, 21), 22)))))

_LOGGER = logging.getLogger('kinect')

JOINTS = ['Base of Spine', 'Middle of Spine', 'Neck', 'Head', 'Left Shoulder',
          'Left Elbow', 'Left Wrist', 'Left Hand', 'Right Shoulder',
          'Right Elbow', 'Right Wrist', 'Right Hand', 'Right Hip', 'Left Knee',
          'Left Ankle', 'Left Foot', 'Right Hip', 'Right Knee', 'Right Ankle',
          'Right Foot', 'Top of Spine', 'Left Hand Tip', 'Left Thumb',
          'Right Hand Tip', 'Right Thumb']


def traverse(t=JOINT_HIERARCHY, p=0):
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

    def _mapper(self):
        return self._kinect._mapper

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
        self._joints = joints = body.joints

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
            length = self.calc_bone_length(
                joints[joint[0]], joints[joint[1]])
            self._bone_lengths[count] = length
            _LOGGER.debug(
                'From {} to {} with length {}'.format(joint[0],
                                                      joint[1],
                                                      length))
            yield line

    def calc_bone_length(self, joint0, joint1):
        return math.sqrt(math.pow(joint0.Position.x - joint1.Position.x, 2) +
                         math.pow(joint0.Position.y - joint1.Position.y, 2) +
                         math.pow(joint0.Position.z - joint1.Position.z, 2))

    def initRecord(self):
        _LOGGER.info('Start recording')

        username = os.environ['Fluid Username'].replace('\n', '')
        exercise = os.environ['Fluid Exercise'].replace('\n', '')
        self._file_handle = open('./data/' + username +
                                 ';' + exercise +
                                 ';' + str(time.time()), "wb+")

    def recordFrame(self, body):
        angles = (str(self.orientationToQuat(
            body.joint_orientations[i].Orientation)) for i in range(25))
        self._file_handle.write(';'.join(angles) + '\n')

    def orientationToQuat(self, orientation):
        return [orientation.w, orientation.x, orientation.y, orientation.z]
