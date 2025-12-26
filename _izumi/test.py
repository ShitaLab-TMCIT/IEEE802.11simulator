import sys
import math
import typing
import os
import glob
import shutil
import time
import re

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

import test2



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

        painter.setPen(pen:=QPen(Qt.GlobalColor.black, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        offsetX = self.size().width() / 2
        offsetY = self.size().height() / 2

        factor = offsetX / self.radius

        painter.drawPoint(QPointF(offsetX,offsetY))

        pen.setColor(QColor(255, 0, 0))
        painter.setPen(pen)
        painter.drawPoint(QPointF(offsetX+self.pointT[0]*factor, offsetY+self.pointT[1]*-factor))
        pen.setColor(QColor(0, 0, 255))
        painter.setPen(pen)
        painter.drawPoint(QPointF(offsetX+self.pointN[0]*factor, offsetY+self.pointN[1]*-factor))


class Vector2Widget(QWidget):
    valueChanged = pyqtSignal(float,float)

    def __init__(self, value: typing.Tuple[float, float]):
        super().__init__()

        layout = QHBoxLayout(self)

        self.labelX = QLabel(f"X:")
        self.labelX.setFixedWidth(50)
        self.inputX = QDoubleSpinBox()
        self.inputX.setRange(-100.0, 100.0)
        self.inputX.setValue(value[0])
        layout.addWidget(self.labelX)
        layout.addWidget(self.inputX)

        self.labelY = QLabel(f"Y:")
        self.labelY.setFixedWidth(50)
        self.inputY = QDoubleSpinBox()
        self.inputY.setRange(-100.0, 100.0)
        self.inputY.setValue(value[1])
        layout.addWidget(self.labelY)
        layout.addWidget(self.inputY)

        self.inputX.valueChanged.connect(self.value_changed)
        self.inputY.valueChanged.connect(self.value_changed)

    def value_changed(self):
        self.valueChanged.emit(self.inputX.value(), self.inputY.value())


    def value(self) -> typing.Tuple[float, float]:
        return (self.inputX.value(), self.inputY.value())


class SettingWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")

        layout = QVBoxLayout(self)

        self.PointLabel = QLabel("Point T:")
        self.PointField = Vector2Widget((0, 0))
        self.PointField.valueChanged.connect(self.calculate)

        self.NoiseLabel = QLabel("Point N:")
        self.NoiseField = Vector2Widget((0, 0))
        self.NoiseField.valueChanged.connect(self.calculate)

        layout.addWidget(self.PointLabel)
        layout.addWidget(self.PointField)
        layout.addWidget(self.NoiseLabel)
        layout.addWidget(self.NoiseField)

        self.RateCombo = QComboBox()
        self.RateCombo.addItems(["6", "9", "12", "18", "24", "36", "48", "54"])
        self.RateCombo.currentIndexChanged.connect(self.calculate)
        layout.addWidget(self.RateCombo)

        self.CulcButton = QPushButton("Calculate")
        self.CulcButton.clicked.connect(self.calculate)
        layout.addWidget(self.CulcButton)

        self.LogText = QTextEdit()
        self.LogText.setReadOnly(True)
        self.LogText.setFont(QFont("Courier New", 10))
        layout.addWidget(self.LogText)


        self.calculate()  # Initial calculation


    def calculate(self):
        P0 = self.PointField.value()
        P1 = self.NoiseField.value()

        P0d = math.sqrt((P0[0]**2 + (P0[1]**2)))
        if P0d == 0:
            self.LogText.setHtml("Distance is zero, cannot calculate received power.")
            return

        P1d = math.sqrt((P1[0]**2 + (P1[1]**2)))
        if P1d == 0:
            self.LogText.setHtml("Distance is zero, cannot calculate received power.")
            return

        d = math.sqrt((P0[0]-P1[0])**2 + (P0[1]-P1[1])**2)
        if d == 0:
            self.LogText.setHtml("Distance to noise point is zero, cannot calculate noise power.")
            return


        Pr0 = test2.calc_Pr(P0d)

        Pr1 = test2.calc_Pr(P1d)

        Pr = test2.calc_Pr(d)

        SNR = test2.calc_SNR(Pr0, Pr)
        NSR = test2.calc_SNR(Pr1, Pr)

        result1 = test2.check_SNR(SNR, int(self.RateCombo.currentText()))
        result2 = test2.check_SNR(NSR, int(self.RateCombo.currentText()))

        color1 = "#00ff00" if result1 else "red"
        color2 = "#00ff00" if result2 else "red"
        self.LogText.setHtml(f"Pr&nbsp;&nbsp;&nbsp;: {Pr0} W<br>Noise: {Pr1} W<br>SNR&nbsp;&nbsp;: {SNR} dB<br><br><span style='color: {color1};'>{result1}</span><br><br>SNR&nbsp;&nbsp;: {NSR} dB<br><span style='color: {color2};'>{result2}</span>")












class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.Layout = QHBoxLayout(self)

        self.mapView = MapViewr()
        self.Layout.addWidget(self.mapView)

        self.Setting = SettingWidget()
        self.Layout.addWidget(self.Setting)

        self.Setting.PointField.valueChanged.connect(self.setMap)
        self.Setting.NoiseField.valueChanged.connect(self.setMap)

        self.mapView.update()

    def setMap(self):
        self.mapView.pointT = self.Setting.PointField.value()
        self.mapView.pointN = self.Setting.NoiseField.value()
        self.mapView.update()









if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
