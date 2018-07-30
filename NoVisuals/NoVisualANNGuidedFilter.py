import sys
sys.path.append('../')
from Filters.ANNGuidedFilter import ann_guided_filter
from tqdm import tqdm, trange
import numpy as np
from ReadRawLAS import read_raw_las_data
from laspy.file import File
import pdb

input1 = "../MantecaDock/fourPallets.las"
output1 = "../Output/temp.las"

pc = np.array([], dtype=np.float32)
pc2 = np.array([], dtype=np.float32)
with File(input1, mode='r') as f:
    input_header = f.header

    raw_points = read_raw_las_data(input1)
    points = ann_guided_filter(raw_points, num_neighbors=50, filter_eps=.07)

    #
    #
    # points2 = read_raw_las_data(output1)
    # for point in tqdm(points2, total=len(points), desc="Adding to pc"):
    #     pc2.addPoint(point)
    #
    # create_point_cloud_plot_qt([pc, pc2])
    # pdb.set_trace()

    with File(output1, mode='w', header=input_header) as file:
        # pdb.set_trace()
        # points = pc.getPoints()
        # print(points)
        allx = []
        ally = []
        allz = []
        # for p in tqdm(points, total=points.GetNumberOfPoints(), desc="Saving"):
        for i in trange(len(points), desc="Saving"):
            p = points[i]
            # print(p)
            allx.append(p[0])
            ally.append(p[1])
            allz.append(p[2])
        file.x = np.array(allx)
        file.y = np.array(ally)
        file.z = np.array(allz)
