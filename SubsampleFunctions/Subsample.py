"""
Vinit Ranjan, Chris Eckman
Lineage Logistics
6/1/18

A method for subsampling points using reservoir sampling (Algorithm R)
https://en.wikipedia.org/wiki/Reservoir_sampling

The algorithm is nice in that you are guaranteed to get desired_size number of points and each point is accepted with
    probability desired_size/len(points)

Inputs:
points - list containing values to sample from
desired_size - integer giving size of desired sample

Returns:
output - list containing sampled points
"""
from numpy import random


def subsample(points, desired_size):
    if len(points) <= desired_size:
        return points
    output = []
    for i in range(desired_size):
        output.append(points[i])

    for j in range(desired_size, len(points)):
        rand = random.randint(0, j)
        if rand < desired_size:
            output[rand] = points[j]
    return output
