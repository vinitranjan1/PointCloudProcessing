import vtk, numpy as np
from ._settings import *
from ._helpers import vtkLineageSystem
import pdb

class WallActor(vtk.vtkPropAssembly, vtkLineageSystem):

    """
    WallActor

    Extends the vtk.vtkPropAssembly class to build a set of walls from a set of paths
    """

    def __init__(self, **kargs):
        super().__init__()
        self.initialized = False
        if kargs: self.build_geometry(**kargs)

        self.initialized = True


    def build_geometry(self, path_count=0, path_vertices_counts=[], path_vertices=[], height=1, opacity=1, color=[1,1,1], **kargs):
        v_idx = 0

        for i in range(int(path_count)):
            __points = vtk.vtkPoints()
            __lines = vtk.vtkCellArray()
            __lines.InsertNextCell(int(path_vertices_counts[i]))

            for v in range(int(path_vertices_counts[i])):
                __points.InsertNextPoint([float(i) for i in path_vertices[v_idx*3:v_idx*3+3]])
                __lines.InsertCellPoint(__points.GetNumberOfPoints()-1)

                v_idx += 1

            __polydata = vtk.vtkPolyData()
            __polydata.SetPoints(__points)
            __polydata.SetLines(__lines)

            __ribbon_filter = vtk.vtkRibbonFilter()
            __ribbon_filter.SetDefaultNormal(0, 0, 1)
            __ribbon_filter.UseDefaultNormalOn()
            __ribbon_filter.SetInputData(__polydata)
            __ribbon_filter.SetWidth(5)

            __extrusion_filter = vtk.vtkLinearExtrusionFilter()
            __extrusion_filter.SetExtrusionTypeToVectorExtrusion()
            __extrusion_filter.CappingOn()
            __extrusion_filter.SetVector(0, 0, float(height))
            __extrusion_filter.SetInputConnection(__ribbon_filter.GetOutputPort())

            __mapper = vtk.vtkPolyDataMapper()
            __mapper.SetInputConnection(__extrusion_filter.GetOutputPort())

            __actor = vtk.vtkActor()
            __actor.SetMapper(__mapper)

            __actor.GetProperty().SetColor([float(i) for i in color]);
            __actor.GetProperty().SetOpacity(float(opacity));

            self.AddPart(__actor)

        return 1
