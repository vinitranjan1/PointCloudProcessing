import vtk
import numpy as np
from VtkPointCloud import VtkPointCloud


class PointCloudPlot:
    def __init__(self, points=VtkPointCloud(), iren=vtk.vtkRenderWindowInteractor(), rw=vtk.vtkRenderWindow()):
        self.points = points
        self.iren = iren
        self.rw = rw
        self.background = (.2, .3, .4)
        self.bottom_left_corner = None

    def plot_point_cloud(self, point_cloud):
        ren = vtk.vtkRenderer()
        ren.AddActor(point_cloud.vtkActor)
        ren.SetBackground(self.background)
        ren.ResetCamera()

        # Render Window
        self.rw.AddRenderer(ren)

        # Interactor
        self.iren.SetRenderWindow(self.rw)

        PointCloudPlot.add_display_angles(ren)

        def edit_display_angle(obj, event):
            PointCloudPlot.__edit_display_angles(self.iren)

        self.iren.AddObserver("LeftButtonPressEvent", edit_display_angle)
        self.iren.AddObserver("LeftButtonReleaseEvent", edit_display_angle)

        # Begin Interaction
        self.rw.Render()

    def add_display_angles(self, ren):
        camera = ren.GetActiveCamera()
        corner = vtk.vtkCornerAnnotation()
        orientation = camera.GetOrientation()
        corner.SetText(0, "(x, y, z) = (%.3f, %.3f, %.3f)" % (orientation[0], orientation[1], orientation[2]))
        ren.AddActor(corner)
        self.bottom_left_corner = corner

    def __edit_display_angles(self, iren):
        xy = iren.GetEventPosition()
        the_ren = iren.FindPokedRenderer(xy[0], xy[1])
        the_ren.RemoveActor(self.bottom_left_corner)
        PointCloudPlot.add_display_angles(the_ren)
