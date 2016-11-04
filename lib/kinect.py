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

    def _get_lines(self, body):
        if not body.is_tracked:
            return
        points = self._kinect.body_joints_to_color_space(body.joints)
        joints = body.joints
        for joint in Kinect2.traverse(Kinect2.JointHierarchy):
            state = (joints[joint[0]].TrackingState,
                     joints[joint[1]].TrackingState)
            if state == (PyKinectV2.TrackingState_NotTracked, PyKinectV2.TrackingState_NotTracked):
                continue
            if state == (PyKinectV2.TrackingState_Inferred, PyKinectV2.TrackingState_Inferred):
                continue
            point = (points[joint[0]], points[joint[1]])
            line = ((point[0].x, point[0].y), (point[1].x, point[1].y))
            yield line

    def get_bodies(self):
        if self._kinect.has_new_body_frame():
            bodies = self._bodies = self._kinect.get_last_body_frame().bodies
        for body in bodies:
            if not body.is_tracked:
                continue
            yield self._get_lines(body)
        return

    def color_frame(self):
        if self._kinect.has_new_color_frame():
            return self._kinect.get_last_color_frame()

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
