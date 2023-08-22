#pragma once

#include <QColor>
#include <QGraphicsPixmapItem>
#include <QGraphicsScene>
#include <QImage>
#include <QPixmap>

namespace arnoldserver {
    namespace gui {

        class QtAov {
            private:
                QGraphicsPixmapItem *pixmapItem;
                QImage data;
                
            public:
                std::string name;
                int dataType;

                QtAov(QGraphicsScene*, std::string, int, int, int);
                ~QtAov();

                bool redraw;

                void setPixelColor(int, int, QColor);
                void draw();
        };

    }
}
