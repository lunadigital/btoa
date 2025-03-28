# Changelog

## 0.6.0

### General

- Complete re-write of BtoA rendering engine code from the ground up, unifying the code for IPR/viewport and batch rendering
- Cameras now expose clip start and clip end values in the Properties panel
- Drops support for Blender 3.x
- Additional misc. bug fixes and optimations

### Preferences

- Arnold can now be installed through BtoA's add-on preferences, simplifying the installation process

### Nodes

- UI cleanup and optimization
- Adds AiFloat, AiVector, AiVectorToRGB, AiRGBToVector, Separate RGBA, AiFloatToRGB, Ray Switch RGBA, Ray Switch Shader, RGB(A)ToFloat, State Int, State Vector, AiSeparateXYZ nodes

### Rendering

- Adds support for AOV rendering
- Standard Surface shader now aware of scene scale, fixing scale-dependent attributes like SSS
- Camera exposure now respected in IPR renders
- Adds render pause/resume button to IPR renders
- Lights now change type during IPR renders (i.e., changing from spot light to area light)

## 0.4.6

- Upgrades BtoA from the old BGL module to the newer GPU module for IPR rendering. Because of this change, Blender 3.0 is now the minimum required version needed to run BtoA.
- Adds an IPR render resolution dropdown to the 3D viewport. Users can choose between 100%, 75%, 50%, and 25% fractional resolutions for faster IPR rendering.
- Adds support for OpenImageDenoise (OIDN) and OptiX denoise imagers in the viewport (but not in final renders yet)
- Adds support for portal lights
- Adds support for packed image textures
- Removes the custom Filmic config we used to ship with BtoA, opting for Blender's internal config instead. Arnold 7 must have fixed the namespace conflict and it's no longer an issue.
- Fixes IPR rendering issues with orthographic cameras
- Render options, light settings, and viewport focal length/clipping values all update interactively during IPR.
- Resizing windows during an IPR render is much more stable.
- Adds logging options and the ability to save Arnold logs to a file in the add-on preferences.
- Fixes bug that didn't change world material node graphs when switching between them in the UI
- Fixes Standard Surface material presets
- Adds feature overrides to the render Properties panel
- Fixes displacement render error
- Additional bug fixes

## 0.4.5

This is an interim release that addresses many of the issues in the 0.4.4 alpha while we continue to work on the 0.5.0 beta.

### General
- Includes bug fixes for Arnold 7 support (Arnold 7 is now the minimum supported version)
- Adds support for Blender 3.*x*

### Rendering
- Includes a number of IPR bug fixes
- "Abort on license fail" and "Render with watermarks" checkboxes are now available in the add-on preferences
- "Ignore missing textures" checkbox has been moved from a per-node option to a global setting in the add-on preferences
- IPR rendering now updates more frequently during the final render pass so it doesn't feel like it gets stuck
- Adds support for orthographic camera rendering in viewport
- Adds basic support for instanced polymeshes and lights
- Fixes viewport display and scaling issues with Arnold lights in IPR
- Render layers now support the holdout flag
- Linked libraries properly support the "indirect only" and "holdout" flags

### Materials & nodes
- Cleans up node presentation in the node graph and "add" menu
- Includes bug fixes for materials so they don't accidentally show up on the wrong objects
- New nodes
    - Range
    - Two-sided material
    - Bump 3D
    - Standard hair
- "Constant" color nodes now work as expected when daisy-chained together
- The "physical sky" node now has a vector direction control you can use to change the orientation of the sun. You can override this setting with an object in the 3D scene like before as well.

## 0.4.4

This is a breaking release of BtoA with a *ton* of new features, including IPR/viewport rendering, render regions, adaptive subdivisions, displacement, and more.

### General
- Added support for Blender 2.93
- Added support for Arnold 7
- Added support for GPU rendering

### Rendering
- Added initial support for IPR/viewport rendering. Most of it works but there are a few bugs to iron out still. These will be addressed in future interim releases.
- BtoA now respects View Layers like Cycles and EEVEE, including "indirect only" visibility
- Added support for View Layer material overrides
- Added support for render regions
- BtoA now supports per-face materials like Cycles and EEVEE
- Objects now have per-object visibility settings (camera, diffuse, specular, etc)
- Added support for film transparency checkbox
- Added support for additional camera types (orthographic, cylindrical, etc)
- Added support for displacement mapping
- Added support for adaptive subdivisions

### Materials & nodes
- AiStandardSurface now comes with a nice list of material presets
- Added new nodes
    - Normal map
    - Round corners
    - Float-to-RGB
    - Float-to-RGBA
    - Multiply
    - Facing Ratio
    - Layer Float
    - Layer RGBA
    - Mix RGBA
    - Physical Sky
    - Color constant
    - Color jitter
    - Composite
    - Shuffle
- World select dropdown now works as expected
- AiShadowMatte now has "background" and "background color" sockets
- Image textures now respect Blender's internal color space settings (no more manual typing!)
- BtoA now supports multiple material outputs in a node tree

### UI Improvements
- AiSkydome now lets you use an object in your scene to control its orientation
- Material link dropdown now shows icon instead of word to match Cycles

## 0.3.0

This release focused on fixing production bugs, UI cleanup, and adding new nodes and features.

### General
- Added support for camera and deformation motion blur
- Render progress bar now updates with render
- Linked library objects now render properly
- Images in linked library materials now resolve their file paths properly on render

### Camera settings
- Depth of field toggle now works properly
- Aperture rotation is now measured in degrees
- Aperture size is now measured according to your scene units
- Focus distance controller now works as expected

### Materials & nodes
- Added support for HDR/world lighting with Arnold's Skydome light
- Materials now respect Data/Object assignments in the Material properties panel
- The empty Arnold World Editor was merged with the existing Arnold Shader editor and given a major UI/UX face-lift to better match Blender defaults
- Cleaned up node UI a bit, opting for wider nodes by default when needed
- Node parameters now show up under the Materials and World properties panel
- Added new nodes
    - Bump2d
    - Mix shader
    - Skydome
- Added new sockets to AiStandardSurface node
    - Thin film parameters
    - Sheen parameters
    - Normal
    - Tangent
    - Coat normal
    - Dielectric priority (requires Arnold SDK 6.1+)
- Added normal map socket to AiAmbientOcclusion, AiLambert
- Added new sockets to AiCarPaint
    - Flake coordinate space
    - Coat normal
- Updated camera properties panels to better reflect Blender defaults

And many more bug fixes!

## 0.2.0

This alpha release focused largely on bug fixes and some small new features after the initial alpha release.

- We completely refactored how BtoA talks to the Arnold SDK in an effort to move toward a truly GPL-compliant add-on. BtoA no longer makes direct calls to the Arnold API and instead interacts with a `btoa` middle-man module, passing data as generic Python objects (strings, ints, floats, lists, etc). We understand this alone may not be enough and are actively talking with Autodesk and other parties to ensure we do everything we can to be compliant with the license.

- Added support for:
    - Fonts
    - Curves
    - Checkerboard shader
    - Cell noise shader
    - Color correction shader

- BtoA now supports Arnold 6.0.1.0 through 6.2.0.1 out-of-the-box.

- Fixes bug that kept users from setting the path to their Arnold SDK installation in the add-on preferences.

- AiStandardSurface node now supports "subsurface type", "transmission depth" parameters.

- Cylinder light gizmo now scales to fit the size of the underlying rectangle light for better viewport visualization.

- Fixes bug that let Arnold nodes show up in non-Arnold node editor spaces.

- Adds depth-of-field focus object to camera panel for better DOF rendering support.

- Light shadow color now renders properly.

- Other minor bug fixes

## 0.1.0

This is the first publicly available alpha meant for community testing.

- Supported on Windows, macOS, and Linux (RedHat Enterprise or compatible)
- Includes support for geometry meshes and the modifier stack.
- Basic light support, including point lights, spot lights, distant lights, quad lights, disk lights, and cylinder lights.
- Supports rendering to the Render Result window, but not in  the viewport yet.
- Basic material/node support
    - Ambient occlusion shader
    - Car paint shader
    - Flat shader
    - Lambert shader
    - Standard surface shader
    - Matte shader
    - Shadow matte shader
    - Wireframe shader
    - Image shader
    - UV projection shader
    - Coordinate space convenience node
- Basic color management support, defaulting to Filmic if no custom OCIO config is set.
- Respects visibility settings in Outliner for rendering