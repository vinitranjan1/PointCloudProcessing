"""
Vinit Ranjan, Chris Eckman
Lineage Logistics
6/1/18

A method for subsampling points using reservoir sampling (Algorithm R)
https://en.wikipedia.org/wiki/Reservoir_sampling

Inputs:
points - list containing values to sample from
desired_size - integer giving size of desired sample

Returns:
output - list containing sampled points
"""
from numpy import random


def subsample(points, desired_size):
    output = []
    for i in range(desired_size):
        output.append(points[i])

    for j in range(desired_size,len(points)):
        rand = random.randint(0, j)
        if rand < desired_size:
            output[rand] = points[j]
    return output
