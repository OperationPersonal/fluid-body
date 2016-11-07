import Tkinter as tk
from Tkinter import *

import pygame as py


class Gui(object):

    def __init__(self):
        self._state = 'EXIT'
        self._root = tk.Tk()
        self.startmenu()

    def startmenu(self):
        root = self._root
        self.addMenuButton(root, self.start, text='start')

    def addMenuButton(self, root, command, width=125, height=125, side=LEFT, text='button'):
        b = self.b = Frame(root, width=width, height=height)
        b.pack(side=side)
        b = Button(b, text=text, command=command)
        b.pack(side=side)
        root.update()

    def start(self):
        self._state = 'START'
        self._root.destroy()

    def restart(self):
        self.__init__()
        self.run()

    def gui_close(self):
        screen = self._screen = py.display.set_mode((750, 750))
        if self._state == 'START':
            screen.fill(py.Color(255, 255, 255))
            py.draw.circle(screen, (0, 0, 0), (375, 375), 125)
            self.runpy()

    def run(self):
        self._root.mainloop()
        self.gui_close()

    def runpy(self):
        # This is where the recordstuff goes
        while True:
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    self.restart()

            py.display.update()

if __name__ == '__main__':
    g = Gui()
    g.run()
