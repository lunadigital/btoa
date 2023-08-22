#include "AtRenderData.h"

namespace arnoldserver {
namespace rndr {

    AtRenderData::AtRenderData() : size(0)
    {

    }

    AtRenderData::~AtRenderData()
    {
        if (aovs) AiFree(aovs);
    }

    AtAov* AtRenderData::add(std::string t_name, int t_width, int t_height, int t_dtype)
    {
        size++;

        if (!aovs)
            aovs = (AtAov*)AiMalloc(sizeof(AtAov));
        else
            aovs = (AtAov*)AiRealloc(aovs, size * sizeof(AtAov));

        int aovSize = t_width * t_height;

        switch(t_dtype)
        {
            case AI_TYPE_RGB:
                aovSize *= 3;
                break;
            case AI_TYPE_RGBA:
                aovSize *= 4;
                break;
        }

        new (aovs + size -1) AtAov(t_name, t_width, t_height, t_dtype);
        aovs[size-1].initBuffer();
    
        return &aovs[size-1];
    }

    AtAov* AtRenderData::findAovByIndex(int index)
    {
        return &aovs[index];
    }

    AtAov* AtRenderData::findAovByName(std::string name)
    {
        for (int i = 0; i < size; i++)
        {
            if (aovs[i].name.c_str() == name) return &aovs[i];
        }

        return nullptr;
    }

    int AtRenderData::getAovIndex(std::string name)
    {
        for (int i = 0; i < size; i++)
        {
            if (aovs[i].name.c_str() == name) return i;
        }

        return -1; // TODO: Think about switching this out with a custom constant, like NULL_INDEX
    }

}
}