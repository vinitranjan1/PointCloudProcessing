from laspy.file import File
import numpy as np
from Utils.AxisAlignedBox3D import AxisAlignedBox3D
from SliceFunctions.NaiveSliceFromLAS import naive_slice_from_las
from PlotUtils.VtkPointCloud import VtkPointCloud

input_file = "../MantecaDock/dock.las"
output_file = "../MantecaDock/fourPallets.las"

inFile = File(input_file, mode='r')
outFile = File(output_file, mode='w', header=inFile.header)

pointCloud = VtkPointCloud()

sliced = naive_slice_from_las(input_file, AxisAlignedBox3D([204.24, -6.7, -1.9], [208.46, -3.24, 3.5]))
# sliced = [[1, 1, 1]]
print("Number of points sliced: %d" % len(sliced))
# for point in sliced:
#     pointCloud.addPoint(point)
#
#     outFile.write(point)
# pdb.set_trace()
allx = np.array([sliced[i][0] for i in range(len(sliced))])
ally = np.array([sliced[i][1] for i in range(len(sliced))])
allz = np.array([sliced[i][2] for i in range(len(sliced))])
outFile.x = allx
outFile.y = ally
outFile.z = allz
# print("Number of points: %d" % len(sliced))
# print('Plotting')
# # Renderer
# renderer = vtk.vtkRenderer()
# renderer.AddActor(pointCloud.vtkActor)
# renderer.SetBackground(.2, .3, .4)
# renderer.ResetCamera()
#
# # Render Window
# renderWindow = vtk.vtkRenderWindow()
# renderWindow.AddRenderer(renderer)
#
# # Interactor
# renderWindowInteractor = vtk.vtkRenderWindowInteractor()
# renderWindowInteractor.SetRenderWindow(renderWindow)
#
# # Begin Interaction
# renderWindow.Render()
# renderWindowInteractor.Start()
inFile.close()
outFile.close()
