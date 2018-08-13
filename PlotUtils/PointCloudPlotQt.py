import vtk
import sys
import os
import cv2
import re
import pdb
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from SubsampleFunctions.SubsampleFrac import subsample_frac
from Filters.ThresholdFilter import threshold_filter
from tqdm import tqdm, trange
import time
from laspy.file import File
from laspy.header import Header
from laspy.util import LaspyException
from Utils.AxisAlignedBox3D import AxisAlignedBox3D
from PlotUtils.CustomInteractorStyle import CustomInteractorStyle
from PlotUtils.VtkTimerCallback import VtkTimerCallback
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog, QMessageBox, QSlider
from PyQt5 import Qt


class PointCloudPlotQt(QWidget):
    def __init__(self, plots=None, las_header=None, axes_on=False, app=None, background=(.2, .3, .4)):
        super().__init__()
        self.plots = plots
        self.las_header = las_header
        self.background = background
        self.default_viewup = (0.0, 1.0, 0.0)
        self.axes_on = axes_on
        # self.app = Qt.QApplication(sys.argv)
        self.app = app
        self.main = Qt.QMainWindow()
        self.main.__init__()
        self.frame = Qt.QFrame()
        self.hl = Qt.QHBoxLayout()
        self.bl = Qt.QVBoxLayout()
        # self.cull_state_machine = QtCore.QStateMachine()
        self.cull_planes_on = False
        self.default_cull_planes = []
        self.default_cull_plane_distances = []
        self.default_cull_planes_bounds = []
        self.culling_slider = None

        self.widgets = []
        self.widget_defaults = []
        self.widget_point_actors = []
        self.axes_actors = []
        if self.plots is not None:
            for i in range(len(plots)):
                vtk_widget = QVTKRenderWindowInteractor(self.frame)
                self.widgets.append(vtk_widget)
                self.hl.addWidget(vtk_widget)
                self.axes_actors.append(vtk.vtkCubeAxesActor2D())
                self.plot_point_cloud_qt(plots[i], vtk_widget)

            for w in self.widgets:
                position = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetPosition()
                focus = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFocalPoint()
                viewup = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetViewUp()
                self.widget_defaults.append((position, focus, viewup))

        self.hl.addLayout(self.bl)
        self.add_button("Toggle Axes", self.__on_toggle_axes_click)
        self.add_button("Snap To First", self.__on_snap_button_click)
        # self.add_button("Translate to Origin", self.__on_translate_to_origin_button_click)
        # self.add_button("Rotate", self.__on_rotate_button_click)
        self.add_button("GoTo Default View", self.__on_default_view_button)
        self.add_button("Set New Default View", self.__on_set_default_view_button)
        self.add_button("Save Plot", self.__on_save_button_click)
        self.add_button("Collapse", self.__on_collapse_button_click)
        self.add_button("Collapse Uniform", self.__on_collapse_uniform_button_click)
        self.add_button("Translate and Rotate XY", self.__on_translate_rotate_xy_button_click)
        self.add_button("Shift Vector", self.__on_shift_vector_click)
        self.add_button("Rotate by Angle", self.__on_rotate_by_angle_click)
        self.add_button("Rotate 90", self.__on_rotate_90_click)
        self.add_button("Auto Rotate", self.__on_auto_rotate_button_click)
        self.add_button("Keep Points Inside Box", self.__on_keep_points_inside_box_click)
        self.add_button("Keep Points Outside Box", self.__on_keep_points_outside_box_click)
        # self.add_statemachine(self.cull_state_machine,"State", "Off", "On")
        self.add_button("Cull Planes Toggle", self.__on_cull_planes_toggle)
        self.add_button("Simulate", self.__on_simulate_button_click)
        self.add_button("Test", self.__on_test_click)
        # self.hl.addWidget(self.culling_slider)
        self.frame.setLayout(self.hl)
        self.main.setCentralWidget(self.frame)
        self.main.show()
        for w in self.widgets:
            w.GetRenderWindow().GetInteractor().Initialize()
            w.GetRenderWindow().GetInteractor().Start()
        # sys.exit(self.app.exec_())

    def plot_point_cloud_qt(self, plot, widget):
        rw = widget.GetRenderWindow()
        iren = widget.GetRenderWindow().GetInteractor()
        # iren.SetRenderWindow(rw)

        ren = vtk.vtkRenderer()
        ren.AddActor(plot.vtkActor)
        self.widget_point_actors.append(plot.vtkActor)
        rw.AddRenderer(ren)
        ren.SetBackground(self.background)

        camera = ren.GetActiveCamera()
        corner = vtk.vtkCornerAnnotation()
        orientation = camera.GetOrientation()
        corner.SetText(0, "(x, y, z) = (%.3f, %.3f, %.3f)" % (orientation[0], orientation[1], orientation[2]))
        ren.AddActor(corner)
        if self.axes_on:
            i = self.widgets.index(widget)
            axes = self.axes_actors[i]
            axes.SetInputConnection(self.plots[i].outline.GetOutputPort())
            axes.SetCamera(camera)
            axes.SetLabelFormat("%6.4g")
            axes.SetFlyModeToOuterEdges()
            axes.SetFontFactor(1.2)
            ren.AddViewProp(axes)

        ren.ResetCamera()

        iren.SetInteractorStyle(CustomInteractorStyle(ren=ren, corner=corner, app=self.app))
        picker = vtk.vtkPointPicker()
        iren.SetPicker(picker)
        rw.Render()

    def add_button(self, label, call):
        button = QPushButton(label, self)
        button.resize(100, 100)
        button.clicked.connect(call)
        self.bl.addWidget(button)
        button.show()

    def __on_cull_planes_toggle(self):
        # print(states)
        self.cull_planes_on = not self.cull_planes_on
        # print(self.cull_planes_on)
        if self.cull_planes_on:
            self.__add_culling_slider()
        else:
            self.__reset_remove_culling_slider()

    def __distance_between_planes(self, far_plane, near_plane):
        # assume planes are in form [A, B, C, D] where plane equation is Ax + By + Cz + D = 0
        far_plane = np.array(far_plane)
        near_plane = np.array(near_plane)
        if not far_plane[2] == 0:
            point_on_far = np.array([0., 0., -far_plane[3] / far_plane[2]])
        elif not far_plane[1] == 0:
            point_on_far = np.array([0., -far_plane[3] / far_plane[1], 0.])
        else:
            point_on_far = np.array([-far_plane[3] / far_plane[1], 0., 0.])

        if not near_plane[2] == 0:
            point_on_near = np.array([0., 0., -near_plane[3] / near_plane[2]])
        elif not near_plane[1] == 0:
            point_on_near = np.array([0., -near_plane[3] / near_plane[1], 0.])
        else:
            point_on_near = np.array([-near_plane[3] / near_plane[0], 0., 0.])

        normal_vector = np.array(far_plane[:3])
        vector_between_planes = point_on_far - point_on_near
        return abs(np.dot(vector_between_planes, normal_vector) / np.linalg.norm(normal_vector))

    @staticmethod
    def __binary_search(arr, left, right, x):
        while left <= right:
            mid = left + int((right - left) / 2)
            if arr[mid] < x:
                left = mid + 1
            else:
                right = mid - 1
        return left-1

    def __add_culling_slider(self):
        # w = self.widgets[0]
        for w in self.widgets:
            planes = [0] * 24
            w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFrustumPlanes(1, planes)
            self.default_cull_planes.append(planes)
        for i in range(len(self.widgets)):
            w = self.widgets[i]
            planes = [0] * 24
            w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFrustumPlanes(1, planes)
            far_plane = planes[16:20]
            near_plane = planes[20:]
            # print(far_plane)
            # print(near_plane)
            self.default_cull_plane_distances.append(self.__distance_between_planes(far_plane, near_plane))
            # print(abs(dist_between_planes))
            vtkplanes = vtk.vtkPlanes()
            vtkplanes.SetFrustumPlanes(planes)
            frustum_source = vtk.vtkFrustumSource()
            frustum_source.SetPlanes(vtkplanes)
            frustum_source.Update()
            # self.plots[i].mapper.SetInputConnection(testsource.GetOutputPort())
            self.plots[i].frustumMapper.SetInputData(frustum_source.GetOutput())
            actor = vtk.vtkActor()
            actor.SetMapper(self.plots[i].frustumMapper)
            actor.GetProperty().SetOpacity(0)
            self.default_cull_planes_bounds.append(w.GetRenderWindow().GetInteractor().
                                                   GetInteractorStyle().ren.ComputeVisiblePropBounds())
            # w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.AddActor(actor)
            w.GetRenderWindow().Render()
            # print(w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetClippingRange())
            # self.plots[i].mapper.SetInputData

        self.culling_slider = QSlider()
        self.culling_slider.setMinimum(0)
        self.culling_slider.setMaximum(100)
        self.culling_slider.setValue(100)
        self.culling_slider.setTickInterval(1)
        self.culling_slider.setTracking(True)
        self.culling_slider.valueChanged.connect(self.__culling_slider_move)
        self.culling_slider.show()
        self.hl.addWidget(self.culling_slider)

    def __culling_slider_move(self):
        # self.culling_slider.setValue(50)
        self.culling_slider.hide()  # slider wasn't updating, this is a really hacky solution
        self.culling_slider.show()
        for i in range(len(self.widgets)):
            w = self.widgets[i]
            planes = [0] * 24
            w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFrustumPlanes(1, planes)
            max_distance = self.default_cull_plane_distances[i]
            far_plane = planes[16:20]
            near_plane = planes[20:]
            z_diff = self.default_cull_planes_bounds[i][5] - self.default_cull_planes_bounds[i][4]
            new_z = self.default_cull_planes_bounds[i][4] + z_diff * self.culling_slider.value() / 100.
            new_bounds = self.default_cull_planes_bounds[i] + tuple()
            new_bounds = np.array(new_bounds)
            new_bounds[5] = new_z
            # w.GetRenderWindow().GetInteractor().GetInteractorStyle().\
            #     ren.ComputeVisiblePropBounds(new_bounds)
            # print(new_bounds)
            w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.ResetCameraClippingRange(new_bounds)
            # print(w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetClippingRange())
            w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.ResetCamera(new_bounds)
            w.update()
            w.Render()
            # print(far_plane)
            # print(near_plane)
            #
            # print(self.default_cull_plane_distances[i])
        # print(self.culling_slider.value())

        # print("moved")

    def __reset_remove_culling_slider(self):
        self.culling_slider.setValue(100)
        self.hl.removeWidget(self.culling_slider)
        self.culling_slider.hide()

    def __on_toggle_axes_click(self):
        for i in range(len(self.axes_actors)):
            # self.axes_actors[i].SetTotalLength(100, 100, 100)
            self.widgets[i].Render()
            self.widgets[i].GetRenderWindow().Render()

    def __on_snap_button_click(self):
        first_plot = self.widgets[0]
        position = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetPosition()
        focus = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFocalPoint()
        viewup = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetViewUp()
        if len(self.widgets) > 1:
            for w in self.widgets[1:]:
                w.GetRenderWindow().GetInteractor().GetInteractorStyle().set_camera_orientation(position, focus, viewup)
                w.GetRenderWindow().GetInteractor().GetInteractorStyle().edit_display_angle()
                # w.update()
                w.GetRenderWindow().Render()
                w.update()
                # print(w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetParallelProjection())

    def __on_default_view_button(self):
        for i in range(len(self.widgets)):
            w = self.widgets[i]
            default = self.widget_defaults[i]
            w.GetRenderWindow().GetInteractor().GetInteractorStyle().\
                set_camera_orientation(default[0], default[1], default[2])
            w.update()
            w.GetRenderWindow().GetInteractor().GetInteractorStyle().edit_display_angle()

    def __on_set_default_view_button(self):
        w = self.app.focusWidget()
        position = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetPosition()
        focus = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFocalPoint()
        viewup = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetViewUp()
        i = self.widgets.index(w)
        self.widget_defaults[i] = (position, focus, viewup)

    def __on_save_button_click(self):
        # note that the next line is correct because "self" refers to the overall PointCloudPlotQt QWidget
        prompt = QInputDialog.getInt(self, "Plot index to save", "Index")
        # note that prompt returns as ('int_inputted', bool) where bool represents if the prompt was accepted
        if prompt[1]:
            try:
                to_save = self.widgets[int(prompt[0])]
                filename = QInputDialog.getText(self, "File Path From LineageProject:", "Name")
                # assume this is from the test folder, TODO figure out better way
                # path = os.path.join(os.path.realpath('..'), filename[0])
                path = filename[0]
                if not path.endswith(".las"):
                    path += ".las"
                if os.path.exists(path):
                    print("Overwriting")
                if self.las_header is None:
                    file_for_header = QInputDialog.getText(self, "Path for Las Header:", "Name")
                    # path_for_header = os.path.join(os.path.realpath('..'), file_for_header[0])
                    path_for_header = file_for_header[0]
                    try:
                        header_file = File(path_for_header, mode='r')
                        temp_las_header = header_file.header
                    except FileNotFoundError:
                        QMessageBox.about(self, "Error", "Invalid path, using default header")
                        temp_las_header = Header()
                    except LaspyException:
                        return
                else:
                    try:
                        temp_las_header = self.las_header
                    except FileNotFoundError:
                        QMessageBox.about(self, "Error", "Invalid path, did not save.")
                        return
            except IndexError:
                QMessageBox.about(self, "Error", "Index out of bounds exception, remember to zero index.")
                return
            with File(path, mode='w', header=temp_las_header) as file:
                # pdb.set_trace()
                pointCloud = self.plots[prompt[0]]
                points = pointCloud.getPoints()
                # print(points)
                allx = []
                ally = []
                allz = []
                # for p in tqdm(points, total=points.GetNumberOfPoints(), desc="Saving"):
                for i in tqdm(range(points.GetNumberOfPoints()), total=points.GetNumberOfPoints(), desc="Saving"):
                    p = points.GetPoint(i)
                    # print(p)
                    allx.append(p[0])
                    ally.append(p[1])
                    allz.append(p[2])
                file.x = np.array(allx)
                file.y = np.array(ally)
                file.z = np.array(allz)
                if self.las_header is None:
                    header_file.close()

    def __on_collapse_button_click(self):
        to_collapse = QInputDialog.getText(self, "Dimension(s) to collapse:", "Here")
        # print(to_collapse)
        if not to_collapse[1]:
            return
        if len(to_collapse[0]) > 2:
            QMessageBox.about(self, "Error", "Invalid input, must be of form such as 'X' or 'XY'")
            return
        elif len(to_collapse[0]) == 1:
            self.__collapse_one_dim(to_collapse[0])
        else:
            self.__collapse_two_dim(to_collapse[0])

    def __on_collapse_uniform_button_click(self):
        to_collapse = QInputDialog.getText(self, "Dimension(s) to collapse:", "Here")
        # print(to_collapse)
        if not to_collapse[1]:
            return
        if not len(to_collapse[0]) == 1:
            QMessageBox.about(self, "Error", "Invalid input, must be of form such as 'Z'")
            return
        else:
            self.__collapse_one_dim(to_collapse[0], uniform_collapse=True)

    def __collapse_one_dim(self, to_collapse, uniform_collapse=False):
        mesh = QInputDialog.getDouble(self, "Meshing Distance", "In meters", decimals=3)
        axes_on = QInputDialog.getItem(self, "Axes On?", "", ["yes", "no"])
        if axes_on[0] == "yes":
            axes_setting = "on"
        else:
            axes_setting = "off"
        w = self.app.focusWidget()
        label_to_dim = {"X": 0, "Y": 1, "Z": 2}
        dim_to_label = {0: "X", 1: "Y", 2: "Z"}
        try:
            collapse_dim = label_to_dim[to_collapse]
        except KeyError:
            QMessageBox.about(self, "Error", "Invalid input, must be of form such as'XY'")
            return
        dims = [0, 1, 2]
        dims.remove(collapse_dim)
        arr1 = []
        arr2 = []
        i = self.widgets.index(w)
        points = self.plots[i].getPoints()
        for k in tqdm(range(points.GetNumberOfPoints()), total=points.GetNumberOfPoints(), desc="Getting Points"):
            p = points.GetPoint(k)
            arr1.append(p[dims[0]])
            arr2.append(p[dims[1]])
        # heatmap, xedges, yedges = np.histogram2d(arr1, arr2, bins=(100, 100))
        # extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

        print("Plotting")
        plt.clf()
        plt.axis('equal')
        plt.axis(axes_setting)
        if axes_on[0] == "yes":
            plt.title("Collapse %s, Mesh %s" % (to_collapse, mesh[0]))
            plt.xlabel(dim_to_label[dims[0]])
            plt.ylabel(dim_to_label[dims[1]])
        # print(min(arr1), max(arr1), min(arr2), max(arr2))
        # print(float(mesh[0]))
        xbins = int((max(arr1) - min(arr1)) / float(mesh[0]))
        ybins = int((max(arr2) - min(arr2)) / float(mesh[0]))
        start = time.time()
        if uniform_collapse:
            hist, xedges, yedges = np.histogram2d(arr1, arr2, bins=(xbins, ybins))
            cutoff = 0
            default_weight = 1.
            weights = []
            for i in trange(len(arr1), desc="Normalizing"):
                x_coord = self.__binary_search(xedges, 0, len(xedges) - 1, arr1[i])
                y_coord = self.__binary_search(yedges, 0, len(yedges) - 1, arr2[i])
                if hist[x_coord][y_coord] > cutoff:
                    weights.append(default_weight / float(hist[x_coord][y_coord]))
                else:
                    weights.append(0)
                # pdb.set_trace()
            plt.hist2d(arr1, arr2, bins=(xbins, ybins), cmap=plt.cm.spring, weights=weights, norm=colors.LogNorm())
            ax = plt.gca()
            ax.set_facecolor([0, 0, 0])
            end = time.time() - start
            print("Finding histogram took %.2f seconds" % end)
            plt.show()
        else:
            print("Finding histogram")
            plt.hist2d(arr1, arr2, bins=(xbins, ybins), cmap=plt.cm.jet, norm=colors.LogNorm())
            end = time.time() - start
            print("Finding histogram took %.2f seconds" % end)
            plt.show()

    def __collapse_two_dim(self, to_collapse):
        mesh = QInputDialog.getText(self, "Meshing Distance", "In meters")
        w = self.app.focusWidget()
        label_to_dim = {"X": 0, "Y": 1, "Z": 2}
        dim_to_label = {0: "X", 1: "Y", 2: "Z"}
        try:
            dim_1 = label_to_dim[to_collapse[0]]
            dim_2 = label_to_dim[to_collapse[1]]
        except KeyError:
            QMessageBox.about(self, "Error", "Invalid input, must be of form such as'XY'")
            return
        dims = [0, 1, 2]
        dims.remove(dim_1)
        dims.remove(dim_2)
        arr = [] #TODO finish this
        i = self.widgets.index(w)
        points = self.plots[i].getPoints()
        for k in tqdm(range(points.GetNumberOfPoints()), total=points.GetNumberOfPoints(), desc="Getting Points"):
            p = points.GetPoint(k)
            arr.append(p[dims[0]])

        pdb.set_trace()
        print("Plotting")
        plt.clf()
        # plt.axis('equal')
        plt.title("Collapse %s, Mesh %s" % (to_collapse, mesh[0]))
        plt.xlabel(dim_to_label[dims[0]])
        plt.ylabel("# Points")
        bins = int((max(arr) - min(arr)) / float(mesh[0]))
        start = time.time()
        print("Finding histogram")
        plt.hist(arr, bins=bins)
        end = time.time() - start
        print("Finding histogram took %.2f seconds" % end)
        # plt.imshow(heatmap, extent=extent, origin='lower')
        plt.show()

    def __on_translate_rotate_xy_button_click(self):
        prompt = QInputDialog.getInt(self, "Plot index to cull", "Index")
        # note that prompt returns as ('int_inputted', bool) where bool represents if the prompt was taken
        if prompt[1]:
            try:
                i = prompt[0]
                w = self.widgets[i]  # only to throw the Index Error if invalid index given
            except IndexError:
                QMessageBox.about(self, "Error", "Index out of bounds exception, remember to zero index.")
                return
        else:
            return #TODO finish this refactor
        comp = re.compile('\([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?\s*,\s*[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?\)')
        corner0 = QInputDialog.getText(self, "Bounding Point 0", "")
        # regex from https://stackoverflow.com/questions/12929308/
        #                                   python-regular-expression-that-matches-floating-point-numbers/12929311

        if corner0[1]:
            m = comp.match(corner0[0])
            if m:
                # print("Match found: ", m.group())
                temp = m.group().replace("(", "")
                temp = temp.replace(")", "")
                temp = re.sub(r"\s+", "", temp).split(",")
                corner_float0 = [float(i) for i in temp]
                # print(corner_float0)
            else:
                print("Invalid point syntax")
                return
        else:
            return

        corner1 = QInputDialog.getText(self, "Bounding Point 1", "")
        if corner1[1]:
            m = comp.match(corner1[0])
            if m:
                # print("Match found: ", m.group())
                temp = m.group().replace("(", "")
                temp = temp.replace(")", "")
                temp = re.sub(r"\s+", "", temp).split(",")
                corner_float1 = [float(i) for i in temp]
                # print(corner_float0)
            else:
                print("Invalid point syntax")
                return
        else:
            return

        corner2 = QInputDialog.getText(self, "Bounding Point 2", "")
        if corner2[1]:
            m = comp.match(corner2[0])
            if m:
                # print("Match found: ", m.group())
                temp = m.group().replace("(", "")
                temp = temp.replace(")", "")
                temp = re.sub(r"\s+", "", temp).split(",")
                corner_float2 = [float(i) for i in temp]
                # print(corner_float0)
            else:
                print("Invalid point syntax")
                return
        else:
            return

        corner3 = QInputDialog.getText(self, "Bounding Point 3", "")
        if corner3[1]:
            m = comp.match(corner3[0])
            if m:
                # print("Match found: ", m.group())
                temp = m.group().replace("(", "")
                temp = temp.replace(")", "")
                temp = re.sub(r"\s+", "", temp).split(",")
                corner_float3 = [float(i) for i in temp]
                # print(corner_float0)
            else:
                print("Invalid point syntax")
                return
        else:
            return

        self.__translate_rotate_xy_helper(corner_float0, corner_float1, corner_float2, corner_float3)

    def __on_shift_vector_click(self):
        prompt = QInputDialog.getInt(self, "Plot index to cull", "Index")
        # note that prompt returns as ('int_inputted', bool) where bool represents if the prompt was taken
        if prompt[1]:
            try:
                i = prompt[0]
                w = self.widgets[i]  # only to throw the Index Error if invalid index given
            except IndexError:
                QMessageBox.about(self, "Error", "Index out of bounds exception, remember to zero index.")
                return
        else:
            return  # TODO finish this refactor

        comp = re.compile('\([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
                          '(\s*,\s*[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?){2}\)')
        shift = QInputDialog.getText(self, "Shift Vector", "")
        # regex from https://stackoverflow.com/questions/12929308/
        #                                   python-regular-expression-that-matches-floating-point-numbers/12929311

        if shift[1]:
            m = comp.match(shift[0])
            if m:
                # print("Match found: ", m.group())
                temp = m.group().replace("(", "")
                temp = temp.replace(")", "")
                temp = re.sub(r"\s+", "", temp).split(",")
                shift_float0 = [float(i) for i in temp]
                # print(corner_float0)
            else:
                print("Invalid point syntax")
                return
        else:
            return

        self.__translate_helper(i, shift_float0)

    def __translate_rotate_xy_helper(self, p0, p1, p2, p3):
        new_origin = np.array(p0)
        s0 = np.array(p0) - new_origin
        s1 = np.array(p1) - new_origin
        s2 = np.array(p2) - new_origin
        s3 = np.array(p3) - new_origin

        w = self.app.focusWidget()
        vec = s1 - s0
        shift = np.append(new_origin, 0)
        angle = np.arctan2(vec[1], vec[0])  # y coordinate comes first
        i = self.widgets.index(w)
        points = self.plots[i].getPoints()
        num_points = points.GetNumberOfPoints()

        rot_matrix = np.matrix([[np.cos(-angle), -np.sin(-angle)], [np.sin(-angle), np.cos(-angle)]])
        for k in trange(num_points, desc="Translating"):
            p = points.GetPoint(k)
            old = np.asarray(p)
            # print(old)
            to_rotate = old - shift
            xy = [[to_rotate[0]], [to_rotate[1]]]
            # print(rot_matrix)
            # print(xy)
            mult = np.matmul(rot_matrix, xy)
            new = np.array([mult.item(0), mult.item(1), to_rotate[2]])
            # print(new)
            # sys.exit()
            points.SetPoint(k, new)
        self.plots[i].vtkCells.Modified()
        self.plots[i].vtkPoints.Modified()
        self.plots[i].vtkDepth.Modified()
        # print(self.plots[i].GetUserTransform())
        # w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.AddActor(vtk.vtkAxesActor())
        w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.ResetCamera()
        w.GetRenderWindow().Render()
        self.__on_set_default_view_button()

    def __translate_helper(self, i, shift):
        w = self.widgets[i]
        points = self.plots[i].getPoints()
        num_points = points.GetNumberOfPoints()
        shift = np.array(shift)

        for k in trange(num_points, desc="Shifting"):
            p = points.GetPoint(k)
            old = np.asarray(p)
            new = old + shift
            points.SetPoint(k, new)
        self.plots[i].vtkCells.Modified()
        self.plots[i].vtkPoints.Modified()
        self.plots[i].vtkDepth.Modified()
        w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.ResetCamera()
        w.GetRenderWindow().Render()
        self.__on_set_default_view_button()

    def __on_auto_rotate_button_click(self):
        mesh = .05
        threshold = .015
        image_fname = "temp.png"
        image_fname_lines = "templines.png"
        prompt = QInputDialog.getInt(self, "Plot index to rotate", "Index")
        # note that prompt returns as ('int_inputted', bool) where bool represents if the prompt was taken
        if prompt[1]:
            try:
                points = self.plots[prompt[0]].getPointsAsArray()
            except IndexError:
                QMessageBox.about(self, "Error", "Index out of bounds exception, remember to zero index.")
                return
        else:
            return
        points = threshold_filter(points, threshold=threshold)
        dims = [0, 1]
        arr1 = []
        arr2 = []
        for k in trange(len(points), desc="Getting Points"):
            p = points[k]
            arr1.append(p[dims[0]])
            arr2.append(p[dims[1]])
        plt.clf()
        plt.axis('equal')
        plt.axis('off')
        # print(min(arr1), max(arr1), min(arr2), max(arr2))
        # print(float(mesh[0]))
        xbins = int((max(arr1) - min(arr1)) / mesh)
        ybins = int((max(arr2) - min(arr2)) / mesh)
        start = time.time()
        print("Finding histogram")
        plt.hist2d(arr1, arr2, (xbins, ybins), cmap=plt.cm.jet, norm=colors.LogNorm())
        end = time.time() - start
        print("Finding histogram took %.2f seconds" % end)
        hist_xmin, hist_xmax = plt.xlim()
        hist_ymin, hist_ymax = plt.ylim()
        # print(plt.xlim())
        # print(plt.ylim())
        plt.savefig(image_fname)
        img = cv2.imread(image_fname, 0)
        height, width = img.shape
        img_xmin, img_xmax = 0, width
        img_ymin, img_ymax = height, 0
        edges = cv2.Canny(img, 50, 200, apertureSize=3)
        min_line_length = 10
        lines = cv2.HoughLinesP(image=edges, rho=1, theta=np.pi / 1800, threshold=50, lines=np.array([]),
                                minLineLength=min_line_length, maxLineGap=25)
        try:
            a, b, c = lines.shape
        except AttributeError:
            print("No lines found, subsample more")
        pos_slopes = []
        neg_slopes = []
        pos_unscale_slopes = []
        neg_unscale_slopes = []

        # translates p from interval (_x0, _x1) to corresponding point in (_y0, _y1)
        def change_of_ref(_p, _x0, _x1, _y0, _y1):
            _slope = (_y1 - _y0) / (_x1 - _x0)
            y_int = _y0 - _slope * _x0
            return _slope * _p + y_int

        for i in range(a):
            cv2.line(img, (lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3]), (0, 0, 255), 1,
                     cv2.LINE_AA)
            p0 = (lines[i][0][0], lines[i][0][1])
            p1 = (lines[i][0][2], lines[i][0][3])
            m_test = (p1[1] - p0[1]) / (p1[0] - p0[0])
            x0 = change_of_ref(p0[0], img_xmin, img_xmax, hist_xmin, hist_xmax)
            y0 = change_of_ref(p0[1], img_ymin, img_ymax, hist_ymin, hist_ymax)
            x1 = change_of_ref(p1[0], img_xmin, img_xmax, hist_xmin, hist_xmax)
            y1 = change_of_ref(p1[1], img_ymin, img_ymax, hist_ymin, hist_ymax)
            m = (y1 - y0) / (x1 - x0)
            if m > 0:
                pos_slopes.append(m)
            else:
                neg_slopes.append(m)
            if m_test > 0:
                pos_unscale_slopes.append(m_test)
            else:
                neg_unscale_slopes.append(m_test)
            al = -m
            bl = 1
            cl = m * x0 - y0
            # print(p0[0], p0[1], x0, y0)
        cv2.imwrite(image_fname_lines, img)
        # positive ones
        try:
            pos_num_bins = int((max(pos_unscale_slopes) - min(pos_unscale_slopes)) / .001)
            pos_h, pos_bin_edges = np.histogram(pos_unscale_slopes, bins=pos_num_bins)
            pos_index_of_max = np.argmax(pos_h)
            pos_min_slope, pos_max_slope = pos_bin_edges[pos_index_of_max], pos_bin_edges[pos_index_of_max + 1]
            pos_max_frac = pos_h[pos_index_of_max] / len(pos_unscale_slopes)
        except ValueError:  # happens if no positive slopes exist, so default to negative
            pos_max_frac = 0

        # negative ones
        try:
            neg_num_bins = int((max(neg_unscale_slopes) - min(neg_unscale_slopes)) / .001)
            neg_h, neg_bin_edges = np.histogram(neg_unscale_slopes, bins=neg_num_bins)
            neg_index_of_max = np.argmax(neg_h)
            neg_min_slope, neg_max_slope = neg_bin_edges[neg_index_of_max], neg_bin_edges[neg_index_of_max + 1]
            neg_max_frac = neg_h[neg_index_of_max] / len(neg_unscale_slopes)
        except ValueError:
            neg_max_frac = 0

        if not pos_max_frac and not neg_max_frac:
            print("Hough lines couldn't find any slanted lines, may need to subsample less")
            return

        slopes_to_avg = []
        if neg_max_frac >= pos_max_frac:
            slopes_used = "neg"
            for slope in neg_unscale_slopes:
                if neg_min_slope <= slope <= neg_max_slope:
                    slopes_to_avg.append(slope)
        else:
            slopes_used = "pos"
            for slope in pos_unscale_slopes:
                if pos_min_slope <= slope <= pos_max_slope:
                    slopes_to_avg.append(slope)
        avg_slope = np.mean(slopes_to_avg)
        angle = np.arctan2(avg_slope, 1)
        # rot_matrix = np.matrix([[np.cos(-angle), -np.sin(-angle)], [np.sin(-angle), np.cos(-angle)]])
        print("Rotating by %.4f degrees" % (angle * 180. / np.pi))
        # print(slopes_used)
        if not np.isnan(angle):
            self.__rotation_helper(prompt[0], angle)

    def __on_rotate_by_angle_click(self):
        prompt = QInputDialog.getInt(self, "Plot index to rotate", "Index")
        # note that prompt returns as ('int_inputted', bool) where bool represents if the prompt was taken
        if prompt[1]:
            try:
                i = prompt[0]
                w = self.widgets[i]  # only to throw the Index Error if invalid index given
            except IndexError:
                QMessageBox.about(self, "Error", "Index out of bounds exception, remember to zero index.")
                return
        else:
            return
        rotation = QInputDialog.getDouble(self, "Angle (Counterclockwise)", "In Degrees", decimals=4)
        if rotation[1]:
            angle = rotation[0] * np.pi / 180.
        else:
            return
        self.__rotation_helper(i, angle)

    def __on_rotate_90_click(self):
        prompt = QInputDialog.getInt(self, "Plot index to rotate", "Index")
        # note that prompt returns as ('int_inputted', bool) where bool represents if the prompt was taken
        if prompt[1]:
            try:
                i = prompt[0]
                w = self.widgets[i]  # only to throw the Index Error if invalid index given
            except IndexError:
                QMessageBox.about(self, "Error", "Index out of bounds exception, remember to zero index.")
                return
        else:
            return
        self.__rotation_helper(i, np.pi/2)

    def __rotation_helper(self, i, angle):
        # print(i)
        # print(self.plots)
        points = self.plots[i].getPoints()
        num_points = points.GetNumberOfPoints()
        rot_matrix = np.matrix([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        for k in trange(num_points, desc="Translating"):
            p = points.GetPoint(k)
            old = np.asarray(p)
            # print(old)
            xy = [[old[0]], [old[1]]]
            # print(rot_matrix)
            # print(xy)
            mult = np.matmul(rot_matrix, xy)
            new = np.array([mult.item(0), mult.item(1), old[2]])
            # print(new)
            # sys.exit()
            points.SetPoint(k, new)
        temp = subsample_frac(self.plots[i].getPointsAsArray(), .1)
        temp_threshold = threshold_filter(temp, threshold=.05)
        minx = min([p[0] for p in temp_threshold])
        miny = min([p[1] for p in temp_threshold])
        del temp_threshold
        minz = 0

        del temp
        self.__translate_helper(i, [-minx, -miny, -minz])

    def __on_keep_points_inside_box_click(self):
        prompt = QInputDialog.getInt(self, "Plot index to cull", "Index")
        # note that prompt returns as ('int_inputted', bool) where bool represents if the prompt was taken
        if prompt[1]:
            try:
                i = prompt[0]
                w = self.widgets[i]  # only to throw the Index Error if invalid index given
            except IndexError:
                QMessageBox.about(self, "Error", "Index out of bounds exception, remember to zero index.")
                return
        else:
            return
        corner0 = QInputDialog.getText(self, "Bounding Point 1", "")
        # regex from https://stackoverflow.com/questions/12929308/
        #                                   python-regular-expression-that-matches-floating-point-numbers/12929311
        comp = re.compile('\([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
                          '(\s*,\s*[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?){2}\)')
        if corner0[1]:
            m = comp.match(corner0[0])
            if m:
                # print("Match found: ", m.group())
                temp = m.group().replace("(", "")
                temp = temp.replace(")", "")
                temp = re.sub(r"\s+", "", temp).split(",")
                corner_float0 = [float(i) for i in temp]
                # print(corner_float0)
            else:
                print("Invalid point syntax")
                return
        else:
            return

        corner1 = QInputDialog.getText(self, "Bounding Point 2", "")
        if corner1[1]:
            m = comp.match(corner1[0])
            if m:
                # print("Match found: ", m.group())
                temp = m.group().replace("(", "")
                temp = temp.replace(")", "")
                temp = re.sub(r"\s+", "", temp).split(",")
                corner_float1 = [float(i) for i in temp]
                # print(corner_float0)
            else:
                print("Invalid point syntax")
                return
        else:
            return

        # print(corner_float0)
        # print(corner_float1)
        bounding_box = AxisAlignedBox3D(corner_float0, corner_float1)
        new_min = bounding_box.min_corner()
        points_to_keep = []
        point_array = self.plots[i].getPointsAsArray()
        for point in tqdm(point_array, total=len(point_array), desc="Clearing Points"):
            if bounding_box.contains_point(point):
                points_to_keep.append(point[:])
        del point_array
        self.plots[i].clearPoints()
        for point in tqdm(points_to_keep, total=len(points_to_keep), desc="Constructing PC"):
            self.plots[i].addPoint(point)
        del points_to_keep
        self.__translate_helper(i, -new_min)

    def __on_keep_points_outside_box_click(self):
        prompt = QInputDialog.getInt(self, "Plot index to cull", "Index")
        # note that prompt returns as ('int_inputted', bool) where bool represents if the prompt was taken
        if prompt[1]:
            try:
                i = prompt[0]
                w = self.widgets[i]  # only to throw the Index Error if invalid index given
            except IndexError:
                QMessageBox.about(self, "Error", "Index out of bounds exception, remember to zero index.")
                return
        else:
            return
        corner0 = QInputDialog.getText(self, "Bounding Point 1", "")
        # regex from https://stackoverflow.com/questions/12929308/
        #                                   python-regular-expression-that-matches-floating-point-numbers/12929311
        comp = re.compile('\([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
                          '(\s*,\s*[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?){2}\)')
        if corner0[1]:
            m = comp.match(corner0[0])
            if m:
                # print("Match found: ", m.group())
                temp = m.group().replace("(", "")
                temp = temp.replace(")", "")
                temp = re.sub(r"\s+", "", temp).split(",")
                corner_float0 = [float(i) for i in temp]
                # print(corner_float0)
            else:
                print("Invalid point syntax")
                return
        else:
            return

        corner1 = QInputDialog.getText(self, "Bounding Point 2", "")
        if corner1[1]:
            m = comp.match(corner1[0])
            if m:
                # print("Match found: ", m.group())
                temp = m.group().replace("(", "")
                temp = temp.replace(")", "")
                temp = re.sub(r"\s+", "", temp).split(",")
                corner_float1 = [float(i) for i in temp]
                # print(corner_float0)
            else:
                print("Invalid point syntax")
                return
        else:
            return

        bounding_box = AxisAlignedBox3D(corner_float0, corner_float1)
        new_min = bounding_box.min_corner()
        points_to_keep = []
        point_array = self.plots[i].getPointsAsArray()
        for point in tqdm(point_array, total=len(point_array), desc="Clearing Points"):
            if not bounding_box.contains_point(point):
                points_to_keep.append(point[:])
        self.plots[i].clearPoints()
        del point_array
        for point in tqdm(points_to_keep, total=len(points_to_keep), desc="Constructing PC"):
            self.plots[i].addPoint(point)
        del points_to_keep

    def __on_simulate_button_click(self):
        w = self.widgets[0]

        sim1 = "/Users/Vinit/PycharmProjects/LineageProject/Simulation/pose_log_mission1_may_3.csv"
        sim2 = "/Users/Vinit/PycharmProjects/LineageProject/Simulation/pose_log_mission1.csv"
        sim3 = "/Users/Vinit/PycharmProjects/LineageProject/Simulation/pose_log_mission2.csv"
        sims = [sim1, sim2, sim3]

        event_lists = []

        for sim in sims:
            with open(sim, 'r') as sim_file:
                sim_reader = csv.reader(sim_file)
                event_list = list(sim_reader)
                event_lists.append(event_list)

        cb = VtkTimerCallback(renderwindow=w.GetRenderWindow(),
                              renderer=w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren,
                              event_lists=event_lists, iterations=[len(e) for e in event_lists])

        w.GetRenderWindow().GetInteractor().AddObserver('TimerEvent', lambda obj, event:
                                                        cb.execute(obj, event, tracking=True,
                                                                   arrows=False, camera_track=-1))

        timer_id = w.GetRenderWindow().GetInteractor().CreateRepeatingTimer(100)
        cb.timer_id = timer_id
        w.GetRenderWindow().GetInteractor().Start()

    def __on_test_click(self):
        pass


def create_point_cloud_plot_qt(plots, input_header=None, axes_on=False):
    app = QApplication(sys.argv)
    pc = PointCloudPlotQt(plots, input_header, axes_on, app)
    sys.exit(app.exec_())
