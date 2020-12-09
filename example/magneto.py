#!/usr/bin/env python3

import sys

from typing import Callable

import struct

from space.models.planetary import formisano1979, mp_formisano1979, bs_formisano1979

import numpy as np

from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DRender import Qt3DRender

from PySide2.QtWidgets import (
    QApplication,
)

from PySide2.QtGui import (
    QVector3D,
    QColor,
)

from PySide2.QtCore import (
    QSize,
    QUrl,
    QRectF,
)

def _createVertexData(theta: float, phi: float, model: Callable, resolution: QSize):
    assert resolution.width() > 1
    assert resolution.height() > 1

    vert_count = resolution.width() * resolution.height()

    # Populate a buffer with the interleaved per-vertex data with
    # vec3 pos, vec2 texCoord, vec3 normal, vec4 tangent
    element_size = 3 + 2 + 3 + 4

    stride = element_size * 4  # sizeof(float)
    th_1d = np.linspace(0, theta, resolution.width())
    ph_1d = np.linspace(0, phi, resolution.height())
    th, ph = np.meshgrid(th_1d, ph_1d, indexing='ij')


    x, y, z = model(th.flatten(), ph.flatten())

    data = np.empty((element_size, vert_count), dtype=np.single)

    data[0] = x
    data[1] = y
    data[2] = z

    # texture coordinates
    data[3] = np.resize(np.linspace(0.0, 1.0, resolution.width()),
                        resolution.width() * resolution.height())

    #if mirrored:
    nv = np.linspace(1.0, 0.0, resolution.height())
    #else:
    #    nv = np.linspace(0.0, 1.0, resolution.height())
    data[4] = np.repeat(nv, resolution.width())

    # normal https://stackoverflow.com/questions/29661574/normalize-numpy-array-columns-in-pytho
    data[5:8] = data[0:3] / np.abs(data[0:3]).max(axis=0)
#
    # tangent
    data[8] = 1.0
    data[9] = 0.0
    data[10] = 0.0
    data[11] = 1.0

    bytes = data.T.tobytes()

    assert len(data.flatten()) == (vert_count * element_size)
    assert len(data.tobytes()) == (vert_count * stride)
    return bytes


def _createPlaneIndexData(resolution: QSize):
    # Create the index data. 2 triangles per rectangular face
    faces = 2 * (resolution.width() - 1) * (resolution.height() - 1)
    indices = 3 * faces

    data = []
    for j in range(resolution.height() - 1):
        rowStartIndex = j * resolution.width()
        nextRowStartIndex = (j + 1) * resolution.width()

        for i in range(resolution.width() - 1):  # Iterate over x

            # Split quad into two triangles
            data.append(rowStartIndex + i)
            data.append(nextRowStartIndex + i)
            data.append(rowStartIndex + i + 1)

            data.append(nextRowStartIndex + i)
            data.append(nextRowStartIndex + i + 1)
            data.append(rowStartIndex + i + 1)

    bytes = np.array(data, dtype=np.int16).tobytes()

    assert len(data) == indices
    assert len(bytes) == (indices * 2)

    return bytes


class ModelGeometry(Qt3DRender.QGeometry):
    def __init__(self, theta: float, phi: float, model: Callable, resolution: QSize, *args, **kwargs):
        super().__init__(*args, **kwargs)

        positionAttribute = Qt3DRender.QAttribute(self)
        normalAttribute = Qt3DRender.QAttribute(self)
        texCoordAttribute = Qt3DRender.QAttribute(self)
        tangentAttribute = Qt3DRender.QAttribute(self)
        indexAttribute = Qt3DRender.QAttribute(self)

        vertexBuffer = Qt3DRender.QBuffer(self)
        indexBuffer = Qt3DRender.QBuffer(self)

        nVerts = resolution.width() * resolution.height()
        stride = (3 + 2 + 3 + 4) * 4  # sizeof(float);
        faces = 2 * (resolution.width() - 1) * (resolution.height() - 1)

        positionAttribute.setName(Qt3DRender.QAttribute.defaultPositionAttributeName())
        positionAttribute.setVertexBaseType(Qt3DRender.QAttribute.Float)
        positionAttribute.setVertexSize(3)
        positionAttribute.setAttributeType(Qt3DRender.QAttribute.VertexAttribute)
        positionAttribute.setBuffer(vertexBuffer)
        positionAttribute.setByteStride(stride)
        positionAttribute.setCount(nVerts)

        texCoordAttribute.setName(Qt3DRender.QAttribute.defaultTextureCoordinateAttributeName())
        texCoordAttribute.setVertexBaseType(Qt3DRender.QAttribute.Float)
        texCoordAttribute.setVertexSize(2)
        texCoordAttribute.setAttributeType(Qt3DRender.QAttribute.VertexAttribute)
        texCoordAttribute.setBuffer(vertexBuffer)
        texCoordAttribute.setByteStride(stride)
        texCoordAttribute.setByteOffset(3 * 4)
        texCoordAttribute.setCount(nVerts)

        normalAttribute.setName(Qt3DRender.QAttribute.defaultNormalAttributeName())
        normalAttribute.setVertexBaseType(Qt3DRender.QAttribute.Float)
        normalAttribute.setVertexSize(3)
        normalAttribute.setAttributeType(Qt3DRender.QAttribute.VertexAttribute)
        normalAttribute.setBuffer(vertexBuffer)
        normalAttribute.setByteStride(stride)
        normalAttribute.setByteOffset(0 * 4)
        normalAttribute.setCount(nVerts)

        tangentAttribute.setName(Qt3DRender.QAttribute.defaultTangentAttributeName())
        tangentAttribute.setVertexBaseType(Qt3DRender.QAttribute.Float)
        tangentAttribute.setVertexSize(4)
        tangentAttribute.setAttributeType(Qt3DRender.QAttribute.VertexAttribute)
        tangentAttribute.setBuffer(vertexBuffer)
        tangentAttribute.setByteStride(stride)
        tangentAttribute.setByteOffset(8 * 4)
        tangentAttribute.setCount(nVerts)

        indexAttribute.setAttributeType(Qt3DRender.QAttribute.IndexAttribute)
        indexAttribute.setVertexBaseType(Qt3DRender.QAttribute.UnsignedShort)
        indexAttribute.setBuffer(indexBuffer)
        indexAttribute.setCount(faces * 3)  # Each primitive has 3 vertices

        vertexBuffer.setData(_createVertexData(theta, phi, model, resolution))
        indexBuffer.setData(_createPlaneIndexData(resolution))

        self.addAttribute(positionAttribute)
        self.addAttribute(texCoordAttribute)
        self.addAttribute(normalAttribute)
        # self.addAttribute(tangentAttribute)
        self.addAttribute(indexAttribute)


class ModelRenderer(Qt3DRender.QGeometryRenderer):
    def __init__(self, theta: float, phi: float, model: Callable, resolution: QSize,
                 points=False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        geometry = ModelGeometry(theta, phi, model, resolution, self)
        #geometry = Qt3DExtras.QSphereGeometry(self)
        #geometry.setRadius(10)

        #self.setPrimitiveType(Qt3DRender.QGeometryRenderer.Points)
        if points:
            self.setPrimitiveType(Qt3DRender.QGeometryRenderer.LineStrip)
        self.setGeometry(geometry)

class NoCullQt3DWindow(Qt3DExtras.Qt3DWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.surfaceSelector = Qt3DRender.QRenderSurfaceSelector()
        self.surfaceSelector.setSurface(self)

        viewport = Qt3DRender.QViewport(self.surfaceSelector)
        viewport.setNormalizedRect(QRectF(0, 0, 1.0, 1.0))

        cameraSelector = Qt3DRender.QCameraSelector(viewport)
        cameraSelector.setCamera(self.camera())

        clearBuffers = Qt3DRender.QClearBuffers(cameraSelector)
        clearBuffers.setBuffers(Qt3DRender.QClearBuffers.ColorDepthBuffer)
        clearBuffers.setClearColor('white')

        renderStateSet = Qt3DRender.QRenderStateSet(clearBuffers)
        cullFace = Qt3DRender.QCullFace(renderStateSet)
        cullFace.setMode(Qt3DRender.QCullFace.NoCulling)
        renderStateSet.addRenderState(cullFace)

        depthTest = Qt3DRender.QDepthTest()
        depthTest.setDepthFunction(Qt3DRender.QDepthTest.Less)
        renderStateSet.addRenderState(depthTest)

        self.setActiveFrameGraph(self.surfaceSelector)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    view = Qt3DExtras.Qt3DWindow()
    # view = NoCullQt3DWindow()
    view.setTitle("3D PySide2")
    view.defaultFrameGraph().setClearColor(QColor(210, 210, 220))

    view.activeFrameGraph()

    # scene = Scene()
    root = Qt3DCore.QEntity()

    ms = Qt3DCore.QEntity(root)
    msr = ModelRenderer(np.pi * 0.75, 2 * np.pi, mp_formisano1979, QSize(10, 10), False, ms)
    ms.addComponent(msr)

    bs = Qt3DCore.QEntity(root)
    bsr = ModelRenderer(np.pi * 0.75, 2 * np.pi, bs_formisano1979, QSize(10, 10), True, bs)
    bs.addComponent(bsr)

    # planeTransform = Qt3DCore.QTransform(ms)
    # planeTransform.setTranslation(QVector3D(0, i, 0))

    # and glue some texture onto our sphere
    # loader = Qt3DRender.QTextureLoader(ms)
    # loader.setSource(QUrl.fromLocalFile('/home/pmp/devel/upstream/qt3d/examples/qt3d/planets-qml/images/solarsystemscope/earthmap2k.jpg'))
    # planeMaterial = Qt3DExtras.QTextureMaterial(ms)
    # planeMaterial.setTexture(loader)

    color = [ QColor.fromRgb(100, 20, 0, 150),
              QColor.fromRgb(20, 100, 0, 150) ]
    i = 0
    for e in [ms, bs]:
        material = Qt3DExtras.QPhongAlphaMaterial(e)
        e.addComponent(material)

        for t in material.effect().techniques():
            for rp in t.renderPasses():
                pointSize = Qt3DRender.QPointSize(e)
                pointSize.setSizeMode(Qt3DRender.QPointSize.SizeMode.Fixed)
                pointSize.setValue(5.0)
                rp.addRenderState(pointSize)

        material.setDiffuse(color[i])
        i += 1

    # plane.addComponent(planeTransform)

    # Camera
    camera = view.camera()
    camera.lens().setPerspectiveProjection(65.0, 16.0 / 9.0, 0.1, 200.0)
    camera.setPosition(QVector3D(0, 50, 50.0))
    camera.setViewCenter(QVector3D(0, 0, 0))

    camController = Qt3DExtras.QOrbitCameraController(root)
    camController.setCamera(camera)

    light_entity = Qt3DCore.QEntity(camera)
    light = Qt3DRender.QPointLight(light_entity)
    light.setColor("white")
    light.setIntensity(1)
    light_entity.addComponent(light)

    view.setRootEntity(root)
    view.show()

    sys.exit(app.exec_())
