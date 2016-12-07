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

STATE_VIEW = 'VIEW'
STATE_RECORD = 'RECORD'
STATE_WAITING = 'WAITING'
STATE_COMPARE = 'COMPARE'

_LOGGER = logging.getLogger('gameinterface')

from kinectwrapper import KinectStream, traverse
from analysis import AnalysisStream


class GameInterface(object):

    def __init__(self, callback=lambda: None, mode=STATE_VIEW, filename=None):
        _LOGGER.info('Started interface')

        game.init()
        self._infoObject = game.display.Info()
        self._state = mode
        self._kinect = KinectStream()
        self._analysis = AnalysisStream(self._kinect, filename)
        self._analysis_width = self._analysis.get_width()
        screen_width = self._infoObject.current_w >> 1
        screen_height = self._infoObject.current_h >> 1
        if self._state == STATE_COMPARE or self._state == STATE_WAITING:
            screen_width += self._analysis_width
        self._screen = game.display.set_mode((screen_width, screen_height),
                                             game.HWSURFACE | game.DOUBLEBUF | game.RESIZABLE, 32)
        _LOGGER.debug('Screen width: {}, Screen height: {}'.format(
            self._screen.get_width(), self._screen.get_height()))
        game.display.set_caption('Fluid Body Analyser')
        self._clock = game.time.Clock()
        self._callback = callback
        self._surface = game.Surface((self._kinect.colorFrameDesc(
        ).Width, self._kinect.colorFrameDesc().Height), 0, 32)
        self._bodies = None
        self._bodies = []
        self._pause = False
        self._audio = AudioInterface(self)

    def quit(self):
        try:
            self._analysis.close()
            self._kinect.close()
        except:
            pass
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
        real_screen_w = self._screen.get_width()
        if self._state == STATE_WAITING or self._state == STATE_COMPARE:
            real_screen_w -= self._analysis_width
        scaled_height = int(scale * (real_screen_w))
        draw_surface = game.transform.scale(
            self._surface, (real_screen_w, scaled_height))
        self._screen.blit(draw_surface, (0, 0))
        if self._state == STATE_WAITING or self._state == STATE_COMPARE:
            analysis_surface = self._analysis.getSurface()
            draw_analysis = game.transform.scale(
                analysis_surface, (analysis_surface.get_width(), scaled_height))
            self._screen.blit(
                draw_analysis, (draw_surface.get_width(), 0))
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
                pass

    def run(self):
        screen, kinect, surface, analysis = self._screen, self._kinect, self._surface, self._analysis
        # body = None
        stop_listening = self._audio.listen()
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
                        if self._state == STATE_RECORD or self._state == STATE_VIEW:
                            self._state = STATE_RECORD if self._state == STATE_VIEW else STATE_VIEW
                            if self._state == STATE_RECORD:
                                kinect.initRecord()
                        else:
                            self._state = STATE_COMPARE if self._state == STATE_WAITING else STATE_WAITING
                    elif event.key == game.K_SPACE:
                        if kinect:
                            for body in self._bodies:
                                if body.is_tracked:
                                    _LOGGER.info('Initializing body lengths')
                                    kinect.initialize(body)
                    elif event.key == game.K_p:
                        if self._pause:
                            _LOGGER.info('Unpause')
                        else:
                            _LOGGER.info('Pause')
                        self._pause = not self._pause
                    elif event.key == game.K_m:
                        self._audio.mute()
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
                    analysis.prepSurface()
                    lines = analysis.getBody(body)
                    self.drawLines(analysis.getBody(
                        body), analysis._analysis_surface, GAME_COLORS[count])
                elif self._state == STATE_WAITING:
                    analysis.prepSurface()

            self.surfaceToScreen()

            self._clock.tick(30)
