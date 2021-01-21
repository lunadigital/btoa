# Arnold for Blender #

BtoA is an unofficial Blender add-on for Autodesk's Arnold render engine.

### Current functionality ###

![Blender scene rendered in Arnold](https://bitbucket.org/luna-digital/btoa/raw/9682a2886a11e27cdc810ea479c32f4cd4822860/examples/polygonal_geometry.jpg)

* BtoA now reads in polygon objects from the Blender scene and syncs with Blender's camera. All objects are shaded with the same red shader, and there is no light support yet (the light you see in the render is hard-coded).
* Images are rendered to your home directory and do not display in the Blender UI yet.

We're in the early days of development, and will be updating code publicly as we make progress. We guarantee that the code you see here will always be up-to-date with what we're working on internally.

The add-on automatically detects the Arnold installation from the $ARNOLD_ROOT environment variable. If this variable is not set, you can manually set the installation location in the add-on preferences.

### Getting involved ###
This add-on is developed and maintained by Aaron Powell at Luna Digital, Ltd. (aaron@lunadigital.tv). Feel free to reach out if you're interested in testing or contributing!