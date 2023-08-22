# Arnold for Blender

Arnold for Blender (BtoA) is a community-developed Blender add-on for the Arnold renderer.

## Unstable Development Branch
In an effort to become fully GPL-compliant, BtoA 0.6.0 is being written from the ground up to follow a client-server model. The new add-on will consist of two major components.

### Arnold RenderServer

RenderServer is a standalone application that can load and render both Arnold Scene Source (.ass) and Universal Scene Description (.usd) scene files. It includes a simplified [RenderView](https://help.autodesk.com/view/ARNOL/ENU/?guid=arnold_for_maya_rendering_am_Arnold_RenderView_Window_html)-like GUI for easy scene rendering outside of Blender, but can also be run headless from the commandline.

Arnold RenderServer's distinguishing feature is the ability to load and manipulate render sessions over TCP.

Arnold RenderServer is licensed under the Apache 2.0 license.

### BtoA Blender Add-on

The BtoA "bridge" add-on will supply the necessary UI and communication components for Blender scenes to work with Arnold RenderServer. Although most of the code will be written in Python, a number of performance-critical functions will be ported to C/CTypes.

The BtoA add-on is licensed under the GPL 3.0 license.

## Building BtoA
In the past, using BtoA was as easy as downloading the Git repo as a zip file and installing in Blender, even for non-release versions. Moving forward, BtoA will need to be built from source using CMake. As our build process develops we will post instructions on how to build BtoA 0.6.0 here.

 ## Legal

Arnold for Blender (BtoA) is developed by Luna Digital, Ltd. and the BtoA community. We are not affiliated with or supported by Autodesk or the Arnold development team.