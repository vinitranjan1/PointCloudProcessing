from tqdm import tqdm, trange
import numpy as np
from laspy.file import File
import pdb


def save_points_as_las(points, file_name, input_header):
    with File(file_name, mode='w', header=input_header) as f:
        # pdb.set_trace()
        # points = pc.getPoints()
        # print(points)
        allx = []
        ally = []
        allz = []
        # for p in tqdm(points, total=points.GetNumberOfPoints(), desc="Saving"):
        for i in trange(len(points), desc="Saving"):
            p = points[i]
            # print(p)
            allx.append(p[0])
            ally.append(p[1])
            allz.append(p[2])
        f.x = np.array(allx)
        f.y = np.array(ally)
        f.z = np.array(allz)
