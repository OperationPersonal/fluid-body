#!/usr/bin/python

from Tkinter import *
import tkFont
from PIL import Image, ImageTk

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
        self._root = root = Tk()
        root.wm_title('Fluid')
        root.geometry('{}x{}'.format(WIDTH, HEIGHT))
        self._font = tkFont.Font(family='Helvetica', size=18)
        self._entry_font = tkFont.Font(family='Helvetica', size=14)
        self.background()
        self.grid()
        self.startmenu()
        # self.login()

    def grid(self):
        for y in range(0, 9):
            self._root.grid_rowconfigure(y, weight=1)
        for x in range(0, 7):
            self._root.grid_columnconfigure(x, weight=1)
        self._root.grid_columnconfigure(2, weight=0)
        self._root.grid_columnconfigure(4, weight=0)

    def background(self):
        self.image = Image.open(
            'C:/Users/Leon/Documents/Fluid/resources/gym.jpg')
        self.img_copy = self.image.copy()
        self.background_image = ImageTk.PhotoImage(self.image)

        self._background = Label(self._root, image=self.background_image)
        self._background.place(x=0, y=0, relwidth=1, relheight=1)
        self._background.bind('<Configure>', self._resize_image)

    def _resize_image(self, event):
        new_width = event.width
        new_height = event.height

        self.image = self.img_copy.resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.image)
        self._background.configure(image=self.background_image)

    def login(self):
        def submit(self):
            self._username = self._user_field.get()
            self._user_field.destroy()
            self._submit.destroy()
            self.startmenu()

        self._user_field = Text(
            self._root, relief='raised', font=self._entry_font, padx=10,
            pady=6, width=35, height=1)
        self._user_field.grid(row=5, column=3)
        entry.insert(0, 'Enter your user name...')
        self._submit = Button(text='Submit', command=submit,
                              font=self._font, relief='raised',
                              overrelief='sunken', cursor='hand2',
                              bg='#F7567C', width=10, height=1, pady=6)
        self._submit.grid(row=6, column=3, sticky='n')

    def startmenu(self):
        def start():
            self._state = 'RECORD'
            self._root.destroy()

        def compare():
            self._record.destroy()
            self._compare.destroy()
            self.listrecords()

        self._record = Button(text='Record', command=start,
                              font=self._font, relief='raised',
                              overrelief='sunken', cursor='hand2',
                              bg='#F7567C', width=10, height=1, pady=6)
        self._compare = Button(text='Compare', command=compare,
                               font=self._font, relief='raised',
                               overrelief='sunken', cursor='hand2',
                               bg='#0BA489', width=10, height=1, pady=6)
        self._record.grid(row=5, column=2)
        self._compare.grid(row=5, column=4)

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
        elif self._state == 'MENU':
            self.__init__()
            self.run()
            return
        elif self._state == 'RECORD':
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
