from laspy.file import File
from tqdm import tqdm
from PlotUtils.PointCloudPlotQt import create_point_cloud_plot_qt
from Utils.ReadRawLAS import read_raw_las_data
from Filters.GuidedFilterkNN import guided_filter_kNN
from PlotUtils.VtkPointCloud import VtkPointCloud

# input_file = "../MantecaDock/dock.las"
input_file = "../MantecaDock/fourPallets.las"
pointCloud = VtkPointCloud()
filteredPointCloud = VtkPointCloud()

with File(input_file, mode='r') as f:
    input_header = f.header

    print("reading %s" % input_file)

    points = read_raw_las_data(input_file)
    for point in tqdm(points, total=len(points), desc="Adding"):
        pointCloud.addPoint(point)

    filtered_points = guided_filter_kNN(points, k=40, filter_eps=.1)
    # filtered_points = radius_outlier_filter(points, r=1, search_eps=0, sd_cutoff=1)
    for filtered_point in tqdm(filtered_points, total=len(filtered_points), desc="Adding"):
        filteredPointCloud.addPoint(filtered_point)

    print("Original has %d points" % len(points))
    print("Filtered has %d points" % len(filtered_points))

    to_plot = [pointCloud, filteredPointCloud]
    create_point_cloud_plot_qt(to_plot)

