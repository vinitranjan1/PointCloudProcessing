import numpy as np
import pdb
from scipy.spatial import kdtree
import time
from tqdm import tqdm, trange
from annoy import AnnoyIndex


def ann_guided_filter(input_cloud, neighbors=40, filter_eps=.05, tree_file=None, dim=3):
    output_cloud = []
    # print("Constructing kdtree")
    # tree = kdtree.KDTree(input_cloud)
    # other_tree = kdtree.KDTree(input_cloud)
    # print("kdtree constructed")
    # print("finding neighbors")

    num = len(input_cloud)
    tree = AnnoyIndex(dim)
    tree.load(tree_file)
    print("Tree loaded from disk")
    neighbor_list = []
    # start = time.time()
    # # neighbor_list = tree.query_ball_tree(other_tree, r=r, p=p, eps=search_eps)
    # end = time.time() - start
    # print("Finding neighbors took %s seconds" % end)
    for k in trange(num, desc="Doing ANN"):
        neighbor_list.append(tree.get_nns_by_item(k, neighbors))

    print("neighbors found")

    for i in trange(len(input_cloud), desc="Filtering"):
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

