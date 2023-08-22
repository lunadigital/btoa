#include "QtAov.h"

namespace arnoldserver {
    namespace gui {

        QtAov::QtAov(QGraphicsScene *scene, std::string t_name, int width, int height, int dtype) :
            name(t_name),
            data(QImage(width, height, QImage::Format_RGBA64)),
            dataType(dtype),
            redraw(false)
        {
            data.fill(Qt::black);

            pixmapItem = new QGraphicsPixmapItem();
            scene->addItem(pixmapItem);
        }

        QtAov::~QtAov()
        {

        }

        void QtAov::setPixelColor(int x, int y, QColor color)
        {
            data.setPixelColor(x, y, color);
        }

        void QtAov::draw()
        {
            pixmapItem->setPixmap(QPixmap::fromImage(data));
            redraw = false;
        }
        
    } 
}
