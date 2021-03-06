"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

A function to subsample from a list of points and accept each point with probability sample_frac

Inputs:
points - list of points to sample from
sample_frac - fraction of desired points

Returns:
out - list of sampled points
"""
import numpy as np
import pdb
from tqdm import tqdm, trange


def subsample_frac(points, sample_frac=.1):
    out = []

    for point in tqdm(points, total=len(points), desc="Sampling"):
        # for i in trange(len(in_file.x), desc="Sampling"):
        if np.random.random_sample() < sample_frac:
            out.append(point)
    return out


# helper function to scale points
def scale(point, scale_factor, offset):
    return (point * scale_factor) + offset
