import vtk
from PlotSinglePointCloud import plot_point_cloud


def add_save_button(plot):
    num = len(plots)
    print(type(plots[0].vtkActor))
    print("Plotting %d plots" % num)
    # plot_point_cloud(plots[0])
    # plot_point_cloud(plots[1])

    iren_list = []
    rw = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(rw)

    for i in range(num):
        ren = vtk.vtkRenderer()
        rw.AddRenderer(ren)
        # print(i/num)
        # print((i+1)/num)
        ren.SetViewport(i/num, 0, (i+1)/num, 1)  # TODO explain what these numbers are

        ren.AddActor(plots[i].vtkActor)

        ren.SetBackground(.2+i/100, .3+i/100, .4+i/100)
        ren.ResetCamera()
    iren.Initialize()
    rw.Render()
    iren.Start()
