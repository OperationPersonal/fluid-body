from pykinect2 import PyKinectV2 as kv2
from pykinect2 import PyKinectRuntime as runtime
from pykinect2.PyKinectV2 import *
import math

JointHierarchy = ((16, 17, 18, 19), (12, 13, 14, 15), (1, 20, ((
    2, 3), (8, 9, 10, ((11, 23), 24)), (4, 5, 6, ((7, 21), 22)))))

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

    def close(self):
        self._kinect.close()

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

    def traverseBody(self, body):
        points = self._kinect.body_joints_to_color_space(body.joints)
        joints = body.joints

    def drawBody(self, body):
        points = self._kinect.body_joints_to_color_space(body.joints)
        joints = body.joints
        positions = [None for i in range(25)]
        for joint in traverse():
            state = (joints[joint[0]].TrackingState,
                     joints[joint[1]].TrackingState)
            if state[0] == TrackingState_NotTracked or state[1] == TrackingState_NotTracked or state == (TrackingState_Inferred, TrackingState_Inferred):
                continue
            point = (points[joint[0]], points[joint[1]])
            line = ((point[0].x, point[0].y), (point[1].x, point[1].y))
            yield line

    def orientationToDegrees(self, orientation):
        x, y, z, w = orientation.x, orientation.y, orientation.z, orientation.w

        pitch = math.atan2(2 * ((y * z) + (w * x)), (w * w) -
                           (x * x) - (y * y) + (z * z)) / math.pi * 180.0
        yaw = math.asin(2 * ((w * y) - (x * z))) / math.pi * 180.0
        roll = math.atan2(2 * ((x * y) + (w * z)), (w * w) +
                          (x * x) - (y * y) - (z * z)) / math.pi * 180.0

        return (pitch, yaw, roll)

    def degreesToCoordinates(self, prev, degrees, length=15):
        pitch, yaw, roll = degrees
        dy = math.sin(pitch) * length
        dx = math.sin(yaw) * length
        return (prev[0] + dx, prev[1] + dy)
