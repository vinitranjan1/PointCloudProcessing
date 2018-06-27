import numpy as np
from tqdm import tqdm


def rounding_filter(input_cloud, decimal_places=2):
    s = set()
    for point in tqdm(input_cloud, total=len(input_cloud), desc="Rounding"):
        rounded = tuple([round(p, decimal_places) for p in point])
        s.add(rounded)
    return np.array(list(s))
