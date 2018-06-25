import numpy as np


def rotate_points(points, sx, ex, sy, ez):
    output = []
    x = np.array([points[i][0] for i in range(len(points))])
    y = np.array([points[i][1] for i in range(len(points))])
    z = np.array([points[i][2] for i in range(len(points))])
    return output
