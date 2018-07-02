import numpy as np
import pdb
from scipy.spatial import kdtree
import time
from tqdm import tqdm, trange
from annoy import AnnoyIndex


def binary_search(tree, arr, left, right, curr, r):
    while left <= right:
        mid = left + int((right - left) / 2)
        # print("left: %f" % left)
        # print("mid: %f" % mid)
        # print("right: %f" % right)
        # if arr[mid] == target:
        #     return mid
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


def ann_radial_filter(input_cloud, r=.1, sd_cutoff=1, tree_file=None, metric='euclidean'):
    output_cloud = []
    # print("Constructing kdtree")
    # tree = kdtree.KDTree(input_cloud)
    # other_tree = kdtree.KDTree(input_cloud)
    # print("kdtree constructed")
    # print("finding neighbors")

    tree = AnnoyIndex(3, metric='euclidean')
    tree.load(tree_file)

    lengths = []
    num_neighbors = 2000
    # start = time.time()
    # # neighbor_list = tree.query_ball_tree(other_tree, r=r, p=p, eps=search_eps)
    # end = time.time() - start
    # print("Finding neighbors took %s seconds" % end)
    for k in trange(len(input_cloud), desc="Doing ANN"):
        lengths.append(get_neighbor_length(k, num_neighbors, int(num_trees*num_neighbors/2), tree, r=r))

        # pdb.set_trace()

    # print("neighbors found")

    # lengths = [len(x) for x in neighbor_list]
    mean = np.mean(lengths)
    std = np.std(lengths)
    print("mean is %f" % mean)
    print("std is %f" % std)
    cutoff = mean - sd_cutoff * std
    for i in trange(len(lengths), desc="Removing outliers"):
        if lengths[i] >= cutoff:
            output_cloud.append(input_cloud[i])
    return output_cloud

