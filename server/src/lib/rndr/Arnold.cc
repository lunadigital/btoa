#include <ai.h>
#include "Arnold.h"
#include "../gui/MainWindow.h"

void qRenderCallback(uint32_t x, uint32_t y, uint32_t width, uint32_t height, float* buffer, void* data)
{
    if (!buffer) return;

    QtAovBuffer *qtBuffer = &MainWindow::buffer;
    QtAov *beauty = qtBuffer->findAovByName("beauty");
    int index = 0;

    for (int by = y; by < y + height; by++)
    {
        for (int bx = x; bx < x + width; bx++)
        {
            beauty->setPixelColor(
                bx,
                by,
                QColor(
                    AiQuantize8bit(bx, by, 0, buffer[index], true),
                    AiQuantize8bit(bx, by, 1, buffer[index + 1], true),
                    AiQuantize8bit(bx, by, 2, buffer[index + 2], true),
                    AiQuantize8bit(bx, by, 3, buffer[index + 3], true)
                )
            );

            index += 4;
        }
    }

    beauty->redraw = true;
    
    AiFree(buffer);
}

void renderSampleScene()
{
    AiBegin();

    // create anew universe to create objects in
    AtUniverse *universe = AiUniverse();
    // start an Arnold session, log to both a file and the console
    AtRenderSession *session = AiRenderSession(universe,  AI_SESSION_BATCH);
    AiMsgSetLogFileName("scene1.log");
    AiMsgSetConsoleFlags(universe, AI_LOG_ALL);
    AiMsgSetLogFileFlags(universe, AI_LOG_ALL);
    // create a sphere geometric primitive
    AtNode *sph = AiNode(universe, AtString("sphere"),  AtString("mysphere"));
    AiNodeSetVec(sph, AtString("center"), 0.0f, 4.0f, 0.0f);
    AiNodeSetFlt(sph, AtString("radius"), 4.0f);

    // create a polymesh, with UV coordinates
    AtNode *mesh = AiNode(universe, AtString("polymesh"), AtString("mymesh"));
    AtArray* nsides_array = AiArray(1, 1, AI_TYPE_UINT, 4);
    AiNodeSetArray(mesh, AtString("nsides"), nsides_array);
    AtArray* vlist_array = AiArray(12, 1, AI_TYPE_FLOAT, -10.f, 0.f, 10.f, 10.f, 0.f, 10.f, -10.f, 0.f, -10.f, 10.f, 0.f, -10.f);
    AiNodeSetArray(mesh, AtString("vlist"), vlist_array);
    AtArray* vidxs_array = AiArray(4, 1, AI_TYPE_UINT, 0, 1, 3, 2);
    AiNodeSetArray(mesh, AtString("vidxs"), vidxs_array);
    AtArray* uvlist_array = AiArray(8, 1, AI_TYPE_FLOAT, 0.f, 0.f, 1.f, 0.f, 1.f, 1.f, 0.f, 1.f);
    AiNodeSetArray(mesh, AtString("uvlist"), uvlist_array);
    AtArray* uvidxs_array = AiArray(4, 1, AI_TYPE_UINT, 0, 1, 2, 3);
    AiNodeSetArray(mesh, AtString("uvidxs"), uvidxs_array);

    // create a red standard surface shader
    AtNode *shader1 = AiNode(universe, AtString("standard_surface"), AtString("myshader1"));
    AiNodeSetRGB(shader1, AtString("base_color"), 1.0f, 0.02f, 0.02f);
    AiNodeSetFlt(shader1, AtString("specular"), 0.05f);

    // create a textured standard surface shader
    AtNode *shader2 = AiNode(universe, AtString("standard_surface"), AtString("myshader2"));
    AiNodeSetRGB(shader2, AtString("base_color"), 1.0f, 0.0f, 0.0f);

    // create an image shader for texture mapping
    //AtNode *image = AiNode(universe, AtString("image"), AtString("myimage"));
    //AiNodeSetStr(image, AtString("filename"), AtString("arnold.png"));
    //AiNodeSetFlt(image, AtString("sscale"), 4.f);
    //AiNodeSetFlt(image, AtString("tscale"), 4.f);
    // link the output of the image shader to the color input of the surface shader
    //AiNodeLink(image, AtString("base_color"), shader2);

    // assign the shaders to the geometric objects
    AiNodeSetPtr(sph, AtString("shader"), shader1);
    AiNodeSetPtr(mesh, AtString("shader"), shader2);

    // create a perspective camera
    AtNode *camera = AiNode(universe, AtString("persp_camera"), AtString("mycamera"));
    // position the camera (alternatively you can set 'matrix')
    AiNodeSetVec(camera, AtString("position"), 0.f, 10.f, 35.f);
    AiNodeSetVec(camera, AtString("look_at"), 0.f, 3.f, 0.f);
    AiNodeSetFlt(camera, AtString("fov"), 45.f);

    // create a point light source
    AtNode *light = AiNode(universe, AtString("point_light"), AtString("mylight"));
    // position the light (alternatively use 'matrix')
    AiNodeSetVec(light, AtString("position"), 15.f, 30.f, 15.f);
    AiNodeSetFlt(light, AtString("intensity"), 4500.f); // alternatively, use 'exposure'
    AiNodeSetFlt(light, AtString("radius"), 4.f); // for soft shadows

    // get the global options node and set some options
    AtNode *options = AiUniverseGetOptions(universe);
    AiNodeSetInt(options, AtString("AA_samples"), 8);
    AiNodeSetInt(options, AtString("xres"), 960);
    AiNodeSetInt(options, AtString("yres"), 540);
    AiNodeSetInt(options, AtString("GI_diffuse_depth"), 4);
    // set the active camera (optional, since there is only one camera)
    AiNodeSetPtr(options, AtString("camera"), camera);

    // create an output driver node 
    AtNode *driver = AiNode(universe, AtString("driver_display_callback"), AtString("mydriver"));
    AiNodeSetPtr(driver, AtString("callback"), (void *)qRenderCallback);

    // create a gaussian filter node
    AtNode *filter = AiNode(universe, AtString("gaussian_filter"), AtString("myfilter"));

    // assign the driver and filter to the main (beauty) AOV,
    // which is called "RGBA" and is of type RGBA
    AtArray *outputs_array = AiArrayAllocate(1, 1, AI_TYPE_STRING);
    AiArraySetStr(outputs_array, 0, AtString("RGBA RGBA myfilter mydriver"));
    AiNodeSetArray(options, AtString("outputs"), outputs_array);

    // finally, render the image!
    AiRender(session, AI_RENDER_MODE_CAMERA);

    // ... or you can write out an .ass file instead
    // AtParamValueMap* params = AiParamValueMap();
    // AiParamValueMapSetInt(params, AtString("mask"), AI_NODE_ALL);
    // AiSceneWrite(universe, "scene1.ass", params); 
    // AiParamValueMapDestroy(params);

    // Arnold session shutdown
    AiRenderSessionDestroy(session);
    AiUniverseDestroy(universe);

    AiEnd();
}

void renderAssScene(std::string filename)
{
    std::string base = "/home/aaronpowell/Git/btoa/server/examples/";
    AiBegin(AI_SESSION_INTERACTIVE);

    AtParamValueMap* params = AiParamValueMap();
    AiParamValueMapSetInt(params, AtString("mask"), AI_NODE_ALL);
    AiSceneLoad(NULL, (base + filename).c_str(), params);
    AiParamValueMapDestroy(params);

    AtNode *options = AiUniverseGetOptions(NULL);
    AiNodeSetInt(options, AtString("AA_samples"), 8);
    AiNodeSetInt(options, AtString("xres"), 960);
    AiNodeSetInt(options, AtString("yres"), 540);

    AtNode *driver = AiNode(NULL, AtString("driver_display_callback"), AtString("mydriver"));
    AiNodeSetPtr(driver, AtString("callback"), (void *)qRenderCallback);

    AtNode *filter = AiNode(NULL, AtString("gaussian_filter"), AtString("myfilter"));

    AtArray *outputs_array = AiArrayAllocate(1, 1, AI_TYPE_STRING);
    AiArraySetStr(outputs_array, 0, AtString("RGBA RGBA myfilter mydriver"));
    AiNodeSetArray(options, AtString("outputs"), outputs_array);

    AiRenderBegin(NULL, AI_RENDER_MODE_CAMERA);

    //AiEnd();
}