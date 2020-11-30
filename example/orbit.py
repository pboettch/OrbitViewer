#!/usr/bin/env python3

# from broni.shapes.primitives import Cuboid
# from broni.shapes.callback import SphericalBoundary, Sheath
# import broni
#
# from astropy.units import km
# from astropy.constants import R_earth
#
# import datetime
# import matplotlib.pyplot as plt
#
# import numpy as np
#
# from space.models.planetary import formisano1979, mp_formisano1979, bs_formisano1979

import sys

from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QPushButton, QLabel
from PySide2.QtCore import Qt, Slot

from PySide2.QtDataVisualization import QtDataVisualization

from PySide2 import QtGui
from PySide2.QtCharts import QtCharts
from PySide2.QtGui import QPainter

from PySide2.QtDataVisualization import QtDataVisualization

from random import randint


if __name__ == '__main__':
    app = QApplication([])
#    window = QWidget()
#    layout = QVBoxLayout()

    # Initialize chart
#    chart = QtCharts.QChart()

#    lineSeries = QtCharts.QLineSeries()

    bars = QtDataVisualization.Q3DBars()
    bars.setFlags(bars.flags() ^ Qt.FramelessWindowHint)

    bars.rowAxis().setRange(0, 4)
    bars.columnAxis().setRange(0, 4)

    # Make some random data points
    # dataSeries = [(i+1, randint(0, 99999)) for i in range(200)]

    series = QtDataVisualization.QBar3DSeries()
    d = [QtDataVisualization.QBarDataItem(v) for v in [1.0, 7.5, 5.0, 2.2]]

    print(series.dataProxy().addRows([d]))

    # series.dataProxy().addRow(d)
    bars.addSeries(series)

    bars.show()

#    layout.addWidget(bars)
#    window.setLayout(layout)

#    window.show()
#    window.resize(1500, 1000)

    sys.exit(app.exec_())

"""

@Slot() # slot decorator
def youClicked():
    label.setText("You clicked the button")

@Slot() #slot decorator
def sliderValue(val):
    label.setText('Slider Value: ' + str(val))


    # coord_sys = "gse"

    # X = np.arange(-200000, 200000, 10).flatten() * km

    app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()  # Define slider widget, note the orientation argument:
    slider = QSlider(Qt.Horizontal)
    slider.valueChanged.connect(sliderValue)

    button = QPushButton("I'm just a Button man")

    label = QLabel('¯\_(ツ)_/¯')
    button.clicked.connect(youClicked)  # clicked signal

    layout.addWidget(label)
    layout.addWidget(button)
    layout.addWidget(slider) # Add the slider
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())

"""
