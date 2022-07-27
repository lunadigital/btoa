#include <ai.h>
#include <vector>
 
namespace ASTR {
   static const AtString callback("callback");
};

namespace NODEDATA {
   int total_aovs = 1;
   std::string serialized_aov_names;
}
 
AI_DRIVER_NODE_EXPORT_METHODS(DriverDisplayCallbackMtd)
 
typedef void (*DisplayCallback)(const char* aovs, uint32_t x, uint32_t y, uint32_t width, uint32_t height, float* buffer);

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
   return pixel_type == AI_TYPE_FLOAT || pixel_type == AI_TYPE_RGB || pixel_type == AI_TYPE_RGBA;
}
 
driver_extension
{
   return NULL;
}

driver_open
{
   // Get total AOVs to render
   AtNode* options = AiUniverseGetOptions();
   AtArray* outputs = AiNodeGetArray(options, AtString("outputs"));
   NODEDATA::total_aovs = AiArrayGetNumElements(outputs);

   // Collect AOV names
   AtString name;
   std::vector<std::string> aovs;

   while(AiOutputIteratorGetNext(iterator, &name, NULL, NULL)) {
      aovs.push_back(name.c_str());
   }

   for (const auto &aov : aovs) NODEDATA::serialized_aov_names += aov + "\\";
}

driver_needs_bucket
{
   return true;
}

driver_prepare_bucket
{}

/*
 * I'm going to try to document this as well as possible for future me - or other devs that look at this code.
 *
 * We support multiple AOVs by saving AOV data in a 1D buffer of type float*. For example, a render with 1 AOV would
 * have a buffer 4096 pixels values long (practically, 4096 * 4), a render with 2 AOVs 8192, etc. We send a serialized
 * list of the rendered AOV names to the callback with the buffer, and the callback separates out the AOV data for
 * the bucket by offsetting and slicing the array for each AOV. See the `update_render_result()` function in
 * "engine/__init__.py" for an example of how this is done.
 *
 * There's probably a more elegant way to do this, but I'm much more fluent in Python development than C++. I know even
 * less about ctypes. This was the best way I could figure out to handle it for now, until someone smarter than me can
 * take a second look.
 */
driver_write_bucket
{
   int pixel_type;
   const void* bucket_data;
   int bucket_offset = 0;
   float* buffer = (float*)AiMalloc(bucket_size_x * bucket_size_y * sizeof(float) * 4 * NODEDATA::total_aovs);

   while(AiOutputIteratorGetNext(iterator, NULL, &pixel_type, &bucket_data))
   {
      int offset = bucket_size_x * bucket_size_y * bucket_offset * 4;

      for (int j = 0; (j < bucket_size_y); j++)
      {
         for (int i = 0; (i < bucket_size_x); i++)
         {
            AtRGBA source = AI_RGBA_ZERO;
            int idx = j * bucket_size_x + i;
            int flipped_idx = (bucket_size_y - j - 1) * bucket_size_x + i;

            switch (pixel_type)
            {
               case AI_TYPE_FLOAT:
               {
                  float f = ((float*)bucket_data)[flipped_idx];
                  source = AtRGBA(f, f, f, 1.0f);
                  break;
               }
               case AI_TYPE_RGB:
               {
                  AtRGB rgb = ((AtRGB*)bucket_data)[flipped_idx];
                  source = AtRGBA(rgb, 1.0f);
                  break;
               }
               case AI_TYPE_RGBA:
               {
                  source = ((AtRGBA*)bucket_data)[flipped_idx];
                  break;
               }
            }

            float* target = &buffer[idx * 4 + offset];
            target[0] = source.r;
            target[1] = source.g;
            target[2] = source.b;
            target[3] = source.a;
         }
      }

      bucket_offset++;
   }

   DisplayCallback cb = (DisplayCallback) AiNodeGetPtr(node, ASTR::callback);
   if (cb)
   {
      (*cb)(NODEDATA::serialized_aov_names.c_str(), bucket_xo, bucket_yo, bucket_size_x, bucket_size_y, buffer);
   }
}
 
driver_process_bucket
{
   
}

driver_close
{

}

node_finish
{

}
 
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