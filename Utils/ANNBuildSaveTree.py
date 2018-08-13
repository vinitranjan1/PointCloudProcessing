from Utils.ReadRawLAS import read_raw_las_data
import time
from tqdm import trange
from annoy import AnnoyIndex



input1 = "MantecaDock/fourPallets.las"
input1 = "MantecaRoom1/room1ANNGuidedN40Epsp07.las"


def ann_build_save_tree(input_cloud, tree_name, dim=3):
    num = len(input_cloud)
    tree = AnnoyIndex(dim, metric='euclidean')
    for k in trange(num, desc="Preparing for ANN"):
        tree.add_item(k, input_cloud[k])

    start = time.time()
    num_trees = 2
    tree.build(num_trees)
    end = time.time() - start
    print("Building %d trees took %d seconds" % (num_trees, end))
    tree.save(tree_name)
    print("Tree saved")


ann_build_save_tree(read_raw_las_data(input1), "MantecaRoom1/room1AGtree.tree")
