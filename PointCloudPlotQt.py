import vtk
from vtk.util import numpy_support
import sys
import os
import pdb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from scipy.stats import gaussian_kde
from tqdm import tqdm, trange
import time
from laspy.file import File
from laspy.header import Header
from laspy.util import LaspyException
from CustomInteractorStyle import CustomInteractorStyle
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog, QMessageBox
from PyQt5 import Qt, QtCore, QtGui


class PointCloudPlotQt(QWidget):
    def __init__(self, plots=None, las_header=None, axes_on=False, app=None):
        super().__init__()
        self.plots = plots
        self.las_header = las_header
        self.background = (.2, .3, .4)
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
        if self.plots is not None:
            for i in range(len(plots)):
                vtk_widget = QVTKRenderWindowInteractor(self.frame)
                self.plot_point_cloud_qt(plots[i], vtk_widget)
                self.widgets.append(vtk_widget)
                self.hl.addWidget(vtk_widget)

            for w in self.widgets:
                position = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetPosition()
                focus = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFocalPoint()
                viewup = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetViewUp()
                self.widget_defaults.append((position, focus, viewup))

        self.hl.addLayout(self.bl)
        self.add_button("Snap To First", self.__on_snap_button_click)
        self.add_button("Translate to Origin", self.__on_translate_to_origin_button_click)
        self.add_button("Rotate", self.__on_rotate_button_click)
        self.add_button("GoTo Default View", self.__on_default_view_button)
        self.add_button("Set New Default View", self.__on_set_default_view_button)
        self.add_button("Save Plot", self.__on_save_button_click)
        self.add_button("Collapse", self.__on_collapse_button_click)
        self.add_button("Test", self.__on_test_click)
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
        # print(i/num)
        # print((i+1)/num)

        ren.SetBackground(self.background)

        camera = ren.GetActiveCamera()
        corner = vtk.vtkCornerAnnotation()
        orientation = camera.GetOrientation()
        corner.SetText(0, "(x, y, z) = (%.3f, %.3f, %.3f)" % (orientation[0], orientation[1], orientation[2]))
        ren.AddActor(corner)
        if self.axes_on:
            axes = vtk.vtkAxesActor()
            ren.AddActor(axes)

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

    def __on_snap_button_click(self):
        first_plot = self.widgets[0]
        position = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetPosition()
        focus = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFocalPoint()
        viewup = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetViewUp()
        if len(self.widgets) > 1:
            for w in self.widgets[1:]:
                w.GetRenderWindow().GetInteractor().GetInteractorStyle().set_camera_orientation(position, focus, viewup)
                w.GetRenderWindow().GetInteractor().GetInteractorStyle().edit_display_angle()
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

    def __on_translate_to_origin_button_click(self):
        w = self.app.focusWidget()
        e = w.GetRenderWindow().GetInteractor().GetEventPosition()
        print(e)
        w.GetRenderWindow().GetInteractor().GetPicker().\
            Pick(e[0], e[1], 0, w.GetRenderWindow().GetRenderers().GetFirstRenderer())
        p = np.asarray(w.GetRenderWindow().GetInteractor().GetPicker().GetPickPosition())
        # p[2] = 0
        print(p)
        i = self.widgets.index(w)
        # points = numpy_support.vtk_to_numpy(self.plots[i].vtkPolyData)
        points = self.plots[i].getPoints()
        num_points = points.GetNumberOfPoints()

        for k in trange(num_points, desc="Shifting"):
            old = np.asarray(points.GetPoint(k))
            points.SetPoint(k, old-p)
        self.plots[i].vtkCells.Modified()
        self.plots[i].vtkPoints.Modified()
        self.plots[i].vtkDepth.Modified()
        # print(self.plots[i].GetUserTransform())
        # w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.AddActor(vtk.vtkAxesActor())
        w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.ResetCamera()
        w.GetRenderWindow().Render()
        # print(old-p)
        # print(p)

    def __on_set_default_view_button(self):
        w = self.app.focusWidget()
        position = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetPosition()
        focus = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFocalPoint()
        viewup = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetViewUp()
        i = self.widgets.index(w)
        self.widget_defaults[i] = (position, focus, viewup)

    def __on_rotate_button_click(self):
        first_plot = self.widgets[0]
        position = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetPosition()
        focus = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFocalPoint()
        viewup = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetViewUp()
        print(position, focus, viewup)

    def __on_save_button_click(self):
        # note that the next line is correct because "self" refers to the overall PointCloudPlotQt QWidget
        prompt = QInputDialog.getInt(self, "Plot index to save", "Index")
        # note that prompt returns as ('int_inputted', bool) where bool represents if the prompt was
        if prompt[1]:
            try:
                to_save = self.widgets[int(prompt[0])]
                filename = QInputDialog.getText(self, "File Path From LineageProject:", "Name")
                # assume this is from the test folder, TODO figure out better way
                path = os.path.join(os.path.realpath('..'), filename[0])
                if not path.endswith(".las"):
                    path += ".las"
                if os.path.exists(path):
                    print("Overwriting")
                if self.las_header is None:
                    file_for_header = QInputDialog.getText(self, "Path for Las Header:", "Name")
                    path_for_header = os.path.join(os.path.realpath('..'), file_for_header[0])
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

    def __collapse_one_dim(self, to_collapse):
        mesh = QInputDialog.getText(self, "Meshing Distance", "In meters")
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
        plt.title("Collapse %s, Mesh %s" % (to_collapse, mesh[0]))
        plt.xlabel(dim_to_label[dims[0]])
        plt.ylabel(dim_to_label[dims[1]])
        # print(min(arr1), max(arr1), min(arr2), max(arr2))
        # print(float(mesh[0]))
        xbins = int((max(arr1) - min(arr1)) / float(mesh[0]))
        ybins = int((max(arr2) - min(arr2)) / float(mesh[0]))
        start = time.time()
        print("Finding histogram")
        plt.hist2d(arr1, arr2, (xbins, ybins), cmap=plt.cm.jet, norm=colors.LogNorm())
        end = time.time() - start
        print("Finding histogram took %d seconds" % end)
        # plt.imshow(heatmap, extent=extent, origin='lower')
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
        print("Finding histogram took %d seconds" % end)
        # plt.imshow(heatmap, extent=extent, origin='lower')
        plt.show()

    def __on_test_click(self):
        w = self.app.focusWidget()
        allx = []
        i = self.widgets.index(w)
        points = self.plots[i].getPoints()
        for k in tqdm(range(points.GetNumberOfPoints()), total=points.GetNumberOfPoints(), desc="Getting X"):
            p = points.GetPoint(k)
            x = p[2]
            allx.append(x)
        plt.hist(allx, bins=1000, range=(-2, 4))
        plt.show()


def create_point_cloud_plot_qt(plots, input_header=None, axes_on=False):
    app = QApplication(sys.argv)
    pc = PointCloudPlotQt(plots, input_header, axes_on, app)
    sys.exit(app.exec_())
