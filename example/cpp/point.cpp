// ============================
// Point.cpp
// ============================
#include "point.h"
#include <Qt3DRender/QAttribute>
#include <Qt3DRender/QBuffer>
#include <Qt3DRender/QBufferDataGenerator>
#include <Qt3DRender/QPointSize>
#include <limits>

using namespace Qt3DRender;

Point::Point(QNode *parent)
    : QGeometryRenderer(parent)
{
	PointGeometry *geometry = new PointGeometry(this);
	// tell OpenGL to expect a point primtiive
	// https://www.khronos.org/opengl/wiki/Primitive#Point_primitives
	setPrimitiveType(PrimitiveType::Points);
	QGeometryRenderer::setGeometry(geometry);
}

Point::~Point() {}

void Point::setPosition(QVector3D position)
{
	static_cast<PointGeometry *>(geometry())->setPosition(position);
}

// set up a vertex buffer with our single vec3 position
QByteArray createPointVertexData(QVector3D position)
{
	const int nVerts = 1;
	const quint32 stride = 3 * sizeof(float);
	// create  a new buffer
	QByteArray bufferBytes;
	// set buffer size to number of vertices
	// we're only drawing one point, so we only have one
	// vec3 representing the position of our point
	bufferBytes.resize(stride * nVerts);

	// tell c++ to interpret this buffer as float so
	// we can use the next few lines to fill it
	float *fptr = reinterpret_cast<float *>(bufferBytes.data());

	*fptr++ = position.x();
	*fptr++ = position.y();
	*fptr++ = position.z();

	return bufferBytes;
}

// set up an index buffer telling OpenGL
// to render our single point
QByteArray createPointIndexData()
{
	QByteArray indexBytes;

	indexBytes.resize(1 * sizeof(quint16));
	quint16 *indexPtr = reinterpret_cast<quint16 *>(indexBytes.data());

	*indexPtr++ = 0;

	return indexBytes;
}

// this functor is responsible for updating the vertex buffer
// it is set as our data generator below
class PointVertexBufferFunctor : public QBufferDataGenerator
{
public:
	explicit PointVertexBufferFunctor(QVector3D position)
	    : position(position) {}

	~PointVertexBufferFunctor() {}

	QByteArray operator()() Q_DECL_FINAL
	{
		return createPointVertexData(position);
	}

	bool operator==(const QBufferDataGenerator &other) const Q_DECL_FINAL
	{
		const PointVertexBufferFunctor *otherFunctor = functor_cast<PointVertexBufferFunctor>(&other);
		if (otherFunctor != nullptr)
			return (otherFunctor->position == position);
		return false;
	}

	QT3D_FUNCTOR(PointVertexBufferFunctor)

private:
	QVector3D position;
};

// this functor is responsible for updating the index buffer
// it is set as our data generator below
class PointIndexBufferFunctor : public QBufferDataGenerator
{
public:
	explicit PointIndexBufferFunctor() {}
	~PointIndexBufferFunctor() {}

	QByteArray operator()() Q_DECL_FINAL
	{
		return createPointIndexData();
	}

	bool operator==(const QBufferDataGenerator &other) const Q_DECL_FINAL
	{
		const PointIndexBufferFunctor *otherFunctor = functor_cast<PointIndexBufferFunctor>(&other);
		if (otherFunctor != nullptr)
			return (true);
		return false;
	}

	QT3D_FUNCTOR(PointIndexBufferFunctor)

private:
	QSize resolution;
};

PointGeometry::PointGeometry(PointGeometry::QNode *parent)
    : QGeometry(parent)
{
	this->init();
}

PointGeometry::~PointGeometry() {}

void PointGeometry::setPosition(QVector3D position)
{
	this->position = position;
	updateVertices();
}

void PointGeometry::updateVertices()
{
	positionAttribute->setCount(3);
	vertexBuffer->setDataGenerator(QSharedPointer<PointVertexBufferFunctor>::create(position));
}

void PointGeometry::updateIndices()
{
	indexAttribute->setCount(1);
	indexBuffer->setDataGenerator(QSharedPointer<PointIndexBufferFunctor>::create());
}

void PointGeometry::init()
{
	positionAttribute = new QAttribute();
	indexAttribute = new QAttribute();
	vertexBuffer = new Qt3DRender::QBuffer();
	indexBuffer = new Qt3DRender::QBuffer();

	const int nVerts = 3;
	const int stride = 0; // since the vertices are "side by side" in the buffer

	// this ultimately ends up configuring the OpenGL vertex array object
	// https://www.khronos.org/opengl/wiki/Vertex_Specification
	// this tells Qt3D / OpenGL to read the data from the buffer,
	// passing the 3 floats into the gl_Position parameter
	// on our shader (in this case the Qt3D default shader)
	positionAttribute->setName(QAttribute::defaultPositionAttributeName());
	positionAttribute->setVertexBaseType(QAttribute::Float);
	positionAttribute->setVertexSize(3);
	positionAttribute->setAttributeType(QAttribute::VertexAttribute);
	positionAttribute->setBuffer(vertexBuffer);
	positionAttribute->setByteStride(stride);
	positionAttribute->setCount(nVerts);

	indexAttribute->setAttributeType(QAttribute::IndexAttribute);
	indexAttribute->setVertexBaseType(QAttribute::UnsignedShort);
	indexAttribute->setBuffer(indexBuffer);

	// Each primitive has 3 vertives
	indexAttribute->setCount(1);

	vertexBuffer->setDataGenerator(QSharedPointer<PointVertexBufferFunctor>::create(position));
	indexBuffer->setDataGenerator(QSharedPointer<PointIndexBufferFunctor>::create());

	addAttribute(positionAttribute);
	addAttribute(indexAttribute);
}

