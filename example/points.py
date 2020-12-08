#!/usr/bin/env python3

import sys

import struct

import numpy as np

from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DRender import Qt3DRender

from PySide2.QtWidgets import (
    QApplication,
)

from PySide2.QtGui import (
    QVector3D,
    QQuaternion,
    QMatrix4x4,
    QColor,
)

from PySide2.QtCore import (
    QObject,
    Property,
    Signal,

    QPropertyAnimation,
    QByteArray,

    qFuzzyCompare,
    QSize
)


class PointGeometry(Qt3DRender.QGeometry):
    def __init__(self, position: QVector3D, *args, **kwargs):
        super().__init__(*args, **kwargs)

        vertexBuffer = Qt3DRender.QBuffer(self)
        indexBuffer = Qt3DRender.QBuffer(self)
        self.positionAttribute = Qt3DRender.QAttribute(self)
        self.indexAttribute = Qt3DRender.QAttribute(self)

        self.positionAttribute.setName(Qt3DRender.QAttribute.defaultPositionAttributeName())
        self.positionAttribute.setVertexBaseType(Qt3DRender.QAttribute.Float)
        self.positionAttribute.setVertexSize(3)
        self.positionAttribute.setAttributeType(Qt3DRender.QAttribute.VertexAttribute)
        self.positionAttribute.setBuffer(vertexBuffer)
        self.positionAttribute.setByteStride(3 * 4)
        self.positionAttribute.setCount(1)

        self.indexAttribute.setName(Qt3DRender.QAttribute.defaultJointIndicesAttributeName())
        self.indexAttribute.setAttributeType(Qt3DRender.QAttribute.IndexAttribute)
        self.indexAttribute.setVertexBaseType(Qt3DRender.QAttribute.UnsignedShort)
        self.indexAttribute.setBuffer(indexBuffer)
        self.indexAttribute.setCount(1)

        data = PointGeometry.createPointVertexData(position)

        vertexBuffer.setData(data)

        print([hex(c) for c in data])

        index = PointGeometry.createPointIndexData()
        indexBuffer.setData(index)
        print([hex(c) for c in index])

        self.addAttribute(self.positionAttribute)
        self.addAttribute(self.indexAttribute)

    def createPointVertexData(position: QVector3D):
        return struct.pack('3f', position.x(), position.y(), position.z())

        # data = np.array((), dtype=np.single)
        # assert len(data.tobytes()) == 12
        # print([hex(c) for c in data.tobytes()])
        # return data.tobytes()

    def createPointIndexData():
        return struct.pack('H', 0)

        # data = np.array([0], dtype=np.uint16)
        # assert len(data.tobytes()) == 2
        # print(data)
        # return data.tobytes()


class Point(Qt3DRender.QGeometryRenderer):
    def __init__(self, position: QVector3D, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._geometry = PointGeometry(position)

        # self._geometry = Qt3DExtras.QSphereGeometry()
        # self._geometry.setRadius(0.3)

        self.setPrimitiveType(Qt3DRender.QGeometryRenderer.Points)
        self.setGeometry(self._geometry)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    view = Qt3DExtras.Qt3DWindow()
    view.setTitle("3D PySide2")
    view.defaultFrameGraph().setClearColor(QColor(210, 210, 220))

    # scene = Scene()
    root = Qt3DCore.QEntity()

    e = []

    for i in range(10):
        point = Qt3DCore.QEntity(root)
        pointMesh = Point(QVector3D(0, i, 0))
        pointTransform = Qt3DCore.QTransform()
        pointTransform.setTranslation(QVector3D(0, i, 0))
        pointMaterial = Qt3DExtras.QPhongMaterial()
        pointMaterial.setDiffuse(QColor(255, 0, 0))

        for t in pointMaterial.effect().techniques():
            for rp in t.renderPasses():
                pointSize = Qt3DRender.QPointSize()
                pointSize.setSizeMode(Qt3DRender.QPointSize.SizeMode.Fixed)
                pointSize.setValue(4.0)
                rp.addRenderState(pointSize)
                e += [pointSize]

        point.addComponent(pointMesh)
        point.addComponent(pointTransform)
        point.addComponent(pointMaterial)
        e += [point, pointMesh, pointTransform, pointMaterial]

    for i in range(2):
        plane = Qt3DCore.QEntity(root)
        planeMesh = Qt3DExtras.QPlaneMesh()
        planeTransform = Qt3DCore.QTransform()
        planeMaterial = Qt3DExtras.QPhongMaterial()
        planeMesh.setWidth(10)
        planeMesh.setHeight(10)
        planeTransform.setTranslation(QVector3D(0, i, 0))
        planeMaterial.setDiffuse(QColor(150, 150, 150))

        plane.addComponent(planeMesh)
        plane.addComponent(planeTransform)
        plane.addComponent(planeMaterial)
        e += [plane, planeMesh, planeTransform, planeMaterial]

    # Camera
    camera = view.camera()
    camera.lens().setPerspectiveProjection(65.0, 16.0 / 9.0, 0.1, 100.0)
    camera.setPosition(QVector3D(0, 2, -20.0))
    camera.setViewCenter(QVector3D(0, 0, 0))

    camController = Qt3DExtras.QOrbitCameraController(root)
    camController.setCamera(camera)

    view.setRootEntity(root)
    view.show()

    sys.exit(app.exec_())
