from laspy.file import File
from tqdm import tqdm, trange
from PointCloudPlotQt import create_point_cloud_plot_qt
from SubsampleFromLASData import subsample_from_las_data
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

# input_file = "../MantecaDock/dock.las"
# x = [1, 2, 3, 4, 6]
# print(binary_search(x, 0, len(x)-1, 5))
# input1 = "../MantecaRoom1/room1sliceANNRadialANNGuided.las"
# input1 = "../MantecaDock/dock.las"
input1 = "../WatsonvilleEngineRoom/compressor.las"
input1 = "../MantecaRoom1/room1.las"
input2 = "../WatsonvilleEngineRoom/compressorANNGuidedN40epsp07.las"
# # input_two = "../MantecaDock/smallAreaGuidedk40.las"
# input2 = "../MantecaDock/palletsGuidedFiltered_k40_eps_tenth.las"
# input3 = "../MantecaDock/palletsGuided_Radial.las"  #radial uses sd_cutoff = 1.5
# input4 = "../MantecaDock/palletsRadial.las"
# input5 = "../MantecaDock/palletsRadial_Guided.las"
# input2 = "../MantecaRoom1/room1sliceANNGuided.las"  # sd_cutoff =
desired_num_points = 100000
pc = VtkPointCloud()
pc2 = VtkPointCloud()
pc3 = VtkPointCloud()
pc4 = VtkPointCloud()
pc5 = VtkPointCloud()
with File(input1, mode='r') as f:
    input_header = f.header
    to_plot = [pc, pc4]
    # print("reading %s" % input_file)

    points = read_raw_las_data(input1)
    for point in tqdm(points, total=len(points), desc="Adding"):
        pc.addPoint(point)

    # points2 = read_raw_las_data(input2)
    # for point in tqdm(points2, total=len(points2), desc="Adding"):
    #     pc2.addPoint(point)

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
    points4 = ann_guided_filter(points, neighbors=40, filter_eps=.07)
    for point in tqdm(points4, total=len(points4), desc="Adding"):
        pc4.addPoint(point)

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
    create_point_cloud_plot_qt(to_plot, input_header=input_header, axes_on=False)
    pdb.set_trace()
    # close after creating, else save won't work
    # f.close()
