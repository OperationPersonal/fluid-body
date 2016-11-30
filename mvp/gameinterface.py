import pygame as game
import ctypes, _ctypes

from pykinect2 import PyKinectV2 as kv2,PyKinectRuntime as runtime
from pykinect2.PyKinectV2 import *

class GameInterface(object):

    def __init__(self, width=750, height=750, background=(255, 255, 255), callback=lambda: None):
        screen = self._screen = game.display.set_mode((width, height))
        game.display.set_caption('Fluid Body Analyser')
        # Make the background - must be tuple
        self._background_color = background
        screen.fill(game.Color(*background))
        self._clock = game.time.Clock()
        self._callback = callback
        self._surface = game.Surface((width, height), depth=32)
        self._kinect = runtime.PyKinectRuntime(runtime.FrameSourceTypes_Color | runtime.FrameSourceTypes_Body)

    def setBackgroundColor(self, background=(255, 255, 255)):
        self._background_color = background
        self._screen.fill(game.Color(*background))

    def quit(self):
        game.quit()
        self._callback()

    def drawCameraInput(self, frame, surface):
        surface.lock()
        addr = self._kinect.surface_as_array(surface.get_buffer())
        ctypes.memmove(addr, frame.ctypes.data, frame.size)
        del addr
        surface.unlock()

    def surfaceToScreen(self):
        scale = self._surface.get_height() / self._surface.get_width()
        scaled_height = scale * self._screen.get_width()
        draw_surface = game.transform.scale(self._surface, (self._screen.get_width()), scaled_height)
        self._screen.blit(draw_surface, (0,0))

    def run(self):
        x = 250
        y = 250
        screen, kinect, surface = self._screen, self._kinect, self._surface
        stream = [( (250, 250), (275, 275) )]
        while True:
            for event in game.event.get():
                if event.type == game.QUIT:
                    self.quit()

            if stream:
                for (start, end) in stream:
                    game.draw.line(self._surface, game.color.THECOLORS["red"], start, end, 8)

            if kinect and kinect.has_new_color_frame():
                self.drawCameraInput(kinect.get_last_color_frame(), surface)

            self.surfaceToScreen()
            game.display.update()
            game.display.flip()

            self._clock.tick(30)
