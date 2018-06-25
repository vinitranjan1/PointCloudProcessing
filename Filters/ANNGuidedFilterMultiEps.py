import numpy as np
import pdb
from scipy.spatial import kdtree
import time
from tqdm import tqdm, trange
from annoy import AnnoyIndex


def ann_guided_filter_multi_eps(input_cloud, neighbors=40, eps_list=[.05, 1.0], dim=3):
    # print("Constructing kdtree")
    # tree = kdtree.KDTree(input_cloud)
    # other_tree = kdtree.KDTree(input_cloud)
    # print("kdtree constructed")
    # print("finding neighbors")

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
    # start = time.time()
    # # neighbor_list = tree.query_ball_tree(other_tree, r=r, p=p, eps=search_eps)
    # end = time.time() - start
    # print("Finding neighbors took %s seconds" % end)
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

