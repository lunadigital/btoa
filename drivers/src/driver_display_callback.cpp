#include <ai.h>
#include <vector>
 
namespace ASTR {
   static const AtString callback("callback");
};
 
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
{}

driver_needs_bucket
{
   return true;
}

driver_prepare_bucket
{}

driver_write_bucket
{
   AtString aov_name;
   int pixel_type;
   const void* bucket_data;

   AtNode* options = AiUniverseGetOptions();
   AtArray* outputs = AiNodeGetArray(options, AtString("outputs"));
   int total_aovs = AiArrayGetNumElements(outputs);

   std::vector<std::string> aovs;
   int bucket_offset = 0;
   float* buffer = (float*)AiMalloc(bucket_size_x * bucket_size_y * sizeof(float) * 4 * total_aovs);

   while(AiOutputIteratorGetNext(iterator, &aov_name, &pixel_type, &bucket_data))
   {
      aovs.push_back(aov_name.c_str());
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

   std::string aov_list;
   for (const auto &aov : aovs) aov_list += aov + "\\";

   DisplayCallback cb = (DisplayCallback) AiNodeGetPtr(node, ASTR::callback);
   if (cb)
   {
      (*cb)(aov_list.c_str(), bucket_xo, bucket_yo, bucket_size_x, bucket_size_y, buffer);
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
   node->name         = "driver_display_callback";
   node->node_type    = AI_NODE_DRIVER;
   strcpy(node->version, AI_VERSION);
   return true;
}