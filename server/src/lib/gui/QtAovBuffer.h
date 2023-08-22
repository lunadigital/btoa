#pragma once

#include "QtAov.h"

#include <string>
#include <vector>

namespace arnoldserver {
    namespace gui {

        class QtAovBuffer {
            private:
                typedef std::vector<QtAov> QtAovVector;
                typedef std::vector<QtAov>::iterator QtAovVectorIter;
                QtAovVector data;
            
            public:
                int width;
                int height;

                QtAovBuffer();
                ~QtAovBuffer();

                QtAov* add(QGraphicsScene*, std::string, int);

                QtAov* findAovByIndex(int);
                QtAov* findAovByName(std::string);
                int getAovIndex(std::string);                

                void setResolution(int, int);
        };

    }
}