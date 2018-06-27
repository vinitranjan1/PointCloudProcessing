import sys
from laspy.file import File
from tqdm import tqdm, trange
from CreateVTKPCFromArray import create_vtkpc_from_array
from PointCloudPlotQt import create_point_cloud_plot_qt
from SubsampleFromLASData import subsample_from_las_data
from SubsampleFrac import subsample_frac
from Filters.RadiusOutlierFilter import radius_outlier_filter
from Filters.ANNGuidedFilter import ann_guided_filter
from Filters.ANNGuidedFilterMultiEps import ann_guided_filter_multi_eps
from Filters.ANNRadialMultiStdev import ann_radial_filter_multi_stdev
from Filters.GuidedFilterkNN import guided_filter_kNN
from Filters.ANNRadialFilter import ann_radial_filter
from NaiveSliceFromLAS import naive_slice_from_las
from AxisAlignedBox3D import AxisAlignedBox3D
import pdb
from ReadRawLAS import read_raw_las_data
from VtkPointCloud import VtkPointCloud
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
