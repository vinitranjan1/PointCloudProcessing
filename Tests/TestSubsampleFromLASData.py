import vtk
import time
from SubsampleFunctions.SubsampleFromLASData import subsample_from_las_data
from PlotUtils.VtkPointCloud import VtkPointCloud

pointCloud = VtkPointCloud()
desired_number_points = 350000
input_file = "../MantecaDock/dock.las"

# txt = open('AllentownRoom2_Cleaned.txt', 'rb')
#
# points = np.array([])
# with open('AllentownRoom2_Cleaned.txt') as f:
#     reader = csv.reader(f, delimiter="\t")
#     i = 0
#     for raw in list(reader):
#         rand = np.random.randint(0, i+1)
#         fix = raw[0].split()
# # TODO finish this, use numpy arrays then convert at the end

#pointCloud.addPoint(np.asarray([float(fix[0]), float(fix[1]), float(fix[2])]))

Start = time.time()
points = subsample_from_las_data(input_file, desired_number_points)
for point in points:
    pointCloud.addPoint(point)
End = time.time() - Start

print("Sampling took %f seconds" % End)
print(len(points))
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
