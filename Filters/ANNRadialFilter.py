"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

A modification to the RadiusOutlierFilter.py algorithm (same basic idea)

The modification is dropping the kD tree to do the k nearest neighbors step for an approximate nearest neighbor tree
    provided from the package annoy

This version trades a little accuracy but for a drastic increase in speed

HEAVILY recommend using this instead of the deterministic one

the binary_search and get_neighbor_length methods are helper functions for the actual filter

Inputs:
input_cloud - list containing point cloud to filter
r - radius to use
sd_cutoff - same as in RadiusOutlierFilter.py, refer there to see exact usage
dim - dimension of points (will likely always be 3 for our applications)
metric - distance metric to use, usually will be Euclidean, check the annoy github page for all options
tree_file - if you want to do multiple trials, you can build and save the ANN tree to disk
    (check https://github.com/spotify/annoy for details) and so, if you supply the file here itll load from disk
    instead od recomputing
config_file - if a flag is put in here, the function will return the result as well as a dictionary of parameters used
    for logging purposes, check NoVisuals/NoVisualMultiRooms.py for usage

Returns:
output_cloud - list containing filtered points
"""
import numpy as np
import pdb
from scipy.spatial import kdtree
import time
from tqdm import tqdm, trange
from annoy import AnnoyIndex


def binary_search(tree, arr, left, right, curr, r):
    while left <= right:
        mid = left + int((right - left) / 2)
        if tree.get_distance(curr, arr[mid]) < r:
            left = mid + 1
        else:
            right = mid - 1
    return left


def get_neighbor_length(k, num_neighbors, search_k_num, tree, r):
    neighbors = num_neighbors
    while 1:
        ann = tree.get_nns_by_item(k, neighbors, search_k=search_k_num, include_distances=False)
        if tree.get_distance(k, ann[-1]) < r:
            # print(ann[1][-1])
            # print("not enough")
            neighbors *= 2
        else:
            cutoff = binary_search(tree, ann, 0, len(ann) - 1, k, r=r)
            return len(ann[:cutoff])


def ann_radial_filter(input_cloud, r=.1, sd_cutoff=1, metric='euclidean', dim=3, tree_file=None, config_file=None):
    output_cloud = []

    num = len(input_cloud)
    num_trees = 2
    if tree_file is not None:
        tree = AnnoyIndex(dim, metric='euclidean')
        tree.load(tree_file)
    else:
        tree = AnnoyIndex(dim, metric='euclidean')
        for k in trange(num, desc="Preparing for ANN"):
            tree.add_item(k, input_cloud[k])

        start = time.time()
        tree.build(num_trees)
        end = time.time() - start
        print("Building %d trees took %d seconds" % (num_trees, end))

    lengths = []
    num_neighbors = 2000
    for k in trange(num, desc="Doing ANN For Radial"):
        lengths.append(get_neighbor_length(k, num_neighbors, int(num_trees*num_neighbors/2), tree, r=r))

        # pdb.set_trace()
    mean = np.mean(lengths)
    std = np.std(lengths)
    print("mean is %f" % mean)
    print("std is %f" % std)
    cutoff = mean - sd_cutoff * std
    for i in trange(len(lengths), desc="Removing Radial outliers"):
        if lengths[i] >= cutoff:
            output_cloud.append(input_cloud[i])
    preserved = "Radial filter preserved %.2f%% of points" % (100. * len(output_cloud) / len(input_cloud))
    print(preserved)
    if config_file is not None:
        return output_cloud, {"r": r, "sd_cutoff": sd_cutoff, "metric": metric, "preserved": preserved}
    return output_cloud

