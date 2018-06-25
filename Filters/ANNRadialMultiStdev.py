import numpy as np
import pdb
from scipy.spatial import kdtree
import time
from tqdm import tqdm, trange
from annoy import AnnoyIndex


def ann_radial_filter_multi_stdev(input_cloud, r=.1, sd_cutoffs=[1, 1.5], metric='euclidean'):
    output_cloud = []
    # print("Constructing kdtree")
    # tree = kdtree.KDTree(input_cloud)
    # other_tree = kdtree.KDTree(input_cloud)
    # print("kdtree constructed")
    # print("finding neighbors")

    num = len(input_cloud)
    tree = AnnoyIndex(3, metric=metric)
    for k in trange(num, desc="Preparing for ANN"):
        tree.add_item(k, input_cloud[k])

    start = time.time()
    num_trees = 4
    tree.build(num_trees)
    end = time.time() - start
    print("Building %d trees took %d seconds" % (num_trees, end))

    def binary_search(arr, left, right, curr):
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

    neighbor_list = []
    # start = time.time()
    # # neighbor_list = tree.query_ball_tree(other_tree, r=r, p=p, eps=search_eps)
    # end = time.time() - start
    # print("Finding neighbors took %s seconds" % end)
    for k in trange(num, desc="Doing ANN"):
        neighbors = 2000
        while 1:
            ann = tree.get_nns_by_item(k, neighbors, search_k=int(num_trees*neighbors/2), include_distances=False)
            if tree.get_distance(k, ann[-1]) < r:
                # print(ann[1][-1])
                # print("not enough")
                neighbors *= 2
            else:
                cutoff = binary_search(ann, 0, len(ann) - 1, k)
                neighbor_list.append(ann[:cutoff])
                break

    pdb.set_trace()

    print("neighbors found")

    outs = []
    for sd in sd_cutoffs:
        outs.append(get_output(input_cloud, neighbor_list, sd))
    pdb.set_trace()
    return outs


def get_output(input_cloud, neighbor_list, sd_cutoff):
    output_cloud = []
    lengths = [len(x) for x in neighbor_list]
    mean = np.mean(lengths)
    std = np.std(lengths)
    print("mean is %f" % mean)
    print("std is %f" % std)
    cutoff = mean - sd_cutoff * std
    for i in trange(len(neighbor_list), desc="Removing outliers"):
        if lengths[i] >= cutoff:
            output_cloud.append(input_cloud[i])
    return output_cloud
