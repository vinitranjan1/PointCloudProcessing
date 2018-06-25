import vtk
import sys
import numpy as np
from VtkPointCloud import VtkPointCloud
from PointCloudPlot import PointCloudPlot
from PyQt5 import Qt, QtCore, QtGui

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class PointCloudWidget(Qt.QMainWindow):
    def __init__(self, points=VtkPointCloud(), widget=None):
        Qt.QMainWindow.__init__(self, parent=None)
        self.vl = Qt.QVBoxLayout()
        self.frame = Qt.QFrame()
        self.widget = widget
        self.vtk_widget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtk_widget)
        self.rw = self.vtk_widget.GetRenderWindow()
        self.iren = self.vtk_widget.GetRenderWindow().GetInteractor()

        self.plot = PointCloudPlot(points, self.rw, self.iren)
