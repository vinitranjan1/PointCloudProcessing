from tqdm import tqdm
from PlotUtils.VtkPointCloud import VtkPointCloud


def create_vtkpc_from_array(points):
    pc = VtkPointCloud()
    for point in tqdm(points, total=len(points), desc="Adding to VTK PC"):
        pc.addPoint(point)
    return pc
