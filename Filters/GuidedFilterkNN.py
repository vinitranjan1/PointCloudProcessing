"""
Vinit Ranjan, Chris Eckman
Lineage Logistics
6/8/18

An implementation of the guided point cloud filtering algorithm from Han, et al., 2017
https://doi.org/10.1007/s11042-017-5310-9

Inputs:
input_cloud - array containing point cloud to filter
k - number of neighbors
filter_eps - (epsilon) desired tuning constant for accuracy, note that this is different from the eps in the query
note, increased radius and decreased eps result in increased filter but longer computation time

Returns:
output - array containing filtered points
"""
import numpy as np
import pdb
from scipy.spatial import kdtree
from tqdm import tqdm, trange


# guided filter implementation assuming neighborhood determined by radius
def guided_filter_kNN(input_cloud, k=50, filter_eps=.05):
    output_cloud = []
    # put all points in kdtree
    print("Constructing kdtree")
    tree = kdtree.KDTree(input_cloud)
    # other_tree = kdtree.KDTree(input_cloud)
    print("kdtree constructed")
    print("finding neighbors")

    neighbor_list = []
    for q in tqdm(input_cloud, total=len(input_cloud), desc="Querying neighbors"):
        _, neighbors = tree.query(x=q, k=k, eps=0.5)
        neighbor_list.append(neighbors)
    # neighbor_list = tree.query(x=input_cloud, k=k, distance_upper_bound=5)
    # print(neighbor_list)

    print("neighbors found")
    # for point in tqdm(input_cloud, total=len(input_cloud)):
    #     neighbors = tree.query_ball_point(point, radius)

    for i in trange(len(input_cloud), desc="Filtering"):
        # remember that neighbor list gives a list of indices that need to be pulled from input_list
        # step 1, as referred to in the paper
        neighbors = neighbor_list[i]
        # step 2
        k = float(len(neighbors))
        # step 3
        p_bar = np.asarray([0., 0., 0.])
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
