import numpy as np
import pdb
from scipy.spatial import kdtree
from ReadRawLAS import read_raw_las_data
import time
from tqdm import tqdm, trange
from annoy import AnnoyIndex


input1 = "MantecaDock/fourPallets.las"


def ann_build_save_tree(input_cloud, tree_name, dim=3):
    num = len(input_cloud)
    tree = AnnoyIndex(dim, metric='euclidean')
    for k in trange(num, desc="Preparing for ANN"):
        tree.add_item(k, input_cloud[k])

    start = time.time()
    num_trees = 4
    tree.build(num_trees)
    end = time.time() - start
    print("Building %d trees took %d seconds" % (num_trees, end))
    tree.save(tree_name)
    print("Tree saved")


ann_build_save_tree(read_raw_las_data(input1), "MantecaDock/fourPallets.tree")
