"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

A utility function to convert an array of points to a VTKPointCloud object for visualization purposes

Inputs:
points - array of points

Returns:
pc - the VTKPointCloud containing the points
"""

from tqdm import tqdm
from PlotUtils.VtkPointCloud import VtkPointCloud


def create_vtkpc_from_array(points):
    pc = VtkPointCloud()
    for point in tqdm(points, total=len(points), desc="Adding to VTK PC"):
        pc.addPoint(point)
    return pc
