import pygame as game
import ctypes
import _ctypes

# from pykinect2 import PyKinectV2 as kv2
# from pykinect2 import PyKinectRuntime as runtime
# from pykinect2.PyKinectV2 import *
from kinectwrapper import KinectStream

class GameInterface(object):

    def __init__(self, width=750, height=750, background=(255, 255, 255), callback=lambda: None):

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
        self._bodyFrame = None

    def setBackgroundColor(self, background=(255, 255, 255)):
        # self._background_color = background
        # self._screen.fill(game.Color(*background))
        pass

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
        draw_surface = None
        game.display.update()

    def run(self):
        x = 250
        y = 250
        screen, kinect, surface = self._screen, self._kinect, self._surface
        # stream = [( (250, 250), (275, 275) )]
        stream = False
        # print kinect.traverse()
        while True:
            for event in game.event.get():
                if event.type == game.QUIT:
                    self.quit()

            if kinect and kinect.hasNewBodyFrame():
                self._bodyFrame = kinect.getLastBodyFrame()

            if self._bodyFrame:
                for body in self._bodyFrame.bodies:
                    if not body.is_tracked:
                        continue
                    stream = kinect.drawBody(body)
                    if stream:# should be if self._kinect has stream of bodystuff or nah
                        for (start, end) in stream:
                            try:
                                game.draw.line(self._surface, game.color.THECOLORS["red"], start, end, 8)
                            except:
                                pass

            # print 'main game loop'

            if kinect and kinect.hasNewColorFrame():
                # print 'kinect loop'
                self.drawCameraInput(kinect.getLastColorFrame(), surface)

            self.surfaceToScreen()
            game.display.update()
            game.display.flip()

            self._clock.tick(15)
