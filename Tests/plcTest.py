import vtk
import csv
import numpy as np
import time
from VtkPointCloud import VtkPointCloud

pointCloud = VtkPointCloud()


Start = time.time()
points = []
with open('../AllentownRoom2_Cleaned.txt') as f:
    reader = csv.reader(f, delimiter="\t")
    for raw in list(reader):
        fix = raw[0].split()
        pointCloud.addPoint(np.asarray([float(fix[0]), float(fix[1]), float(fix[2])]))
End = time.time() - Start
# if random.uniform(0, 1) <= 0.2:
#     try:
#         fix = raw[0].split()
#         pointCloud.addPoint(np.asarray([float(fix[0]), float(fix[1]), float(fix[2])]))
#     except:
#         pdb.set_trace()

print('Reading took %f seconds' % End)
print('Plotting')
# Renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(pointCloud.vtkActor)
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
