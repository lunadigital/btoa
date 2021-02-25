# Arnold for Blender #

Arnold for Blender (or BtoA) provides a bridge to the Arnold renderer from within Blender's standard interface. BtoA is an unofficial Blender add-on and is not affiliated with Autodesk or Arnold.

## Features ##

| Geometry & Objects | Lights              | Shaders            | Textures     | UI Elements                     |
| ------------------ | ------------------- | ------------------ | ------------ | ------------------------------- |
| Cameras            | Spot light          | Lambert            | Cell noise   | Material nodes                  | 
| Mesh objects       | Distant (sun) light | Standard Surface   | Checkerboard | Renders images to Render Result |
| Curves             | Spot light          | Ambient Occlusion  | Image        | No viewport rendering yet       |
| Fonts              | Quad light          | Car Paint          |              |                                 |
|                    | Disk light          | Flat               |              |                                 |
|                    | Cylinder light      | Matte              |              |                                 |
|                    |                     | Shadow matte       |              |                                 |
|                    |                     | Wireframe          |              |                                 |

## Documentation ##
For installation instructions, [visit the project wiki](https://github.com/lunadigital/btoa/wiki). Whether or not you're new to Arnold, the [Arnold documentation](https://www.arnoldrenderer.com/arnold/documentation/) should answer most of your Arnold-specific questions. We're working on documentation for BtoA, including additional wiki pages and YouTube tutorials.

## Downloads ##
Arnold for Blender (BtoA 0.1.0-alpha) is available for Windows, macOS, and Linux. [Go to the downloads page](https://github.com/lunadigital/btoa/releases).

## Support ##
Arnold for Blender (BtoA) is not affiliated with or supported by Autodesk or Arnold. For bug reports, please [open a new issue](https://github.com/lunadigital/btoa/issues) on the issue tracker - do not open issues for support questions. Instead, we recommend [joining the discussion](https://blenderartists.org/t/arnold-for-blender-0-1-0-alpha-release/1284309) on the BlenderArtist forums.

## Community ##
The best way to engage with the BtoA community is to [join the Arnold for Blender Discord server](https://discord.gg/MqZpKFtsNT).

## Requirements & Platforms ##
* Compatible with Blender 2.83 LTS or above
* Requires Arnold SDK 6.0.4.0 or above

## Example renders ##
<div style="display: flex">
<div style="flex: 1.7761; padding-right: 10px;">
<img src="https://github.com/lunadigital/btoa/raw/dev/examples/Render_002_Web.jpg" />
</div>
<div style="flex: 0.7995">
<img src="https://github.com/lunadigital/btoa/raw/dev/examples/Render_001.png" />
</div>
</div>