import math
import os
import sys
import time
from pathlib import Path
import matplotlib
import matplotlib.figure
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import cv2 as cv
import numpy as np
import pandas as pd
from scipy.spatial import distance as dist
import csv
import os
from Mark_Images import MarkFigures
from Homography_Calibration_ui import Calibration
from Radiobuttons import RadioButtons
import re


class HomographyCalibration(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(HomographyCalibration, self).__init__(parent)
        self.toggleoption = 'Homography'
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        upload_csv = QAction('Upload csv', self)
        upload_image = QAction('Upload image', self)
        upload_video = QAction("Upload video", self)
        upload_image_folder = QAction('Upload image folder', self)
        fileMenu.addAction(upload_csv)
        fileMenu.addAction(upload_image)
        fileMenu.addAction(upload_video)
        fileMenu.addAction(upload_image_folder)
        upload_csv.triggered.connect(self.upload_csv)
        upload_image.triggered.connect(self.upload_image)
        upload_video.triggered.connect(self.upload_video)
        upload_image_folder.triggered.connect(self.upload_image_folder)
        self.label = MarkFigures()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.center()
        self.setWindowTitle('Homography-MPC software')
        self.grid = QtWidgets.QGridLayout()
        self.grid.spacing()
        self.central_widget = QWidget()
        self.rectangle = Calibration()
        self.figure = matplotlib.figure.Figure(figsize=(7, 3))
        self.canvas = FigureCanvas(self.figure)
        self.radiobuttons = RadioButtons()

        self.calibrateButton = QPushButton("Calibrate")
        self.calibrateButton.clicked.connect(self.startCalibration)
        self.saveButton = QPushButton("Save")
        self.saveButton.resize(150, 50)
        self.saveButton.clicked.connect(self.saveToCSV)

        self.grid.addWidget(self.label, 3, 1)
        self.grid.addWidget(self.canvas, 3, 3)
        self.grid.addWidget(self.rectangle, 5, 3)
        self.grid.addWidget(self.radiobuttons, 5, 1)
        self.grid.addWidget(self.calibrateButton, 7, 3)
        self.grid.addWidget(self.saveButton, 8, 3)

        self.central_widget.setLayout(self.grid)
        self.setCentralWidget(self.central_widget)

        self.radiobuttons.b1.toggled.connect(self.RadioButtonFunction)
        self.radiobuttons.b2.toggled.connect(self.RadioButtonFunction)
        self.radiobuttons.b3.toggled.connect(self.RadioButtonFunction)
        self.radiobuttons.b4.toggled.connect(self.RadioButtonFunction)

    def RadioButtonFunction(self):

        if self.radiobuttons.b1.isChecked():
            self.toggleoption = self.radiobuttons.b1.text()
            self.label.mpcEvents(self.radiobuttons.b1.text())
            if self.label.image_copy is not None:
                self.label.processImage(self.label.image_copy)
            self.initUI()
        else:
            self.gridmpc = QtWidgets.QGridLayout()
            self.gridmpc.spacing()
            self.central_widget_mpc = QWidget()
            self.gridmpc.addWidget(self.label, 3, 1)
            self.gridmpc.addWidget(self.radiobuttons, 5, 1)
            self.gridmpc.addWidget(self.saveButton, 8, 3)
            self.central_widget_mpc.setLayout(self.gridmpc)
            self.setCentralWidget(self.central_widget_mpc)

            if self.radiobuttons.b2.isChecked():
                self.toggleoption = self.radiobuttons.b2.text()
                self.label.mpcEvents(self.radiobuttons.b2.text())

            if self.radiobuttons.b3.isChecked():
                self.toggleoption = self.radiobuttons.b3.text()
                self.label.mpcEvents(self.radiobuttons.b3.text())

            if self.radiobuttons.b4.isChecked():
                self.toggleoption = self.radiobuttons.b4.text()
                self.label.mpcEvents(self.radiobuttons.b4.text())

            if self.label.image_copy is not None:
                self.label.processImage(self.label.image_copy)

    def upload_csv(self):
        self.csv = True
        self.folder = False
        buttonflag = True
        self.filename = QFileDialog.getOpenFileName(None, 'Open file', os.getcwd(), "csv files (*.csv)")
        if os.path.exists(self.filename[0]):
            print("File uploaded " + self.filename[0])
            self.file = self.filename[0]
            self.label.csvUrls(self.filename[0], buttonflag)

    def upload_video(self):
        self.csv = False
        self.folder = False
        buttonflag = False
        self.filename = QFileDialog.getOpenFileName(None, 'Open file', os.getcwd(), "Video files (*.mp4)")
        if os.path.exists(self.filename[0]):
            self.file = self.filename[0]
            self.label.videoFile(self.file, buttonflag)

    def upload_image(self):
        self.csv = False
        self.folder = False
        buttonflag = False
        self.filename = QFileDialog.getOpenFileName(None, 'Open file', os.getcwd(), "Image Files (*.png *.jpg *.bmp)")
        if os.path.exists(self.filename[0]):
            self.file = self.filename[0]
            self.label.imageFile(self.file, buttonflag)

    def upload_image_folder(self):
        self.csv = False
        self.folder = True
        buttonFlag = True
        directory = QFileDialog.getExistingDirectory(self, 'Select image folder')
        self.filename = directory
        self.label.imageFolder(directory, buttonFlag)

    def startCalibration(self):
        self.transformed_width = int(self.rectangle.rectangleWidthEdit.text())
        self.transformed_height = int(self.rectangle.rectangleHeightEdit.text())
        self.refPt = self.label.refpt

        if len(self.refPt) < 4:
            msg = QtWidgets.QMessageBox.information(self, "Mark points",
                                                    "Mark 4 points and then press the calibrate button")
        else:
            self.pts1 = self.order_points(np.array(self.refPt, dtype=np.float32))
            print(f"First set of points: {self.pts1}")
            top_left = np.array((500, 500))
            pts2 = np.float32([top_left + [0, 0],
                               top_left + [self.transformed_width, 0],
                               top_left + [self.transformed_width, self.transformed_height],
                               top_left + [0, self.transformed_height]])

            self.M = cv.getPerspectiveTransform(self.pts1, pts2)
            print(self.M)

            self.plot1()

    def order_points(self, pts):
        xSorted = pts[np.argsort(pts[:, 0]), :]
        leftMost = xSorted[:2, :]
        rightMost = xSorted[2:, :]
        leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        (tl, bl) = leftMost
        D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
        (br, tr) = rightMost[np.argsort(D)[::-1], :]
        return np.array([tl, tr, br, bl], dtype="float32")

    def saveToCSV(self):
        try:

            if self.csv:
                df = pd.read_csv(self.filename[0], index_col=False)
                if "Line_Pt1" not in df.columns:
                    df["Line_Pt1"] = ""
                if "Line_Pt2" not in df.columns:
                    df["Line_Pt2"] = ""
                if "dir_src" not in df.columns:
                    df["dir_src"] = ""
                if "dir_dest" not in df.columns:
                    df["dir_dest"] = ""
                if "roi" not in df.columns:
                    df["roi"] = ""
                if "Rectangle Height" not in df.columns:
                    df["Rectangle Height"] = ""
                if "Rectangle Width" not in df.columns:
                    df["Rectangle Width"] = ""
                if "Matrix" not in df.columns:
                    df["Matrix"] = ""
                if "Calibrated points" not in df.columns:
                    df["Calibrated points"] = ""
                if "refPt" not in df.columns:
                    df["refPt"] = ""
                rowindex = df.index[self.label.index]
                self.inputInCSV(df, rowindex, self.filename[0])


            elif not self.csv:

                if not os.path.exists('Camera_Calibration_details.csv'):
                    with open('Camera_Calibration_details.csv', 'a+', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(
                            ["Camera_Name", "FileName", "Line_Pt1", "Line_Pt2", "dir_src", "dir_dest", "roi",
                             "Calibrated points", "Rectangle Width",
                             "Rectangle Height",
                             "Matrix", "refPt"])

                    file.close()

                if self.folder:
                    for file, image_array in self.label.folder_dict.items():
                        if np.array_equal(image_array, self.label.image_array):
                            self.file = file
                df = pd.read_csv('Camera_Calibration_details.csv', index_col=False)
                if not self.existingRowCheck(df):
                    self.inputFileUploadInCSV(df)
            print("Written in csv")
        except:
            pass

    def existingRowCheck(self, df):

        exists = df.isin([Path(self.file).stem]).any().any()

        if exists:
            index = df.FileName[df.FileName == Path(self.file).stem].index.tolist()[0]
            self.inputInCSV(df, index, 'Camera_Calibration_details.csv')

        return exists

    def inputFileUploadInCSV(self, df):
        i = 0
        with open('Camera_Calibration_details.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0]:
                    i = i + 1

                else:
                    break
        csvfile.close()
        df.loc[i, "Camera_Name"] = "Camera" + str(i)
        df.loc[i, "FileName"] = Path(self.file).stem
        self.inputInCSV(df, i, 'Camera_Calibration_details.csv')

        csvfile.close()
        self.figure.clf()

    def plot1(self):
        self.figure.clf()
        frame = self.label.static_image.copy()
        for pt in self.refPt:
            cv.circle(frame, (int(pt[0]), int(pt[1])), 8, (200, 0, 0), -1)
        ax1 = self.figure.add_subplot(121)
        ax1.set_title('Input')
        ax1.imshow(frame[..., ::-1])
        dst = cv.warpPerspective(frame, self.M, (frame.shape[1] * 2, frame.shape[0] * 2))
        ax2 = self.figure.add_subplot(122)
        ax2.set_title('Output')
        ax2.imshow(dst[..., ::-1])
        # t = time.localtime()
        # timestamp = time.strftime('%b-%d-%Y_%H%M', t)
        # self.figure.savefig("Matplots" + " " + timestamp + ".png")
        self.canvas.draw_idle()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def inputInCSV(self, df, index, filename):
        if self.toggleoption == 'Homography':
            df.loc[index, "Calibrated points"] = str(self.pts1.astype(int))
            df.loc[index, "Rectangle Width"] = self.transformed_width
            df.loc[index, "Rectangle Height"] = self.transformed_height
            df.loc[index, "Matrix"] = str(self.M.astype(int))
            df.loc[index, "refPt"] = str(self.label.refpt)

        elif self.toggleoption == 'MPC - Line crossing':
            df.loc[index, "Line_Pt1"] = str(int(self.label.linepts[0].x())) + ", " + str(
                int(self.label.linepts[0].y()))
            df.loc[index, "Line_Pt2"] = str(int(self.label.linepts[1].x())) + ", " + str(int(self.label.linepts[1].y())
                                                                                        )

        elif self.toggleoption == 'MPC - RoI':
            df.loc[index, "roi"] = str(int(self.x1)) + ",  " + str(int(self.y1)
                                                                               ) + ",  " + str(
                int(self.x2)) + ", " + str(int(self.y2)
                                                             )

        elif self.toggleoption == 'MPC - Direction of entry':
            df.loc[index, "dir_src"] = int(self.label.src)
            df.loc[index, "dir_dest"] = int(self.label.dest)

        df.to_csv(filename, index=False)


app = QtWidgets.QApplication(sys.argv)
app.aboutToQuit.connect(app.deleteLater)
GUI = HomographyCalibration()
GUI.show()
sys.exit(app.exec_())
