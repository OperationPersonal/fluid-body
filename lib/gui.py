from Tkinter import *
from gameinterface import GameInterface
import os
import logging
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

    def restart(self):
        self.__init__()
        self.run()

    def listrecords(self):
        root = self._root
        menu = Frame(root, width=500, height=500)
        menu.grid(columnspan=4, padx=100, pady=100)

        def addRecord(handle, name, buttons=[]):

            def startcompare():
                self._state = 'COMPARE' if handle and name else 'MENU'
                self._recording = handle
                self._title = name
                root.destroy()

            b = Frame(menu, width=125, height=125)
            b.grid(row=len(buttons), sticky=W)
            buttons.append(b)
            b = Button(b, text=name or 'Cancel', command=startcompare)
            b.pack(side=LEFT)

        records = self.get_records()
        # [('file handle', 'Assigned Name')]
        addRecord(None, None)
        for record in records:
            print(record)
            addRecord(*record)

    def get_records(self):
        for f in os.listdir('./data'):
            print f
        return list((f, f) for f in os.listdir('./data') if f != '.gitignore')

    def gui_close(self):
        if self._state == 'QUIT':
            return sys.exit()
        if self._state == 'MENU':
            self.__init__()
            self.run()
            return
        if self._state == 'RECORD':
            game = GameInterface(callback=self.restart)
            game.run()
        elif self._state == 'COMPARE':
            game = GameInterface(callback=self.restart, filename=self._recording, mode='COMPARE')
            game.run()

    def run(self):
        self._root.mainloop()
        self.gui_close()

if __name__ == '__main__':
    g = Gui()
    g.run()
