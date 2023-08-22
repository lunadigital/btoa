#pragma once

#include <ai.h>

#include <string>

namespace arnoldserver {
namespace rndr {

    struct AtAov {
        AtString name;
        int dtype;
        int width;
        int height;
        int size;
        bool redraw;
        float *data;

        AtAov();
        AtAov(std::string, int, int, int);
        ~AtAov();

        void initBuffer();
    };

}
}