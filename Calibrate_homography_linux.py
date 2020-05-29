# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'homography_frame.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from pathlib import Path
import os
import math


class Ui_MainWindow(object):  ###############UI  creation using pyqt5
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 300)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.uploadButton = QtWidgets.QPushButton(self.centralwidget)
        self.uploadButton.setGeometry(QtCore.QRect(280, 80, 181, 51))
        font = QtGui.QFont()
        font.setFamily("Myanmar Text")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.uploadButton.setFont(font)
        self.uploadButton.setAutoDefault(False)
        self.uploadButton.setDefault(False)
        self.uploadButton.setFlat(False)
        self.uploadButton.setObjectName("uploadButton")
        self.uploadButton.clicked.connect(self.uploadvideo)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(75, 80, 271, 41))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 200, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Homography calibration"))
        self.uploadButton.setText(_translate("MainWindow", "Upload"))
        self.label.setText(_translate("MainWindow", "Upload Video:"))

    def uploadvideo(self):  ###############Upload button function to upload the video
        self.filename = QFileDialog.getOpenFileName(None, 'Open file',
                                                    os.getcwd(), "Video files (*.mp4)")
        MainWindow.hide()
        points = []
        self.homography_frame(self.filename, points)

    def homography_frame(self, filename,
                         points):  ###############Video frame to capture the points(marking and altering)
        cap = cv.VideoCapture(filename[0])
        ret = False
        while not ret:
            ret, frame = cap.read()
        staticframe = frame.copy()
        if len(points) != 0:
            for i in points:
                cv.circle(frame, (i[0], i[1]), 8, (200, 0, 0), -1)
        frame_OG = frame.copy()

        def get_calibration_points():
            refPt = points
            global frame

            def get_rect(event, x, y, flags, refPt):
                distance_dict = {}
                d = []
                if event == cv.EVENT_LBUTTONUP:
                    if flags == cv.EVENT_FLAG_LBUTTON:
                        refPt.append([x, y])
                        centre = (x, y)
                        cv.circle(frame, centre, 8, (200, 0, 0),
                                  -1)  ###############Marking the frames with circular points
                        cv.imshow('Select your points', frame)
                    elif event == cv.EVENT_FLAG_CTRLKEY + cv.EVENT_FLAG_LBUTTON:
                        frame_new = staticframe.copy()
                        try:
                            for pt in refPt:  ################Points need to be marked in the rectangular shape(4 points only)
                                distance = math.sqrt((x - pt[0]) ** 2 + (y - pt[1]) ** 2)
                                d.append(distance)
                                distance_dict[distance] = pt
                            minimum_ditance = min(d)
                            if len(refPt) != 0:
                                refPt.remove(distance_dict.get(
                                    minimum_ditance))  ###############Deleting the positional points from the reference points matrix to delete the points marked in the ui
                        except:
                            pass
                        for pt in refPt:
                            cv.circle(frame_new, (pt[0], pt[1]), 8, (200, 0, 0), -1)
                        cv.addWeighted(frame, 0.0, frame_new, 1, 0, frame)
                        cv.imshow('Select your points', frame)

            cv.namedWindow('Select your points', 0)
            frame = frame_OG.copy()
            cv.putText(frame, text="Start from top left point, go clockwise", org=(10, 50),
                       fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 125, 0), thickness=2)
            cv.imshow('Select your points', frame)
            cv.setMouseCallback('Select your points', get_rect, refPt)
            cv.waitKey()
            return refPt

        self.calibration_points = get_calibration_points()
        self.pts1 = np.array(self.calibration_points, dtype=np.float32)
        print(f"First set of points: {self.pts1}")
        self.rectanglewindow(event=True)

    def rectanglewindow(self,
                        event):  ###############Ui window to get the scale for the rectangle we have plotted using(Height and width to b mentioned in integers)
        plt.close(fig=None)
        dlg = QtWidgets.QDialog(None)
        dlg.setWindowTitle("Rectangle width and height")
        self.width = QtWidgets.QLineEdit(dlg)
        self.width.setGeometry(QtCore.QRect(170, 100, 151, 31))
        self.width.setObjectName("width")

        self.height = QtWidgets.QLineEdit(dlg)
        self.height.setGeometry(QtCore.QRect(550, 100, 151, 31))
        self.height.setObjectName("height")

        self.label_2 = QtWidgets.QLabel(dlg)
        self.label_2.setGeometry(QtCore.QRect(30, 100, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_2.setText("Recatngle width:")

        self.label_3 = QtWidgets.QLabel(dlg)
        self.label_3.setGeometry(QtCore.QRect(400, 100, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)

        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_3.setText("Rectangle height:")

        self.Calibratebutton = QtWidgets.QPushButton(dlg)
        self.Calibratebutton.setGeometry(QtCore.QRect(250, 200, 193, 28))
        self.Calibratebutton.setText("Calibrate")
        font = QtGui.QFont()
        font.setFamily("Myanmar Text")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.Calibratebutton.setFont(font)
        self.Calibratebutton.clicked.connect(dlg.hide)
        dlg.exec_()
        transformed_width = int(self.width.text())
        transformed_height = int(self.height.text())
        # %%
        top_left = np.array((500, 500))
        pts2 = np.float32([top_left + [0, 0],
                           top_left + [transformed_width, 0],
                           top_left + [transformed_width, transformed_height],
                           top_left + [0, transformed_height]])

        self.M = cv.getPerspectiveTransform(self.pts1, pts2)
        dst = cv.warpPerspective(frame, self.M, (frame.shape[1] * 2, frame.shape[0] * 2))
        plt.figure(figsize=(10, 5))
        plt.ion()
        plt.show()
        plt.subplot(121), plt.imshow(frame[..., ::-1]), plt.title('Input')
        plt.subplot(122), plt.imshow(dst[..., ::-1]), plt.title('Output')
        axrect = plt.axes([0.19, 0.05, 0.4, 0.075])
        axprev = plt.axes([0.60, 0.05, 0.2, 0.075])
        axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
        bnext = Button(axnext, 'Save')
        bprev = Button(axprev, 'Mark Points Again!!')
        rect = Button(axrect, 'Change the height and width of the rectangle!!')
        plt.draw()
        bnext.on_clicked(self.nextwindow)
        bprev.on_clicked(self.previouswindow)
        rect.on_clicked(self.rectanglewindow)
        plt.pause(100.00)

    def nextwindow(self, event):
        plt.close(fig=None)
        print(self.M)
        inputfilename = Path(self.filename[0]).stem
        matrix_file = 'calibration_' + inputfilename + '.npz'
        self.M.dump(matrix_file)
        # self.uploadvideo()
        cv.destroyAllWindows()
        MainWindow.show()

    def previouswindow(self,
                       event):  ###############Clicking the Mark points again button to change the marked points to alter calibration
        print("Previous button")
        plt.close(fig=None)
        self.homography_frame(self.filename, self.calibration_points)
        return False


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
