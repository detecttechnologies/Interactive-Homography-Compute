from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *

class Calibration(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Calibration, self).__init__(parent)

        self.initUI()

    def initUI(self):
        grid = QtWidgets.QGridLayout()
        grid.spacing()
        rectangleWidth = QLabel('Rectangle Width:')
        rectangleHeight = QLabel('Rectangle Height:')
        rectangleWidth.setAlignment(QtCore.Qt.AlignRight)
        rectangleHeight.setAlignment(QtCore.Qt.AlignRight)
        self.rectangleWidthEdit = QLineEdit()
        self.rectangleHeightEdit = QLineEdit()

        grid.addWidget(rectangleWidth, 0, 0)
        grid.addWidget(self.rectangleWidthEdit, 0, 2)
        grid.addWidget(rectangleHeight, 1, 0)
        grid.addWidget(self.rectangleHeightEdit, 1, 2)
        self.setLayout(grid)