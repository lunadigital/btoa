#include <ai.h>
#include <vector>
#include "renderdata.h"
 
AI_DRIVER_NODE_EXPORT_METHODS(DriverDisplayCallbackMtd)
 
typedef void (*DisplayCallback)(btoa::AtRenderData* buffer);

node_parameters
{
   AiParameterPtr("callback", NULL);
}
 
node_initialize
{
   AiDriverInitialize(node, true);
}

node_update
{}

driver_supports_pixel_type
{
   return pixel_type == AI_TYPE_FLOAT ||
          pixel_type == AI_TYPE_RGB ||
          pixel_type == AI_TYPE_RGBA ||
          pixel_type == AI_TYPE_VECTOR;
}
 
driver_extension
{
   return NULL;
}

driver_open
{}

driver_needs_bucket
{
   return true;
}

driver_prepare_bucket
{}

driver_write_bucket
{
   btoa::AtRenderData* buffer = (btoa::AtRenderData*) AiMalloc(sizeof(btoa::AtRenderData));
   btoa::AiRenderDataInitialize(
      buffer,
      bucket_xo,
      bucket_yo,
      bucket_size_x,
      bucket_size_y
      );

   AtString name;
   int pixel_type;
   const void* bucket_data;

   while(AiOutputIteratorGetNext(iterator, &name, &pixel_type, &bucket_data))
   {
      // Add new AOV to buffer
      int channels = 1;
      if (pixel_type == AI_TYPE_RGB || pixel_type == AI_TYPE_VECTOR)
         channels = 3;
      else if (pixel_type == AI_TYPE_RGBA)
         channels = 4;

      auto aov = btoa::AiRenderDataAddAOV(buffer, name, channels);

      // Process color data
      for (int y = 0; y < bucket_size_y; y++)
      {
         for (int x = 0; x < bucket_size_x; x++)
         {
            int idx = y * bucket_size_x + x;
            int flipped_idx = (bucket_size_y - y - 1) * bucket_size_x + x;
            float* target = &aov->data[idx * aov->channels];

            switch (pixel_type)
            {
               case AI_TYPE_FLOAT:
               {
                  target[0] = ((float*)bucket_data)[flipped_idx];
                  break;
               }
               case AI_TYPE_RGB:
               {
                  AtRGB rgb_data = ((AtRGB*)bucket_data)[flipped_idx];
                  target[0] = rgb_data.r;
                  target[1] = rgb_data.g;
                  target[2] = rgb_data.b;
                  break;
               }
               case AI_TYPE_RGBA:
               {
                  AtRGBA rgba_data = ((AtRGBA*)bucket_data)[flipped_idx];
                  target[0] = rgba_data.r;
                  target[1] = rgba_data.g;
                  target[2] = rgba_data.b;
                  target[3] = rgba_data.a;
                  break;
               }
               case AI_TYPE_VECTOR:
               {
                  AtVector vector_data = ((AtVector*)bucket_data)[flipped_idx];
                  target[0] = vector_data.x;
                  target[1] = vector_data.y;
                  target[2] = vector_data.z;
                  break;
               }
            }
         }
      }
   }

   DisplayCallback cb = (DisplayCallback) AiNodeGetPtr(node, AtString("callback"));
   if (cb) (*cb)(buffer);
}
 
driver_process_bucket
{}

driver_close
{}

node_finish
{}
 
node_loader
{
   if (i > 0)
      return false;
 
   node->methods      = DriverDisplayCallbackMtd;
   node->name         = "btoa_display_driver";
   node->node_type    = AI_NODE_DRIVER;
   strcpy(node->version, AI_VERSION);
   return true;
}