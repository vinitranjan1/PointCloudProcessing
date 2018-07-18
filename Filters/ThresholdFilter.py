import numpy as np
from tqdm import tqdm, trange
import pdb


def threshold_filter(input_cloud, dim_to_collapse="Z", mesh=0.05, threshold=.25):
    output_cloud = []
    hist, xedges, yedges = __collapse_one_dim(input_cloud, dim_to_collapse, mesh)
    max_value = max([max(i) for i in hist])
    cutoff = int(threshold * max_value)
    # hist = np.array([[1, .5], [.25, .1]])
    # xedges = np.array([0, 1, 2])
    # yedges = np.array([3, 4, 5])
    # # print(cutoff)
    # cutoff = .2
    # mask = [[0] * (len(yedges) - 1)] * (len(xedges) - 1)
    mask = (hist >= cutoff)
    # print(mask)
    # exit(1)

    # for i in range(len(xedges) - 1):
    #     for j in range(len(yedges) - 1):
    #         if hist[i][j] >= cutoff:
    #             mask[i][j] = 1

    # bins_to_keep = []
    # for i in range(len(xedges)-1):
    #     for j in range(len(yedges)-1):
    #         if hist[i][j] >= cutoff:
    #             bins_to_keep.append([(xedges[i], xedges[i+1]), (yedges[j], yedges[j+1])])
    # new_mask = np.array([[False] * len(mask[0])] * len(mask))
    # for b in bins_to_keep:
    #     # print(b[0][0])
    #     # print(np.argwhere(xedges == b[0][0])[0][0])
    #     i = np.argwhere(xedges == b[0][0])[0][0]
    #     j = np.argwhere(yedges == b[1][0])[0][0]
    #     assert mask[i][j]
    #     new_mask[i][j] = True
    # assert np.all(mask == new_mask)
    # for p in tqdm(input_cloud, total=len(input_cloud), desc="Filtering"):
    #     for b in bins_to_keep:
    #         if point_in_bin(p, b):
    #             output_cloud.append(p)
    #             break

    # print(len(bins_to_keep))
    # count = 0
    # for i in mask:
    #     print(i)
    #     for j in i:
    #         if j:
    #             count += 1
    # print(count)

    for p in tqdm(input_cloud, total=len(input_cloud), desc="Filtering"):
        try:
            x_coord = binary_search(xedges, 0, len(xedges) - 1, p[0])
            y_coord = binary_search(yedges, 0, len(yedges) - 1, p[1])
            # while not xedges[x_coord] <= p[0] <= xedges[x_coord + 1]:
            #     if xedges[x_coord] > p[0]:
            #         x_coord -= 1
            #     else:
            #         x_coord += 1
            # while not yedges[y_coord] <= p[1] <= yedges[y_coord + 1]:
            #     if yedges[y_coord] > p[1]:
            #         y_coord -= 1
            #     else:
            #         y_coord += 1
            # assert p[0] >= xedges[x_coord]
            # assert p[0] < xedges[x_coord+1]
            # i = np.argwhere(xedges == p[0])[0][0]
            # j = np.argwhere(yedges == p[1])[0][0]

            # x_coord = search(xedges, p[0])
            # y_coord = search(yedges, p[1])

            if mask[x_coord][y_coord]:
                output_cloud.append(p)
        except (IndexError, AssertionError) as e:
            raise e
    return output_cloud


def point_in_bin(point, target_bin):
    return target_bin[0][0] <= point[0] <= target_bin[0][1] and target_bin[1][0] <= point[1] <= target_bin[1][1]


def __collapse_one_dim(points, to_collapse, mesh):
    label_to_dim = {"X": 0, "Y": 1, "Z": 2}
    dim_to_label = {0: "X", 1: "Y", 2: "Z"}
    collapse_dim = label_to_dim[to_collapse]
    dims = [0, 1, 2]
    dims.remove(collapse_dim)
    arr1 = []
    arr2 = []
    for k in trange(len(points), desc="Getting Points"):
        p = points[k]
        arr1.append(p[dims[0]])
        arr2.append(p[dims[1]])
    # heatmap, xedges, yedges = np.histogram2d(arr1, arr2, bins=(100, 100))
    # extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

    # print(min(arr1), max(arr1), min(arr2), max(arr2))
    # print(float(mesh[0]))
    xbins = int((max(arr1) - min(arr1)) / float(mesh))
    ybins = int((max(arr2) - min(arr2)) / float(mesh))
    return np.histogram2d(arr1, arr2, bins=(xbins, ybins))


def binary_search(arr, left, right, x):
    while left <= right:
        mid = left + int((right - left) / 2)
        if arr[mid] < x:
            left = mid + 1
        else:
            right = mid - 1
    return left-1


def search(arr, val):
    for i in range(len(arr)-1):
        if arr[i] <= val <= arr[i+1]:
            return i
