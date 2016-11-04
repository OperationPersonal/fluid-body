import csv
from lib. kinect import Kinect2

file = "1478280688.29"

kinect = Kinect2()

def read(file):
    reader = csv.reader(open("../data/" + file, "r"), delimiter=';', skipinitialspace=True)
    values = []
    for row in reader:
        yield [ eval(x) for x in row]

def get_frame(values):
    traversal = kinect.traverse(kinect.JointHierarchy)
    coords = []
    for x in traversal:
        print x

print get_frame(read(file))
