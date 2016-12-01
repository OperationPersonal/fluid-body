import os

from pykinect2 import PyKinectRuntime, PyKinectV2
from pykinect2.PyKinectV2 import *


class Kinect2(object):

    def traverse(self, t, p=0):
        for item in t:
            if not isinstance(item, tuple):
                yield(p, item)
                p = item
            else:
                for j in self.traverse(item, p):
                    yield j

    def __init__(self):
        self._kinect = PyKinectRuntime.PyKinectRuntime(
            PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)
        self._kinect.max_body_count = 6
        self._bodies = None
        self.JointHierarchy = ((16, 17, 18, 19), (12, 13, 14, 15), (1, 20, ((
            2, 3), (8, 9, 10, ((11, 23), 24)), (4, 5, 6, ((7, 21), 22)))))
        self._surface = (self._kinect.color_frame_desc.Width,
                         self._kinect.color_frame_desc.Height)
        self._output = open('./data/' + str(time.time()), "wb+")
        self._bodyindex = False
        self._selected = None

    def get_file_names(self):
        return list(f for f in os.listdir('./data') if os.path.isfile(f))

    def select(self, fname):
        self._selected = csv.reader(
            open('./data/' + fname, 'r'), delimiter=';', skipinitialspace=True)

    def _get_coords(self, prev, q, t, l):
        if not self._body:
            return
        length = math.hypot(l[0][0] - l[1][0], l[0][1] - l[1][1])
        dy = math.sin(q[0]) * length
        dx = math.sin(q[1]) * length
        return (prev[0] + dx, prev[1] + dy)

    def get_next_recorded_frame(self, prev=(0, 0)):
        frame = [eval(x) for x in self._selected.next()]
        lines = self._get_lines(self._body)
        traversal = list(self.traversal(self.JointHierarchy))
        linemap = [None for i in range(25)]
        for i in range(len(lines)):
            t = traversal[i]
            l = lines[i]
            prev = linemap[t[0]]
            nextcoords = self._get_coords(prev, frame[t[1]], t, l)
            linemap[t[0]] = nextcoords

    def close(self):
        self._kinect.close()

    def _get_lines(self, body):
        if not body.is_tracked:
            return
        points = self._kinect.body_joints_to_color_space(body.joints)
        joints = body.joints
        for joint in self.traverse(self.JointHierarchy):
            state = (joints[joint[0]].TrackingState,
                     joints[joint[1]].TrackingState)
            if state == (PyKinectV2.TrackingState_NotTracked, PyKinectV2.TrackingState_NotTracked):
                continue
            if state == (PyKinectV2.TrackingState_Inferred, PyKinectV2.TrackingState_Inferred):
                continue
            point = (points[joint[0]], points[joint[1]])
            line = ((point[0].x, point[0].y), (point[1].x, point[1].y))
            yield line

    def color_frame(self):
        if self._kinect.has_new_color_frame():
            return self._kinect.get_last_color_frame()

    def record_frame(self):
        if self._kinect.has_new_body_frame():
            bodies = self._bodies = self._kinect.get_last_body_frame()
        for body in bodies:
            if not body.is_tracked:
                continue
            self._write_frame(body)
            break

    def _write_frame(self, body):
        angles = str(self.orientation_to_degrees(body.joint_orientations[i].Orientation)) for i in range(25)
        self._output.write(';'.join(angles) + '\n')

        for i in range(25):
            orientation = self._orientation_to_degrees(quats[i].Orientation)

    def orientation_to_degrees(self, orientation):
        x = orientation.x
        y = orientation.y
        z = orientation.z
        w = orientation.w

        pitch = yaw = roll = 0
        pitch = math.atan2(2 * ((y * z) + (w * x)), (w * w) -
                           (x * x) - (y * y) + (z * z)) / math.pi * 180.0
        yaw = math.asin(2 * ((w * y) - (x * z))) / math.pi * 180.0
        roll = math.atan2(2 * ((x * y) + (w * z)), (w * w) +
                          (x * x) - (y * y) - (z * z)) / math.pi * 180.0

        return (pitch, yaw, roll)
