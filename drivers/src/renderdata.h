#ifndef BTOA_BUFFER
#define BTOA_BUFFER

namespace btoa {
    struct AtAOV
    {
        const char* name;
        int channels;
        float* data;
    };

    struct AtRenderData
    {
        int x;       // x position
        int y;       // y position
        int width;   // bucket width
        int height;  // bucket height
        int size;    // total size of AOVs for memory management (width * height * channels)
        int count;   // total number of buckets
        AtAOV* aovs; // array of aov data for this bucket
    };

    void AiRenderDataInitialize(AtRenderData*, int, int, int, int);
    AtAOV* AiRenderDataAddAOV(AtRenderData*, AtString, int);
}

#endif