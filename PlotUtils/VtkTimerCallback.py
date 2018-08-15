"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

Another VTK utility class, used to handle simulations

Inputs:
renderwindow - the VTKRenderWindow the sim will run in
renderer - the VTKRenderer in renderwindow
event_lists - list of lists of events, and for each list in event_lists, will have a separate sphere
iterations - list of iteration numbers, i.e. [100, 200] means sim1 is 100 iterations while sim2 is 200 iterations

Note that if there is only one simulation, then it still assumes the list of events x is passed as [x]
"""
import vtk
import time
import pdb
from tqdm import tqdm, trange
import numpy as np


class VtkTimerCallback:
    def __init__(self, renderwindow, renderer, event_lists, iterations):
        self.event_numbers = [0] * len(event_lists)
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
        self.shift2 = np.array([0, .27, 0])
        self.set_z = 2.5
        self.event_lists = event_lists
        self.sphere_actors = [[] for i in range(len(event_lists))]
        self.arrow_actors = [[] for i in range(len(event_lists))]

        self.renderwindow.Render()
        self.renderwindow.GetInteractor().Initialize()

    def execute(self, obj, event, tracking=False, arrows=False, camera_track=-1):
        iren = obj
        camera_dist = 20
        view_angle = np.pi/12
        for i in range(len(self.event_lists)):
            if self.iterations[i] > 0:
                self.execute_single(iren, event, i, tracking, arrows)
        try:
            if camera_track > -1 and len(self.sphere_actors[camera_track]) > 1:
                camera = self.renderwindow.GetInteractor().GetInteractorStyle().camera
                obj_loc = np.array(self.sphere_actors[camera_track][-1].GetCenter())
                cam_loc = np.array(self.sphere_actors[camera_track][-2].GetCenter())
                pos_diff = obj_loc - cam_loc
                pos_diff_hat = pos_diff / np.linalg.norm(pos_diff)
                scaled_diff = pos_diff_hat * camera_dist

                position = obj_loc - scaled_diff
                focus = obj_loc
                viewup = np.array([0, 0, 1])

                camera.SetPosition(position)
                camera.SetFocalPoint(focus)
                camera.SetViewUp(viewup)
                self.renderwindow.GetInteractor().GetInteractorStyle().edit_display_angle()
                # self.renderer.ResetCamera()
        except IndexError:
            pass
        self.renderwindow.Render()
        time.sleep(.1)
        if np.all(np.array(self.iterations) == 0):
            self.destroy_sim(obj, event)

    def execute_single(self, iren, event, i, tracking, arrows):
        new_pos = np.array([float(i) for i in self.event_lists[i][self.event_numbers[i]][1:4]])
        new_pos = self.transform(new_pos)

        sphere_source = vtk.vtkSphereSource()
        sphere_source.SetCenter(new_pos)
        sphere_source.SetRadius(self.sphere_radius)

        sphere_mapper = vtk.vtkPolyDataMapper()
        sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())
        sphere_actor = vtk.vtkActor()
        sphere_actor.SetMapper(sphere_mapper)
        sphere_actor.GetProperty().SetColor(self.leading_sphere_color)

        try:
            if not tracking:
                self.renderer.RemoveActor(self.sphere_actors[i][-1])
            else:
                # https://www.vtk.org/Wiki/VTK/Examples/Cxx/Visualization/ReverseAccess
                # above link shows how to reverse access source from actor
                # pdb.set_trace()
                self.sphere_actors[i][-1].GetProperty().SetColor(self.non_leading_sphere_color)
                alg = self.sphere_actors[i][-1].GetMapper().GetInputConnection(0, 0).GetProducer()
                ref = vtk.vtkSphereSource.SafeDownCast(alg)
                ref.SetRadius(self.sphere_radius / 2.)

                if arrows:
                    # create the arrows
                    # https://www.vtk.org/Wiki/VTK/Examples/Python/GeometricObjects/Display/OrientedArrow
                    arrow_source = vtk.vtkArrowSource()
                    arrow_source.SetShaftRadius(.05)
                    arrow_source.SetTipRadius(.1)
                    arrow_source.SetTipLength(.1)

                    start_point = self.sphere_actors[i][-1].GetCenter()
                    end_point = new_pos
                    # print(start_point, end_point)

                    normalized_x = [0] * 3
                    normalized_y = [0] * 3
                    normalized_z = [0] * 3

                    math = vtk.vtkMath()
                    math.Subtract(end_point, start_point, normalized_x)
                    length = math.Norm(normalized_x)
                    math.Normalize(normalized_x)

                    arbitrary = np.random.rand(3)
                    math.Cross(normalized_x, arbitrary, normalized_z)

                    math.Cross(normalized_z, normalized_x, normalized_y)
                    matrix = vtk.vtkMatrix4x4()

                    matrix.Identity()
                    for j in range(3):
                        matrix.SetElement(j, 0, normalized_x[j])
                        matrix.SetElement(j, 1, normalized_y[j])
                        matrix.SetElement(j, 2, normalized_z[j])

                    transform = vtk.vtkTransform()
                    transform.Translate(start_point)
                    transform.Concatenate(matrix)
                    length /= 2
                    transform.Scale(length, length, length)

                    transformPD = vtk.vtkTransformPolyDataFilter()
                    transformPD.SetTransform(transform)
                    transformPD.SetInputConnection(arrow_source.GetOutputPort())

                    arrow_mapper = vtk.vtkPolyDataMapper()
                    arrow_actor = vtk.vtkActor()

                    arrow_mapper.SetInputConnection(transformPD.GetOutputPort())
                    arrow_actor.SetMapper(arrow_mapper)
                    self.renderer.AddActor(arrow_actor)
                    self.arrow_actors[i].append(arrow_actor)
        except IndexError:
            pass

        self.sphere_actors[i].append(sphere_actor)
        self.renderer.AddActor(sphere_actor)
        self.iterations[i] -= 1
        self.event_numbers[i] += 1

    def destroy_sim(self, obj, event):
        iren = obj
        for i in range(len(self.event_lists)):
            self.event_numbers[i] = 0
            for sphere in self.sphere_actors[i]:
                self.renderer.RemoveActor(sphere)
            for arrow in self.arrow_actors[i]:
                self.renderer.RemoveActor(arrow)
            self.sphere_actors[i] = []
            self.arrow_actors[i] = []
        iren.DestroyTimer(self.timer_id)

    # this function is to transform Area 17's reference frame to ours
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
