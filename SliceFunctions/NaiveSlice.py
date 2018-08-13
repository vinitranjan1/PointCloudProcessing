"""
Vinit Ranjan, Chris Eckman
Lineage Logistics
6/5/18

Naive implementation of slicing algorithm by brute force checking from list of points

Inputs:
data - list of points to slice from
slice_box - AxisAlignedBox3D that gives desired slice points

Returns:
points - list containing sliced points
"""
from Utils.AxisAlignedBox3D import AxisAlignedBox3D
from tqdm import tqdm


def naive_slice(data, slice_box=AxisAlignedBox3D()):
    points = []
    lower_corner = slice_box.min_corner()
    upper_corner = slice_box.max_corner()
    for datum in tqdm(data, total=len(data), desc="Slicing"):
        if lower_corner[0] <= datum[0] <= upper_corner[0] and lower_corner[1] <= datum[1]\
                <= upper_corner[1] and lower_corner[2] <= datum[2] <= upper_corner[2]:
            points.append(datum)
    return points
