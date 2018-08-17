"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

An slight modification of the guided point cloud filtering algorithm from Han, et al., 2017
https://doi.org/10.1007/s11042-017-5310-9

The modification is dropping the kD tree to do the k nearest neighbors step for an approximate nearest neighbor tree
    provided from the package annoy

This version trades a little accuracy but for a drastic increase in speed

HEAVILY recommend using this instead of the deterministic one

Inputs:
input_list - list containing point cloud to filter
num_neighbors - number of neighbors
filter_eps - (epsilon) as desired tuning constant for accuracy (look at paper for details)
dim - dimension of points (will likely always be 3 for our applications)
tree_file - if you want to do multiple trials, you can build and save the ANN tree to disk
    (check https://github.com/spotify/annoy for details) and so, if you supply the file here itll load from disk
    instead of recomputing
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


def ann_guided_filter(input_list, num_neighbors=40, filter_eps=.05, dim=3, tree_file=None, config_file=None):
    output_cloud = []

    num = len(input_list)
    if tree_file is not None:
        tree = AnnoyIndex(dim, metric='euclidean')
        tree.load(tree_file)
    else:
        tree = AnnoyIndex(dim, metric='euclidean')
        for k in trange(num, desc="Preparing for ANN"):
            tree.add_item(k, input_list[k])

        start = time.time()
        num_trees = 2
        tree.build(num_trees)
        end = time.time() - start
        print("Building %d trees took %d seconds" % (num_trees, end))

    for i in trange(len(input_list), desc="ANN + Filtering"):
        # remember that neighbor list gives a list of indices that need to be pulled from input_list
        # step 1, as referred to in the paper
        neighbors = tree.get_nns_by_item(i, num_neighbors)
        # step 2
        k = float(len(neighbors))
        # step 3
        p_bar = np.asarray([0.] * dim)
        for n in neighbors:
            # print(input_list[n])
            try:
                p_bar += input_list[n]
            except IndexError:
                pdb.set_trace()
        p_bar /= k
        # print(p_bar)
        # step 4
        temp = 0
        for n in neighbors:
            temp += np.dot(input_list[n], input_list[n])
        temp /= k
        centroid_dot = np.dot(p_bar, p_bar)
        a = (temp - centroid_dot) / ((temp - centroid_dot) + filter_eps)
        # step 5
        b = p_bar - a*p_bar
        # step 6
        try:
            output_cloud.append(a * input_list[i] + b)
        except TypeError:
            output_cloud.append(a * np.array(input_list[i]) + b)
    if config_file is not None:
        return output_cloud, {"num_neighbors": num_neighbors, "filter_eps": filter_eps, "dim": dim}
    return output_cloud
