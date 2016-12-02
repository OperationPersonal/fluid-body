import pygame as game
import ctypes
import _ctypes

import csv

# from pykinect2 import PyKinectV2 as kv2
# from pykinect2 import PyKinectRuntime as runtime
# from pykinect2.PyKinectV2 import *
from kinectwrapper import KinectStream

ANALYSIS_WIDTH = 400

class GameInterface(object):

    def __init__(self, callback=lambda: None, filename="1478280688.29"):

        game.init()
        self._infoObject = game.display.Info()
        screen = self._screen = game.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1),
                                               game.HWSURFACE | game.DOUBLEBUF | game.RESIZABLE, 32)
        game.display.set_caption('Fluid Body Analyser')
        # Make the background - must be tuple
        # self._background_color = background
        # screen.fill(game.Color(*background))
        self._clock = game.time.Clock()
        self._callback = callback
        # self._kinect = runtime.PyKinectRuntime(FrameSourceTypes_Color | FrameSourceTypes_Body)
        self._kinect = KinectStream()
        self._surface = game.Surface((self._kinect.colorFrameDesc().Width, self._kinect.colorFrameDesc().Height), 0, 32)
        self._bodies = None
        if filename:
            self._analysis = game.Surface((ANALYSIS_WIDTH, self._kinect.colorFrameDesc().Height))
        self._currfile = filename

    def setBackgroundColor(self, background=(255, 255, 255)):
        # self._background_color = background
        # self._screen.fill(game.Color(*background))
        pass

    def setFileName(self, filename):
        self._currfile = filename

    def quit(self):
        game.quit()
        self._callback()

    def drawCameraInput(self, frame, surface):
        surface.lock()
        addr = self._kinect.surfaceAsArray(surface.get_buffer())
        ctypes.memmove(addr, frame.ctypes.data, frame.size)
        del addr
        surface.unlock()

    def surfaceToScreen(self):
        scale = float(self._surface.get_height()) / self._surface.get_width()
        scaled_height = int(scale * self._screen.get_width())

        draw_surface = game.transform.scale(self._surface, (self._screen.get_width(), scaled_height))
        self._screen.blit(draw_surface, (0, 0))
        if self._currfile:
            analysis_surface = game.transform.scale(self._analysis, (ANALYSIS_WIDTH, scaled_height))
            self._screen.blit(analysis_surface, (self._screen.get_width() - ANALYSIS_WIDTH, 0))
            analysis_surface = None

        draw_surface = None
        game.display.update()

    def run(self):
        x = 250
        y = 250
        screen, kinect, surface = self._screen, self._kinect, self._surface
        body = None
        # print kinect.traverse()

        f = None
        if self._currfile:
            f = csv.reader(open("data/" + self._currfile, "r"),
                        delimiter=';', skipinitialspace=True)

        while True:
            for event in game.event.get():
                if event.type == game.QUIT:
                    self.quit()
                elif event.type == game.VIDEORESIZE:  # window resized
                    self._screen = game.display.set_mode(event.dict['size'],
                        game.HWSURFACE | game.DOUBLEBUF | game.RESIZABLE, 32)

            if kinect and kinect.hasNewColorFrame():
                # print 'kinect loop'
                self.drawCameraInput(kinect.getLastColorFrame(), surface)

            # print 'main loop'
            if kinect and kinect.hasNewBodyFrame():
                # print 'body refresh'
                self._bodies = kinect.getLastBodyFrame()
            # print bodyFrame
            if self._bodies:
                for body in self._bodies.bodies:
                    if not body.is_tracked:
                        continue
                    for (start, end) in kinect.drawBody(body):
                        try:
                            game.draw.line(self._surface, game.color.THECOLORS["red"], start, end, 8)
                        except:
                            pass

                    if f:
                        self._analysis.fill((0, 0, 0))
                        try:
                            new_line = f.next()
                        except:
                            f = None
                        else:
                            joint_data = [eval(x) for x in new_line]
                            for (start, end) in kinect.traverseBody(joint_data):
                                try:
                                    game.draw.line(self._analysis, game.color.THECOLORS["green"], start, end, 8)
                                except:
                                    pass

            self.surfaceToScreen()
            game.display.update()
            game.display.flip()

            self._clock.tick(120)
