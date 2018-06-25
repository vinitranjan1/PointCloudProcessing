import time
from laspy.file import File
import vtk
import numpy as np
from tqdm import tqdm
from AxisAlignedBox3D import AxisAlignedBox3D
from NaiveSliceFromLAS import naive_slice_from_las
from NaiveSlice import naive_slice
from SubsampleFromLASData import subsample_from_las_data
from ReadRawLAS import read_raw_las_data
from VtkPointCloud import VtkPointCloud
from PointCloudPlotQt import create_point_cloud_plot_qt
import pdb

input_file = "../MantecaRoom1/room1.las"
# out_file = "../MantecaDock/smallArea.las"
pointCloud = VtkPointCloud()
filteredPointCloud = VtkPointCloud()

with File(input_file, mode='r') as f:
    input_header = f.header

    print("reading %s" % input_file)

    points = read_raw_las_data(input_file)
    for point in tqdm(points, total=len(points), desc="Adding"):
        pointCloud.addPoint(point)

    filtered_points = naive_slice(points, AxisAlignedBox3D([-70, -20, 1.94], [10, 90, 2.54]))
    for filtered_point in tqdm(filtered_points, total=len(filtered_points), desc="Adding"):
        filteredPointCloud.addPoint(filtered_point)

    print("Original has %d points" % len(points))
    print("Sliced has %d points" % len(filtered_points))

    to_plot = [pointCloud, filteredPointCloud]
    create_point_cloud_plot_qt(to_plot)


# # inFile = File(out_file, mode='r')
# # outFile = File(out_file, mode='w', header=inFile.header)
#
# pointCloud = VtkPointCloud()
#
# print("reading from %s" % input_file)
# sliced = naive_slice_from_las(input_file, AxisAlignedBox3D([197.5000, -6.7000, -.2000], [209.5000, 1.0600, 8.6000]))
# # pdb.set_trace()
# # 1975000, 2095000, -67000, 10600, -2000, 86000 minx maxx miny maxy minz maxz
# for point in tqdm(sliced, total=len(sliced), desc="Adding"):
#     pointCloud.addPoint(point)
#
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
# # outFile.close()
