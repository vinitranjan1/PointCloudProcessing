import vtk
import time
import pdb
from SubsampleFunctions.SubsampleFromLASData import subsample_from_las_data
from PlotUtils.VtkPointCloud import VtkPointCloud

pointCloud = VtkPointCloud()
cube = vtk.vtkCubeSource()
cube.SetBounds(-9.0, 10.2, -3, 10, -1, 5)
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputConnection(cube.GetOutputPort())
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)
cubeActor.GetProperty().SetOpacity(.5)

desired_number_points = 100000
# input_file = "../MantecaRoom1/room1.las"
input_file = "../MantecaDock/fourPallets.las"

Start = time.time()
points = subsample_from_las_data(input_file, desired_number_points)
# points = [[0, 0, 0]]
for point in points:
    pointCloud.addPoint(point)
End = time.time() - Start

print("Sampling took %f seconds" % End)
print(len(points))
print('Plotting')
# Renderer
renderer = vtk.vtkRenderer()
# pointCloud.vtkActor.SetMapper(cubeMapper)


renderer.AddActor(cubeActor)
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
renderWindowInteractor.Initialize()

pdb.set_trace()
renderWindow.Render()
renderWindowInteractor.Start()
