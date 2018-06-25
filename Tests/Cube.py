# import vtk python module
import vtk

# create polygonal cube geometry
#   here a procedural source object is used,
#   a source can also be, e.g., a file reader
cube = vtk.vtkCubeSource()
cube.SetBounds(-1, 1, -1, 1, -1, 1)
print(cube.GetZLength())

# map to graphics library
#   a mapper is the interface between the visualization pipeline
#   and the graphics model
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(cube.GetOutputPort())  # connect source and mapper

# an actor represent what we see in the scene,
# it coordinates the geometry, its properties, and its transformation
aCube = vtk.vtkActor()
aCube.SetMapper(mapper)
aCube.GetProperty().SetColor(0, 1, 0)  # cube color green

# a renderer and render window
ren1 = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren1)

# an interactor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# add the actor to the scene
ren1.AddActor(aCube);
ren1.SetBackground(1, 1, 1)  # Background color white

# render an image (lights and cameras are created automatically)
renWin.Render()

# begin mouse interaction
iren.Start()
