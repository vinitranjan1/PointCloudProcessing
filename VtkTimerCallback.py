import vtk
import time
from tqdm import tqdm, trange
import numpy as np


class VtkTimerCallback:
    def __init__(self, renderwindow, renderer, iterations):
        self.event_number = 0
        self.renderer = renderer
        self.renderwindow = renderwindow
        self.iterations = iterations
        self.position = np.array([0., 0., 0.])
        self.actor = None
        self.timer_id = None
        self.sphere_radius = .575
        self.leading_sphere_color = [1.0, 0.0, 0.0]
        self.non_leading_sphere_color = [1.0, 1.0, 1.0]
        self.shift1 = np.array([5.137, 3.0, 0])
        self.shift2 = np.array([-.25, .27, 0])
        self.set_z = 2.5
        self.sphere_actors = []

        self.renderwindow.Render()
        self.renderwindow.GetInteractor().Initialize()

    def execute(self, obj, event, event_list, tracking=False):
        iren = obj
        if self.iterations == 0:
            self.event_number = 0
            iren.DestroyTimer(self.timer_id)
            for sphere in self.sphere_actors:
                self.renderer.RemoveActor(sphere)
            self.sphere_actors = []
            return

        try:
            new_pos = np.array([float(i) for i in event_list[self.event_number][1:4]])
            new_pos = self.transform(new_pos)
            sphere_source = vtk.vtkSphereSource()
            sphere_source.SetCenter(new_pos)
            sphere_source.SetRadius(self.sphere_radius)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere_source.GetOutputPort())
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(self.leading_sphere_color)
            try:
                if not tracking:
                    self.renderer.RemoveActor(self.sphere_actors[-2])
                else:
                    # https://www.vtk.org/Wiki/VTK/Examples/Cxx/Visualization/ReverseAccess
                    # above link shows how to reverse access source from actor
                    self.sphere_actors[-2].GetProperty().SetColor(self.non_leading_sphere_color)
                    alg = self.sphere_actors[-2].GetMapper().GetInputConnection(0, 0).GetProducer()
                    ref = vtk.vtkSphereSource.SafeDownCast(alg)
                    ref.SetRadius(self.sphere_radius / 2.)
            except IndexError:
                pass  # the point of this is just to handle the very first sphere, at which point there is no -2

            self.sphere_actors.append(actor)
            self.renderer.AddActor(actor)
            iren.GetRenderWindow().Render()
            self.event_number += 1
            self.iterations -= 1
            time.sleep(.05)
        except IndexError:
            print(self.event_number)

    def transform(self, old_pos):
        angle = -0.008726  # 0.5 degrees
        ret = old_pos[:]
        ret[1] = -1 * old_pos[1]
        rot_matrix = np.matrix([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])

        xy = [[ret[0]], [ret[1]]]
        mult = np.matmul(rot_matrix, xy)
        ret = np.array([mult.item(0), mult.item(1), ret[2]])

        ret += self.shift1 + self.shift2
        ret[2] = self.set_z
        return ret
