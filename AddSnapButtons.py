from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import vtk


def add_snap_buttons(widgets):
    first_widget = widgets[0]
    for w in widgets:
        button = QPushButton('Snap')
        w.add
