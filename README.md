# Arnold for Blender #

BtoA is an unofficial Blender add-on for Autodesk's Arnold render engine.

We're in the early days of development, and will be updating code publicly as we make progress. We guarantee that the code you see here will always be up-to-date with what we're working on internally.

### Features ###

| Geometry & Objects              | Lights              | Shaders            | Textures | UI Elements                     |
| ------------------------------- | ------------------- | ------------------ | -------- | ------------------------------- |
| Cameras                         | Spot light          | Lambert            | Image    | Material nodes                  | 
| Polygon meshes                  | Distant (sun) light | Standard Surface   |          | Renders images to Render Result |
| (No modifier stack support yet) | Spot light          | Ambient Occlusion  |          | No viewport rendering yet       |
|                                 | Quad light          | Car Paint          |          |                                 |
|                                 | Disk light          | Flat               |          |                                 |
|                                 | Cylinder light      | Matte              |          |                                 |
|                                 |                     | Shadow matte       |          |                                 |
|                                 |                     | Wireframe          |          |                                 |

### Example renders ###
![Blender scene rendered in Arnold](https://bitbucket.org/luna-digital/btoa/raw/6531748064be792af98c537d1816d6841bf029e8/examples/lambert.png)
![Arnold light types in Blender](https://bitbucket.org/luna-digital/btoa/raw/8ca83472a8ac33bc0f9b8238c0c882b7e4828925/examples/arnold_light_types.jpg)
