#include "AtAov.h"

namespace arnoldserver {
namespace rndr {

    AtAov::AtAov()
    {
        
    }

    AtAov::AtAov(std::string t_name, int t_width, int t_height, int t_dtype) :
        name(AtString(t_name.c_str())),
        width(t_width),
        height(t_height),
        dtype(t_dtype)
    {
        size = width * height;

        switch(dtype)
        {
            case AI_TYPE_RGB:
                size *= 3;
                break;
            case AI_TYPE_RGBA:
                size *= 4;
                break;
        }

        redraw = false;
    }

    AtAov::~AtAov()
    {
        if (data) AiFree(data);
    }

    void AtAov::initBuffer()
    {
        data = (float*)AiMalloc(size * sizeof(float));
        std::fill_n(data, size, 0.0f);
    }
}
}