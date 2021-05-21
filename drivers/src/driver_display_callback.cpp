#include <ai.h>
 
namespace ASTR {
   static const AtString callback("callback");
   static const AtString callback_data("callback_data");
   static const AtString color_space("color_space");
};
 
AI_DRIVER_NODE_EXPORT_METHODS(DriverDisplayCallbackMtd)
 
typedef void (*DisplayCallback)(uint32_t x, uint32_t y, uint32_t width, uint32_t height, float* buffer, void* data);
 
node_parameters
{
   AiParameterPtr("callback"     , NULL  );
   AiParameterPtr("callback_data", NULL  );  // This value will be passed directly to the callback function
}
 
node_initialize
{
   AiDriverInitialize(node, false);
}
 
node_update
{
}
 
driver_supports_pixel_type
{
   switch (pixel_type)
   {
      case AI_TYPE_FLOAT:
      case AI_TYPE_RGB:
      case AI_TYPE_RGBA:
         return true;
      default:
         return false;
   }
}
 
driver_extension
{
   return NULL;
}
 
driver_open
{
}
 
driver_needs_bucket
{
   return true;
}
 
driver_prepare_bucket
{
   DisplayCallback cb = (DisplayCallback) AiNodeGetPtr(node, ASTR::callback);
 
   // Call the callback function with a NULL buffer pointer, to indicate
   // a bucket is going to start being rendered.
   if (cb)
   {
      void *cb_data = AiNodeGetPtr(node, ASTR::callback_data);
      (*cb)(bucket_xo, bucket_yo, bucket_size_x, bucket_size_y, NULL, cb_data);
   }
}
 
driver_write_bucket
{
   int pixel_type;
   const void* bucket_data;
 
   // Get the first AOV layer
   if (!AiOutputIteratorGetNext(iterator, NULL, &pixel_type, &bucket_data))
      return;
 
   // Allocates memory for the final pixels in the bucket
   //
   // This memory is not released here. The client code is
   // responsible for its release, which must be done using
   // the AiFree() function in the Arnold API
   float* buffer = (float*)AiMalloc(bucket_size_x * bucket_size_y * sizeof(float) * 4);
 
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
 
         float* target = &buffer[idx * 4];
         target[0] = source.r;
         target[1] = source.g;
         target[2] = source.b;
         target[3] = source.a;
      }
   }
 
   // Sends the buffer with the final pixels to the callback for display.
   //
   // The callback receives ownership over this buffer, so it must
   // release it when it is done with it, using the AiFree() function
   // in the Arnold API.
   //
   // The reason for doing this is to decouple this code from the visualization
   // process, so, as soon as the buffer is ready, this driver will send it to
   // the callback and return to the rendering process, which will continue
   // asynchronously, in parallel with the visualization of the bucket, carried
   // out by the client code.
   //
   DisplayCallback cb = (DisplayCallback) AiNodeGetPtr(node, ASTR::callback);
   if (cb)
   {
      void *cb_data = AiNodeGetPtr(node, ASTR::callback_data);
      (*cb)(bucket_xo, bucket_yo, bucket_size_x, bucket_size_y, buffer, cb_data);
   }
}
 
driver_process_bucket
{
   // Use this instead of driver_write_bucket for best performance, if your
   // callback handling code is thread safe.
}
 
driver_close
{
}
 
node_finish
{
}
 
node_loader
{
   if (i>0)
      return false;
 
   node->methods      = DriverDisplayCallbackMtd;
   node->name         = "driver_display_callback";
   node->node_type    = AI_NODE_DRIVER;
   strcpy(node->version, AI_VERSION);
   return true;
}