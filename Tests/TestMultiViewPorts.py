from tqdm import tqdm

from MultiPlotPointCloud import multi_plot_point_cloud
from ReadRawLAS import read_raw_las_data
from VtkPointCloud import VtkPointCloud

# input_file = "../MantecaDock/dock.las"
input_file = "../MantecaDock/fourPallets.las"
desired_num_points = 20000
pointCloud = VtkPointCloud()

print("reading %s" % input_file)

points = read_raw_las_data(input_file)
for point in tqdm(points, total=len(points), desc="Adding"):
    # need to double index because in las file, point[0] returns the entire point
    # print(np.asarray([point[0][0], point[0][1], point[0][2]]))
    pointCloud.addPoint(point)
    # pdb.set_trace()
# pdb.set_trace()


multi_plot_point_cloud([pointCloud, pointCloud])
