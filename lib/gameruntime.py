from dis import dis
from pprint import pprint

import pygame


# import


class GameRunTime(object):

  def __init__(self):
    pygame.init()
    self._clock = pygame.time.Clock()
    self._display_info = pygame.display.Info()
    self._screen = pygame.display.set_mode(
        (self._display_info.current_w >> 1, self._display_info.current_h >> 1), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)

    pygame.display.set_captioon("Fluid-Body")

    self._done = False
    self._

  def run(self):
    pprint('hi')
    pprint(vars(pygame.display))
    pprint(dir(self._screen), indent=2)

if __name__ == '__main__':
  game = GameRunTime()
  game.run()
