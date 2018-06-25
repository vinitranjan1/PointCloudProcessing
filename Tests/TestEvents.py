import vtk

num = 2


def p(obj, event):
    xy = iren.GetEventPosition()
    the_ren = iren.FindPokedRenderer(xy[0], xy[1])
    print(the_ren.GetBackground())
    camera = the_ren.GetActiveCamera()
    # camera.Azimuth(120.)
    # camera.SetPosition(.5, 1.0, 1.0)
    print(camera.GetOrientation())
    print("Clicked")

# pointCloud = VtkPointCloud()
cube = vtk.vtkCubeSource()
cube.SetBounds(-1, 1, -1, 1, -1, 1)
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputConnection(cube.GetOutputPort())
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)
cubeActor.GetProperty().SetOpacity(.5)


# Renderer
ren = vtk.vtkRenderer()
# pointCloud.vtkActor.SetMapper(cubeMapper)


ren.AddActor(cubeActor)
# ren.AddActor(pointCloud.vtkActor)
ren.SetBackground(.2, .3, .4)
ren.ResetCamera()

# Render Window
rw = vtk.vtkRenderWindow()
rw.AddRenderer(ren)

# Interactor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(rw)

# Begin Interaction
iren.Initialize()
iren.AddObserver("LeftButtonPressEvent", p)

rw.Render()
for i in range(num):
    ren = vtk.vtkRenderer()
    rw.AddRenderer(ren)
    # print(i/num)
    # print((i+1)/num)
    ren.SetViewport(i / num, 0, (i + 1) / num, 1)  # TODO explain what these numbers are

    ren.AddActor(cubeActor)

    ren.SetBackground(.2 + i / 100, .3 + i / 100, .4 + i / 100)
    ren.ResetCamera()

# button_rep = vtk.vtkTexturedButtonRepresentation2D()
# button = vtk.vtkButtonWidget()
# # button
# button.SetInteractor(iren)
# button.SetRepresentation(button_rep)
# upper_right = vtk.vtkCoordinate()
# upper_right.SetCoordinateSystemToNormalizedDisplay()
# upper_right.SetValue(1.0, 1.0, 1.0)
# sz = 50
#
# bds = [upper_right.GetComputedDisplayValue(ren)[0] - sz]
# bds.append(bds[0] + sz)
# bds.append(upper_right.GetComputedDisplayValue(ren)[1] - sz)
# bds.append(bds[2] + sz)
# bds.append(0)
# bds.append(0)
# print(bds)
# button.On()

iren.Start()
