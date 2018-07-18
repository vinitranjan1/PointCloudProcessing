import sys
from laspy.file import File
from tqdm import tqdm, trange
from CreateVTKPCFromArray import create_vtkpc_from_array
from PointCloudPlotQt import create_point_cloud_plot_qt
from SubsampleFromLASData import subsample_from_las_data
from SubsampleFracFromLAS import subsample_frac_from_las_data
from Filters.RadiusOutlierFilter import radius_outlier_filter
from Filters.ANNGuidedFilter import ann_guided_filter
from Filters.ANNGuidedFilterPrebuiltTree import ann_guided_filter_prebuilt_tree
from Filters.ANNGuidedFilterMultiEps import ann_guided_filter_multi_eps
from Filters.ANNRadialMultiStdev import ann_radial_filter_multi_stdev
from Filters.GuidedFilterkNN import guided_filter_kNN
from Filters.ANNRadialFilter import ann_radial_filter
from Filters.RoundingFilter import rounding_filter
from Filters.ThresholdFilter import threshold_filter
from NaiveSlice import naive_slice
from NaiveSliceFromLAS import naive_slice_from_las
from AxisAlignedBox3D import AxisAlignedBox3D
import pdb
from ReadRawLAS import read_raw_las_data
from VtkPointCloud import VtkPointCloud
import h5py
sys.path.append('../')

# input_file = "../MantecaDock/dock.las"
# x = [1, 2, 3, 4, 6]
# print(binary_search(x, 0, len(x)-1, 5))
# input1 = "../MantecaRoom5/room5scan1/room5scan1.las"
# input1 = "../MantecaDock/fourPallets.las"
# input1 = "../MantecaRoom1/room1slice.las"
# input1 = "../MantecaCompressorRoom/compressorRoom.las"
# input1 = "../MantecaRoom1/room1ANNGuidedN40Epsp07.las"
# input1 = "../MantecaRoom1/room1AGRounded.las"
# input1 = "../MantecaRoom5/room5.las"
# input1 = "../MantecaDock/dock.las"
# input1 = "../MantecaRoom1/room1.las"
# input1 = "../MantecaRoom1/room1AGRoundedARSDC1p3.las"
# input1 = "../MantecaRoom2/room2.las"
# input1 = "../MantecaRoom2/room2SAGN40epsp05.las"
# input1 = "../MantecaRoom4/room4S.las"
input1 = "../MantecaRoom3/room3.las"
# input1 = "../MantecaRoom6/room6S.las"
# input1 = "../MantecaRoom1/room1slice.las"
# input1 = "../MantecaDock/dock.las"
# input1 = "../MantecaRoom4/Ceckman.las"

desired_num_points = 100000
with File(input1, mode='r') as f:
    input_header = f.header
    to_plot = []
    # print("reading %s" % input_file)

    # samp = subsample_frac_from_las_data(input1, .05)
    # points = naive_slice(samp, AxisAlignedBox3D([-100, -50, 2], [400, 100, 3]))
    # points = naive_slice_from_las(input1, AxisAlignedBox3D([-100, -50, 2], [400, 100, 3]))
    points = subsample_frac_from_las_data(input1, .05)
    # points = read_raw_las_data("../MantecaRoom2/room2F.las")
    # points = rounding_filter(points)
    pc = create_vtkpc_from_array(points)
    to_plot.append(pc)

    # points2 = threshold_filter(points, threshold=.01)
    # pc2 = create_vtkpc_from_array(points2)
    # to_plot.append(pc2)

    # points3 = rounding_filter(points2, decimal_places=3)
    # pc3 = create_vtkpc_from_array(points3)
    # to_plot.append(pc3)
    #
    # points4 = ann_radial_filter(points3, r=.01)
    # pc4 = create_vtkpc_from_array(points4)
    # to_plot.append(pc4)

    # points2 = threshold_filter(points, threshold=.12)
    # pc2 = create_vtkpc_from_array(points2)
    # to_plot.append(pc2)
    #
    # points3 = threshold_filter(points, threshold=.15)
    # pc3 = create_vtkpc_from_array(points3)
    # to_plot.append(pc3)

    # point_sets = ann_radial_filter_multi_stdev(points, h5dir="../MantecaRoom1/", h5f="room1AGRoundedAR")
    # for p in point_sets:
    #     to_plot.append(create_vtkpc_from_array(p))

    # points2 = read_raw_las_data(input2)
    # pc2 = create_vtkpc_from_array(points2)

    # points3 = ann_radial_filter(points, r=.07, sd_cutoff=.5) # TODO this gives mean=307 and std=232
    # points3 = read_raw_las_data(input3)
    # for point in tqdm(points3, total=len(points3), desc="Adding"):
    #     pc3.addPoint(point)

    # points4 = ann_guided_filter(points3, neighbors=40, filter_eps=.07)
    # for point in tqdm(points4, total=len(points4), desc="Adding"):
    #     pc4.addPoint(point)

    # points2 = read_raw_las_data(input2)
    # for point in tqdm(points2, total=len(points2), desc="Adding"):
    #     pc2.addPoint(point)
    #
    # points3 = read_raw_las_data(input3)
    # for point in tqdm(points3, total=len(points3), desc="Adding"):
    #     pc3.addPoint(point)
    #
    # points4 = ann_guided_filter(points, neighbors=40, filter_eps=.07)
    # for point in tqdm(points4, total=len(points4), desc="Adding"):
    #     pc4.addPoint(point)

    # points_set = ann_guided_filter_multi_eps(points, neighbors=40, eps_list=[.05, .06, .07, .08, .09])
    # for pset in points_set:
    #     new_pc = VtkPointCloud()
    #     for point in tqdm(pset, total=len(pset), desc="Adding"):
    #         new_pc.addPoint(point)
    #     to_plot.append(new_pc)

    # points_set = ann_radial_filter_multi_stdev(points, r=.07, sd_cutoffs=[1.2, 1.25, 1.3])
    # for pset in points_set:
    #     new_pc = VtkPointCloud()
    #     for point in tqdm(pset, total=len(pset), desc="Adding"):
    #         new_pc.addPoint(point)
    #     to_plot.append(new_pc)

    # points2 = ann_radial_filter(points, r=.07, sd_cutoff=1.3)
    # # points2 = guided_filter_kNN(points, k=40, filter_eps=.05)
    # for point in tqdm(points2, total=len(points2), desc="Adding"):
    #     pc2.addPoint(point)

    # points3 = radius_outlier_filter(points2, .1, search_eps=.5, p=2, sd_cutoff=1.4)
    # for point in tqdm(points3, total=len(points3), desc="Adding"):
    #     pc3.addPoint(point)
    #
    # points4 = radius_outlier_filter(points, .1, search_eps=.5, p=2, sd_cutoff=1.5)
    # for point in tqdm(points4, total=len(points4), desc="Adding"):
    #     pc4.addPoint(point)
    #
    # points5 = guided_filter_kNN(points4, k=40, filter_eps=.05)
    # for point in tqdm(points5, total=len(points5), desc="Adding"):
    #     pc5.addPoint(point)

    # points2 = radius_outlier_filter(points, r=.1, search_eps=.5, p=2, sd_cutoff=1.3)
    # for point in tqdm(points2, total=len(points2), desc="Adding"):
    #     pc2.addPoint(point)
    #
    # filtered_points = guided_filter_kNN(points2, k=40, filter_eps=.1)
    # # filtered_points = radius_outlier_filter(points, r=1, search_eps=0, sd_cutoff=1)
    # for filtered_point in tqdm(filtered_points, total=len(filtered_points), desc="Adding"):
    #     fpc.addPoint(filtered_point)

    # to_plot = [pc, pc2, pc3, pc4, pc5]

    # create_point_cloud_plot_qt(to_plot, input_header)
    # to_plot = [pc, pc2, pc3, pc4]

    create_point_cloud_plot_qt(to_plot, input_header=input_header, axes_on=True)
    pdb.set_trace()
    # close after creating, else save won't work
    # f.close()
