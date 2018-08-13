from laspy.file import File
from tqdm import tqdm
from PointCloudPlotQt import create_point_cloud_plot_qt
from Filters.ANNGuidedFilter import ann_guided_filter
import pdb
import numpy as np
from ReadRawLAS import read_raw_las_data
from VtkPointCloud import VtkPointCloud

# input_file = "../MantecaDock/dock.las"
# x = [1, 2, 3, 4, 6]
# print(binary_search(x, 0, len(x)-1, 5))
input1 = "../MantecaRoom1/rack.las"
input2 = "../MantecaRoom1/rackGuided.las"
pc = VtkPointCloud()
pc2 = VtkPointCloud()
pc3 = VtkPointCloud()
with File(input1, mode='r') as f:
    input_header = f.header
    # print("reading %s" % input_file)

    points = read_raw_las_data(input1)
    for point in tqdm(points, total=len(points), desc="Adding"):
        pc.addPoint(point)

    points_z = [point[2] for point in points]
    points2d = [point[:2] for point in points]

    points_f = ann_guided_filter(points2d, neighbors=1000, filter_eps=.1, dim=2)

    # pdb.set_trace()
    for i in range(len(points)):
        # points_f[i].append(points_z[i])
        points_f[i] = np.append(points_f[i], points_z[i])

    pdb.set_trace()
    for point in tqdm(points_f, total=len(points_f), desc="Adding"):
        pc2.addPoint(point)

    points3 = read_raw_las_data(input2)
    for point in tqdm(points3, total=len(points3), desc="Adding"):
        pc3.addPoint(point)

    to_plot = [pc, pc3, pc2]
    create_point_cloud_plot_qt(to_plot, axes_on=False)
    pdb.set_trace()
    # close after creating, else save won't work
    # f.close()
