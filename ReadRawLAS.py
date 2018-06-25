import numpy as np
import pdb
from laspy.file import File
from tqdm import tqdm, trange
from ScalePoint import scale_point


def read_raw_las_data(filename):
    points = []

    in_file = File(filename, mode='r')
    scales = in_file.header.scale
    offsets = in_file.header.offset
    x_s, y_s, z_s = scales[0], scales[1], scales[2]
    x_o, y_o, z_o = offsets[0], offsets[1], offsets[2]

    for point in tqdm(in_file.points, total=len(in_file.points), desc="Reading"):
        points.append(np.asarray([scale_point(point[0][0], x_s, x_o),
                                  scale_point(point[0][1], y_s, y_o),
                                  scale_point(point[0][2], z_s, z_o)], dtype=np.float32))
    in_file.close()
    return points
