"""
Vinit Ranjan, Chris Eckman
Lineage Logistics
6/5/18

Naive implementation of slicing algorithm by brute force checking from data

Inputs:
filename - path to csv/text file with data
slice_box - AxisAlignedBox3D that gives desired slice points

Returns:
points - list containing sliced points
"""
import csv
import numpy as np
from AxisAlignedBox3D import AxisAlignedBox3D


def naive_slice_from_data(filename, slice_box=AxisAlignedBox3D()):
    points = []
    with open(filename) as f:
        lower_corner = slice_box.min()
        upper_corner = slice_box.max()
        reader = csv.reader(f, delimiter="\t")
        for raw in list(reader):
            fix = raw[0].split()
            if lower_corner[0] <= float(fix[0]) <= upper_corner[0] and lower_corner[1] <= float(fix[1])\
                    <= upper_corner[1] and lower_corner[2] <= float(fix[2]) <= upper_corner[2]:
                points.append(np.asarray([float(fix[0]), float(fix[1]), float(fix[2])]))
    return points
