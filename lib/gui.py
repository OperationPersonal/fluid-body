import Tkinter as tk
from Tkinter import *

import pygame as py


class Gui(object):

    def __init__(self):
        self._state = 'QUIT'
        self._menucol = 0
        root = self._root = Tk()
        root.wm_title('Fluid')
        self.startmenu()

    def startmenu(self):
        root = self._root
        menu = Frame(root, width=500, height=500)
        menu.grid(columnspan=500, rowspan=500, padx=100, pady=100)

        def addMenuButton(command, width=125, height=125, side=LEFT, text='button', col=[]):
            b = Frame(menu, width=width, height=height)
            b.grid(column=len(col), row=0)
            col.append(b)
            b = Button(b, text=text, command=command)
            b.pack(side=side)
            root.update()

        def setstate(state):
            def temp():  # Returns function using closure to set current state and exit loop
                self._state = state
                self._root.destroy()
            return temp

        def compare():
            menu.destroy()
            self.listrecords()

        addMenuButton(setstate('START'), text='Start')
        addMenuButton(setstate('RECORD'), text='Record')
        addMenuButton(compare, text='Compare')

    def listrecords(self):
        root = self._root
        menu = Frame(root, width=500, height=500)
        menu.grid(columnspan=4)

        def addRecord(handle, name, buttons=[]):

            def startcompare():
                self._state = 'COMPARE' if handle and name else 'MENU'
                self._recording = handle
                self._title = name
                root.destroy()

            b = Frame(menu, width=125, height=125)
            b.grid(column=len(buttons))
            buttons.append(b)
            b = Button(b, text=name or 'Exit', command=startcompare)
            b.pack()

        records = [('file handle', 'Assigned Name')]
        for record in records:
            addRecord(*record)
        addRecord(None, None)

    def gui_close(self):
        if self._state == 'QUIT':
            sys.exit()
            return
        if self._state == 'MENU':
            self.__init__()
            self.run()
            return
        screen = self._screen = py.display.set_mode((750, 750))
        screen.fill(py.Color(255, 255, 255))
        if self._state == 'START':
            py.draw.circle(screen, (0, 0, 0), (375, 375), 125)
        elif self._state == 'RECORD':
            py.draw.circle(screen, (0, 255, 0), (375, 375), 125)
        if self._state == 'COMPARE':
            print(self._recording, self._title)
            py.draw.circle(screen, (0, 0, 255), (375, 375), 125)
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
                    self.__init__()
                    self.run()

            py.display.update()

if __name__ == '__main__':
    g = Gui()
    g.run()
