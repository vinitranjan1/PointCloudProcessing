import numpy as np
from tqdm import tqdm


def rounding_filter(input_cloud, decimal_places=2, config_file=None):
    s = set()
    for point in tqdm(input_cloud, total=len(input_cloud), desc="Rounding"):
        rounded = tuple([round(p, decimal_places) for p in point])
        s.add(rounded)
    if config_file is not None:
        return np.array(list(s)), {"decimal_places": decimal_places}
    return np.array(list(s))
