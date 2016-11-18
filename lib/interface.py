import pygame as game


class GameInterface(object):

    def __init__(self, width=750, height=750, background=(255, 255, 255), callback=lambda: None):
        screen = self._screen = game.display.set_mode((width, height))
        # Make the background - must be tuple
        self._background_color = background
        screen.fill(game.Color(*background))
        self._clock = game.time.Clock()
        self._callback = callback

    def setBackgroundColor(self, background=(255, 255, 255)):
        self._background_color = background
        self._screen.fill(game.Color(*background))

    def run(self):
        x = 250
        y = 250
        screen = self._screen
        while True:
            for event in game.event.get():
                if event.type == game.QUIT:
                    game.quit()
                    self._callback()

            # game logic goes here
            game.draw.circle(screen, (0, 0, 0), (x, y), 50)
            x += 5
            y += 5

            self._clock.tick(30)

            game.display.update()
