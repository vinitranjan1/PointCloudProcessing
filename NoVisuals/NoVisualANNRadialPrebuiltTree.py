import sys
sys.path.append('../')
from Filters.ANNGuidedFilterPrebuiltTree import ann_guided_filter_prebuilt_tree
from Filters.ANNRadialFilterPrebuiltTreeMultiStdev import ann_radial_filter_prebuilt_tree_multi_stdev
from tqdm import tqdm, trange
from SavePointsAsLAS import save_points_as_las
import numpy as np
from annoy import AnnoyIndex
from ReadRawLAS import read_raw_las_data
from laspy.file import File
import pdb
import h5py


input1 = "../MantecaRoom1/room1.las"
output1 = "../MantecaRoom1/room1ANNGuidedN40Epsp07.las"
tree_file = "../MantecaRoom1/room1tree.tree"

pc = np.array([], dtype=np.float32)
pc2 = np.array([], dtype=np.float32)
with File(input1, mode='r') as f:
    input_header = f.header

    raw_points = read_raw_las_data(input1)
    points = ann_radial_filter_prebuilt_tree_multi_stdev(raw_points, r=.6, tree_file=tree_file)

    #
    #
    # points2 = read_raw_las_data(output1)
    # for point in tqdm(points2, total=len(points), desc="Adding to pc"):
    #     pc2.addPoint(point)
    #
    # create_point_cloud_plot_qt([pc, pc2])
    pdb.set_trace()
    # save_points_as_las(points, output1, input_header)

