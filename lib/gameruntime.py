import csv
import math

import pygame
from kinect import Kinect2


class GameRunTime(object):

    def __init__(self):
        pygame.init()
        self._clock = pygame.time.Clock()
        self._display_info = pygame.display.Info()
        self._screen = pygame.display.set_mode(
            (self._display_info.current_w >> 1, self._display_info.current_h >> 1), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)

        pygame.display.set_caption("Fluid-Body")

        self._done = False
        self._kinect = Kinect2()
        self._record = False
        self._compare = False

        self._frame_surface = pygame.Surface(self._kinect._surface, 0, 32)

    def _set_frame(self):
        self._kinect

    def draw(self):
        height_width_ratio = self._frame_surface.get_height() / \
            self._frame_surface.get_width()
        screen_width = self._screen.get_width()
        screen_height = int(screen_width * height_width_ratio)
        draw_surface = pygame.transform.scale(
            self._frame_surface, (screen_width, screen_height))
        self._screen.blit(draw_surface, (0, 0))
        pygame.display.update()
        pygame.display.flip()

    def run(self):
        while not self._done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._done = True
                elif event.type == pygame.VIDEORESIZE:
                    self._screen = pygame.display.set_mode(
                        event.dict['size'], pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)
            self.draw()
            self._clock.tick(30)
        self._kinect.close()
        pygame.quit()


if __name__ == '__main__':
    game = GameRunTime()
    game.run()
