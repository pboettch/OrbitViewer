// ============================
// Point.h
// ============================

#include <Qt3DRender/QBuffer>
#include <Qt3DRender/QGeometryRenderer>
#include <QVector3D>
#include <QtCore/QSize>

class Point : public Qt3DRender::QGeometryRenderer {
Q_OBJECT
public:
    explicit Point(Qt3DCore::QNode *parent = nullptr);
    ~Point();
public slots:
    void setPosition(QVector3D position);
};

class PointGeometry : public Qt3DRender::QGeometry {
Q_OBJECT
public:
    explicit PointGeometry(QNode *parent = nullptr);
    ~PointGeometry();


    QVector3D position;

    void init();
    void updateVertices();
    void updateIndices();

	Qt3DRender::QBuffer * vertexBuffer;
    Qt3DRender::QBuffer * indexBuffer;
    Qt3DRender::QAttribute * positionAttribute;
    Qt3DRender::QAttribute * indexAttribute;

public slots:
    void setPosition(QVector3D position) ;

};

