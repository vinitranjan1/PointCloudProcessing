import numpy as np
import pdb
from laspy.file import File
from tqdm import tqdm, trange


def subsample_from_las_data(filename, desired_number_points=10000):
    points = []

    with File(filename, mode='r') as in_file:
        scales = in_file.header.scale
        offsets = in_file.header.offset
        x_s, y_s, z_s = scales[0], scales[1], scales[2]
        x_o, y_o, z_o = offsets[0], offsets[1], offsets[2]

        i = 0
        for point in tqdm(in_file.points, total=len(in_file.points), desc="Sampling"):
            # for i in trange(len(in_file.x), desc="Sampling"):
            if i < desired_number_points:
                points.append(np.asarray([scale(point[0][0], x_s, x_o),
                                          scale(point[0][1], y_s, y_o),
                                          scale(point[0][2], z_s, z_o)], dtype=np.float32))
                # points.append(np.asarray([in_file.x[i], in_file.y[i], in_file.z[i]], dtype=np.float32))
                # pdb.set_trace()
            else:
                rand = np.random.randint(0, i)
                if rand < desired_number_points:
                    points[rand] = np.asarray([scale(point[0][0], x_s, x_o),
                                               scale(point[0][1], y_s, y_o),
                                               scale(point[0][2], z_s, z_o)], dtype=np.float32)
            i += 1
    return points


# helper function to scale points
def scale(point, scale_factor, offset):
    return (point * scale_factor) + offset
