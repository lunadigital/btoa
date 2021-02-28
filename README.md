# Arnold for Blender #

Arnold for Blender (or BtoA) provides a bridge to the Arnold renderer from within Blender's standard interface. BtoA is an unofficial Blender add-on and is not affiliated with Autodesk or Arnold.

## Features ##

<table style="width: 100%; margin-bottom: 25px;">
  <tr>
    <th style="width: 30%;">Geometry & Objects</th>
    <td>
        <ul style="list-style: none;">
            <li>Cameras</li>
            <li>Mesh objects</li>
            <li>Curves</li>
            <li>Fonts</li>
        </ul>
    </td>
  </tr>
  <tr>
    <th style="width: 30%;">Lights</th>
    <td>
        <ul style="list-style: none;">
            <li>Point light</li>
            <li>Distant light</li>
            <li>Spot light</li>
            <li>Quad light</li>
            <li>Disk light</li>
            <li>Cylinder light</li>
        </ul>
    </td>
  </tr>
  <tr>
    <th style="width: 30%;">Surface Shaders</th>
    <td>
        <ul style="list-style: none;">
            <li>Ambient occlusion<li>
            <li>Car paint</li>
            <li>Flat</li>
            <li>Lambert</li>
            <li>Matte<li>
            <li>Shadow matte</li>
            <li>Standard surface<li>
            <li>Wireframe<li>
        </ul>
    </td>
  </tr>
  <tr>
    <th style="width: 30%;">Texture Shaders</th>
    <td>
        <ul style="list-style: none;">
            <li>Cell noise</li>
            <li>Checkerboard</li>
            <li>Image</li>
        </ul>
    </td>
  </tr>
  <tr>
    <th style="width: 30%;">Color Shaders</th>
    <td>
        <ul style="list-style: none;">
            <li>Color correct</li>
        </ul>
    </td>
  </tr>
  <tr>
    <th style="width: 30%;">Utility Shaders</th>
    <td>
        <ul style="list-style: none;">
            <li>UV projection</li>
            <li>Coordinate space (convenience node)</li>
        </ul>
    </td>
  </tr>
  <tr>
    <th style="width: 30%;">UI Elements</th>
    <td>
        <ul style="list-style: none;">
            <li>Arnold-dedicated material node editor</li>
            <li>Render images to Render Result window (but no viewport rendering yet)</li>
        </ul>
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