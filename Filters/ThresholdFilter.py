"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

A function for "threshold filtering" - the idea is that you mesh all the points into bins of size mesh x mesh
    by removing dim_to_collapse
Any points that live in a bin, b, such that the number of points in b is at least the threshold*max(size(bins))
    are the points that survive
For example, if there are 4 bins and the number of points are [1, 1.5, 3, 4] and threshold = .5, then the points in
    bins of size 3 and 4 survive the filter because the max is 4 and 4 * .5 = 2

Inputs:
filename - las file to read in
dim_to_collapse - dimension to remove from consideration, i.e. using "Z" meshes in the XY-plane
    must be either "X", "Y", or "Z"
mesh - bin size, so resulting bins are size mesh x mesh
threshold - parameter used to determing required density for bins to survive

Returns:
output_list - list of thresholded points
"""
import numpy as np
from tqdm import tqdm, trange
import pdb


def threshold_filter(input_list, dim_to_collapse="Z", mesh=0.05, threshold=.25):
    output_list = []
    hist, xedges, yedges = __collapse_one_dim(input_list, dim_to_collapse, mesh)
    max_value = max([max(i) for i in hist])
    cutoff = int(threshold * max_value)
    mask = (hist >= cutoff)

    for p in tqdm(input_list, total=len(input_list), desc="Filtering"):
            x_coord = binary_search(xedges, 0, len(xedges) - 1, p[0])
            y_coord = binary_search(yedges, 0, len(yedges) - 1, p[1])
            if mask[x_coord][y_coord]:
                output_list.append(p)
    return output_list


def point_in_bin(point, target_bin):
    return target_bin[0][0] <= point[0] <= target_bin[0][1] and target_bin[1][0] <= point[1] <= target_bin[1][1]


def __collapse_one_dim(points, to_collapse, mesh):
    label_to_dim = {"X": 0, "Y": 1, "Z": 2}
    dim_to_label = {0: "X", 1: "Y", 2: "Z"}
    collapse_dim = label_to_dim[to_collapse]
    dims = [0, 1, 2]
    dims.remove(collapse_dim)
    arr1 = []
    arr2 = []
    for k in trange(len(points), desc="Getting Points"):
        p = points[k]
        arr1.append(p[dims[0]])
        arr2.append(p[dims[1]])
    xbins = int((max(arr1) - min(arr1)) / float(mesh))
    ybins = int((max(arr2) - min(arr2)) / float(mesh))
    return np.histogram2d(arr1, arr2, bins=(xbins, ybins))


def binary_search(arr, left, right, x):
    while left <= right:
        mid = left + int((right - left) / 2)
        if arr[mid] < x:
            left = mid + 1
        else:
            right = mid - 1
    return left-1


def search(arr, val):
    for i in range(len(arr)-1):
        if arr[i] <= val <= arr[i+1]:
            return i
