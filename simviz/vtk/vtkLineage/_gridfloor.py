import vtk
import numpy as np

class vtkGridFloorActor(vtk.vtkActor):

    """
    vtkGridFloorActor

    Extend the vtk.vtkActor class to build a set of lines that represent a ground. The lines fade around the periphery.
    """

    def __init__(self, renderer, **kargs):
        super().__init__()
        self.__addGrid2(renderer, **kargs)

    def __addGrid(self, renderer, x, y, size, grid_size):
        x_offset = x
        y_offset = y

        x_min = x - size[0] * 0.5
        x_max = x + size[0] * 0.5
        x_step = grid_size
        y_min = y - size[1] * 0.5
        y_max = y + size[1] * 0.5
        y_step = grid_size

        xCoords = vtk.vtkFloatArray()
        yCoords = vtk.vtkFloatArray()
        for i in np.arange(x_min+x_offset, x_max+x_offset, x_step): xCoords.InsertNextValue(i)
        for i in np.arange(y_min+y_offset, y_max+y_offset, y_step): yCoords.InsertNextValue(i)

        # The coordinates are assigned to the rectilinear grid. Make sure that
        # the number of values in each of the XCoordinates, YCoordinates,
        # and ZCoordinates is equal to what is defined in SetDimensions().
        rgrid = vtk.vtkRectilinearGrid()
        rgrid.SetDimensions(xCoords.GetNumberOfTuples(), yCoords.GetNumberOfTuples(), 1)
        rgrid.SetXCoordinates(xCoords)
        rgrid.SetYCoordinates(yCoords)

        # Extract a plane from the grid to see what we've got.
        plane = vtk.vtkRectilinearGridGeometryFilter()
        plane.SetInputData(rgrid)
        plane.SetExtent(0, xCoords.GetNumberOfTuples(), 0, yCoords.GetNumberOfTuples(), 0, 1)

        gridMapper = vtk.vtkPolyDataMapper()
        gridMapper.SetInputConnection(plane.GetOutputPort())

        self.SetMapper(gridMapper)
        self.GetProperty().SetRepresentationToWireframe()
        self.GetProperty().SetColor(0, 0, 0)
        self.GetProperty().SetOpacity(0.025)

        renderer.AddActor(self)

    def __addGrid2(self, renderer, x=0, y=0, size=10, grid_size=1, feather=0, color_axes=False):
        x_offset = x
        y_offset = y

        try: x_size = size[0]
        except: x_size = size
        try: y_size = size[1]
        except: y_size = size

        x_min = x_offset - x_size * 0.5
        x_max = x_offset + x_size * 0.5
        try: x_step = grid_size[0]
        except: x_step = grid_size
        try: x_feather = feather[0]
        except: x_feather = feather
        x_feather = min(x_feather, x_size * 0.5)
        y_min = y_offset - y_size * 0.5
        y_max = y_offset + y_size * 0.5
        try: y_step = grid_size[1]
        except: y_step = grid_size
        try: y_feather = feather[1]
        except: y_feather = feather
        y_feather = min(y_feather, y_size * 0.5)

        self.__points = vtk.vtkPoints()
        self.__line_color = vtk.vtkUnsignedCharArray()
        self.__line_color.SetNumberOfComponents(4)
        self.__line_indices = vtk.vtkCellArray()
        for x_dir in [-1, 1]:
            for x in np.arange(x_offset + x_step * x_dir, x_offset + x_size * 0.5 * x_dir, x_step * x_dir):
                self.__points.InsertNextPoint(x, y_min, 0) # beginning point
                self.__points.InsertNextPoint(x, y_min + y_feather, 0) # beginning feather end point
                self.__points.InsertNextPoint(x, y_max - y_feather, 0) # end feather start point
                self.__points.InsertNextPoint(x, y_max, 0) # end point
                self.__line_indices.InsertNextCell(4)
                self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-4)
                self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-3)
                self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-2)
                self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-1)
                self.__line_color.InsertNextTuple([0, 0, 0, 0])
                self.__line_color.InsertNextTuple([0, 0, 0, min(min(abs(x-x_min), abs(x-x_max))/x_feather,1)*255*0.25])
                self.__line_color.InsertNextTuple([0, 0, 0, min(min(abs(x-x_min), abs(x-x_max))/x_feather,1)*255*0.25])
                self.__line_color.InsertNextTuple([0, 0, 0, 0])

        for y_dir in [-1, 1]:
            for y in np.arange(y_offset + y_step * y_dir, y_offset + y_size * 0.5 * y_dir, y_step * y_dir):
                self.__points.InsertNextPoint(x_min, y, 0)
                self.__points.InsertNextPoint(x_min + x_feather, y, 0)
                self.__points.InsertNextPoint(x_max - x_feather, y, 0)
                self.__points.InsertNextPoint(x_max, y, 0)
                self.__line_indices.InsertNextCell(4)
                self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-4)
                self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-3)
                self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-2)
                self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-1)
                self.__line_color.InsertNextTuple([0, 0, 0, 0])
                self.__line_color.InsertNextTuple([0, 0, 0, min(min(abs(y-y_min), abs(y-y_max))/y_feather,1)*255*0.25])
                self.__line_color.InsertNextTuple([0, 0, 0, min(min(abs(y-y_min), abs(y-y_max))/y_feather,1)*255*0.25])
                self.__line_color.InsertNextTuple([0, 0, 0, 0])

        # Add x axes line
        self.__points.InsertNextPoint(x_offset, y_min, 0) # beginning point
        self.__points.InsertNextPoint(x_offset, y_min + y_feather, 0) # beginning feather end point
        self.__points.InsertNextPoint(x_offset, y_max - y_feather, 0) # end feather start point
        self.__points.InsertNextPoint(x_offset, y_max, 0) # end point
        self.__line_indices.InsertNextCell(4)
        self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-4)
        self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-3)
        self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-2)
        self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-1)

        if color_axes:
            self.__line_color.InsertNextTuple([0, 255, 0, 0])
            self.__line_color.InsertNextTuple([0, 255, 0, min(min(abs(x_offset-x_min), abs(x_offset-x_max))/x_feather,1)*255])
            self.__line_color.InsertNextTuple([0, 255, 0, min(min(abs(x_offset-x_min), abs(x_offset-x_max))/x_feather,1)*255])
            self.__line_color.InsertNextTuple([0, 255, 0, 0])
        else:
            self.__line_color.InsertNextTuple([0, 0, 0, 0])
            self.__line_color.InsertNextTuple([0, 0, 0, min(min(abs(x_offset-x_min), abs(x_offset-x_max))/x_feather,1)*255*0.25])
            self.__line_color.InsertNextTuple([0, 0, 0, min(min(abs(x_offset-x_min), abs(x_offset-x_max))/x_feather,1)*255*0.25])
            self.__line_color.InsertNextTuple([0, 0, 0, 0])

        # add y axes
        self.__points.InsertNextPoint(x_min, y_offset, 0)
        self.__points.InsertNextPoint(x_min + x_feather, y_offset, 0)
        self.__points.InsertNextPoint(x_max - x_feather, y_offset, 0)
        self.__points.InsertNextPoint(x_max, y_offset, 0)
        self.__line_indices.InsertNextCell(4)
        self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-4)
        self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-3)
        self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-2)
        self.__line_indices.InsertCellPoint(self.__points.GetNumberOfPoints()-1)

        if color_axes:
            self.__line_color.InsertNextTuple([255, 0, 0, 0])
            self.__line_color.InsertNextTuple([255, 0, 0, min(min(abs(y_offset-y_min), abs(y_offset-y_max))/y_feather,1)*255*0.75])
            self.__line_color.InsertNextTuple([255, 0, 0, min(min(abs(y_offset-y_min), abs(y_offset-y_max))/y_feather,1)*255*0.75])
            self.__line_color.InsertNextTuple([255, 0, 0, 0])
        else:
            self.__line_color.InsertNextTuple([0, 0, 0, 0])
            self.__line_color.InsertNextTuple([0, 0, 0, min(min(abs(y_offset-y_min), abs(y_offset-y_max))/y_feather,1)*255*0.25])
            self.__line_color.InsertNextTuple([0, 0, 0, min(min(abs(y_offset-y_min), abs(y_offset-y_max))/y_feather,1)*255*0.25])
            self.__line_color.InsertNextTuple([0, 0, 0, 0])

        self.__polydata = vtk.vtkPolyData()
        self.__polydata.SetPoints(self.__points)
        self.__polydata.SetLines(self.__line_indices)
        self.__polydata.GetPointData().SetScalars(self.__line_color)

        self.__mapper = vtk.vtkPolyDataMapper()
        self.__mapper.SetInputData(self.__polydata)

        self.SetMapper(self.__mapper)
        self.GetProperty().SetOpacity(0.5);
        renderer.AddActor(self)
