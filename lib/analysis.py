import pygame as game
from pykinect2.PyKinectV2 import _CameraSpacePoint as csp
import logging
import math
from csv import reader
import os

import kinect

DATA_DIR = 'data/'
SPEED_LIMIT = 12


__author__ = "Leon Chou and Roy Xu"

_LOGGER = logging.getLogger('analysis')


def _m_to_cm(v):
    return int(v * 100 // 1)


class AnalysisStream(object):

    class _Frames(object):

        def __init__(self, frames):
            self._f = frames
            self._c = 0

        def __iter__(self):
            for f in self._f:
                yield f

        def _change_frame(self, change):
            self._c += change
            if self._c < 0:
                self._c = 0
            elif self._c >= len(self._f):
                self._c = len(self._f) - 1

        def get_c(self):
            return self._c

        def set_frame(self, frame):
            self._c = frame
            self._change_frame(0)

        def _reset_frame(self):
            self._c = 0

        def get_frame(self):
            return self._f[self._c]

        def get_next_frame(self, skip=1):
            self._change_frame(skip)
            return self.get_frame()

        def get_prev_frame(self, skip=1):
            self._change_frame(-skip)
            return self.get_frame()

    def __init__(self, kinect, file_name):
        self._kinect = kinect
        self.open_analysis(file_name)

    def _joint_to_tuple(self, j, end=3):
        return (j.Position.x, j.Position.y, j.Position.z)[:end]

    def _color_to_tuple(self, cs, end=2):
        try:
            return (cs.x, cs.y)[:end]
        except:
            return(cs[0], cs[1])[:end]

    def _camera_to_tuple(self, cam, end=3):
        return (cam.x, cam.y, cam.z)[:end]

    def _camera_to_color(self, point):
        return self._kinect._kinect._mapper.MapCameraPointToColorSpace(point)

    def _reset_frames(self):
        self._init_raw_camera_frames()
        self._init_camera_frames()
        self._init_color_frames()

    def _q_mult(self, q, r):
        return (r[0] * q[0] - r[1] * q[1] - r[2] * q[2] - r[3] * q[3],
                r[0] * q[1] + r[1] * q[0] - r[2] * q[3] + r[3] * q[2],
                r[0] * q[2] + r[1] * q[3] + r[2] * q[0] - r[3] * q[1],
                r[0] * q[3] - r[1] * q[2] + r[2] * q[1] + r[3] * q[0])

    def _q_to_coords(self, start, quat, length):
        r = (0.0, 0.0, length, 0.0)
        q_conj = (quat[0], -quat[1], -quat[2], -quat[3])
        end_vector = self._q_mult(self._q_mult(quat, r), q_conj)[1:]
        return (end_vector[0] + start.x,
                end_vector[1] + start.y, end_vector[2] + start.z)

    def _init_raw_camera_frames(self):
        frames = []
        for quats in self._raw_quats:
            def callback(body, q=quats):
                outline = [None for i in range(25)]
                joints = body.joints
                outline[0] = csp(*self._joint_to_tuple(joints[0]))
                for count, (start, end) in enumerate(kinect.traverse()):
                    if not outline[start]:
                        continue
                    scale = self._kinect.getBoneLength(count)
                    outline[end] = csp(*self._q_to_coords(
                        outline[start], q[end], scale))
                return outline
            frames.append(callback)
        self._raw_camera = self._Frames(frames)

    def _init_camera_frames(self):
        frames = []
        for frame in self._raw_camera:
            if len(frames) == 0:
                frames.append(frame)
                continue
            for s in range(SPEED_LIMIT):
                def callback(body, curr=frame, prev=frames[-1], speed=s):
                    curr = curr(body)
                    prev = prev(body)
                    outline = [None for i in range(25)]
                    for count, (j1, j2) in enumerate(zip(prev, curr)):
                        if j1 is None or j2 is None:
                            continue
                        x1, y1, z1 = self._camera_to_tuple(j1)
                        x2, y2, z2 = self._camera_to_tuple(j2)
                        dx = speed * (x2 - x1) / SPEED_LIMIT
                        dy = speed * (y2 - y1) / SPEED_LIMIT
                        dz = speed * (z2 - z1) / SPEED_LIMIT
                        outline[count] = csp(x1 + dx, y1 + dy, z1 + dz)
                    return outline
                frames.append(callback)
            frames.append(frame)
        self.camera = self._Frames(frames)

    def _init_color_frames(self):
        if not self.camera:
            raise NotImplementedError('Init camera frames first')
        frames = []
        for frame in self.camera:
            def callback(body, f=frame):
                cam_f = f(body)
                color = [self._camera_to_color(
                    cam_f[i]) for i in range(25)]
                return [self._color_to_tuple(c) for c in color]
            frames.append(callback)
        self.color = self._Frames(frames)

    def open_analysis(self, filename):
        if not filename:
            raise LookupError('No filename passed')
        file_path = DATA_DIR + filename
        try:
            file_handle = reader(
                open(file_path, 'rb'),
                delimiter=';',
                skipinitialspace=True)
        except:
            os.remove(file_path)
            raise EOFError('File not parsed correctly; Removed file')
        else:
            self._raw_quats = [[eval(q) for q in frame]
                               for frame in file_handle]
            self._reset_frames()

    def color_points_to_bones(self, cp):
        cp = list(cp)
        for start, end in kinect.traverse():
            try:
                yield (cp[start], cp[end])
            except:
                yield (None, None)

    def get_worst_body_part(self, body):
        frame = self.camera.get_frame()(body)
        frame = [self._camera_to_tuple(frame[i]) for i in range(25)]
        joints = [self._joint_to_tuple(body.joints[i]) for i in range(25)]
        _LOGGER.info('frame {} joints {}'.format(frame, joints))
        dists = [(x2 - x1, y2 - y1, z2 - z1)
                 for (x1, y1, z1), (x2, y2, z2) in zip(joints, frame)]
        return max(((max(dists[i], key=lambda v: abs(v)), i)
                    for i in range(25)),
                   key=lambda t: abs(t[0]))[1]

    def get_dist_dir(self, frame, body, index):
        j1, j2 = self._camera_to_tuple(
            frame[index]), self._joint_to_tuple(body.joints[index])
        if not (j1 and j2):
            raise KeyError('Not tracking joint')
        skip = [3, 15, 19, 21, 22, 23, 24]
        dist = (v2 - v1 for v1, v2 in zip(j1, j2))
        return max(((d, i) for i, d in enumerate(dist)),
                   key=lambda t: abs(t[0]) if t[1] not in skip else 0)

    def get_status_message(self, dist, direction, joint_type):
        message = 'Move {} {} centimeters {}'

        joint = kinect.JOINTS[joint_type]
        dist = _m_to_cm(dist)
        if direction == 0:
            direction = 'left' if dist < 0 else 'right'
        elif direction == 1:
            direction = 'upward' if dist < 0 else 'downward'
        else:
            direction = 'forward' if dist < 0 else 'backward'

        return message.format(joint, abs(dist), direction)

    def close(self):
        pass
