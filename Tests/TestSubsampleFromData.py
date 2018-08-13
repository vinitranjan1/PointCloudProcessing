import vtk

from TextFunctions.SubsampleFromTextData import subsample_from_data
from PlotUtils.VtkPointCloud import VtkPointCloud

pointCloud = VtkPointCloud()
desired_number_points = 10000

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

points = subsample_from_data("../AllentownRoom2_Cleaned.txt", desired_number_points)
for point in points:
    pointCloud.addPoint(point)

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
