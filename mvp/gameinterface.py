import pygame as game

class GameInterface(object):

    def __init__(self, width=750, height=750, background=(255, 255, 255), callback=lambda: None):
        screen = self._screen = game.display.set_mode((width, height))
        # Make the background - must be tuple
        self._background_color = background
        screen.fill(game.Color(*background))
        self._clock = game.time.Clock()
        self._callback = callback
        self._surface = game.Surface((width, height), depth=32)

    def setBackgroundColor(self, background=(255, 255, 255)):
        self._background_color = background
        self._screen.fill(game.Color(*background))

    def quit(self):
        game.quit()
        self._callback()

    def run(self):
        x = 250
        y = 250
        screen = self._screen
        stream = None
        while True:
            for event in game.event.get():
                if event.type == game.QUIT:
                    self.quit()

            if stream:
                for (start, end) in stream:
                    game.draw.line(self._surface, game.color.THECOLORS["red"], start, end, 8)

            # game logic goes here
            game.draw.circle(screen, (0, 0, 0), (x, y), 50)
            x += 5
            y += 5

            self._clock.tick(30)

            game.display.update()
