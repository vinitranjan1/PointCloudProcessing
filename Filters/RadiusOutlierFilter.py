import numpy as np
import pdb
from scipy.spatial import kdtree
import time
from tqdm import tqdm, trange


def radius_outlier_filter(input_cloud, r=1, search_eps=0, p=2, sd_cutoff=1):
    output_cloud = []
    print("Constructing kdtree")
    tree = kdtree.KDTree(input_cloud)
    other_tree = kdtree.KDTree(input_cloud)
    print("kdtree constructed")
    print("finding neighbors")
    # neighbor_list = []
    # for point in tqdm(input_cloud, total=len(input_cloud), desc="Finding Neighbors"):
    #     neighbor_list.append(tree.query_ball_point(point, r=r, eps=search_eps))

    start = time.time()
    neighbor_list = tree.query_ball_tree(other_tree, r=r, p=p, eps=search_eps)
    end = time.time() - start
    print("Finding neighbors took %s seconds" % end)

    lengths = [len(x) for x in neighbor_list]
    mean = np.mean(lengths)
    std = np.std(lengths)
    cutoff = mean - sd_cutoff*std
    for i in trange(len(neighbor_list), desc="Removing outliers"):
        if lengths[i] >= cutoff:
            output_cloud.append(input_cloud[i])

    return output_cloud
