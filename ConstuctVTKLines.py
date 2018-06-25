"""
Helper function that creates vtk line objects given an AxisAlignedBox3D object
"""
import vtk
from AxisAlignedBox3D import AxisAlignedBox3D


def create_vtk_lines(box):
    p = vtk.vtkPoints()
    l = vtk.vtkCellArray()
    box_points = box.get_corners()
    box_lines = box.get_edges()
    p.SetNumberOfPoints(len(box_points))
    for i in range(len(box_points)):
        p.SetPoint(i, (box_points[i][0], box_points[i][1], box_points[i][2]))
    return p, l
