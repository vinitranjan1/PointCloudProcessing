"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

A function to subsample from a list of points and accept each point with probability sample_frac
Equivalent to SubsampleFrac.py, only it reads directly from the .las file

Inputs:
points - list of points to sample from
sample_frac - fraction of desired points

Returns:
points - list of sampled points
"""
import numpy as np
import pdb
from laspy.file import File
from tqdm import tqdm, trange


def subsample_frac_from_las_data(filename, sample_frac=.1):
    points = []

    with File(filename, mode='r') as in_file:
        scales = in_file.header.scale
        offsets = in_file.header.offset
        x_s, y_s, z_s = scales[0], scales[1], scales[2]
        x_o, y_o, z_o = offsets[0], offsets[1], offsets[2]

        for point in tqdm(in_file.points, total=len(in_file.points), desc="Sampling"):
            # for i in trange(len(in_file.x), desc="Sampling"):
            if np.random.random_sample() < sample_frac:
                points.append(np.array([scale(point[0][0], x_s, x_o),
                                          scale(point[0][1], y_s, y_o),
                                          scale(point[0][2], z_s, z_o)], dtype=np.float32))
    return points


# helper function to scale points
def scale(point, scale_factor, offset):
    return (point * scale_factor) + offset
