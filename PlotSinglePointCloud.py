import vtk
import pdb


def plot_point_cloud(point_cloud):
    renderer = vtk.vtkRenderer()
    renderer.AddActor(point_cloud.vtkActor)
    renderer.SetBackground(.2, .3, .4)
    renderer.ResetCamera()

    # Render Window
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    # pdb.set_trace()

    # Interactor
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # Begin Interaction
    renderWindow.Render()
    renderWindowInteractor.Start()
