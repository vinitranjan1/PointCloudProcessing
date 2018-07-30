import vtk
from tqdm import tqdm, trange
from numpy import random
import random


class VtkPointCloud:

    def __init__(self, zMin=-1, zMax=13, maxNumPoints=1e10):
        self.maxNumPoints = maxNumPoints
        self.vtkPolyData = vtk.vtkPolyData()
        self.clearPoints()
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.vtkPolyData)
        self.mapper.SetColorModeToDefault()
        self.mapper.SetScalarRange(zMin, zMax)
        self.mapper.SetScalarVisibility(1)

        self.frustumMapper = vtk.vtkPolyDataMapper()

        # For bounding box outline
        self.vtkActor = vtk.vtkActor()
        self.vtkActor.SetMapper(self.mapper)
        self.outline = vtk.vtkOutlineFilter()
        self.outline.SetInputData(self.vtkPolyData)
        # self.outline.SetInputConnection(self.vtkPolyData.GetOutputPort())
        self.mapOutline = vtk.vtkPolyDataMapper()
        self.mapOutline.SetInputConnection(self.outline.GetOutputPort())
        self.outlineActor = vtk.vtkActor()
        self.outlineActor.SetMapper(self.mapOutline)
        self.outlineActor.GetProperty().SetColor(0, 0, 0)

    def addPoint(self, point):
        # if self.vtkPoints.GetNumberOfPoints() < self.maxNumPoints:
        pointId = self.vtkPoints.InsertNextPoint(point[:])
        self.vtkDepth.InsertNextValue(point[2])
        self.vtkCells.InsertNextCell(1)
        self.vtkCells.InsertCellPoint(pointId)
        # else:
        #     r = random.randint(0, self.maxNumPoints)
        #     self.vtkPoints.SetPoint(r, point[:])
        self.vtkCells.Modified()
        self.vtkPoints.Modified()
        self.vtkDepth.Modified()

    def getPoints(self):
        return self.vtkPoints

    def getPointsAsArray(self):
        output = []
        points = self.vtkPoints
        for k in trange(points.GetNumberOfPoints(), desc="Getting Points As Array"):
            output.append(points.GetPoint(k) + tuple())  # makes a copy
        return output

    def clearPoints(self):
        self.vtkPoints = vtk.vtkPoints()
        self.vtkCells = vtk.vtkCellArray()
        self.vtkDepth = vtk.vtkDoubleArray()
        self.vtkDepth.SetName('DepthArray')
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkDepth)
        self.vtkPolyData.GetPointData().SetActiveScalars('DepthArray')
