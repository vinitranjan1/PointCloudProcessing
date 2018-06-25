from AxisAlignedBox3D import AxisAlignedBox3D
from laspy.file import File
from tqdm import tqdm


def naive_slice_from_las(filename, slice_box=AxisAlignedBox3D()):
    points = []

    in_file = File(filename, mode='r')
    scales = in_file.header.scale
    offsets = in_file.header.offset
    x_s, y_s, z_s = scales[0], scales[1], scales[2]
    x_o, y_o, z_o = offsets[0], offsets[1], offsets[2]

    lower_corner = slice_box.min()
    upper_corner = slice_box.max()
    for datum in tqdm(in_file.points, total=len(in_file.points), desc="Slicing"):
        # print([datum[0][0], datum[0][1], datum[0][2]])
        if lower_corner[0] <= scale(datum[0][0], x_s, x_o) <= upper_corner[0]\
                and lower_corner[1] <= scale(datum[0][1], y_s, y_o) <= upper_corner[1]\
                and lower_corner[2] <= scale(datum[0][2], z_s, z_o) <= upper_corner[2]:
            points.append([scale(datum[0][0], x_s, x_o), scale(datum[0][1], y_s, y_o), scale(datum[0][2], z_s, z_o)])
    in_file.close()
    return points


def scale(point, scale_factor, offset):
    return (point * scale_factor) + offset
