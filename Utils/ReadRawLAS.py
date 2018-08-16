"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

A function to read in points from a las file and return as a list
Equivalent to subsample_frac_from_las(filename, sample_frac=1) from SubsampleFracFromLAS.py

Inputs:
filename - las file to read in

Returns:
points - list of points
"""
import numpy as np
import pdb
from laspy.file import File
from tqdm import tqdm, trange


def scale_point(point, scale_factor, offset):
    return (point * scale_factor) + offset


def read_raw_las_data(filename):
    points = []

    with File(filename, mode='r') as in_file:
        scales = in_file.header.scale
        offsets = in_file.header.offset
        x_s, y_s, z_s = scales[0], scales[1], scales[2]
        x_o, y_o, z_o = offsets[0], offsets[1], offsets[2]

        for point in tqdm(in_file.points, total=len(in_file.points), desc="Reading"):
            points.append(np.array([scale_point(point[0][0], x_s, x_o),
                                      scale_point(point[0][1], y_s, y_o),
                                      scale_point(point[0][2], z_s, z_o)], dtype=np.float32))
    return points
