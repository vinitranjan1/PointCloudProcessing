import vtk, numpy as np
from ._settings import *
from ._helpers import vtkLineageSystem

class BayDoorActor(vtk.vtkActor, vtkLineageSystem):

    """
    BayDoorActor

    Extends vtk.vtkActor to build a 3D representation of a bay door from minimal information
    """

    def __init__(self, **kargs):
        super().__init__()
        self.initialized = False
        if kargs: self.build_geometry_door_border(**kargs)

        self.initialized = True


    def build_geometry_rectangle_primative(self, location=None, facing_vector=np.array([0, -1, 0])):
        """
        Builds the geometry as a rectangle primative
        """

        if not location: return -1
        location = np.array(location + [0]*(3-len(location)))

        # level parent cart
        self.__source = vtk.vtkCubeSource()
        self.__source.SetBounds(
            -1 * PALLET_SLOT.x, 1 * PALLET_SLOT.x,
            -0.05 * PALLET_SLOT.y, 0.05 * PALLET_SLOT.y,
            0, 2 * PALLET_SLOT.z)
        self.__mapper = vtk.vtkPolyDataMapper()
        self.__mapper.SetInputConnection(self.__source.GetOutputPort())
        self.SetMapper(self.__mapper)
        self.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d('white'))


        return 1

    def build_geometry_door_border(self, location=None, facing_vector=np.array([0, -1, 0]), width=2*PALLET_SLOT.x, height=1.5*PALLET_SLOT.z, thickness=0.15*PALLET_SLOT.y):
        """
        Builds the border of the bay door as an extruded trim
        """

        if not location: return -1
        location = np.array(location + [0]*(3-len(location)))

        v_up = np.array([0, 0, 1])
        v_left = np.cross(facing_vector, v_up)
        v_left = v_left / np.linalg.norm(v_left)

        __points = vtk.vtkPoints()
        __lines = vtk.vtkCellArray()

        __lines.InsertNextCell(4)
        __points.InsertNextPoint(+v_left * width * 0.5)
        __lines.InsertCellPoint(__points.GetNumberOfPoints()-1)
        __points.InsertNextPoint(+v_left * width * 0.5 + v_up * height)
        __lines.InsertCellPoint(__points.GetNumberOfPoints()-1)
        __points.InsertNextPoint(-v_left * width * 0.5 + v_up * height)
        __lines.InsertCellPoint(__points.GetNumberOfPoints()-1)
        __points.InsertNextPoint(-v_left * width * 0.5 + v_up)
        __lines.InsertCellPoint(__points.GetNumberOfPoints()-1)

        __polydata = vtk.vtkPolyData()
        __polydata.SetPoints(__points)
        __polydata.SetLines(__lines)

        __ribbon_filter = vtk.vtkRibbonFilter()
        __ribbon_filter.VaryWidthOn()
        __ribbon_filter.SetDefaultNormal(facing_vector)
        __ribbon_filter.UseDefaultNormalOn()
        __ribbon_filter.SetInputData(__polydata)
        __ribbon_filter.SetWidth(thickness)

        __extrusion_filter = vtk.vtkLinearExtrusionFilter()
        __extrusion_filter.SetExtrusionTypeToVectorExtrusion()
        __extrusion_filter.CappingOn()
        __extrusion_filter.SetVector(facing_vector * thickness * 2)
        __extrusion_filter.SetInputConnection(__ribbon_filter.GetOutputPort())

        __mapper = vtk.vtkPolyDataMapper()
        __mapper.SetInputConnection(__extrusion_filter.GetOutputPort())

        self.SetMapper(__mapper)
        self.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d('white'));
        self.SetPosition(location - facing_vector * thickness)

        return 1
