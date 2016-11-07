import os
import platform
import Tkinter as tk
from Tkinter import *

import pygame

root = tk.Tk()
# creates embed frame for pygame window
embed = tk.Frame(root, width=500, height=500)
embed.grid(columnspan=(600), rowspan=500)  # Adds grid
embed.pack(side=LEFT)  # packs window to the left
buttonwin = tk.Frame(root, width=75, height=125)
buttonwin.pack(side=LEFT)
button2 = tk.Frame(root, width=75, height=125)
button2.pack(side=LEFT)
# os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
# if platform.system == "Windows":
#     os.environ['SDL_VIDEODRIVER'] = 'windib'

blackcircle, whitecircle = 0, 0
# os.environ['blackcircle']/


def draw():
    os.environ['blackcircle'] = 'True'
    # print('hi', blackcircle)
    root.destroy()


def draw2():
    whitecircle = True
    print('hi2', whitecircle)
    root.destroy()

button1 = Button(buttonwin, text='Draw',  command=draw)
button1.pack(side=LEFT)
button2draw = Button(button2, text="2", command=draw2)
button2draw.pack(side=LEFT)
root.update()

root.mainloop()

print(blackcircle, whitecircle)

pygame.display.init()
screen = pygame.display.set_mode((500, 500))
screen.fill(pygame.Color(255, 255, 255))
pygame.display.update()
if os.environ['blackcircle'] == 'True':
    print('lmao')
    pygame.draw.circle(screen, (0, 0, 0), (250, 250), 125)
if whitecircle:
    print('lmao2')
    pygame.draw.circle(screen, (255, 0, 0), (250, 250), 125)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
