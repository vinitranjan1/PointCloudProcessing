"""
Vinit Ranjan, Chris Eckman
Lineage Logistics
6/4/18

A method for subsampling points using reservoir sampling (Algorithm R)
https://en.wikipedia.org/wiki/Reservoir_sampling

Key distinction is that this method samples as it reads the data instead of reading all the data
and then going back and sampling

Significantly faster for the point cloud sampling because it dodges adding points unless the random integer falls in
the desired range

Inputs:
filename - path to csv/text file with data
desired_number_points - desired number of points to be sampled

Returns:
points - list containing sampled points
"""
import csv
import numpy as np


def subsample_from_data(filename, desired_number_points=10000):
    points = []
    with open(filename) as f:
        reader = csv.reader(f, delimiter="\t")
        i = 0
        for raw in list(reader):
            if i < desired_number_points:
                fix = raw[0].split()
                points.append(np.asarray([float(fix[0]), float(fix[1]), float(fix[2])]))
            else:
                rand = np.random.randint(0, i)
                if rand < desired_number_points:
                    fix = raw[0].split()
                    points[rand] = np.asarray([float(fix[0]), float(fix[1]), float(fix[2])])
            i += 1
    return points
