#!/usr/bin/env python3

import sys

import numpy as np

from spwc import sscweb

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
)


class Line(Qt3DCore.QEntity):
    def __init__(self,
                 points: np.array,
                 color: QColor, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print(points, points.shape, points.dtype, len(points.tobytes()))

        self._geo = Qt3DRender.QGeometry(self)

        # position vertices (start and end)
        self.buffer = Qt3DRender.QBuffer(self._geo)
        self.buffer.setData(points.tobytes())

        print(self.buffer.data().size())

        self.positionAttribute = Qt3DRender.QAttribute(self._geo)
        self.positionAttribute.setName(Qt3DRender.QAttribute.defaultPositionAttributeName())
        self.positionAttribute.setVertexBaseType(Qt3DRender.QAttribute.Double)
        self.positionAttribute.setVertexSize(3)
        self.positionAttribute.setAttributeType(Qt3DRender.QAttribute.VertexAttribute)
        self.positionAttribute.setBuffer(self.buffer)
        self.positionAttribute.setByteStride(points.shape[1] * 8)  # sizeof(float)
        self.positionAttribute.setCount(points.shape[0])
        self._geo.addAttribute(self.positionAttribute)  # We add the vertices in the geometry

        # connectivity between vertices
        self.indices = np.arange(0, points.shape[0], dtype=np.uint32).tobytes()

        self.indexBuffer = Qt3DRender.QBuffer(self._geo)
        self.indexBuffer.setData(self.indices)

        self.indexAttribute = Qt3DRender.QAttribute(self._geo)
        self.indexAttribute.setVertexBaseType(Qt3DRender.QAttribute.UnsignedInt)
        self.indexAttribute.setAttributeType(Qt3DRender.QAttribute.IndexAttribute)
        self.indexAttribute.setBuffer(self.indexBuffer)
        self.indexAttribute.setCount(points.shape[0])
        self._geo.addAttribute(self.indexAttribute)  # We add the indices linking the points in the geometry

        # mesh
        self.line = Qt3DRender.QGeometryRenderer(self)
        self.line.setGeometry(self._geo)
        self.line.setPrimitiveType(Qt3DRender.QGeometryRenderer.LineStrip)

        self.material = Qt3DExtras.QPhongMaterial(self)
        self.material.setAmbient(color)

        self.addComponent(self.line)
        self.addComponent(self.material)


class OrbitTransformController(QObject):
    def __init__(self, turn_vector: QVector3D, pos: QVector3D, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._radius = 1.0
        self._angle = 0
        self._target = None
        self._matrix = QMatrix4x4()
        self._turn = turn_vector
        self._pos = pos

    def setTarget(self, target: Qt3DCore.QTransform):
        if self._target != target:
            self._target = target
            self.targetChanged.emit()

    def target(self):
        return self._target

    def setRadius(self, radius: float):
        if not qFuzzyCompare(radius, self._radius):
            self._radius = radius
            self._updateMatrix()
            self.radiusChanged.emit()

    def radius(self):
        return self._radius

    def setAngle(self, angle: float):
        if not qFuzzyCompare(angle, self._angle):
            self._angle = angle
            self._updateMatrix()
            self.angleChanged.emit()

    def angle(self):
        return self._angle

    def _updateMatrix(self):
        self._matrix.setToIdentity()
        self._matrix.rotate(self._angle, self._turn)
        self._matrix.translate(self._radius + self._pos.x(), self._pos.y(), self._pos.z())
        self._target.setMatrix(self._matrix)

    target = Property(Qt3DCore.QTransform, target, setTarget)
    radius = Property(float, radius, setRadius)
    angle = Property(float, angle, setAngle)

    targetChanged = Signal()
    radiusChanged = Signal()
    angleChanged = Signal()


class SphereEntity(Qt3DCore.QEntity):
    def __init__(self, root, turn, pos, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sphereEntity = Qt3DCore.QEntity(root)
        self.sphereMesh = Qt3DExtras.QSphereMesh()
        self.sphereMesh.setRadius(1)
        self.sphereMesh.setGenerateTangents(True)

        self.sphereTransform = Qt3DCore.QTransform()
        self.controller = OrbitTransformController(turn, pos, self.sphereTransform)
        self.controller.setTarget(self.sphereTransform)
        self.controller.setRadius(100.0)

        # self.sphereRotateTransformAnimation = QPropertyAnimation(self.sphereTransform)
        # self.sphereRotateTransformAnimation.setTargetObject(self.controller)
        # self.sphereRotateTransformAnimation.setPropertyName(b"angle")
        # self.sphereRotateTransformAnimation.setStartValue(0)
        # self.sphereRotateTransformAnimation.setEndValue(360)
        # self.sphereRotateTransformAnimation.setDuration(10000)
        # self.sphereRotateTransformAnimation.setLoopCount(-1)
        # self.sphereRotateTransformAnimation.start()

        self.sphereEntity.addComponent(self.sphereMesh)
        self.sphereEntity.addComponent(self.sphereTransform)

        self.material = Qt3DExtras.QPhongMaterial(root)
        self.sphereEntity.addComponent(self.material)


class Sphere(Qt3DCore.QEntity):
    def __init__(self, root, pos, rad, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sphereEntity = Qt3DCore.QEntity(root)
        self.sphereMesh = Qt3DExtras.QSphereMesh()
        self.sphereMesh.setRadius(rad)
        self.sphereMesh.setGenerateTangents(True)

        self.sphereTransform = Qt3DCore.QTransform()
        self.sphereTransform.setTranslation(pos)

        self.sphereEntity.addComponent(self.sphereMesh)
        self.sphereEntity.addComponent(self.sphereTransform)

        self.material = Qt3DExtras.QPhongMaterial(root)
        self.sphereEntity.addComponent(self.material)


class Scene(Qt3DCore.QEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.material = Qt3DExtras.QPhongMaterial(self)

        # self.torusEntity = Qt3DCore.QEntity(self)
        # self.torusMesh = Qt3DExtras.QTorusMesh()
        # self.torusMesh.setRadius(5)
        # self.torusMesh.setMinorRadius(1)
        # self.torusMesh.setRings(100)
        # self.torusMesh.setSlices(20)

        # self.torusTransform = Qt3DCore.QTransform()
        # self.torusTransform.setScale3D(QVector3D(1.5, 1, 0.5))
        # self.torusTransform.setTranslation(QVector3D(0, 0, 0))  # position
        # self.torusTransform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 45.0))

        # self.torusEntity.addComponent(self.torusMesh)
        # self.torusEntity.addComponent(self.torusTransform)
        # self.torusEntity.addComponent(self.material)

        # self.cuboid = Qt3DExtras.QCuboidMesh()
        # # CuboidMesh Transform
        # self.cuboidTransform = Qt3DCore.QTransform()
        # self.cuboidTransform.setScale(10.0)
        # self.cuboidTransform.setTranslation(QVector3D(5.0, -4.0, 0.0))

        # self.cuboidMaterial = Qt3DExtras.QPhongAlphaMaterial()
        # self.cuboidMaterial.setDiffuse(QColor.fromRgb(120, 20, 20))
        # self.cuboidMaterial.setAlpha(0.5)

        # self.cuboidEntity = Qt3DCore.QEntity(self)
        # self.cuboidEntity.addComponent(self.cuboid)
        # self.cuboidEntity.addComponent(self.cuboidMaterial)
        # self.cuboidEntity.addComponent(self.cuboidTransform)

        # self.sphere = []
        # count = 100
        # for i in range(count):
        #    self.sphere.append(SphereEntity(self, QVector3D(i, i, i), QVector3D(0, 100 * i / count, 0)))

        points = np.array([[0, -1000, 0],
                           [0, 1000, 0],
                           [1000, 1000, 1000],
                           [1000, 1000, 2000]
                           ], dtype=np.float)

        ssc = sscweb.SscWeb()
        sv = ssc.get_orbit(product="mms1",
                           start_time="2020-10-10",
                           stop_time="2020-10-24",
                           coordinate_system='gse')

        points = sv.data[::50, 0:3] / 10000

        self.line = Line(points, QColor.fromRgb(0, 255, 0), self)

        #self.spheres = []
        #for p in points:
        #    # print(p, p[0])
        #    self.spheres.append(Sphere(self, QVector3D(p[0], p[1], p[2]), 0.1))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    view = Qt3DExtras.Qt3DWindow()

    scene = Scene()

    # Camera
    camera = view.camera()
    camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
    camera.setPosition(QVector3D(0, 0, 100.0))
    camera.setViewCenter(QVector3D(0, 0, 0))

    # For camera controls
    camController = Qt3DExtras.QOrbitCameraController(scene)
    camController.setLinearSpeed(50.0)
    camController.setLookSpeed(180.0)
    camController.setCamera(camera)

    view.setRootEntity(scene)
    view.show()

    sys.exit(app.exec_())
