from laspy.file import File
import numpy as np

input_file = "MantecaRoom1/room1.las"

inFile = File(input_file, mode='r')
print(type(inFile.points))


inFile.close()
