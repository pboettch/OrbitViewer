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

from typing import List

from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QLineEdit,
    QLabel,

)

from PySide2.QtCore import Signal, Qt, Slot


class _BaseWidget(QWidget):
    updated = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._enabled = QCheckBox("Enabled")
        self._enabled.setCheckState(Qt.CheckState.Checked)
        self._enabled.stateChanged.connect(self._updated)

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._enabled)

        self.setLayout(self._layout)

    @Slot()
    def _updated(self):
        self.updated.emit()

    @property
    def enabled(self):
        return self._enabled.isChecked()

    def _add_labeled_edit(self, value: float, label: str):
        edit = QLineEdit(str(value))
        edit.textChanged.connect(self._updated)

        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel(label))
        hlayout.addWidget(edit)
        self._layout.addLayout(hlayout)

        return edit


class SphereWidget(_BaseWidget):
    def __init__(self, x: float, y: float, z: float, d: float, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._d = self._add_labeled_edit(d, "Diameter")
        self._x = self._add_labeled_edit(x, "X")
        self._y = self._add_labeled_edit(y, "Y")
        self._z = self._add_labeled_edit(z, "Z")


class CuboidWidget(_BaseWidget):
    def _add_labeled_edit_3(self, x, y, z: float, label: str):
        a = QLineEdit(str(x))
        a.textChanged.connect(self._updated)

        b = QLineEdit(str(y))
        b.textChanged.connect(self._updated)

        c = QLineEdit(str(z))
        c.textChanged.connect(self._updated)

        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel(label))
        hlayout.addWidget(a)
        hlayout.addWidget(b)
        hlayout.addWidget(c)
        self._layout.addLayout(hlayout)

        return a, b, c

    def __init__(self, x: float, y: float, z: float, w: float, h: float, d: float, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._x, self._y, self._z = self._add_labeled_edit_3(x, y, z, "P0")

        self._w = self._add_labeled_edit(w, "Width (X)")
        self._h = self._add_labeled_edit(h, "Height (Y)")
        self._d = self._add_labeled_edit(d, "Depth (Z)")


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("My Form")

        # Create layout and add widgets
        layout = QVBoxLayout()
        s = SphereWidget(10, 20, 30, 100)
        s.updated.connect(self.updated)
        layout.addWidget(s)
        s = SphereWidget(100, 120, 130, 200)
        s.updated.connect(self.updated)
        layout.addWidget(s)

        s = CuboidWidget(10, 10, 20, 300, 400, 500)
        s.updated.connect(self.updated)
        layout.addWidget(s)

        # Set dialog layout
        self.setLayout(layout)

    @Slot()
    def updated(self):
        print('something has been updated')


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())

"""

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

    print(series.dataProxy().addRow([d]))

    # series.dataProxy().addRow(d)
    bars.addSeries(series)

    bars.show()

#    layout.addWidget(bars)
#    window.setLayout(layout)

#    window.show()
#    window.resize(1500, 1000)

    sys.exit(app.exec_())

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
