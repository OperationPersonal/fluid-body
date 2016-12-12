import pygame as game
import logging
from datetime import datetime

import os

_LOGGER = logging.getLogger('statusbar')

# qo aH I SONR KNOQ RHat is happening righ tnow this is so weoid
# dsadjsaddjdksad jsdjnxzc shashjn


class StatusBar(object):

    def __init__(self, fontname='Futura-Medium', fontsize=24,
                 size=(500, 40), user='', color='white', audio=None):
        self._fontname = fontname
        self._fontsize = fontsize
        self.set_font(fontname, fontsize)
        self._surface = game.Surface(size)
        self._user = os.environ['Fluid Username'].replace('\n', '')
        self._line = ''
        self._color = game.color.THECOLORS['white']
        self._audio = audio

        self._analysis = None

    def to_lines(self, line):
        self._line = line

    def to_analysis(self, line):
        self._analysis = line
        self._audio.speak(line)
        _LOGGER.debug('line {}'.format(line))

    def set_font(self, fontname=None, fontsize=None):
        self._fontname = fontname = fontname if fontname else self._fontname
        self._fontsize = fontsize = fontsize if fontsize else self._fontsize
        self._font = game.font.Font(
            'resources/{}.ttf'.format(fontname), fontsize)
        self._side_font = game.font.Font(
            'resources/{}.ttf'.format(fontname), fontsize - 7)

    def get_surface(self):
        self._surface.fill((0, 0, 0))
        username = self._side_font.render(self._user, True, self._color)
        status = self._font.render(self._line, True, self._color)
        formatted_time = datetime.strftime(datetime.now(), '%m/%d/%y %I:%M %p')
        time = self._side_font.render(formatted_time, True, self._color)
        left_offset = 10
        centered_height = (self._surface.get_height() -
                           status.get_height()) // 2
        side_height = (self._surface.get_height() - time.get_height()) - 5
        status_pos = (left_offset, centered_height)
        time_pos = (self._surface.get_width() -
                    time.get_width() - 10, side_height)
        username_pos = (time_pos[0] - username.get_width() - 10,
                        side_height)

        if self._analysis is not None:
            an = self._font.render(self._analysis, True,
                                   game.color.THECOLORS['red'])
            anpos = (210, centered_height)
            self._surface.blit(an, anpos)
        self._surface.blit(username, username_pos)
        self._surface.blit(status, status_pos)
        self._surface.blit(time, time_pos)
        return self._surface
