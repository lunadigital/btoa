#include "QtAovBuffer.h"

namespace arnoldserver {
    namespace gui {

        QtAovBuffer::QtAovBuffer()
        {

        }

        QtAovBuffer::~QtAovBuffer()
        {

        }

        QtAov* QtAovBuffer::add(QGraphicsScene *scene, std::string name, int dataType)
        {
            data.push_back(QtAov(scene, name, width, height, dataType));
            return &data.back();
        }

        QtAov* QtAovBuffer::findAovByIndex(int index)
        {
            if (index < data.size()) return &data[index];
            return nullptr;
        }

        QtAov* QtAovBuffer::findAovByName(std::string name)
        {
            for (QtAovVectorIter iter = data.begin(); iter < data.end(); iter++)
            {
                if (iter->name == name) return &(*iter);
            }

            return nullptr;
        }

        int QtAovBuffer::getAovIndex(std::string name)
        {
            for (QtAovVectorIter iter = data.begin(); iter < data.end(); iter++)
            {
                if (iter->name == name) return iter - data.begin();
            }

            return -1;
        }

        void QtAovBuffer::setResolution(int t_width, int t_height)
        {
            width = t_width;
            height = t_height;
        }

    }
}