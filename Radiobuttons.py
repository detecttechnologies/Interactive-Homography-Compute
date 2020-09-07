from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

class RadioButtons(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(RadioButtons, self).__init__(parent)

        self.initUI()

    def initUI(self):
        grid = QtWidgets.QGridLayout()
        grid.spacing()
        self.b1 = QRadioButton("Homography")
        self.b1.setChecked(True)
        self.b2 = QRadioButton("MPC - Line crossing")
        self.b3 = QRadioButton("MPC - Direction of entry")
        self.b4 = QRadioButton("MPC - RoI")
        grid.addWidget(self.b1, 0, 0)
        grid.addWidget(self.b2, 0, 1)
        grid.addWidget(self.b3, 0, 2)
        grid.addWidget(self.b4, 0, 3)
        self.setLayout(grid)
