#include <ai.h>
#include "renderdata.h"

namespace btoa {
    void AiRenderDataInitialize(AtRenderData* buffer, int x, int y, int width, int height)
    {
        buffer->x = x;
        buffer->y = y;
        buffer->width = width;
        buffer->height = height;

        buffer->count = 0;
        buffer->size = 0;
        
        buffer->aovs = (AtAOV*) AiMalloc(buffer->size * sizeof(AtAOV));
    }

    AtAOV* AiRenderDataAddAOV(AtRenderData* buffer, AtString name, int channels)
    {
        int aov_size = buffer->width * buffer->height * channels;

        buffer->count++;
        buffer->size += aov_size;

        buffer->aovs = (AtAOV*) AiRealloc(buffer->aovs, buffer->size * sizeof(AtAOV));
    
        auto aov = &buffer->aovs[buffer->count - 1];
        aov->name = name.c_str();
        aov->channels = channels;
        aov->data = (float*) AiMalloc(aov_size * sizeof(float));

        return aov;
    }
}