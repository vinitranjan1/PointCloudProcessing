from laspy.file import File
from PlotUtils.PointCloudPlotQt import create_point_cloud_plot_qt
from Utils.ReadRawLAS import read_raw_las_data
from Filters.RoundingFilter import rounding_filter
from PlotUtils.CreateVTKPCFromArray import create_vtkpc_from_array

# input_file = "../MantecaDock/dock.las"
input_file = "../MantecaRoom1/room1.las"
input2 = "../MantecaDock/palletsRoundedp01.las"


with File(input_file, mode='r') as f:
    input_header = f.header

    print("reading %s" % input_file)

    points = read_raw_las_data(input_file)
    pc = create_vtkpc_from_array(points)

    rounded = rounding_filter(points)
    pc2 = create_vtkpc_from_array(rounded)

    to_plot = [pc, pc2]
    create_point_cloud_plot_qt(to_plot, input_header=input_header)

