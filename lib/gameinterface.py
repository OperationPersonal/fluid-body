import pygame as game
import ctypes
import _ctypes
import csv
import random
import logging

from lib.audio import AudioInterface

GAME_COLORS = [game.color.THECOLORS["red"],
               game.color.THECOLORS["blue"],
               game.color.THECOLORS["green"],
               game.color.THECOLORS["orange"],
               game.color.THECOLORS["purple"],
               game.color.THECOLORS["yellow"],
               game.color.THECOLORS["violet"]]

STATE_VIEW = 1
STATE_RECORD = 0
STATE_COMPARE = 'COMPARE'

from kinectwrapper import KinectStream, traverse
from analysis import AnalysisStream

ANALYSIS_WIDTH = 600


class GameInterface(object):

    def __init__(self, callback=lambda: None, mode=STATE_VIEW, filename=None):
        logging.info('Started interface')

        game.init()
        self._infoObject = game.display.Info()
        screen = self._screen = game.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1),
                                                      game.HWSURFACE | game.DOUBLEBUF | game.RESIZABLE, 32)
        game.display.set_caption('Fluid Body Analyser')
        self._clock = game.time.Clock()
        self._callback = callback
        self._kinect = KinectStream()
        self._surface = game.Surface((self._kinect.colorFrameDesc(
        ).Width, self._kinect.colorFrameDesc().Height), 0, 32)
        self._bodies = None
        self._analysis = AnalysisStream(self._kinect, filename)
        self._state = mode
        self._currfile = filename
        self._bodies = []
        self._pause = False

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

        draw_surface = game.transform.scale(
            self._surface, (self._screen.get_width(), scaled_height))
        self._screen.blit(draw_surface, (0, 0))
        if self._state == STATE_COMPARE:
            # print('bltting analysis')
            analysis_surface = self._analysis.getSurface()
            draw_analysis = game.transform.scale(
                analysis_surface, (analysis_surface.get_width(), scaled_height))
            self._screen.blit(
                draw_analysis, (self._screen.get_width() - analysis_surface.get_width(), 0))
        draw_surface = draw_analysis = analysis_surface = None
        game.display.update()
        game.display.flip()

    def drawLines(self, lines, surface, color=None, width=8):
        color = random.choice(GAME_COLORS) if not color else color
        if not lines:
            return
        lines = list(lines)
        if not lines[0]:
            return
        font = game.font.Font(None, 60)
        traversal = list(traverse())
        for index, (start, end) in enumerate(lines):
            if start is None or end is None:
                continue
            try:
                game.draw.line(surface, color, start, end, width)
                game.draw.circle(surface, color, map(
                    lambda i: int(i), end), 20, 0)
                jointnum = font.render(str(traversal[index][1]), 0,
                                       game.color.THECOLORS['black'])
                surface.blit(jointnum, map(lambda c: c - 20, end))
            except Exception as e:
                logging.warning(e)

    def run(self):
        x = 250
        y = 250
        screen, kinect, surface, analysis = self._screen, self._kinect, self._surface, self._analysis
        body = None

        audio = AudioInterface(self)
        stop_listening = audio.listen()
        while True:
            for event in game.event.get():
                if event.type == game.QUIT:
                    stop_listening()
                    self.quit()
                elif event.type == game.VIDEORESIZE:  # window resized
                    self._screen = game.display.set_mode(event.dict['size'],
                                                         game.HWSURFACE | game.DOUBLEBUF | game.RESIZABLE, 32)
                elif event.type == game.KEYDOWN:
                    if event.key == game.K_RETURN:
                        self._state = (self._state + 1) % 2
                        if self._state == STATE_RECORD:
                            kinect.initRecord()
                    elif event.key == game.K_SPACE:
                        if kinect:
                            for body in self._bodies:
                                if body.is_tracked:
                                    logging.debug('Initializing body lengths')
                                    kinect.initialize(body)
                    elif event.key == game.K_p:
                        self._pause = not self._pause
            if self._pause:
                continue

            if kinect:
                if kinect.hasNewColorFrame():  # must draw camera frame first or else the body gets covered
                    self.drawCameraInput(kinect.getLastColorFrame(), surface)
                if kinect.hasNewBodyFrame():
                    self._bodies = kinect.getLastBodyFrame().bodies

            # print bodyFrame
            for count, body in enumerate(self._bodies):
                if not body.is_tracked:
                    continue
                self.drawLines(kinect.drawBody(body),
                               self._surface, GAME_COLORS[count])
                if self._state == STATE_RECORD:
                    kinect.recordFrame(body)
                elif self._state == STATE_COMPARE:
                    # print('analyzing')
                    analysis.prepSurface()
                    lines = analysis.getBody(body)
                    # print(lines)
                    self.drawLines(analysis.getBody(
                        body), analysis._analysis_surface, GAME_COLORS[count])

            self.surfaceToScreen()

            self._clock.tick(30)
