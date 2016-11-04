import pygame
from kinect import Kinect2


class GameRunTime(object):

    def __init__(self):
        pygame.init()
        self._clock = pygame.time.Clock()
        self._display_info = pygame.display.Info()
        self._screen = pygame.display.set_mode(
            (self._display_info.current_w >> 1, self._display_info.current_h >> 1), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)

        pygame.display.set_captioon("Fluid-Body")

        self._done = False
        self._kinect = Kinect2()

    def draw(self):
        pass

    def run(self):
        pass

if __name__ == '__main__':
    game = GameRunTime()
    game.run()
