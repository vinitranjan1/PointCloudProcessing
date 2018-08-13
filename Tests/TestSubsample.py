"""
A test for Subsample.py
"""
import vtk
from vtk.util import numpy_support
import csv
import numpy as np
from VtkPointCloud import VtkPointCloud
from SubsampleFunctions.Subsample import subsample

pointCloud = VtkPointCloud()
desired_number_points = 10000

txt = open('../AllentownRoom2_Cleaned.txt', 'rb')


with open('../AllentownRoom2_Cleaned.txt') as f:
    reader = csv.reader(f, delimiter="\t")
    for raw in list(reader):
        fix = raw[0].split()
        pointCloud.addPoint(np.asarray([float(fix[0]), float(fix[1]), float(fix[2])]))

print('Subsampling')
print(type(pointCloud.vtkPoints))
data = numpy_support.vtk_to_numpy(pointCloud.vtkPoints.GetData())
sample = subsample(data, desired_number_points)
print(len(sample))
sampleCloud = VtkPointCloud()
for point in sample:
    sampleCloud.addPoint(point)

print('Plotting')
# Renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(sampleCloud.vtkActor)
renderer.SetBackground(.2, .3, .4)
renderer.ResetCamera()

# Render Window
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# Interactor
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Begin Interaction
renderWindow.Render()
renderWindowInteractor.Start()
