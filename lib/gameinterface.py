#!/usr/bin/python

import pygame as game
import ctypes

import logging

import kinect
import analysis
import audio
import status

"""Main game interface. Draws surfaces and contains main loop"""

__author__ = "Leon Chou and Roy Xu"

GAME_COLORS = [game.color.THECOLORS["red"],
               game.color.THECOLORS["blue"],
               game.color.THECOLORS["green"],
               game.color.THECOLORS["orange"],
               game.color.THECOLORS["purple"],
               game.color.THECOLORS["yellow"],
               game.color.THECOLORS["violet"],
               game.color.THECOLORS["black"],
               game.color.THECOLORS['white']]

STATE_VIEW = 'VIEW'
STATE_RECORD = 'RECORD'
STATE_WAITING = 'WAITING'
STATE_COMPARE = 'COMPARE'

STATUS_HEIGHT = 40

_LOGGER = logging.getLogger('gameinterface')

FPS = 30

GET_WORST_BODY_PART = game.USEREVENT + 1


class GameInterface(object):
    """Wrapper for game interface"""

    MAX_SPEED = 5

    def __init__(self, callback=lambda: None,
                 mode=STATE_VIEW, filename=None, user='Leon'):
        _LOGGER.info('Started interface')

        game.init()
        self._infoObject = game.display.Info()
        self._state = mode
        screen_width = self._infoObject.current_w >> 1
        screen_height = (self._infoObject.current_h >> 1) + STATUS_HEIGHT
        self._screen = game.display.set_mode((screen_width,
                                              screen_height),
                                             game.HWSURFACE |
                                             game.DOUBLEBUF |
                                             game.RESIZABLE, 32)
        _LOGGER.info('Screen width: {}, Screen height: {}'.format(
            self._screen.get_width(), self._screen.get_height()))
        self._kinect = kinect.KinectStream()
        self._surface = game.Surface((self._kinect.colorFrameDesc(
        ).Width, self._kinect.colorFrameDesc().Height), 0, 32)
        self._analysis = analysis.AnalysisStream(
            self._kinect, filename)if filename else None
        self._status_bar = status.StatusBar(fontsize=24,
                                            size=(self._screen.get_width(),
                                                  STATUS_HEIGHT), user=user)
        game.display.set_caption('Fluid Body Analyzer')
        self._callback = callback
        self._bodies = []
        self._pause = False
        self._audio = audio.AudioInterface(self)
        self._speed = 2
        self._clock = game.time.Clock()

        if self._analysis:
            self._worst = None
            self._body = None
            game.time.set_timer(GET_WORST_BODY_PART, 2000)  # 2 seconds

    def quit(self):
        """Closes the game interface cleanly without
        ripping any connections or anything dangling"""
        self._status_bar.to_lines('Closing')
        game.quit()
        self._callback()
        try:
            self._analysis.close()
            self._kinect.close()
            self._stop_listening()
        except:
            pass

    def drawCameraInput(self, frame, surface):
        """Takes the kinect's camera output (colorframe) and uses c's
        memmove to throw it onto the screen surface's buffer"""

        surface.lock()
        addr = self._kinect.surfaceAsArray(surface.get_buffer())
        ctypes.memmove(addr, frame.ctypes.data, frame.size)
        del addr
        surface.unlock()

    def surfaceToScreen(self):
        """Takes the current screen that we were drawing on and the
        analysis screen and blits it onto the game screen"""

        scale = float(self._surface.get_height()) / self._surface.get_width()
        real_screen_w = self._screen.get_width()
        scaled_height = int(scale * (real_screen_w))
        draw_surface = game.transform.scale(
            self._surface, (real_screen_w, scaled_height))
        self._screen.blit(draw_surface, (0, 0))
        self._screen.blit(self._status_bar.get_surface(),
                          (0, self._screen.get_height() - STATUS_HEIGHT))
        draw_surface = analysis_surface = None
        game.display.update()
        game.display.flip()

    def drawLines(self, lines, surface, color=None, width=8):
        """Takes a list of tuples, each containing two endpoints
        of a line segment to draw on a 2d surface"""

        color = random.choice(GAME_COLORS) if not color else color
        lines = list(lines)
        if not lines or len(lines) < 1:
            return
        font = game.font.Font(None, 60)
        traversal = list(kinect.traverse())
        for index, (start, end) in enumerate(lines):
            if start is None or end is None:
                continue
            try:
                game.draw.line(surface, color, start, end, width)
                jointtype = traversal[index][1]
                if jointtype not in [21, 22, 23, 24]:
                    game.draw.circle(surface, color, map(
                        lambda i: int(i), end), 20, 0)
            except TypeError:
                pass

    def toggle_state(self):
        if self._state == STATE_RECORD or self._state == STATE_VIEW:
            self._state = STATE_RECORD if self._state == STATE_VIEW \
                else STATE_VIEW
        else:
            self._state = STATE_COMPARE if self._state == STATE_WAITING \
                else STATE_WAITING

        if self._state == STATE_RECORD:
            self._kinect.initRecord()

    def event_trigger(self, event):
        if event.type == game.QUIT:
            self.quit()
        elif event.type == game.VIDEORESIZE:  # window resized
            self._screen = game.display.set_mode(
                event.dict['size'],
                game.HWSURFACE | game.DOUBLEBUF |
                game.RESIZABLE, 32)
        elif event.type == GET_WORST_BODY_PART and self._body:
            self._worst = self._analysis.get_worst_body_part(self._body)
        elif event.type == game.KEYDOWN:
            if event.key == game.K_ESCAPE:
                self.quit()
            state_record = self._state == STATE_RECORD
            state_view = self._state == STATE_VIEW
            state_waiting = self._state == STATE_WAITING
            state_compare = self._state == STATE_COMPARE
            if event.key == game.K_RETURN:
                if state_record or state_view:
                    self.toggle_state()
                else:
                    if state_waiting:
                        _LOGGER.info('Start comparison')
                        self._state = STATE_COMPARE
                    else:
                        self._state = STATE_WAITING
            elif event.key == game.K_p:
                if self._pause:
                    self._status_bar.to_lines('Resumed')
                else:
                    self._status_bar.to_lines('Paused')
                    self.surfaceToScreen()
                self._pause = not self._pause
            elif event.key == game.K_m:
                self._audio.mute()
            elif event.key == game.K_r:
                if state_compare or state_waiting:
                    self._analysis.reset_frame()
            elif event.key == game.K_UP:
                self._speed = self._speed - 1 if self. _speed > 1 else 1
            elif event.key == game.K_DOWN:
                self._speed = self._speed + \
                    1 if self._speed < GameInterface.MAX_SPEED \
                    else GameInterface.MAX_SPEED

    def run(self):
        """Main game runtime of the code, when this process stops it should quit,
        Checks pygame events, can be paused using 'P', muted using 'M'
        Toggles current state using 'return'"""

        screen, kinect = self._screen, self._kinect,
        surface, analysis = self._surface, self._analysis

        status_body = None

        self._stop_listening = self._audio.listen()
        while True:
            for event in game.event.get():
                self.event_trigger(event)

            if self._pause:
                continue

            if kinect:
                if kinect.hasNewColorFrame():  # Must go first
                    self.drawCameraInput(kinect.getLastColorFrame(), surface)
                if kinect.hasNewBodyFrame():
                    self._bodies = kinect.getLastBodyFrame().bodies

            # Set analysis callback
            if self._state == STATE_COMPARE and \
                    any(body.is_tracked for body in self._bodies):
                color_analysis = analysis.color.get_next_frame(self._speed)
                camera_analysis = analysis.camera.get_next_frame(self._speed)

            for count, body in enumerate(self._bodies):
                if not body.is_tracked:
                    continue
                self._body = body
                self.drawLines(
                    kinect.drawBody(body),
                    self._surface, GAME_COLORS[2], width=4)
                if self._state == STATE_RECORD:
                    kinect.recordFrame(body)
                    break
                elif self._state == STATE_COMPARE and \
                        color_analysis and camera_analysis:
                    color = color_analysis(body)  # x, y
                    lines = list(analysis.color_points_to_bones(color))
                    self.drawLines(lines, self._surface, GAME_COLORS[1])

                    if self._worst:
                        _LOGGER.info('worst {}'.format(self._worst))
                        camera = camera_analysis(body)  # x, y, z
                        vector = analysis.get_dist_dir(
                            camera, body, self._worst)
                        message = analysis.get_status_message(
                            vector[0], vector[1], self._worst)
                        self._status_bar.to_analysis(message)
            self.surfaceToScreen()

            self._clock.tick(FPS)
