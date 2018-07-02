import numpy as np
import pdb
from scipy.spatial import kdtree
from ReadRawLAS import read_raw_las_data
import time
from tqdm import tqdm, trange
from annoy import AnnoyIndex



input1 = "MantecaDock/fourPallets.las"
input1 = "MantecaRoom1/room1ANNGuidedN40Epsp07.las"


def ann_build_save_tree(input_cloud, tree_name, dim=3):
    num = len(input_cloud)
    tree = AnnoyIndex(dim, metric='euclidean')
    for k in trange(num, desc="Preparing for ANN"):
        tree.add_item(k, input_cloud[k])

    start = time.time()
<<<<<<< Updated upstream
    num_trees = 4
=======
    num_trees = 2
>>>>>>> Stashed changes
    tree.build(num_trees)
    end = time.time() - start
    print("Building %d trees took %d seconds" % (num_trees, end))
    tree.save(tree_name)
    print("Tree saved")


<<<<<<< Updated upstream
ann_build_save_tree(read_raw_las_data(input1), "MantecaDock/fourPallets.tree")
=======
ann_build_save_tree(read_raw_las_data(input1), "MantecaRoom1/room1AGtree.tree")
>>>>>>> Stashed changes
