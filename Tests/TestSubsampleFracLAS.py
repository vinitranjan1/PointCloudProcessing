import sys
from laspy.file import File
from PlotUtils.CreateVTKPCFromArray import create_vtkpc_from_array
from PlotUtils.PointCloudPlotQt import create_point_cloud_plot_qt
from SubsampleFunctions.SubsampleFrac import subsample_frac
import pdb
from Utils.ReadRawLAS import read_raw_las_data

sys.path.append('../')

# input_file = "../MantecaDock/dock.las"
# x = [1, 2, 3, 4, 6]
# print(binary_search(x, 0, len(x)-1, 5))
input1 = "../MantecaDock/fourPallets.las"

desired_num_points = 100000
with File(input1, mode='r') as f:
    input_header = f.header
    # print("reading %s" % input_file)

    points = read_raw_las_data(input1)
    points2 = subsample_frac(points, .1)

    pc = create_vtkpc_from_array(points)
    pc2 = create_vtkpc_from_array(points2)

    to_plot = [pc, pc2]
    create_point_cloud_plot_qt(to_plot, input_header=input_header, axes_on=False)
    pdb.set_trace()
    # close after creating, else save won't work
    # f.close()
