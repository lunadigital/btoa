# Arnold for Blender #

Arnold for Blender (or BtoA) provides a bridge to the Arnold renderer from within Blender's standard interface. BtoA is an unofficial Blender add-on and is not affiliated with Autodesk or Arnold.

## Features ##

<table style="width: 100%; margin-bottom: 25px;">
  <tr>
    <th>Geometry & Objects</th>
    <td>
        <br />
        Cameras<br />
        Mesh objects<br />
        Curves<br />
        Fonts<br />
        <br />
    </td>
  </tr>
  <tr>
    <th>Lights</th>
    <td>
        <br />
        Point light<br />
        Distant light<br />
        Spot light<br />
        Quad light<br />
        Disk light<br />
        Cylinder light<br />
        <br />
    </td>
  </tr>
  <tr>
    <th>Surface Shaders</th>
    <td>
        <br />
        Ambient occlusion<br />
        Car paint<br />
        Flat<br />
        Lambert<br />
        Matte<br />
        Shadow matte<br />
        Standard surface<br />
        Wireframe<br />
        <br />
    </td>
  </tr>
  <tr>
    <th>Texture Shaders</th>
    <td>
        <br />
        Cell noise<br />
        Checkerboard<br />
        Image<br />
        <br />
    </td>
  </tr>
  <tr>
    <th>Color Shaders</th>
    <td>
        <br />
        Color correct<br />
        <br />
    </td>
  </tr>
  <tr>
    <th>Utility Shaders</th>
    <td>
        <br />
        UV projection<br />
        Coordinate space (convenience node)<br />
        <br />
    </td>
  </tr>
  <tr>
    <th>UI Elements</th>
    <td>
        <br />
        Arnold-dedicated material node editor<br />
        Render images to Render Result window (but no viewport rendering yet)<br />
        <br />
    </td>
  </tr>
</table>

## Documentation ##
For installation instructions, [visit the project wiki](https://github.com/lunadigital/btoa/wiki). Whether or not you're new to Arnold, the [Arnold documentation](https://www.arnoldrenderer.com/arnold/documentation/) should answer most of your Arnold-specific questions. We're working on documentation for BtoA, including additional wiki pages and YouTube tutorials.

## Downloads ##
Arnold for Blender (BtoA 0.2.0-alpha) is available for Windows, macOS, and Linux. [Go to the downloads page](https://github.com/lunadigital/btoa/releases).

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