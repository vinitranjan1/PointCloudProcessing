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
sd_cutoffs - list of sd_cutoffs to try
dim - dimension of points (will likely always be 3 for our applications)
metric - distance metric to use, usually will be Euclidean, check the annoy github page for all options
tree_file - if you want to do multiple trials, you can build and save the ANN tree to disk
    (check https://github.com/spotify/annoy for details) and so, if you supply the file here itll load from disk
    instead od recomputing
h5_file - the 'lengths' array is the number of neighbors per point, you can use h5py to save this array to disk and
    load it in - essentially an even further checkpoint

Returns:
outs - list of lists of points, same size as eps_list
"""
import numpy as np
import pdb
from scipy.spatial import kdtree
import time
from tqdm import tqdm, trange
from annoy import AnnoyIndex
import h5py


def binary_search(tree, arr, left, right, curr, r):
    while left <= right:
        mid = left + int((right - left) / 2)
        if tree.get_distance(curr, arr[mid]) < r:
            left = mid + 1
        else:
            right = mid - 1
    return left


def get_neighbor_length(k, num_neighbors, tree, r):
    neighbors = num_neighbors
    while 1:
        ann = tree.get_nns_by_item(k, neighbors, include_distances=False)
        if tree.get_distance(k, ann[-1]) < r:
            # print(ann[1][-1])
            # print("not enough")
            neighbors *= 2
        else:
            cutoff = binary_search(tree, ann, 0, len(ann) - 1, k, r=r)
            return len(ann[:cutoff])


def ann_radial_filter_multi_stdev(input_cloud, r=.1, sd_cutoffs=[1, 1.5], metric='euclidean', dim=3, tree_file=None,
                                  h5_file=None):
    if h5_file is None:
        num = len(input_cloud)
        if tree_file is not None:
            tree = AnnoyIndex(dim, metric='euclidean')
            tree.load(tree_file)
        else:
            tree = AnnoyIndex(3, metric=metric)
            for k in trange(num, desc="Preparing for ANN"):
                tree.add_item(k, input_cloud[k])

            start = time.time()
            num_trees = 4
            tree.build(num_trees)
            end = time.time() - start
            print("Building %d trees took %d seconds" % (num_trees, end))

        lengths = []
        num_neighbors = 2000
        for k in trange(num, desc="Doing ANN"):
            lengths.append(get_neighbor_length(k, num_neighbors, tree, r=r))

        print("neighbors found")
    else:
        print("h5 file found at "+h5_file)
        with h5py.File(h5_file, 'r') as hf:
            lengths = hf[h5_file][:]

    outs = []
    for sd in sd_cutoffs:
        outs.append(get_output(input_cloud, lengths, sd))
    pdb.set_trace()
    return outs


def get_output(input_cloud, lengths, sd_cutoff):
    output_cloud = []
    mean = np.mean(lengths)
    std = np.std(lengths)
    print("mean is %f" % mean)
    print("std is %f" % std)
    cutoff = mean - sd_cutoff * std
    for i in trange(len(lengths), desc="Removing outliers"):
        if lengths[i] >= cutoff:
            output_cloud.append(input_cloud[i])
    return output_cloud
