import vtk
from numpy import floor
from PlotSinglePointCloud import plot_point_cloud


def multi_plot_point_cloud(plots, name="Plot"):
    num = len(plots)
    print(type(plots[0].vtkActor))
    print("Plotting %d plots" % num)
    # plot_point_cloud(plots[0])
    # plot_point_cloud(plots[1])

    annotation_list = [None]*num
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
        annotation_list[i] = add_display_angles(ren)
        ren.ResetCamera()
    iren.Initialize()

    def edit_display_angle(obj, event):
        __edit_display_angles(iren, num, annotation_list)

    iren.AddObserver("LeftButtonPressEvent", edit_display_angle)
    iren.AddObserver("LeftButtonReleaseEvent", edit_display_angle)
    rw.Render()
    rw.SetWindowName(name)
    iren.Start()


def add_display_angles(ren):
    camera = ren.GetActiveCamera()
    corner = vtk.vtkCornerAnnotation()
    orientation = camera.GetOrientation()
    corner.SetText(0, "(x, y, z) = (%.3f, %.3f, %.3f)" % (orientation[0], orientation[1], orientation[2]))
    ren.AddActor(corner)
    return corner


def __edit_display_angles(iren, num, annotation_list):
    xy = iren.GetEventPosition()
    the_ren = iren.FindPokedRenderer(xy[0], xy[1])
    ren_index = find_index(xy[0] / iren.GetSize()[0], num)
    prev_corner = annotation_list[ren_index]
    the_ren.RemoveActor(prev_corner)
    annotation_list[ren_index] = add_display_angles(the_ren)


def find_index(dec, num):
    return int(floor(num*dec))
    # if dec < 1/num:
    #     return i
    # else:
    #     return find_index(dec - 1/num, num, i+1)
