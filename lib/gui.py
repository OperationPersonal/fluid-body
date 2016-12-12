#!/usr/bin/python

from Tkinter import *
import tkFont
from PIL import Image, ImageTk

import os
import logging
from datetime import datetime

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
        self._record_font = tkFont.Font(family='Helvetica', size=12)
        self.background()
        self.grid()
        if 'Fluid Username' not in os.environ:
            self.login()
        else:
            self.startmenu()

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
        def submit():
            self._username = self._user_field.get(1.0, 'end')
            os.environ['Fluid Username'] = self._username
            self._user_field.destroy()
            self._submit.destroy()
            self.startmenu()

        def on_entry_click(event):
            if 'Username' in self._user_field.get(1.0, 'end'):
                self._user_field.delete(1.0, "end")
                self._user_field.insert(1.0, '')

        self._user_field = Text(
            self._root, relief='raised', font=self._entry_font, padx=10,
            pady=6, width=35, height=1)
        self._user_field.grid(row=5, column=3)
        self._user_field.insert(1.0, 'Username')
        self._user_field.bind('<FocusIn>', on_entry_click)
        self._submit = Button(text='Submit', command=submit,
                              font=self._font, relief='raised',
                              overrelief='sunken', cursor='hand2',
                              bg='#0BA489', width=8, height=1, pady=0)
        self._submit.grid(row=6, column=3, sticky='n')

    def record_name(self):
        def submit():
            self._record_name = self._record_field.get(1.0, 'end')
            os.environ['Fluid Exercise'] = self._record_name
            self._state = 'RECORD'
            self._root.destroy()

        def on_entry_click(event):
            if 'Exercise Name' in self._record_field.get(1.0, 'end'):
                self._record_field.delete(1.0, "end")
                self._record_field.insert(1.0, '')

        self._record_field = Text(
            self._root, relief='raised', font=self._entry_font, padx=10,
            pady=6, width=35, height=1)
        self._record_field.grid(row=5, column=3)
        self._record_field.insert(1.0, 'Exercise Name')
        self._record_field.bind('<FocusIn>', on_entry_click)
        self._submit = Button(text='Submit', command=submit,
                              font=self._font, relief='raised',
                              overrelief='sunken', cursor='hand2',
                              bg='#0BA489', width=8, height=1, pady=0)
        self._submit.grid(row=6, column=3, sticky='n')

    def startmenu(self):
        def start():
            self._record.destroy()
            self._compare.destroy()
            self.record_name()

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
        record_frame = Frame(self._root)
        record_frame.grid(row=4, column=3)

        def cancel():
            self._state = 'MENU'
            root.destroy()

        def addRecord(handle, name, count):
            def startcompare():
                self._state = 'COMPARE'
                self._recording = handle
                self._title = name
                root.destroy()

            name_parts = name.split(';')
            spacing = '                 '
            name = (name_parts[0] + spacing + name_parts[1] + spacing +
                    datetime.fromtimestamp(float(name_parts[2])).strftime(
                '%m/%d/%Y'))
            record = Button(record_frame, text=name, command=startcompare,
                            font=self._record_font, background='white',
                            relief='flat', cursor='hand2')
            record.grid(row=count, column=0, sticky='nwes')

        records = self.get_records()
        count = 0
        for record in records:
            addRecord(records[0], record[1], count)
            count += 1
        cancel_button = Button(record_frame, text='Cancel', command=cancel,
                               font=self._entry_font, relief='raised',
                               overrelief='sunken', cursor='hand2',
                               bg='#F7567C', width=10, height=1)
        spacing = Label(record_frame)
        spacing.grid(row=count + 1, column=0)
        cancel_button.grid(row=count + 2, column=0)

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
