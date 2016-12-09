#!/usr/bin/python

from Tkinter import *
import tkFont

import os
import logging

import gameinterface

"""Tkinter gui that launches pygame according to button pressed"""

__author__ = "Leon Chou and Roy Xu"
WIDTH = 960
HEIGHT = 590


class Gui(object):

    def __init__(self):
        self._state = 'QUIT'
        self._menucol = 0
        self._root = root = Tk()
        root.wm_title('Fluid')
        root.geometry('{}x{}'.format(WIDTH, HEIGHT))
        self.background()
        self.logo()
        self.startmenu()

    def logo(self):
        logo_image = PhotoImage(
            file='C:/Users/Leon/Documents/Fluid/resources/logo.gif')
        logo_label = Label(self._root, image=logo_image)
        logo_label.place(x=0, y=0, relwidth=1, relheight=1)
        logo_label.photo = logo_image

    def background(self):
        background_image = PhotoImage(
            file='C:/Users/Leon/Documents/Fluid/resources/gym.gif')
        background_label = Label(self._root, image=background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        background_label.photo = background_image

    def startmenu(self):
        button_frame = Frame(self._root, width=50, height=10, pady=230)
        button_frame.pack()

        def addMenuButton(command, width=10, height=1, side=LEFT,
                          text='button', color='black'):
            font = tkFont.Font(family='Helvetica', size=18)
            b = Button(button_frame, text=text, command=command,
                       width=width, height=height, font=font,
                       relief='flat', bg=color)
            b.pack(side=side, padx=10)

        def setstate(state):
            def temp():
                # Returns function using closure to set current state and exit
                # loop
                self._state = state
                self._root.destroy()
            return temp

        def compare():
            menu.destroy()
            self.listrecords()

        addMenuButton(setstate('RECORD'), text='Record', color='red')
        addMenuButton(compare, text='Compare', color='green')

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
        addRecord(None, None)
        for record in records:
            addRecord(*record)

    def get_records(self):
        return list((f, f) for f in os.listdir('./data') if f != '.gitignore')

    def gui_close(self):
        if self._state == 'QUIT':
            return sys.exit()
        if self._state == 'MENU':
            self.__init__()
            self.run()
            return
        if self._state == 'RECORD':
            game = gameinterface.GameInterface(callback=self.restart)
            game.run()
        elif self._state == 'COMPARE':
            game = gameinterface.GameInterface(callback=self.restart,
                                               filename=self._recording,
                                               mode='WAITING')
            game.run()

    def run(self):
        self._root.mainloop()
        self.gui_close()
