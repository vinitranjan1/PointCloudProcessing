import vtk
from vtk.util import numpy_support
import sys
import os
import cv2
import pdb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from SubsampleFrac import subsample_frac
from Filters.ThresholdFilter import threshold_filter
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

        self.widgets = []
        self.widget_defaults = []
        self.widget_point_actors = []
        self.axes_actors = []
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
        self.add_button("Toggle Axes", self.__on_toggle_axes_click)
        self.add_button("Snap To First", self.__on_snap_button_click)
        # self.add_button("Translate to Origin", self.__on_translate_to_origin_button_click)
        # self.add_button("Rotate", self.__on_rotate_button_click)
        self.add_button("GoTo Default View", self.__on_default_view_button)
        self.add_button("Set New Default View", self.__on_set_default_view_button)
        self.add_button("Save Plot", self.__on_save_button_click)
        self.add_button("Collapse", self.__on_collapse_button_click)
        self.add_button("Translate and Rotate XY", self.__on_translate_rotate_xy_button_click)
        self.add_button("Translate Z", self.__on_translate_z_button_click)
        self.add_button("New Origin", self.__on_new_origin_click)
        self.add_button("Rotate by Angle", self.__on_rotate_by_angle_click)
        self.add_button("Rotate 90", self.__on_rotate_90_click)
        self.add_button("Auto Rotate", self.__on_auto_rotate_button_click)
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

    def __on_toggle_axes_click(self):
        pass

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

    # def __on_translate_to_origin_button_click(self):
    #     w = self.app.focusWidget()
    #     e = w.GetRenderWindow().GetInteractor().GetEventPosition()
    #     print(e)
    #     w.GetRenderWindow().GetInteractor().GetPicker().\
    #         Pick(e[0], e[1], 0, w.GetRenderWindow().GetRenderers().GetFirstRenderer())
    #     p = np.asarray(w.GetRenderWindow().GetInteractor().GetPicker().GetPickPosition())
    #     # p[2] = 0
    #     print(p)
    #     i = self.widgets.index(w)
    #     # points = numpy_support.vtk_to_numpy(self.plots[i].vtkPolyData)
    #     points = self.plots[i].getPoints()
    #     num_points = points.GetNumberOfPoints()
    #
    #     for k in trange(num_points, desc="Shifting"):
    #         old = np.asarray(points.GetPoint(k))
    #         points.SetPoint(k, old-p)
    #     self.plots[i].vtkCells.Modified()
    #     self.plots[i].vtkPoints.Modified()
    #     self.plots[i].vtkDepth.Modified()
    #     # print(self.plots[i].GetUserTransform())
    #     # w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.AddActor(vtk.vtkAxesActor())
    #     w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.ResetCamera()
    #     w.GetRenderWindow().Render()
    #     # print(old-p)
    #     # print(p)

    def __on_set_default_view_button(self):
        w = self.app.focusWidget()
        position = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetPosition()
        focus = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFocalPoint()
        viewup = w.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetViewUp()
        i = self.widgets.index(w)
        self.widget_defaults[i] = (position, focus, viewup)

    # def __on_rotate_button_click(self):
    #     first_plot = self.widgets[0]
    #     position = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetPosition()
    #     focus = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetFocalPoint()
    #     viewup = first_plot.GetRenderWindow().GetInteractor().GetInteractorStyle().camera.GetViewUp()
    #     print(position, focus, viewup)

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
        mesh = QInputDialog.getDouble(self, "Meshing Distance", "In meters", decimals=2)
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
        print("Finding histogram")
        plt.hist2d(arr1, arr2, (xbins, ybins), cmap=plt.cm.jet, norm=colors.LogNorm())
        end = time.time() - start
        print("Finding histogram took %d seconds" % end)
        # TODO: .xaxis.label.set_visible(False)
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

    def __on_translate_rotate_xy_button_click(self):
        # p0 = (-27.6, -12.1)
        # p1 = (1.27, -1.55)
        # p2 = (-26.2, -74.06)
        # p3 = (-55.2, 63.53)
        p0x = QInputDialog.getDouble(self, "First Point X", "", decimals=2)
        if p0x[1]:
            p0y = QInputDialog.getDouble(self, "First Point Y", "", decimals=2)
        else:
            return
        if p0y[1]:
            p1x = QInputDialog.getDouble(self, "Second Point X", "", decimals=2)
        else:
            return
        if p1x[1]:
            p1y = QInputDialog.getDouble(self, "Second Point Y", "", decimals=2)
        else:
            return
        if p1y[1]:
            p2x = QInputDialog.getDouble(self, "Third Point X", "", decimals=2)
        else:
            return
        if p2x[1]:
            p2y = QInputDialog.getDouble(self, "Third Point Y", "", decimals=2)
        else:
            return
        if p2y[1]:
            p3x = QInputDialog.getDouble(self, "Fourth Point X", "", decimals=2)
        else:
            return
        if p3x[1]:
            p3y = QInputDialog.getDouble(self, "Fourth Point Y", "", decimals=2)
        else:
            return
        if p3y[1]:
            self.__translate_rotate_xy_helper((p0x[0], p0y[0]), (p1x[0], p1y[0]), (p2x[0], p2y[0]), (p3x[0], p3y[0]))

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

    def __on_translate_z_button_click(self):
        shift = QInputDialog.getDouble(self, "Z Shift", "", decimals=2)
        if shift[1]:
            self.__translate_z_helper(shift[0])

    def __translate_z_helper(self, shift):
        w = self.app.focusWidget()
        i = self.widgets.index(w)
        points = self.plots[i].getPoints()
        num_points = points.GetNumberOfPoints()

        for k in trange(num_points, desc="Shifting"):
            p = points.GetPoint(k)
            old = np.asarray(p)
            new = np.array([old[0], old[1], old[2] + shift])
            points.SetPoint(k, new)
        self.plots[i].vtkCells.Modified()
        self.plots[i].vtkPoints.Modified()
        self.plots[i].vtkDepth.Modified()
        w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.ResetCamera()
        w.GetRenderWindow().Render()
        self.__on_set_default_view_button()

    def __on_new_origin_click(self):
        w = self.app.focusWidget()
        i = self.widgets.index(w)
        points = self.plots[i].getPoints()
        num_points = points.GetNumberOfPoints()

    def __translate_helper(self, shift, i):
        w = self.widgets[i]
        points = self.plots[i].getPoints()
        num_points = points.GetNumberOfPoints()

        for k in trange(num_points, desc="Shifting"):
            p = points.GetPoint(k)
            old = np.asarray(p)
            new = np.array([old[0] + shift[0], old[1] + shift[1], old[2] + shift[2]])
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

        # print(img_xmin, img_xmax)
        # print(hist_xmin, hist_xmax)
        # print("###")
        # print(img_ymin, img_ymax)
        # print(hist_xmin, hist_xmax)
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
        # rot_slope = np.mean(pos_slopes)  #TODO: make more robust by binning slopes (~.01) and taking mean of highest
        # cv2.namedWindow(image_file, cv2.WINDOW_NORMAL)
        # cv2.resizeWindow(image_file, 600, 600)
        #
        # cv2.imshow(image_file, img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # print(rot_slope)
        # angle = np.arctan2(rot_slope, 1)
        # print(angle)
        # print("###")

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
        print(angle)
        print(slopes_used)
        if not np.isnan(angle):
            self.__rotation_helper(prompt[0], angle)
            # if slopes_used == "neg":
            #     self.__rotation_helper(prompt[0], angle)
            # else:
            #     self.__rotation_helper(prompt[0], -angle)

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
        rotation = QInputDialog.getDouble(self, "Angle (Counterclockwise)", "In Degrees", decimals=2)
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
        temp_threshold = threshold_filter(temp, threshold=.01)
        minX = min([p[0] for p in temp_threshold])
        minY = min([p[1] for p in temp_threshold])
        del temp_threshold
        minZ = 0
        # try:
        #     temp_threshold = threshold_filter(temp, dim_to_collapse="Y", threshold=.01)
        #     minZ = min([p[2] for p in temp_threshold])
        #     del temp_threshold
        # except (IndexError, AssertionError):
        #     minZ = 0
        #     print("Couldn't shift Z")

        del temp
        self.__translate_helper([-minX, -minY, -minZ], i)
        #
        # self.plots[i].vtkCells.Modified()
        # self.plots[i].vtkPoints.Modified()
        # self.plots[i].vtkDepth.Modified()
        # # print(self.plots[i].GetUserTransform())
        # # w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren.AddActor(vtk.vtkAxesActor())
        # self.widgets[i].GetRenderWindow().GetInteractor().GetInteractorStyle().ren.ResetCamera()
        # self.widgets[i].GetRenderWindow().Render()
        # self.__on_set_default_view_button()

    def __on_test_click(self):
        p0 = (-27.6, -12.1)
        p1 = (1.27, -1.55)
        p2 = (-26.2, -74.06)
        p3 = (-55.2, 63.53)
        self.__translate_rotate_xy_helper(p0, p1, p2, p3)
        w = self.app.focusWidget()
        i = self.widgets.index(w)
        points = self.plots[i].getPointsAsArray()
        print(type(points))
        points = threshold_filter(points, .03)
        # self.plots[i].clearPoints()

    # def __on_test_click(self):
    #     w = self.app.focusWidget()
    #     allx = []
    #     i = self.widgets.index(w)
    #     points = self.plots[i].getPoints()
    #     for k in tqdm(range(points.GetNumberOfPoints()), total=points.GetNumberOfPoints(), desc="Getting X"):
    #         p = points.GetPoint(k)
    #         x = p[2]
    #         allx.append(x)
    #     plt.hist(allx, bins=1000, range=(-2, 4))
    #     plt.show()


def create_point_cloud_plot_qt(plots, input_header=None, axes_on=False):
    app = QApplication(sys.argv)
    pc = PointCloudPlotQt(plots, input_header, axes_on, app)
    sys.exit(app.exec_())
