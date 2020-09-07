import ast
import math
import os
from pathlib import Path

import PyQt5
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2 as cv
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class MarkFigures(QtWidgets.QWidget):
    def __init__(self, parent=None):
        self.mpc = "Social Distancing"

        self.csvFlag = False
        self.imageFlag = False
        self.rtsp_urls = []
        self._zoom = 0
        self.url_dict = {}
        self.filename = ''
        self.image_copy = None


        super(MarkFigures, self).__init__(parent)

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
        self.filename = filename
        image = cv.imread(filename)
        self.arrowLeftButton.setEnabled(flag)
        self.arrowRightButton.setEnabled(flag)
        self.cvToQImage(image)

    def imageFolder(self, directory, flag):
        self.folder_dict = {}
        self.csvFlag = False
        self.imageFlag = True
        self.index = 0
        self.images = []
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                img = cv.imread(os.path.join(directory, filename))
                if img is not None:
                    self.folder_dict[os.path.join(directory, filename)] = img
                    self.images.append(cv.imread(os.path.join(directory, filename)))

        self.arrowLeftButton.setEnabled(flag)
        self.arrowRightButton.setEnabled(flag)
        self.image_array = self.images[self.index]
        self.cvToQImage(self.image_array)

    def csvUrls(self, filename, flag):
        self.index = 0
        self.csvFlag = True
        self.imageFlag = False
        self.arrowLeftButton.setEnabled(flag)
        self.arrowRightButton.setEnabled(flag)
        self.filename = filename
        df = pd.read_csv(self.filename)
        self.rtsp_urls = df["IP_address"].to_list()

        for url in self.rtsp_urls:
            cap = cv.VideoCapture(url)
            ret, image = cap.read()
            if not ret:
                self.rtsp_urls.remove(url)
        for urls in self.rtsp_urls:
            cap = cv.VideoCapture(urls)
            ret, image = cap.read()
            self.url_dict[urls] = image

        self.csvVideo(self.rtsp_urls[self.index])

    def csvVideo(self, url):
        self.cvToQImage(self.url_dict[url])

    def videoFile(self, filename, flag):
        self.filename = filename
        self.arrowLeftButton.setEnabled(flag)
        self.arrowRightButton.setEnabled(flag)
        cap = cv.VideoCapture(filename)
        ret, image = cap.read()
        self.cvToQImage(image)

    def mpcEvents(self, mpcevent):
        self.mpc = mpcevent

    def cvToQImage(self, static_image):

            self.static_image = static_image.copy()

            cv.putText(self.static_image, text="Start from top left point, go clockwise", org=(10, 50),
                       fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 125, 0), thickness=2)
            image = QtGui.QImage(self.static_image, self.static_image.shape[1],
                                 self.static_image.shape[0], self.static_image.shape[1] * 3, QtGui.QImage.Format_RGB888)
            image = image.rgbSwapped()
            self.image_copy = image.copy()

            self.processImage(image)

    def processImage(self, image):
       try:

            self.image = QtGui.QPixmap.fromImage(image).scaled(
                image.width(),
                image.height(),
                aspectRatioMode=Qt.KeepAspectRatio,
                transformMode=Qt.SmoothTransformation,
            )

            self.scene = QGraphicsScene()
            self.scene.setSceneRect(0, 0, self.image.width(), self.image.height())
            self.scene.addPixmap(self.image)

            self.gv.setScene(self.scene)

            self.gv.viewport().installEventFilter(self)

            self.refpt = []
            self.item_dict = {}
            self.items = []

            self.linepts = []
            self.clicks = []
            self.arrowClicks = []
            self.src = ''
            self.dest = ''

            self._start = QtCore.QPointF()
            self._current_rect_item = None
            self.final_point = None

            self.rectangleItem = []

            if self.csvFlag:
                df = pd.read_csv(self.filename)
                rowindex = df[df['IP_address'] == self.rtsp_urls[self.index]].index.item()
                self.existingEventIdentification(rowindex, df)

            else:
                if os.path.exists('Camera_Calibration_details.csv'):
                    df = pd.read_csv('Camera_Calibration_details.csv')
                    if self.imageFlag:
                        rowindex = df[
                            df['FileName'] == Path([*self.folder_dict][self.index]).stem].index.item()
                    else:
                        rowindex = df[df['FileName'] == (Path(self.filename).stem)].index.item()

                    self.existingEventIdentification(rowindex, df)
       except:
           pass

    def eventFilter(self, obj, event):
        d = []
        distance_dict = {}
        if obj == self.gv.viewport() and event.type() == QtCore.QEvent.MouseButtonPress and self.mpc == 'Homography':
            if event.button() == QtCore.Qt.LeftButton:
                if len(self.refpt) < 4:
                    p = self.gv.mapToScene(event.pos())
                    self.refpt.append([p.__pos__().x(), p.__pos__().y()])
                    self.draw(p.__pos__().x(), p.__pos__().y())

                else:
                    msg = QtWidgets.QMessageBox.information(self, "4 points allowed",
                                                            "You are allowed to mark only 4 points on the image")
            elif event.button() == QtCore.Qt.RightButton:
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

        elif obj == self.gv.viewport() and event.type() == QtCore.QEvent.MouseButtonPress and self.mpc == "MPC - Line crossing":
            p = self.gv.mapToScene(event.pos())
            self.clicks.append(p.__pos__())
            if len(self.clicks) == 2:
                self.drawLine()


        elif obj == self.gv.viewport() and event.type() == QtCore.QEvent.MouseButtonPress and self.mpc == "MPC - Direction of entry":
            p = self.gv.mapToScene(event.pos())
            self.arrowClicks.append(p.__pos__())
            if len(self.arrowClicks) == 2:
                self.drawArrowedLine(self.arrowClicks[0].x(), self.arrowClicks[1].x(), self.arrowClicks[0].y(),
                                     self.arrowClicks[1].y())

        elif obj == self.gv.viewport() and event.type() == QtCore.QEvent.MouseButtonPress and self.mpc == "MPC - RoI" and len(
                self.rectangleItem) == 0:
            if event.button() == QtCore.Qt.LeftButton:
                self._current_rect_item = QtWidgets.QGraphicsRectItem()
                self._current_rect_item.setPen(QtGui.QPen(QtCore.Qt.blue, 5, QtCore.Qt.SolidLine))
                self._current_rect_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)


                self.scene.addItem(self._current_rect_item)
                self.rectangleItem.append(self._current_rect_item)
                self._start = self.gv.mapToScene(event.pos())
                r = QtCore.QRectF(self._start, self._start)

                self._current_rect_item.setRect(r)

        elif obj == self.gv.viewport() and event.type() == QtCore.QEvent.MouseMove and self.mpc == "MPC - RoI":
            if self._current_rect_item is not None:
                r = QtCore.QRectF(self._start, self.gv.mapToScene(event.pos())).normalized()
                self._current_rect_item.setRect(r)
                self.final_point = self.gv.mapToScene(event.pos())
        elif obj == self.gv.viewport() and event.type() == QtCore.QEvent.MouseButtonRelease and self.mpc == "MPC - RoI":
            self._current_rect_item = None


        

        return QWidget.eventFilter(self, self.gv.viewport(), event)

    def draw(self, x, y):
        it = QtWidgets.QGraphicsEllipseItem(0, 0, 10, 10)
        it.setPen(QtGui.QPen(QtCore.Qt.blue, 4, QtCore.Qt.SolidLine))
        it.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
        self.scene.addItem(it)
        it.setPos(x, y)
        self.items.append(it)
        self.item_dict[it] = [x, y]

    def undo(self, delete_item):
        for key, value in self.item_dict.items():
            if delete_item == value:
                it = key
                self.scene.removeItem(it)
                del it
                break

    def drawLine(self):
        it = QtWidgets.QGraphicsLineItem(self.clicks[0].x(), self.clicks[0].y(), self.clicks[1].x(), self.clicks[1].y())
        it.setPen(QtGui.QPen(QtCore.Qt.blue, 5, QtCore.Qt.SolidLine))
        self.scene.addItem(it)
        self.linepts = self.clicks

    def drawArrowedLine(self, x0, x1, y0, y1):
        self.arrowLineItem(x0, x1, y0, y1, QtCore.Qt.blue)
        self.src, self.dest = self.get_directions([(x0, y0), (x1, y1)])
        self.arrowClicks = []

    def wheelEvent(self, event):
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



    def existingEventIdentification(self, rowindex, df):
      if rowindex >= 0:
        if self.mpc == 'MPC - Line crossing':
            self.drawExistingLine(rowindex, df)

        if self.mpc == 'MPC - RoI':
            self.drawExistingRectangle(rowindex, df)

        if self.mpc == 'MPC - Direction of entry':
            self.drawExistingArrowDirection(rowindex, df)

        elif self.mpc == 'Homography':
            self.existingEllipseItem(rowindex, df)

    def drawExistingLine(self, rowindex, df):
        linepoint1, linepoint2 = (df['Line_Pt1'].loc[rowindex]).split(","), (df['Line_Pt2'].loc[rowindex]).split(",")
        if len(linepoint1) != 0 and len(linepoint2) != 0:
            it = QtWidgets.QGraphicsLineItem(float(linepoint1[0]), float(linepoint1[1]),
                                             float(linepoint2[0]), float(linepoint2[1]))
            it.setPen(QtGui.QPen(QtCore.Qt.green, 5, QtCore.Qt.SolidLine))
            self.scene.addItem(it)

    def drawExistingRectangle(self, rowindex, df):
        roi = (df['roi'].loc[rowindex]).split(",")
        if len(roi) != 0:
            rect_item = QtWidgets.QGraphicsRectItem()
            rect_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
            rect_item.setPen(QtGui.QPen(QtCore.Qt.green, 5, QtCore.Qt.SolidLine))
            self.scene.addItem(rect_item)
            r = QtCore.QRectF(PyQt5.QtCore.QPointF(float(roi[0]), float(roi[1])),
                              PyQt5.QtCore.QPointF(float(roi[2]), float(roi[3])))
            rect_item.setRect(r)

    def drawExistingArrowDirection(self, rowindex, df):
        direction = []
        arrowLinePoints = []
        src = df['dir_src'].loc[rowindex]
        dest = df['dir_dest'].loc[rowindex]
        if src and dest != '':
            direction.append(src)
            direction.append(dest)
        img_size = (int(self.image.width()), int(self.image.height()))

        for i in self.convert_corners_to_coordinates(direction, img_size):
            for j in i:
                arrowLinePoints.append(j)
        x0, y0= (arrowLinePoints[0]+arrowLinePoints[2])/2 , (arrowLinePoints[1]+arrowLinePoints[3])/2
        self.arrowLineItem(x0,arrowLinePoints[2],y0, arrowLinePoints[3], QtCore.Qt.green)


    def existingEllipseItem(self,rowindex, df):
        calibrated_points = df['refPt'].loc[rowindex]
        self.refpt = ast.literal_eval(calibrated_points)
        for i in self.refpt:
            self.draw(i[0], i[1])

    def arrowLineItem(self, x0,x1,y0,y1,color):
        h = math.sqrt((y1 - y0) ** 2 + (x1 - x0) ** 2)
        dir_x, dir_y = x1 - x0, y1 - y0
        q_x, q_y = +dir_y / h, -dir_x / h

        C_x, C_y = x1 - (1 * dir_x) + (300 * q_x / 2.0), y1 - (1 * dir_y) + (300 * q_y / 2.0)

        D_x, D_y = x1 - (1 * dir_x) - (300 * q_x / 2.0), y1 - (1 * dir_y) - (300 * q_y / 2.0)

        division_x_1, division_y_1 = (3 * x1 + 1 * C_x) / 4, (3 * y1 + 1 * C_y) / 4

        division_x_2, division_y_2 = (3 * x1 + 1 * D_x) / 4, (3 * y1 + 1 * D_y) / 4

        it = QtWidgets.QGraphicsLineItem(x0, y0, x1, y1)
        it.setPen(QtGui.QPen(color, 5, QtCore.Qt.SolidLine))
        self.scene.addItem(it)
        it = QtWidgets.QGraphicsLineItem(x1, y1, division_x_1, division_y_1)
        it.setPen(QtGui.QPen(color, 5, QtCore.Qt.SolidLine))
        self.scene.addItem(it)
        it = QtWidgets.QGraphicsLineItem(x1, y1, division_x_2, division_y_2)
        it.setPen(QtGui.QPen(color, 5, QtCore.Qt.SolidLine))
        self.scene.addItem(it)

    def convert_corners_to_coordinates(self, direction, img_size):
        corner_coordinates = []
        for corner_idx in direction:
            if corner_idx == 1:
                corner_coordinates.append((0, 0))
            elif corner_idx == 2:
                corner_coordinates.append((img_size[0], 0))
            elif corner_idx == 3:
                corner_coordinates.append(img_size)
            elif corner_idx == 4:
                corner_coordinates.append((0, img_size[1]))
        return corner_coordinates

    def get_directions(self, points):
        p1, p2 = points
        solns_p1_x, solns_p1_y = set(), set()
        if p1[0] < p2[0]:  # if p1 x is less than p2's x
            if p1[1] > p2[1]:
                return 4, 2
            elif p1[1] < p2[1]:
                return 1, 3
            else:
                return 1, 2  # same as 4,3
        elif p1[0] > p2[0]:
            if p1[1] > p2[1]:
                return 3, 1
            elif p1[1] < p2[1]:
                return 2, 4
            else:
                return 2, 1  # same as 4,3
        else:
            if p1[1] > p2[1]:
                return 4, 1  # same as 2,3
            else:
                return 1, 4

        return dir_src, dir_dst

    def previousImage(self):

        if self.csvFlag and self.index > 0:
            self.index = self.index - 1
            self.csvVideo(self.rtsp_urls[self.index])
            print(self.index)
        elif self.imageFlag and self.index > 0:
            self.index = self.index - 1
            self.image_array = self.images[self.index]
            self.cvToQImage(self.image_array)

    def nextImage(self):
        if self.csvFlag and self.index < len(self.rtsp_urls) - 1:
            self.index = self.index + 1
            self.csvVideo(self.rtsp_urls[self.index])

        elif self.imageFlag and self.index < len(self.images):
            self.index = self.index + 1
            self.image_array = self.images[self.index]
            self.cvToQImage(self.image_array)
