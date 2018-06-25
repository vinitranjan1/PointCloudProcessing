import sys
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)
button = QtWidgets.QPushButton("Hello World")
button.setFixedSize(500, 500)
button.show()
app.exec_()
