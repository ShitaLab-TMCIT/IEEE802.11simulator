import sys
import math
import typing
import os
import glob
import shutil
import time

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *



class MapViewr(QWidget):

    pointT : typing.Tuple[float, float] = (0.0, 0.0)
    pointN : typing.Tuple[float, float] = (0.0, 0.0)

    radius : int = 20

    def __init__(self):
        super().__init__()

        self.setFixedSize(400,400)



    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor(255, 255, 255))

        painter.setPen(QPen(Qt.GlobalColor.black, 4))

        offsetX = self.size().width() / 2
        offsetY = self.size().height() / 2

        factor = offsetX / self.radius

        painter.drawPoint(QPointF(offsetX,offsetY))
        painter.drawPoint(QPointF(offsetX+self.pointT[0]*factor, offsetY+self.pointT[1]*factor))
        painter.drawPoint(QPointF(offsetX+self.pointN[0]*factor, offsetY+self.pointN[1]*factor))





class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.Layout = QHBoxLayout(self)

        self.mapView = MapViewr()
        self.Layout.addWidget(self.mapView)

        self.mapView.pointT = (-10.0, 1.0)
        self.mapView.pointN = (15.0, 2.0)









if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
