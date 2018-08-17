"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

A filter that rounds off points to the desired number of decimal places and removes any overlapping points

Inputs:
input_list - list of points to round
decimal_places - number of decimal places to round to
config_file - if a flag is put in here, the function will return the result as well as a dictionary of parameters used
    for logging purposes, check NoVisuals/NoVisualMultiRooms.py for usage

Returns:
list of rounded points
"""
import numpy as np
from tqdm import tqdm


def rounding_filter(input_list, decimal_places=2, config_file=None):
    s = set()  # sets only use unique elements
    for point in tqdm(input_list, total=len(input_list), desc="Rounding"):
        rounded = tuple([round(p, decimal_places) for p in point])  # can only hash immutable objects in the set
        s.add(rounded)
    if config_file is not None:
        return np.array(list(s)), {"decimal_places": decimal_places}
    return np.array(list(s))
