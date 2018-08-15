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
