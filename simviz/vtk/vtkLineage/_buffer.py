from ._settings import AISLE

import vtk, numpy as np
from ._helpers import vtkLineageSystem
# import pdb

class BufferActor(vtk.vtkPropAssembly, vtkLineageSystem):

    """
    BufferActor

    Extends vtk.vtkActor to build a 3D representation of buffer from minimal information
    """

    def __init__(self, **kargs):
        super().__init__()
        self.initialized = False
        if kargs: self.build_geometry_ribbon(**kargs)
        if 'arrow' in kargs and kargs['arrow']: self.build_geometry_arrow(**kargs)
        if 'name' in kargs and kargs['name']: self.build_geometry_name(**kargs)

        self.initialized = True


    def build_geometry_tube(self, start=None, end=None, **kargs):
        """
        Builds the geometry to represent the buffer as a tube along its length
        """
        # pdb.set_trace()
        if not start or not end or start == end: return -1

        self.__points = vtk.vtkLineSource()
        self.__points.SetPoint1([float(i) for i in start])
        self.__points.SetPoint2([float(i) for i in end])

        self.__tubefilter = vtk.vtkTubeFilter()
        self.__tubefilter.SetInputConnection(self.__points.GetOutputPort())
        self.__tubefilter.SetRadius(6.0)
        self.__tubefilter.SetNumberOfSides(6)
        self.__tubefilter.CappingOn()

        self.__mapper = vtk.vtkPolyDataMapper()
        self.__mapper.SetInputConnection(self.__tubefilter.GetOutputPort())

        self.__actor = vtk.vtkActor()
        self.__actor.SetMapper(self.__mapper)

        self.AddPart(self.__actor)

        return 1


    def build_geometry_ribbon(self, start=None, end=None, width=AISLE.length*0.5, **kargs):
        # pdb.set_trace()
        """
        Builds the geometry to represent the buffer as a ribbon along its length, extending half its width past either end
        """
        if not start or not end or start == end: return -1

        se = vtk.vtkVector3d([float(f)-float(i) for f,i in zip(start, end)])
        se.Normalize()
        se.Set(*[i*width for i in se])

        self.__points = vtk.vtkPoints()
        self.__points.InsertNextPoint([float(i)+j for i,j in zip(start, se)])
        self.__points.InsertNextPoint([float(i)-j for i,j in zip(end, se)])

        self.__lines = vtk.vtkCellArray()
        self.__lines.InsertNextCell(2)
        self.__lines.InsertCellPoint(0)
        self.__lines.InsertCellPoint(1)

        self.__polydata = vtk.vtkPolyData()
        self.__polydata.SetPoints(self.__points)
        self.__polydata.SetLines(self.__lines)

        self.__ribbon_filter = vtk.vtkRibbonFilter()
        self.__ribbon_filter.SetDefaultNormal(0, 0, 1)
        self.__ribbon_filter.UseDefaultNormalOn()
        self.__ribbon_filter.SetInputData(self.__polydata)
        self.__ribbon_filter.SetWidth(width)

        self.__mapper = vtk.vtkPolyDataMapper()
        self.__mapper.SetInputConnection(self.__ribbon_filter.GetOutputPort())

        self.__actor = vtk.vtkActor()
        self.__actor.SetMapper(self.__mapper)

        self.__actor.GetProperty().SetDiffuseColor(1, 1, 1)
        self.__actor.GetProperty().SetDiffuse(0.3)
        self.__actor.GetProperty().SetAmbientColor(0.7, 0.7, 0.7)
        self.__actor.GetProperty().SetAmbient(0.7)
        self.__actor.GetProperty().SetSpecularColor(0.5, 0.5, 0.5)
        self.__actor.GetProperty().SetSpecular(0)
        self.__actor.GetProperty().SetSpecularPower(0)

        self.AddPart(self.__actor)

        return 1

    def build_geometry_arrow(self, start=None, end=None, **kargs):
        # pdb.set_trace()
        """
        Builds geometry to represent directionality of buffer as an arrow above the buffer's center
        """
        if not start or not end or start == end: return -1

        # directional vector along buffer
        v = np.array([float(i) for i in end]) - np.array([float(i) for i in start])
        v = v / np.linalg.norm(v)

        self.__arrow_source = vtk.vtkArrowSource()
        self.__arrow_source.SetShaftRadius(0.025)
        self.__arrow_source.SetTipLength(0.25)

        self.__arrow_mapper = vtk.vtkPolyDataMapper()
        self.__arrow_mapper.SetInputConnection(self.__arrow_source.GetOutputPort())
        self.__arrow_actor = vtk.vtkActor()
        self.__arrow_actor.SetMapper(self.__arrow_mapper)

        self.__arrow_actor.SetScale(100)
        self.__arrow_actor.GetProperty().SetColor([1.0, 0.5, 0.5]);
        self.__arrow_actor.RotateWXYZ(np.arccos(np.dot(v, np.array([1, 0, 0]))) * 180.0 / np.pi,
                                      # cross product if the two vectors are not colinear
                                      *(np.cross(np.array([1, 0, 0]), v) if abs(np.dot(v, np.array([1, 0, 0]))) != 1 else \
                                      # otherwise, perpendicular vector to v (numerically stablized based on component comparison)
                                       (np.array([v[1], -v[0], 0]) if abs(v[2])<abs(v[0]) else np.array([0, -v[2], v[1]]))))
        self.__arrow_actor.SetPosition(np.array([float(i) for i in end]) * 0.5 +
                                       np.array([float(i) for i in start]) * 0.5 +
                                       np.array([0, 0, 25]) -
                                       np.array(self.__arrow_actor.GetCenter()))


        self.AddPart(self.__arrow_actor)

        return 1

    def build_geometry_name(self, start=None, end=None, name=None, **kargs):
        # pdb.set_trace()
        """
        Builds a small text actor above the buffer to show its object name
        """
        if not start or not end or not name or start == end: return -1

        self.__name_actor = vtk.vtkTextActor3D()
        self.__name_actor.SetInput(str(name))
        _b = self.__name_actor.GetBounds()

        self.__name_actor.GetTextProperty().SetColor([0.2, 0.2, 0.2]);
        self.__name_actor.SetPosition(np.array([float(i) for i in end]) * 0.5 +
                                       np.array([float(i) for i in start]) * 0.5 +
                                       np.array([0, 0, 10]) -
                                       np.array([(min+max)*0.5 for min, max in zip(_b[::2], _b[1::2])]))

        self.AddPart(self.__name_actor)

        return 1
