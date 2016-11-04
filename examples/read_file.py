import csv
import math
from lib. kinect import Kinect2

file = "1478280688.29"

kinect = Kinect2()

def read(file):
    reader = csv.reader(open("data/" + file, "r"), delimiter=';', skipinitialspace=True)
    values = []
    for row in reader:
        yield [ eval(x) for x in row]

def get_coords(start, angles, length):
    y = math.sin(angles[0]) * length
    x = math.sin(angles[1]) * length
    return (start[0] + x, start[1] + y)

def get_frame(values, h, w):
    traversal = kinect.traverse(kinect.JointHierarchy)
    length = 50
    coords = [None for x in range(25)]
    coords[0] = (w / 2, 600)
    for x in traversal:
        coords[x[1]] = get_coords(coords[x[0]], values[x[1]], length)
    return coords

print get_frame(list(read(file))[0], 1200, 1200)
