from AxisAlignedBox3D import AxisAlignedBox3D
from laspy.file import File
from tqdm import tqdm
import numpy as np


def naive_slice_from_las(filename, slice_box=AxisAlignedBox3D()):
    points = []

    with File(filename, mode='r') as in_file:
        scales = in_file.header.scale
        offsets = in_file.header.offset
        x_s, y_s, z_s = scales[0], scales[1], scales[2]
        x_o, y_o, z_o = offsets[0], offsets[1], offsets[2]

        lower_corner = slice_box.min_corner()
        upper_corner = slice_box.max_corner()
        for datum in tqdm(in_file.points, total=len(in_file.points), desc="Slicing"):
            # print([datum[0][0], datum[0][1], datum[0][2]])
            s0 = scale(datum[0][0], x_s, x_o)
            s1 = scale(datum[0][1], y_s, y_o)
            s2 = scale(datum[0][2], z_s, z_o)
            if lower_corner[0] <= s0 <= upper_corner[0]\
                    and lower_corner[1] <= s1 <= upper_corner[1]\
                    and lower_corner[2] <= s2 <= upper_corner[2]:
                points.append(np.array([s0, s1, s2]))
        print("sliced %d points" % len(points))
    return points


def scale(point, scale_factor, offset):
    return (point * scale_factor) + offset
