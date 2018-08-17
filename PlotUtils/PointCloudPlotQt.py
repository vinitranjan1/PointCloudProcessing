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
from BaseProjectDirectory import base_project_dir
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
        """
        :param plots: list of VTKPointClouds to plot
        :param las_header: a las_header that is optionally supplied if reading from a las file, helpful for saving
        :param axes_on: flag for turning axes on/off
        :param app: the main QApplication driving the GUI
        :param background: tuple of 0-1's for background color
        """
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
        self.add_buttons()
        self.frame.setLayout(self.hl)
        self.main.setCentralWidget(self.frame)
        self.main.show()
        for w in self.widgets:
            w.GetRenderWindow().GetInteractor().Initialize()
            w.GetRenderWindow().GetInteractor().Start()
        # sys.exit(self.app.exec_())

    def add_buttons(self):
        """
        a function for organization purposes, put all the buttons you want here
        """
        self.add_button("Toggle Axes", self.__on_toggle_axes_click)
        self.add_button("Snap To First", self.__on_snap_button_click)
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
        self.add_button("Simulate", self.__on_simulate_button_click)
        self.add_button("Test", self.__on_test_click)

    def add_button(self, label, call):
        """
        :param label: the desired label for the button in the GUI
        :param call: the desired functional call when the button is click

        note that if you want to pass in a function with arguments, you need use a lambda, i.e.
        self.add_button("Example", lambda x: self.__example_function(x))

        """
        button = QPushButton(label, self)
        button.resize(100, 100)
        button.clicked.connect(call)
        self.bl.addWidget(button)
        button.show()

    def plot_point_cloud_qt(self, plot, widget):
        """
        :param plot: the specific VTKPointCloud being plotted
        :param widget: the QVTKRenderWindowInteractor that acts as the container for the specific VTK object

        A function to plot a single VTKPointCloud
        """
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
        i = self.widgets.index(widget)
        axes = self.axes_actors[i]
        axes.SetInputConnection(self.plots[i].outline.GetOutputPort())
        axes.SetCamera(camera)
        axes.SetLabelFormat("%6.4g")
        axes.SetFlyModeToOuterEdges()
        axes.SetFontFactor(1.2)
        if self.axes_on:
            ren.AddViewProp(axes)

        ren.ResetCamera()

        iren.SetInteractorStyle(CustomInteractorStyle(ren=ren, corner=corner, app=self.app))
        # a picker is used for clicking interactions if you want any cutsom ones
        picker = vtk.vtkPointPicker()
        iren.SetPicker(picker)
        rw.Render()

    @staticmethod
    def __binary_search(arr, left, right, x):
        """
        :param arr: array to search
        :param left: index to start left pointer
        :param right: index to start right pointer
        :param x: value we're searching for
        :return: index of where the point would exist

        Note that the use of this binary search is such that because of the number of decimals on these points,
            x will never exactly be found, so that check isnt even considered and it just finds the location where
            x would be
        """
        while left <= right:
            mid = left + int((right - left) / 2)
            if arr[mid] < x:
                left = mid + 1
            else:
                right = mid - 1
        return left-1

    def __on_toggle_axes_click(self):
        """
        A function to toggle the axes on/off
        """
        if self.axes_on:
            for i in range(len(self.axes_actors)):
                w = self.widgets[i]
                w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.RemoveViewProp(self.axes_actors[i])
                w.Render()
                w.GetRenderWindow().Render()
            self.axes_on = False
        else:
            for i in range(len(self.axes_actors)):
                w = self.widgets[i]
                w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.AddViewProp(self.axes_actors[i])
                w.Render()
                w.GetRenderWindow().Render()
            self.axes_on = True

    def __on_snap_button_click(self):
        """
        A function that cases all of the other plots to snap to the same orientation as the first one
        """
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
        """
        A function that snaps all plots to their original orientation (A reset)
        """
        for i in range(len(self.widgets)):
            w = self.widgets[i]
            default = self.widget_defaults[i]
            w.GetRenderWindow().GetInteractor().GetInteractorStyle().\
                set_camera_orientation(default[0], default[1], default[2])
            w.update()
            w.GetRenderWindow().GetInteractor().GetInteractorStyle().edit_display_angle()

    def __on_set_default_view_button(self):
        """
        A function that changes the default view of the MOST RECENTLY INTERACTED WITH plot to where it currently is
        """
        w = self.app.focusWidget()
        position = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetPosition()
        focus = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFocalPoint()
        viewup = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetViewUp()
        i = self.widgets.index(w)
        self.widget_defaults[i] = (position, focus, viewup)

    def __on_save_button_click(self):
        """
        Function to save a plot as a las file
        Note that the file will save relative to wherever the plotting function is called from
        So if calling from Main.py, can just do Data/temp.las to save it in the Data folder

        Note that the second prompt will only come up if the entire GUI was initialized with self.las_header = None
        In which case, this second prompt wants an existing las file from which it will copy the header
        This is why its easier to pass in the las_header when initializing the GUI, saves trouble on this step
        """
        # note that the next line is correct because "self" refers to the overall PointCloudPlotQt QWidget
        prompt = QInputDialog.getInt(self, "Plot index to save", "Index")
        # note that prompt returns as ('int_inputted', bool) where bool represents if the prompt was accepted
        if prompt[1]:
            try:
                to_save = self.widgets[int(prompt[0])]
                filename = QInputDialog.getText(self, "File Path From LineageProject:", base_project_dir)
                # path = os.path.join(os.path.realpath('..'), filename[0])
                if not filename[1]:
                    return
                path = filename[0]
                if not path.endswith(".las"):
                    path += ".las"
                if os.path.exists(path):
                    print("Overwriting")
                if self.las_header is None:
                    file_for_header = QInputDialog.getText(self, "Path for Las Header:", base_project_dir)
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
        """
        Function that takes in the desired dimension to collapse, valid inputs are in the form 'X' or 'XY'
            Note that collapsing 'Z' means removing the Z dimension
        Needs to be capitalized # TODO theres no reason for this, modify to accept lowercase as well
        Depending on if you collapse one or two dimensions, it calls the respective helper method
        """
        prompt = QInputDialog.getInt(self, "Plot index to collapse", "Index")
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
        to_collapse = QInputDialog.getText(self, "Dimension(s) to collapse:", "Here")
        # print(to_collapse)
        if not to_collapse[1]:
            return
        if len(to_collapse[0]) > 2:
            QMessageBox.about(self, "Error", "Invalid input, must be of form such as 'X' or 'XY'")
            return
        elif len(to_collapse[0]) == 1:
            self.__collapse_one_dim(i, to_collapse[0])
        else:
            self.__collapse_two_dim(i, to_collapse[0])

    def __on_collapse_uniform_button_click(self):
        """
        Function that does essentially same thing as self.__on_collapse_button_click, only this function
            calls it such that the resultant plot will have any nonzero points in the 2D histogram all be
            brought up to the same intensity
        Also, this one does not handle the case of collapsing two dimensions
        """
        prompt = QInputDialog.getInt(self, "Plot index to collapse", "Index")
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
        to_collapse = QInputDialog.getText(self, "Dimension(s) to collapse:", "Here")
        # print(to_collapse)
        if not to_collapse[1]:
            return
        if not len(to_collapse[0]) == 1:
            QMessageBox.about(self, "Error", "Invalid input, must be of form such as 'Z'")
            return
        else:
            self.__collapse_one_dim(i, to_collapse[0], uniform_collapse=True)

    def __collapse_one_dim(self, i, to_collapse, uniform_collapse=False):
        """
        :param i: plot index to collapse
        :param to_collapse: dimension to collapse
        :param uniform_collapse: flag to determine if the collapsed 2D histogram should or should not weight the
            intensities based on the number of points in the bin

        this helper function actually calculates the creates the 2D histogram for plot at index i
        """
        mesh = QInputDialog.getDouble(self, "Meshing Distance", "In meters", decimals=3)
        axes_on = QInputDialog.getItem(self, "Axes On?", "", ["yes", "no"])
        if axes_on[0] == "yes":
            axes_setting = "on"
        else:
            axes_setting = "off"
        w = self.widgets[i]
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

    def __collapse_two_dim(self, i, to_collapse):
        """
        :param i: plot index to collapse
        :param to_collapse: dimensions to collapse

        this helper function actually calculates the creates the histogram for plot at index i
        """
        mesh = QInputDialog.getDouble(self, "Meshing Distance", "In meters", decimals=3)
        w = self.widgets[i]
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
        arr = []
        points = self.plots[i].getPoints()
        for k in tqdm(range(points.GetNumberOfPoints()), total=points.GetNumberOfPoints(), desc="Getting Points"):
            p = points.GetPoint(k)
            arr.append(p[dims[0]])

        # pdb.set_trace()
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
        """
        One of the rotation functions, lets you pick four points in the XY plane and the first and point picked
            will be moved to the origin while the second point will be on the positive x-axis
        When prompting for points, they need to be of the form (x, y)
        # TODO remove the prompt for points 3/4, they aren't actually used for anything since points 1/2 define the rotation
        """
        prompt = QInputDialog.getInt(self, "Plot index to translate/rotate", "Index")
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
        comp = re.compile('\([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?\s*,\s*[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?\)')

        # regex from https://stackoverflow.com/questions/12929308/
        #                                   python-regular-expression-that-matches-floating-point-numbers/12929311
        corners = []
        for c in range(4):
            corner = QInputDialog.getText(self, "Bounding Point " + str(c), "")
            if corner[1]:
                m = comp.match(corner[0])
                if m:
                    # print("Match found: ", m.group())
                    temp = m.group().replace("(", "")
                    temp = temp.replace(")", "")
                    temp = re.sub(r"\s+", "", temp).split(",")
                    corners.append([float(j) for j in temp])
                    # print(corner_float0)
                else:
                    print("Invalid point syntax, needs to be like (x, y)")
                    return
            else:
                return

        corner_float0 = corners[0]
        corner_float1 = corners[1]
        corner_float2 = corners[2]
        corner_float3 = corners[3]

        self.__translate_rotate_xy_helper(i, corner_float0, corner_float1, corner_float2, corner_float3)

    def __on_shift_vector_click(self):
        """
        Function to prompt for the vector by which you want to shift all points in a certain plot
        """
        prompt = QInputDialog.getInt(self, "Plot index to shift", "Index")
        # note that prompt returns as ('int_inputted', bool) where bool represents if the prompt was taken
        if prompt[1]:
            try:
                i = prompt[0]
                w = self.widgets[i]  # only to throw the Index Error if invalid index given
            except IndexError:
                QMessageBox.about(self, "Error", "Index out of bounds exception, remember to zero index.")
                return
        else:
            return  #]]

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

    def __translate_rotate_xy_helper(self, i, p0, p1, p2, p3):
        """
        :param i: plot index to act on
        :param p0: first point
        :param p1: second point
        :param p2: third point
        :param p3: fourth point
        # TODO remove p2/p3, they arent actualy used for anything

        The helper function corresponding to self.__on_translate_rotate_xy_button_click
        """
        new_origin = np.array(p0)
        s0 = np.array(p0) - new_origin
        s1 = np.array(p1) - new_origin
        s2 = np.array(p2) - new_origin
        s3 = np.array(p3) - new_origin

        w = self.widgets[i]
        vec = s1 - s0
        shift = np.append(new_origin, 0)
        angle = np.arctan2(vec[1], vec[0])  # y coordinate comes first
        i = self.widgets.index(w)
        points = self.plots[i].getPoints()
        num_points = points.GetNumberOfPoints()

        rot_matrix = np.matrix([[np.cos(-angle), -np.sin(-angle)], [np.sin(-angle), np.cos(-angle)]])
        for k in trange(num_points, desc="Rotating"):
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
        """
        :param i: index of plot to shift
        :param shift: vector to shift by

        Helper function to shift all points in plot i by vector shift

        """
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
        """
        A somewhat convoluted algorithm that uses the inherent warehouse structure to try to auto rotate to snap
            the outer wall of the warehouse to the coordinate axes

        First, the algorithm uses the threshold filter to remove ghost points because the walls should survive it
        Then, it creates the 2D histogram in the Z dimension and uses openCV's Houghline algorithm to try and
            sketch in the lines, a majority of which should line up with the walls
        Then, it bins the slopes and takes the bin with the highest number of points because there can be some random
            lines that arent actually the walls, but the bin with the highest number of points is in some sense the
            "most confident" slope, which then get averaged
        This slope is then used for rotation so that it lines up with the axis
        It is recommended that when you use this function, you agree to the prompt where it shifts the new minimum
            to the origin, but not strictly necessary because the plot can always be shifted
        """
        mesh = .05
        threshold = .015
        image_fname = "Data/temp.png"
        image_fname_lines = "Data/templines.png"
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

        # NOTE that in openCV, and in general computer coordinate systems, the system is origin at top left
        #   positive x right, positive y down, hence why positive and negative may appear to be flipped
        #   but they actually are correct

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
        except OverflowError:
            print("Divide by zero found, meaning infinite slope, so should already be rotated")
            return

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
        """
        Function that prompts for plot to rotate points in and the angle IN DEGREES to rotate by
            Note that the angle is converted to radians before passing to the helper function
        """
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
        """
        Function that prompts for plot index to rotate points and rotates 90 degrees counterclockwise
        Convenient to have this be its own button because the auto rotate can be off by 90 degrees
        """
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
        """
        :param i: plot index to rotate
        :param angle: angle IN RADIANS to rotate by

        Helper function that rotates points in plot i by angle in radians

        Note that this helper function, after rotation, prompts for if you want to move the new minimum value to the
            origin, but it uses the threshold filter first for robustness
        """
        # print(i)
        # print(self.plots)
        points = self.plots[i].getPoints()
        num_points = points.GetNumberOfPoints()
        rot_matrix = np.matrix([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        for k in trange(num_points, desc="Rotating"):
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

        to_shift = QInputDialog.getItem(self, "Shift new min to origin?", "", ["yes", "no"])
        if to_shift[0] == "yes":
            temp = subsample_frac(self.plots[i].getPointsAsArray(), .1)
            temp_threshold = threshold_filter(temp, threshold=.05)
            minx = min([p[0] for p in temp_threshold])
            miny = min([p[1] for p in temp_threshold])
            del temp_threshold
            minz = 0

            del temp
            print("shifting to new min")
            self.__translate_helper(i, [-minx, -miny, -minz])
        else:
            self.plots[i].vtkCells.Modified()
            self.plots[i].vtkPoints.Modified()
            self.plots[i].vtkDepth.Modified()
            self.widgets[i].GetRenderWindow().GetInteractor().GetInteractorStyle().ren.ResetCamera()
            self.widgets[i].GetRenderWindow().Render()

    def __on_keep_points_inside_box_click(self):
        """
        A function that prompts for two points to define an AxisAlignedBox3D and all points INSIDE the box are kept
        """
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
        """
        A function that prompts for two points to define an AxisAlignedBox3D and all points OUTSIDE the box are kept
        TODO in all honesty, this method and self.__on_keep_points_inside_box_click should be the same method
        TODO    with a flag as to whether the points are kept or discarded, but I got lazy
        """
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
        """
        Function that runs simulations in the FIRST plot
        """
        w = self.widgets[0]

        sim1 = "Simulation/pose_log_mission1_may_3.csv"
        sim2 = "Simulation/pose_log_mission1.csv"
        sim3 = "Simulation/pose_log_mission2.csv"
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
    """
    :param plots: list of VTKPointClouds to plot
    :param input_header: las file header, mostly for saving purposes
    :param axes_on: flag for turning on/off axes

    The driver function to start the GUI, should always start the GUI by calling this method
    """
    app = QApplication(sys.argv)
    pc = PointCloudPlotQt(plots, input_header, axes_on, app)
    sys.exit(app.exec_())
