import sys
from laspy.file import File
from tqdm import tqdm, trange
from CreateVTKPCFromArray import create_vtkpc_from_array
from PointCloudPlotQt import create_point_cloud_plot_qt
from SubsampleFunctions.SubsampleFracFromLAS import subsample_frac_from_las_data
import time
import numpy as np
import cvxpy as cp

sys.path.append('../')

input1 = "../MantecaRoom1/room1slice.las"
input2 = "../MantecaRoom1/room1sliceANNRadialANNGuided.las"


# def max_bin(point_set):
#     arr1 = []
#     arr2 = []
#     for k in trange(len(point_set), desc="Getting Points"):
#         p = point_set[k]
#         arr1.append(p[0])
#         arr2.append(p[2])
#     mesh = .05
#     xbins = int((max(arr1) - min(arr1)) / mesh)
#     ybins = int((max(arr2) - min(arr2)) / mesh)
#     start = time.time()
#     print("Finding histogram")
#     H, xedges, yedges = np.histogram2d(arr1, arr2, bins=(xbins, ybins))
#     end = time.time() - start
#     print("Finding histogram took %d seconds" % end)
#     # pdb.set_trace()
#     return max([max(i) for i in H])

def min_xy(point_set):
    min_dist = np.inf
    out = None
    for p in tqdm(point_set, total=len(point_set), desc="Finding min XY"):
        if xy_dist(p) < np.inf:
            out = p
    return out


def xy_dist(p):
    x = p[0]
    y = p[1]
    return np.sqrt(x ** 2 + y ** 2)


def max_bin(orig_point_set, _theta):
    point_set = orig_point_set
    arr = []
    # print(_theta.value)
    if _theta.value is None:
        angle = 0
    else:
        angle = _theta.value
    # pdb.set_trace()
    shift = np.array(min_xy(point_set))
    rot_matrix = np.matrix([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    for k in trange(len(point_set), desc="Translating"):
        p = point_set[k]
        old = np.asarray(p)
        # print(old)
        to_rotate = old - shift
        xy = [[to_rotate[0]], [to_rotate[1]]]
        # print(rot_matrix)
        # print(xy)
        mult = np.matmul(rot_matrix, xy)
        new = np.array([mult.item(0), mult.item(1), to_rotate[2]])
        # print(new)
        # sys.exit()
        point_set[k] = new
    for k in trange(len(point_set), desc="Getting Points for Histogram"):
        arr.append(point_set[k][0])  # x dimension

    mesh = .05
    bins = int((max(arr) - min(arr)) / mesh)
    start = time.time()
    print("Finding histogram")
    H, edges = np.histogram(arr, bins=bins)
    end = time.time() - start
    print("Finding histogram took %d seconds" % end)
    # del point_set
    print(max(H))
    return max(H)


with File(input1, mode='r') as f:
    input_header = f.header
    to_plot = []

    # points = subsample_frac_from_las_data(input1, .0625)
    # pc = create_vtkpc_from_array(points)
    # to_plot.append(pc)

    points2 = subsample_frac_from_las_data(input2, .0625)
    pc2 = create_vtkpc_from_array(points2)
    to_plot.append(pc2)

    theta = cp.Variable(1)
    objective = cp.Maximize(max_bin(points2, theta))
    constraints = [0 <= theta, theta <= np.pi / 2.]
    prob = cp.Problem(objective, constraints)
    result = prob.solve()

    # print(max_bin(points2, theta))
    print(theta.value)
    pc3 = create_vtkpc_from_array(points2)
    to_plot.append(pc3)
    # pdb.set_trace()

    create_point_cloud_plot_qt(to_plot, input_header=input_header, axes_on=True)
