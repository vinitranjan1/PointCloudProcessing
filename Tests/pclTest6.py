import vtk

# create a rendering window and renderer
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(400, 400)

# create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

#setup points and vertices
Points = vtk.vtkPoints()
Vertices = vtk.vtkCellArray()

for i in range(255):
  for j in range(255):
    id = Points.InsertNextPoint(i, j, 1)
    Vertices.InsertNextCell(1)
    Vertices.InsertCellPoint(id)
    #setup colors
    Colors = vtk.vtkUnsignedCharArray()
    Colors.SetNumberOfComponents(3)
    Colors.SetName("Colors")
    Colors.InsertNextTuple3(255, i, j)

polydata = vtk.vtkPolyData()
polydata.SetPoints(Points)
polydata.SetVerts(Vertices)
polydata.GetPointData().SetVectors(Colors)
polydata.Modified()
polydata.Update()

######
mapper = vtk.vtkPolyDataMapper()
mapper.SetInput(polydata)

actor = vtk.vtkActor()
actor.SetMapper(mapper)
ren.AddActor(actor)

# enable user interface interactor
renWin.Render()
iren.Initialize()
iren.Start()