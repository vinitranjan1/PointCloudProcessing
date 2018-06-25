from laspy.file import File
import numpy as np
import vtk
import time
import pdb
from tqdm import tqdm
from ReadRawLAS import read_raw_las_data
from ScalePoint import scale_point
from VtkPointCloud import VtkPointCloud

# input_file = "../MantecaDock/dock.las"
input_file = "../MantecaDock/fourPallets.las"
pointCloud = VtkPointCloud()

print("reading %s" % input_file)

points = read_raw_las_data(input_file)
for point in tqdm(points, total=len(points), desc="Adding"):
    # need to double index because in las file, point[0] returns the entire point
    # print(np.asarray([point[0][0], point[0][1], point[0][2]]))
    pointCloud.addPoint(point)
    # pdb.set_trace()
# pdb.set_trace()

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
