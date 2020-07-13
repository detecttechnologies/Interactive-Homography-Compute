import math
import os
import sys
from pathlib import Path
import matplotlib
import matplotlib.figure
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QFileDialog, QLabel, QLineEdit, QPushButton, QWidget, QAction
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import cv2 as cv
import numpy as np
import pandas as pd
from scipy.spatial import distance as dist
import csv


class HomographyCalibration(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(HomographyCalibration, self).__init__(parent)

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.center()
        self.setWindowTitle('Homography software')
        grid = QtWidgets.QGridLayout()
        grid.spacing()
        self.central_widget = QWidget()

        self.label = MarkCalibrationPoints()
        self.figure = matplotlib.figure.Figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        rectangleWidth = QLabel('Rectangle Width')
        rectangleHeight = QLabel('Rectangle Height')
        rectangleWidth.setAlignment(QtCore.Qt.AlignRight)
        rectangleHeight.setAlignment(QtCore.Qt.AlignRight)
        self.rectangleWidthEdit = QLineEdit()
        self.rectangleHeightEdit = QLineEdit()
        calibrateButton = QPushButton("Calibrate")
        calibrateButton.clicked.connect(self.startCalibration)
        saveButton = QPushButton("Save")
        saveButton.resize(150, 50)
        saveButton.clicked.connect(self.saveMatrix)
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
        grid.addWidget(self.label, 3, 1, 1, 2)
        grid.addWidget(self.canvas, 3, 3, 1, 2)

        grid.addWidget(rectangleWidth, 5, 1, 1, 2)
        grid.addWidget(self.rectangleWidthEdit, 5, 3, 1, 2)
        grid.addWidget(rectangleHeight, 6, 1, 1, 2)
        grid.addWidget(self.rectangleHeightEdit, 6, 3, 1, 2)
        grid.addWidget(calibrateButton, 7, 3, 1, 2)
        grid.addWidget(saveButton, 8, 3)

        self.central_widget.setLayout(grid)
        self.setCentralWidget(self.central_widget)
        self.folder_dict = {}

    def upload_csv(self):                                                                                        //Allows you to upload a csv file with a list of url's
        self.csv = True
        self.folder = False
        buttonflag = True
        self.filename = QFileDialog.getOpenFileName(None, 'Open file', os.getcwd(), "csv files (*.csv)")
        print("File uploaded " + self.filename[0])
        self.file = self.filename[0]
        self.label.csvUrls(self.filename[0], buttonflag)

    def upload_video(self):                                                                                     //Allows the user to upload the video file
        self.csv = False
        self.folder = False
        buttonflag = False
        self.filename = QFileDialog.getOpenFileName(None, 'Open file', os.getcwd(), "Video files (*.mp4)")
        self.file = self.filename[0]
        self.label.videoFile(self.file, buttonflag)

    def upload_image(self):                                                                                    //Allows the user to upload an image
        self.csv = False
        self.folder = False
        buttonflag = False
        self.filename = QFileDialog.getOpenFileName(None, 'Open file', os.getcwd(), "Image Files (*.png *.jpg *.bmp)")
        self.file = self.filename[0]
        self.label.imageFile(self.file, buttonflag)

    def upload_image_folder(self):                                                                            //Allows the user to upload an image folder with the bunch of images
        self.csv = False
        self.folder = True
        buttonFlag = True
        directory = QFileDialog.getExistingDirectory(self, 'Select image folder')
        images = []
        for filename in os.listdir(directory):
            img = cv.imread(os.path.join(directory, filename))
            if img is not None:
                self.folder_dict[os.path.join(directory, filename)] = img
                images.append(cv.imread(os.path.join(directory, filename)))
        self.label.imageFolder(images, buttonFlag)

    def startCalibration(self):                                                                            //Calls the image and allows you to mark 4 points. Height and width of the rectangle is to be specified in the ui
        print("In calibration")
        self.transformed_width = int(self.rectangleWidthEdit.text())
        self.transformed_height = int(self.rectangleHeightEdit.text())
        print(self.transformed_height)
        print(self.transformed_width)
        self.refPt = self.label.refpt
        if len(self.refPt) < 4:
            msg = QtWidgets.QMessageBox.information(self, "Mark points",
                                                    "Mark 4 points and then press the calibrate button")
        else:
            self.pts1 = np.array(self.refPt, dtype=np.float32)
            self.pts1 = self.order_points(self.pts1)
            print(f"First set of points: {self.pts1}")
            top_left = np.array((500, 500))
            pts2 = np.float32([top_left + [0, 0],
                               top_left + [self.transformed_width, 0],
                               top_left + [self.transformed_width, self.transformed_height],
                               top_left + [0, self.transformed_height]])

            self.M = cv.getPerspectiveTransform(self.pts1, pts2)
            print(self.M)

            self.plot1()

    def order_points(self, pts):                                                                          //Sorts the 4 points in the clockwise fashion
        xSorted = pts[np.argsort(pts[:, 0]), :]
        leftMost = xSorted[:2, :]
        rightMost = xSorted[2:, :]
        leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        (tl, bl) = leftMost
        D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
        (br, tr) = rightMost[np.argsort(D)[::-1], :]
        return np.array([tl, tr, br, bl], dtype="float32")

    def saveMatrix(self):                                                                                //File written in csv
        if self.csv:
            self.df = pd.read_csv(self.filename[0], index_col=[0])
            if "Rectangle Height" not in self.df.columns:
                self.df["Rectangle Height"] = ""
            if "Rectangle Width" not in self.df.columns:
                self.df["Rectangle Width"] = ""
            if "Matrix" not in self.df.columns:
                self.df["Matrix"] = ""
            if "Marked points" not in self.df.columns:
                self.df["Marked Points"] = ""
            self.rownumber = self.label.index
            self.rowindex = self.df.index[self.rownumber]
            self.df.loc[self.rowindex, "Rectangle Height"] = self.transformed_height
            self.df.loc[self.rowindex, "Rectangle Width"] = self.transformed_width
            self.df.loc[self.rowindex, "Matrix"] = self.M.tostring()
            self.df.loc[self.rowindex, "Marked Points"] = self.pts1.tostring()
            self.df.to_csv(self.filename[0])

            print("File saved")
        elif self.csv == False:
            print("Saving'''''''''''''")
            if not os.path.exists('Camera_Calibration_details.csv'):
                with open('Camera_Calibration_details.csv', 'a+', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        ["Camera_Name", "FileName", "Calibrated points", "Rectangle Width", "Rectangle Height",
                         "Matrix"])

                file.close()

            if self.folder:
                for file, image_array in self.folder_dict.items():
                    if np.array_equal(image_array, self.label.image_array):
                        self.file = file
            if not self.existingRowCheck():
                self.writeCSV()

    def existingRowCheck(self):                     

        df = pd.read_csv('Camera_Calibration_details.csv', index_col=[0])
        exists = df.isin([Path(self.file).stem]).any().any()
        if exists:
            index = df.FileName[df.FileName == Path(self.file).stem].index.tolist()[0]
            df.loc[index, "Calibrated points"] = self.pts1.tostring()
            df.loc[index, "Rectangle Width"] = self.transformed_width
            df.loc[index, "Rectangle Height"] = self.transformed_height
            df.loc[index, "Matrix"] = self.M.tostring()
            df.to_csv('Camera_Calibration_details.csv')
        return exists

    def writeCSV(self):
        i = 0
        with open('Camera_Calibration_details.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                print(row)
                if row[0]:
                    i = i + 1

                else:
                    break
        CameraName = "Camera" + str(i)

        with open('Camera_Calibration_details.csv', 'a+', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [CameraName, Path(self.file).stem, self.pts1.tostring(), self.transformed_width,
                 self.transformed_height,
                 self.M.tostring()])
            csvfile.close()

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
        self.canvas.draw_idle()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class MarkCalibrationPoints(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MarkCalibrationPoints, self).__init__(parent)
        self.csvFlag = False
        self.imageFlag = False
        self.rtsp_urls = []
        self._zoom = 0
        lay = QtWidgets.QHBoxLayout(self)
        self.arrowLeftButton = QtWidgets.QToolButton()
        self.arrowLeftButton.setArrowType(Qt.LeftArrow)
        self.arrowLeftButton.clicked.connect(self.previousImage)
        self.gv = QtWidgets.QGraphicsView()
        self.arrowRightButton = QtWidgets.QToolButton()
        self.arrowRightButton.setArrowType(Qt.RightArrow)
        self.arrowRightButton.clicked.connect(self.nextImage)
        lay.addWidget(self.arrowLeftButton)
        lay.addWidget(self.gv)
        lay.addWidget(self.arrowRightButton)

    def imageFile(self, filename, flag):
        image = cv.imread(filename)
        self.arrowLeftButton.setEnabled(flag)
        self.arrowRightButton.setEnabled(flag)
        self.cvToQImage(image)

    def imageFolder(self, imageList, flag):
        self.csvFlag = False
        self.imageFlag = True
        self.arrowLeftButton.setEnabled(flag)
        self.arrowRightButton.setEnabled(flag)
        self.index = 0
        self.imageList = imageList
        self.image_array = self.imageList[self.index]
        self.cvToQImage(self.image_array)

    def csvUrls(self, filename, flag):
        self.index = 0
        self.csvFlag = True
        self.imageFlag = False
        self.arrowLeftButton.setEnabled(flag)
        self.arrowRightButton.setEnabled(flag)
        df = pd.read_csv(filename, index_col=[0])
        self.rtsp_urls = df["IP_address"].to_list()                                                                 //change your column name from IP_address to your respective column that has the video urls
        for url in self.rtsp_urls:
            cap = cv.VideoCapture(url)
            ret, image = cap.read()
            if not ret:
                self.rtsp_urls.remove(url)

        self.csvVideo(self.rtsp_urls[self.index])

    def csvVideo(self, url):
        cap = cv.VideoCapture(url)
        ret, image = cap.read()
        self.cvToQImage(image)

    def videoFile(self, filename, flag):
        self.arrowLeftButton.setEnabled(flag)
        self.arrowRightButton.setEnabled(flag)
        cap = cv.VideoCapture(filename)
        ret, image = cap.read()
        self.cvToQImage(image)

    def cvToQImage(self, static_image):
        try:
            print("Converting image..")
            self.static_image = static_image.copy()

            cv.putText(self.static_image, text="Start from top left point, go clockwise", org=(10, 50),
                       fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 125, 0), thickness=2)
            image = QtGui.QImage(self.static_image, self.static_image.shape[1], \
                                 self.static_image.shape[0], self.static_image.shape[1] * 3, QtGui.QImage.Format_RGB888)
            image = image.rgbSwapped()
            self.processImage(image)
        except:
            pass

    def processImage(self, image):                                                        
        self.refpt = []
        self.item_dict = {}
        self.image = QtGui.QPixmap.fromImage(image).scaled(
            image.width(),
            image.height(),
            aspectRatioMode=Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation,
        )
        self.scene = QtWidgets.QGraphicsScene(0, 0, image.width(), image.height())
        self.scene.addPixmap(self.image)
        self.gv.setScene(self.scene)
        self.gv.installEventFilter(self)
        self.items = []

    def eventFilter(self, obj, event):
        d = []
        distance_dict = {}
        if obj == self.gv and event.type() == QtCore.QEvent.MouseButtonPress:                                                //Mouse Left click to mark a point on the image
            if event.button() == QtCore.Qt.LeftButton:
                if len(self.refpt) < 4:
                    p = self.gv.mapToScene(event.pos())
                    self.refpt.append([p.__pos__().x(), p.__pos__().y()])
                    self.draw(p)
                else:
                    msg = QtWidgets.QMessageBox.information(self, "4 points allowed",
                                                            "Your allowed to mark only 4 points on the image")
            elif event.button() == QtCore.Qt.RightButton:                                                                   //Mouse Right click to remove the closes marked point
                p = self.gv.mapToScene(event.pos())
                if len(self.refpt) != 0:
                    for i in self.refpt:
                        distance = math.sqrt((p.__pos__().x() - i[0]) ** 2 + (p.__pos__().y() - i[1]) ** 2)
                        d.append(distance)
                        distance_dict[distance] = i
                    minimum_ditance = min(d)
                    if len(self.refpt) != 0:
                        self.refpt.remove(distance_dict.get(minimum_ditance))
                    self.undo(distance_dict.get(minimum_ditance))

        return QtWidgets.QWidget.eventFilter(self, obj, event)

    def draw(self, p): 
        it = QtWidgets.QGraphicsEllipseItem(0, 0, 10, 10)
        it.setPen(QtGui.QPen(QtCore.Qt.blue, 3, QtCore.Qt.SolidLine))
        it.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
        self.scene.addItem(it)
        it.setPos(p)
        self.items.append(it)
        self.item_dict[it] = [p.__pos__().x(), p.__pos__().y()]

    def undo(self, delete_item):
        for key, value in self.item_dict.items():
            if delete_item == value:
                it = key
                self.scene.removeItem(it)
                del it
                print("Item deleted......")
                break

    def wheelEvent(self, event):                                                                                        //Mouse wheel event to oom in and out the image
        if event.angleDelta().y() > 0:
            factor = 1.05
            self._zoom += 1
        else:
            factor = 0.95
            self._zoom -= 1

        if self._zoom > 0:

            self.gv.scale(factor, factor)
        else:
            self._zoom = 0


    def previousImage(self):

        if self.csvFlag and self.index > 0:
            self.index = self.index - 1
            self.csvVideo(self.rtsp_urls[self.index])
            print(self.index)
        elif self.imageFlag and self.index > 0:
            self.index = self.index - 1
            self.image_array = self.imageList[self.index]
            self.cvToQImage(self.image_array)

    def nextImage(self):
        if self.csvFlag and self.index < len(self.rtsp_urls) - 1:
            self.index = self.index + 1
            self.csvVideo(self.rtsp_urls[self.index])

        elif self.imageFlag and self.index < len(self.imageList):
            self.index = self.index + 1
            self.image_array = self.imageList[self.index]
            self.cvToQImage(self.image_array)



app = QtWidgets.QApplication(sys.argv)
app.aboutToQuit.connect(app.deleteLater)
GUI = HomographyCalibration()
GUI.show()
sys.exit(app.exec_())
