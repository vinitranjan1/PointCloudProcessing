"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

An slight modification of the guided point cloud filtering algorithm from Han, et al., 2017
https://doi.org/10.1007/s11042-017-5310-9

Look at ANNGuidedFilter.py for more details

This script is for the case where you want to try tuning epsilon and do different epsilons at the same time

Inputs:
input_list - list containing point cloud to filter
neighbors - number of neighbors
eps_list - list of epsilons you want to try
dim - dimension of points (will likely always be 3 for our applications)

Returns:
outs - list of lists of points, same size as eps_list
"""
import numpy as np
import pdb
from scipy.spatial import kdtree
import time
from tqdm import tqdm, trange
from annoy import AnnoyIndex


def ann_guided_filter_multi_eps(input_cloud, neighbors=40, eps_list=[.05, 1.0], dim=3):
    num = len(input_cloud)
    tree = AnnoyIndex(dim, metric='euclidean')
    for k in trange(num, desc="Preparing for ANN"):
        tree.add_item(k, input_cloud[k])

    start = time.time()
    num_trees = 5
    tree.build(num_trees)
    end = time.time() - start
    print("Building %d trees took %d seconds" % (num_trees, end))

    neighbor_list = []
    for k in trange(num, desc="Doing ANN"):
        neighbor_list.append(tree.get_nns_by_item(k, neighbors))

    print("neighbors found")

    outs = []
    for eps in eps_list:
        outs.append(get_output(input_cloud, neighbor_list, eps, dim))
    pdb.set_trace()
    return outs


def get_output(input_cloud, neighbor_list, filter_eps, dim):
    output_cloud = []
    for i in trange(len(input_cloud), desc=("Filtering %f" % filter_eps)):
        # remember that neighbor list gives a list of indices that need to be pulled from input_list
        # step 1, as referred to in the paper
        neighbors = neighbor_list[i]
        # step 2
        k = float(len(neighbors))
        # step 3
        p_bar = np.asarray([0.] * dim)
        for n in neighbors:
            # print(input_cloud[n])
            try:
                p_bar += input_cloud[n]
            except IndexError:
                pdb.set_trace()
        p_bar /= k
        # print(p_bar)
        # step 4
        temp = 0
        for n in neighbors:
            temp += np.dot(input_cloud[n], input_cloud[n])
        temp /= k
        centroid_dot = np.dot(p_bar, p_bar)
        a = (temp - centroid_dot) / ((temp - centroid_dot) + filter_eps)
        # step 5
        b = p_bar - a*p_bar
        # step 6
        output_cloud.append(a*input_cloud[i]+b)

    return output_cloud

