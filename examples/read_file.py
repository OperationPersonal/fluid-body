import csv

file = "1478278237.87"

def read(file):
    reader = csv.reader(open("../data/" + file, "r"), delimiter=';', skipinitialspace=True)
    values = []
    for row in reader:
        values.append([ eval(x) for x in row])
    return values

print read(file)
